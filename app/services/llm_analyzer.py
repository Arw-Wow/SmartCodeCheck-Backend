import json
import re
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.models import AnalysisRequest, AnalysisResponse, ComparisonRequest, ComparisonResponse, IssueDetail

class LLMService:
    def __init__(self):
        # 初始化 OpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None
        )

    def _clean_json_string(self, json_str: str) -> str:
        """清理 LLM 返回的 Markdown 格式，提取纯 JSON"""
        # 移除 ```json 和 ``` 标记
        cleaned = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
        cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def analyze_code(self, req: AnalysisRequest) -> AnalysisResponse:
        system_prompt = """
        你是一个资深的代码审计专家。请根据用户提供的代码和维度进行分析。
        必须严格按照 JSON 格式返回结果，不要包含任何额外的解释文本。
        返回格式模板：
        {
            "score": <0-100的整数>,
            "issues": [
                {
                    "dimension": "<维度名>",
                    "type": "<Error/Warning/Info>",
                    "description": "<问题描述>",
                    "line": <行号int, 如果无法确定填null>,
                    "suggestion": "<修改建议>"
                }
            ]
        }
        """
        
        user_prompt = f"""
        编程语言: {req.language if req.language == 'Auto' else '根据代码内容判断'}
        检测维度: {', '.join(req.dimensions)}
        代码内容:
        {req.code_content}
        """

        try:
            response = await self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, # 低温度保证输出稳定
                response_format={"type": "json_object"} # 强制 JSON 模式 (仅部分模型支持，如不支持请注释掉)
            )
            
            content = response.choices[0].message.content
            data = json.loads(self._clean_json_string(content))
            
            return AnalysisResponse(**data)
            
        except Exception as e:
            print(f"LLM Error: {e}")
            # 发生错误时的兜底返回，防止前端崩溃
            return AnalysisResponse(
                score=0,
                issues=[IssueDetail(
                    dimension="系统",
                    type="Error",
                    description=f"模型分析失败: {str(e)}",
                    suggestion="请检查 API Key 配置或网络连接"
                )]
            )

    async def compare_codes(self, req: ComparisonRequest) -> ComparisonResponse:
        system_prompt = """
        你是代码对比专家。请对比两段代码的优劣。
        必须严格按照 JSON 格式返回结果。
        返回格式模板：
        {
            "summary": "<一句话总结对比结果>",
            "score_a": <0-100>,
            "score_b": <0-100>,
            "dimension_scores": {
                "<维度名>": [<分数A>, <分数B>] 
            }
        }
        """
        
        user_prompt = f"""
        编程语言: {req.language if req.language == 'Auto' else '根据代码内容判断'}
        检测维度: {', '.join(req.dimensions)}
        
        [代码 A]:
        {req.code_a}
        
        [代码 B]:
        {req.code_b}
        """

        try:
            response = await self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(self._clean_json_string(content))
            
            # 这里简化处理，details_a/b 可以设为 None，或者另外调用 analyze_code 获取详情
            return ComparisonResponse(
                summary=data['summary'],
                score_a=data['score_a'],
                score_b=data['score_b'],
                dimension_scores=data['dimension_scores'],
                details_a=None,
                details_b=None
            )
            
        except Exception as e:
            return ComparisonResponse(
                summary=f"对比失败: {str(e)}",
                score_a=0, 
                score_b=0, 
                dimension_scores={}
            )

llm_service = LLMService()