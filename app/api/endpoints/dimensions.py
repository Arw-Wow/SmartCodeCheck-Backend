from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.core.database import get_db
from app.core import models
from app.models.user import User, CustomDimension

router = APIRouter()

@router.get("/", response_model=List[models.DimensionOut])
def get_my_dimensions(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """获取当前用户的所有自定义维度"""
    return current_user.dimensions

@router.post("/", response_model=models.DimensionOut)
def create_dimension(
    dim_in: models.DimensionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """创建新的自定义维度"""
    # 查重：同一个用户不能有同名的维度
    existing = db.query(CustomDimension).filter(
        CustomDimension.user_id == current_user.id,
        CustomDimension.name == dim_in.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Dimension with this name already exists")

    new_dim = CustomDimension(
        name=dim_in.name,
        description=dim_in.description,
        user_id=current_user.id
    )
    db.add(new_dim)
    db.commit()
    db.refresh(new_dim)
    return new_dim

@router.delete("/{name}")
def delete_dimension(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """根据名称删除维度"""
    # 查找
    dim = db.query(CustomDimension).filter(
        CustomDimension.user_id == current_user.id,
        CustomDimension.name == name
    ).first()

    if not dim:
        raise HTTPException(status_code=404, detail="Dimension not found")

    db.delete(dim)
    db.commit()
    return {"status": "success"}