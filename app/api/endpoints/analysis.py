from fastapi import APIRouter, HTTPException, Depends
from app.core.models import AnalysisRequest, AnalysisResponse, ComparisonRequest, ComparisonResponse
from app.services.llm_analyzer import llm_service
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code_endpoint(
    request: AnalysisRequest,
    current_user: User = Depends(deps.get_current_user) # 新增：必须登录才能调用
):
    """
    单代码质量检测接口 (需认证)
    """
    if not request.code_content.strip():
        raise HTTPException(status_code=400, detail="Code content cannot be empty")
        
    return await llm_service.analyze_code(request)

@router.post("/compare", response_model=ComparisonResponse)
async def compare_codes_endpoint(
    request: ComparisonRequest,
    current_user: User = Depends(deps.get_current_user) # 新增：必须登录才能调用
):
    """
    双代码对比接口 (需认证)
    """
    return await llm_service.compare_codes(request)