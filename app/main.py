from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import SQLAlchemyError
import os
import time

from app.config import settings
from app.infrastructure.database.database import init_db
from app.api import auth, tasks, subtitles, task_subtitles

# 创建FastAPI应用
app = FastAPI(
    title="Subtitle API",
    description="基于Whisper的音视频字幕生成API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为特定的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 自定义异常处理
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理SQLAlchemy异常"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error", "error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理一般异常"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# 自定义OpenAPI文档
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# 依赖项覆盖：替换tasks.py中的临时依赖
def override_get_current_user(current_user: auth.UserResponse = auth.Depends(auth.get_current_active_user)):
    """覆盖获取当前用户的依赖"""
    return current_user


# 注册路由
app.include_router(auth.router, prefix=settings.API_PREFIX)

# 先注册tasks路由，然后覆盖依赖
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.dependency_overrides[tasks.get_current_user] = override_get_current_user

app.include_router(subtitles.router, prefix=settings.API_PREFIX)
app.include_router(task_subtitles.router, prefix=settings.API_PREFIX)


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to Subtitle API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的事件"""
    # 初始化数据库
    init_db()
    
    # 创建必要的目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.WHISPER_MODEL_PATH, exist_ok=True)
    
    print("Application startup complete")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的事件"""
    print("Application shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)