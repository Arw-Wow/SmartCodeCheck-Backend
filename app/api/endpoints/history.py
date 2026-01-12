from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.api import deps
from app.core.database import get_db
from app.core import models
from app.models.user import User, AnalysisHistory

router = APIRouter()

MAX_HISTORY_COUNT = 10

@router.get("/", response_model=List[models.HistoryOut])
def get_history(
    type: str = None, # 可选筛选 detection 或 comparison
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """获取当前用户的历史记录，按时间倒序"""
    query = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id)
    if type:
        query = query.filter(AnalysisHistory.type == type)
    
    return query.order_by(desc(AnalysisHistory.created_at)).all()

@router.post("/", response_model=models.HistoryOut)
def create_history(
    history_in: models.HistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """创建历史记录，如果超过10条则删除最旧的"""
    
    # 1. 检查当前类型的记录数量
    count = db.query(AnalysisHistory).filter(
        AnalysisHistory.user_id == current_user.id,
        AnalysisHistory.type == history_in.type
    ).count()

    # 2. 如果达到上限，删除最旧的一条
    if count >= MAX_HISTORY_COUNT:
        oldest = db.query(AnalysisHistory).filter(
            AnalysisHistory.user_id == current_user.id,
            AnalysisHistory.type == history_in.type
        ).order_by(AnalysisHistory.created_at.asc()).first()
        
        if oldest:
            db.delete(oldest)
            # flush 确保删除操作在添加之前被处理
            db.flush()

    # 3. 添加新记录
    new_record = AnalysisHistory(
        user_id=current_user.id,
        type=history_in.type,
        data=history_in.data
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.delete("/{id}")
def delete_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """删除指定历史记录"""
    record = db.query(AnalysisHistory).filter(
        AnalysisHistory.id == id,
        AnalysisHistory.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="History not found")
    
    db.delete(record)
    db.commit()
    return {"status": "success"}