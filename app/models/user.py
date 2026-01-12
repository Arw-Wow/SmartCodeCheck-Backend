from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON
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
    # 历史记录关联
    history_records = relationship("AnalysisHistory", back_populates="owner", cascade="all, delete-orphan")

class CustomDimension(Base):
    __tablename__ = "custom_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)       # 维度名称，如 "代码风格"
    description = Column(String)            # 维度定义
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="dimensions")
    
# 历史记录模型
class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, index=True) # "detection" 或 "comparison"
    
    # 使用 JSON 类型存储完整的状态（包括代码、配置、结果）
    # SQLite (新版), PostgreSQL, MySQL 5.7+ 都支持 JSON
    data = Column(JSON, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="history_records")