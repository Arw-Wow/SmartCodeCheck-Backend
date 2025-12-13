import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartCodeCheck API"
    VERSION: str = "1.0.0"
    
    # API 配置
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: Optional[str] = None
    MODEL_NAME: str = "deepseek-chat" # 或者 gpt-4o, deepseek-chat
    
    # CORS 配置 (解析 JSON 字符串为列表)
    # 默认允许常见的本地开发端口，如果需要可通过环境变量覆盖
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()