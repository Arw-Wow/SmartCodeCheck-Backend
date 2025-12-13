from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- 请求模型 ---

class AnalysisRequest(BaseModel):
    code_content: str = Field(..., description="待检测的代码片段", min_length=1)
    language: str = Field(..., description="编程语言", example="Python")
    dimensions: List[str] = Field(..., description="检测维度", example=["correctness", "security"])
    custom_definitions: Dict[str, str] = {}   # 接收自定义维度的定义 { "维度名": "详细定义" }
    generation_instruction: Optional[str] = Field(None, description="可选的代码生成指令，用于结合指令评估代码")
    model_name: Optional[str] = Field(None, description="可选的大模型名称；为空则使用后端默认")

class ComparisonRequest(BaseModel):
    code_a: str
    code_b: str
    language: str
    dimensions: List[str]
    custom_definitions: Dict[str, str] = {}
    generation_instruction: Optional[str] = Field(None, description="可选的统一代码生成指令，用于对比分析时参考")
    model_name: Optional[str] = Field(None, description="可选的大模型名称；为空则使用后端默认")

# --- 响应模型 (与前端一致) ---

class IssueDetail(BaseModel):
    dimension: str
    type: str = Field(..., description="Warning, Error, Info")
    description: str
    line: Optional[int] = None
    suggestion: str

class AnalysisResponse(BaseModel):
    score: int
    issues: List[IssueDetail]

class ComparisonResponse(BaseModel):
    summary: str
    score_a: int
    score_b: int
    dimension_scores: Dict[str, List[int]] # {"efficiency": [80, 90]}
    # 嵌套详细分析，可选
    details_a: Optional[AnalysisResponse] = None
    details_b: Optional[AnalysisResponse] = None