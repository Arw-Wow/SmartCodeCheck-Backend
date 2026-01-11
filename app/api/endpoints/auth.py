from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security, models
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User # 引入数据库模型
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=models.UserOut)
def register(
    user_in: models.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    用户注册接口
    """
    # 1. 检查用户名是否存在
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    
    # 2. 创建新用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=models.Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容的登录接口 (username + password -> token)
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    # 验证用户是否存在及密码是否正确
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # 生成 Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=models.UserOut)
def read_users_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    获取当前登录用户信息 (需携带 Token)
    """
    return current_user