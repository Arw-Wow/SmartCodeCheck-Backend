import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartCodeCheck API"
    VERSION: str = "1.0.0"
    
    # 仅保留敏感信息在环境变量
    OPENAI_API_KEY: str

    # --- 本地模型配置 ---
    LOCAL_LLM_BASE_URL: str = "http://localhost:8080/v1" # 默认本地地址
    LOCAL_LLM_API_KEY: str = "EMPTY"                     # 本地通常不需要 Key
    LOCAL_MODEL_NAME: str = "my-finetuned-model"         # 默认本地模型名称
    
    # CORS 配置 (解析 JSON 字符串为列表)
    # 默认允许常见的本地开发端口，如果需要可通过环境变量覆盖
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()