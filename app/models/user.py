from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 建立关联：一个用户拥有多个自定义维度
    dimensions = relationship("CustomDimension", back_populates="owner")

class CustomDimension(Base):
    __tablename__ = "custom_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)       # 维度名称，如 "代码风格"
    description = Column(String)            # 维度定义
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="dimensions")