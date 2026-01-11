from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import analysis, health, auth
from app.core.database import Base, engine
from app.api.endpoints import analysis, health, auth, dimensions

# 自动创建数据库表 (Simple Migration)
Base.metadata.create_all(bind=engine)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend for SmartCodeCheck"
    )

    # CORS 设置 - 允许前端访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(dimensions.router, prefix="/api/v1/dimensions", tags=["Dimensions"])
    app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 仅用于本地调试运行，生产环境建议使用命令行启动
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)