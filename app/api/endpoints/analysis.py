from fastapi import APIRouter, HTTPException
from app.core.models import AnalysisRequest, AnalysisResponse, ComparisonRequest, ComparisonResponse
from app.services.llm_analyzer import llm_service

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code_endpoint(request: AnalysisRequest):
    """
    单代码质量检测接口
    """
    if not request.code_content.strip():
        raise HTTPException(status_code=400, detail="Code content cannot be empty")
        
    return await llm_service.analyze_code(request)

@router.post("/compare", response_model=ComparisonResponse)
async def compare_codes_endpoint(request: ComparisonRequest):
    """
    双代码对比接口
    """
    return await llm_service.compare_codes(request)