import json
import re
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.models import AnalysisRequest, AnalysisResponse, ComparisonRequest, ComparisonResponse, IssueDetail

DEFAULT_BASE_URL = "https://api.agicto.cn/v1"
DEFAULT_MODEL = "deepseek-v3.1"

# 可选择的模型白名单
AVAILABLE_MODELS = {
    "qwen3-coder-plus",
    "gpt-5-mini",
    "gpt-5",
    "deepseek-v3.1",
    "gemini-3-pro-preview",
}

class LLMService:
    def __init__(self):
        # 1. 云端客户端
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=DEFAULT_BASE_URL
        )

        # 2. 本地客户端
        self.local_client = AsyncOpenAI(
            api_key=settings.LOCAL_LLM_API_KEY,
            base_url=settings.LOCAL_LLM_BASE_URL
        )

    def _build_dimension_instruction(self, dimensions: list, custom_defs: dict) -> str:
        """辅助函数：构建维度说明"""
        desc = f"请重点分析以下维度: {', '.join(dimensions)}。"
        if custom_defs:
            desc += "\n注意以下自定义维度的特定定义："
            for name, definition in custom_defs.items():
                if name in dimensions: # 只有当该维度被选中时才添加定义
                    desc += f"\n- 【{name}】: {definition}"
        return desc

    def _clean_json_string(self, json_str: str) -> str:
        """清理 LLM 返回的 Markdown 格式，提取纯 JSON"""
        # 移除 ```json 和 ``` 标记
        cleaned = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
        cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def analyze_code(self, req: AnalysisRequest) -> AnalysisResponse:
        # 构建包含自定义定义的 Prompt
        dim_instruction = self._build_dimension_instruction(req.dimensions, req.custom_definitions)
        
        system_prompt = """
        你是一个资深的代码审计专家。
        {dim_instruction}
        必须严格按照 JSON 格式返回结果，不要包含任何额外的解释文本。
        返回格式模板：
        {{
            "score": <0-100的整数>,
            "issues": [
                {{
                    "dimension": "<维度名>",
                    "type": "<Error/Warning/Info>",
                    "description": "<问题描述>",
                    "line": <行号int, 如果无法确定填null>,
                    "suggestion": "<修改建议>"
                }}
            ]
        }}
        """.format(dim_instruction=dim_instruction)
        
        instruction_part = ""
        if getattr(req, 'generation_instruction', None):
            instruction_part = f"\n请结合以下代码指令进行分析：\n{req.generation_instruction}\n"

        user_prompt = f"""
        编程语言: {req.language if req.language != 'Auto' else '根据代码内容判断'}
        检测维度: {', '.join(req.dimensions)}
        {instruction_part}
        代码内容:
        {req.code_content}
        """

        try:
            # --- 模型与客户端选择逻辑 ---
            req_model = getattr(req, 'model_name', None)
            
            # 默认情况：使用云端客户端和默认模型
            target_client = self.client
            model_to_use = DEFAULT_MODEL
            
            # 判断 1: 如果用户指定了本地模型名称 (在 .env 中配置的名字)
            if req_model == settings.LOCAL_MODEL_NAME:
                target_client = self.local_client
                model_to_use = settings.LOCAL_MODEL_NAME
                print(f"正在使用本地模型: {model_to_use}")
                
            # 判断 2: 如果用户指定了云端白名单内的模型
            elif req_model and req_model in AVAILABLE_MODELS:
                model_to_use = req_model
            # -----------------------------------

            response = await target_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"} 
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
        # 构建包含自定义定义的 Prompt
        dim_instruction = self._build_dimension_instruction(req.dimensions, req.custom_definitions)

        system_prompt = """
        你是代码对比专家。
        {dim_instruction}
        必须严格按照 JSON 格式返回结果。
        返回格式模板：
        {{
            "summary": "<一句话总结对比结果>",
            "score_a": <0-100>,
            "score_b": <0-100>,
            "dimension_scores": {{
                "<维度名>": [<分数A>, <分数B>] 
            }}
        }}
        """.format(dim_instruction=dim_instruction)
        
        instruction_part = ""
        if getattr(req, 'generation_instruction', None):
            instruction_part = f"\n请结合以下代码指令进行分析：\n{req.generation_instruction}\n"

        user_prompt = f"""
        编程语言: {req.language if req.language != 'Auto' else '根据代码内容判断'}
        检测维度: {', '.join(req.dimensions)}
        {instruction_part}
        
        [代码 A]:
        {req.code_a}
        
        [代码 B]:
        {req.code_b}
        """

        try:
            req_model = getattr(req, 'model_name', None)
            target_client = self.client
            model_to_use = DEFAULT_MODEL
            
            if req_model == settings.LOCAL_MODEL_NAME:
                target_client = self.local_client
                model_to_use = settings.LOCAL_MODEL_NAME
            elif req_model and req_model in AVAILABLE_MODELS:
                model_to_use = req_model

            response = await target_client.chat.completions.create(
                model=model_to_use, 
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