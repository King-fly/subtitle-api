import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path

from app.config import settings
from app.infrastructure.database.database import get_db
from app.infrastructure.database.repositories.task_repository import TaskRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.application.task_service import TaskService
from app.application.auth_service import AuthService
from app.schemas.task import (
    TaskCreate, TaskResponse, TaskListResponse, TaskStatusResponse,
    TaskPriorityUpdate, TaskCreateResponse, TaskStatus
)
from app.schemas.auth import UserResponse

# 创建路由器
router = APIRouter(prefix="/tasks", tags=["tasks"])

# API密钥认证
api_key_scheme = HTTPBearer(auto_error=False)


def get_current_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(api_key_scheme),
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    """从API密钥获取当前用户"""
    if not credentials:
        return None
    
    api_key = credentials.credentials
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    user = auth_service.get_user_by_api_key(api_key)
    if user:
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            api_key=user.api_key,
            created_at=user.created_at
        )
    return None


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """获取任务服务"""
    task_repository = TaskRepository(db)
    return TaskService(task_repository)


def get_current_user(
    current_user_from_api: Optional[UserResponse] = Depends(get_current_user_from_api_key),
    current_user_from_token: Optional[UserResponse] = Depends(lambda: None)  # 这个依赖会在主应用中被替换
) -> UserResponse:
    """获取当前用户（支持API密钥和JWT令牌）"""
    user = current_user_from_api or current_user_from_token
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    model: str = Form("base"),
    priority: int = Form(0),
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """创建新的字幕生成任务"""
    # 验证文件类型
    allowed_extensions = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".mp4", ".avi", ".mov", ".mkv", ".wmv"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # 创建上传目录
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 创建任务
    try:
        task = task_service.create_task(
            user_id=current_user.id,
            file_path=str(file_path),
            filename=file.filename,
            language=language,
            model=model,
            priority=priority
        )
        
        return TaskCreateResponse(
            id=task.id,
            user_id=task.user_id,
            filename=task.filename,
            language=task.language,
            model=task.model,
            status=task.status,
            progress=task.progress,
            priority=task.priority,
            created_at=task.created_at
        )
    except ValueError as e:
        # 删除已上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 删除已上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("", response_model=TaskListResponse)
def get_tasks(
    status: Optional[TaskStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """获取用户的任务列表"""
    skip = (page - 1) * limit
    tasks = task_service.get_tasks(current_user.id, status, skip, limit)
    
    # 获取总数
    total_tasks = len(task_service.get_tasks(current_user.id, status))
    
    return TaskListResponse(
        total=total_tasks,
        page=page,
        limit=limit,
        tasks=[
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                filename=task.filename,
                language=task.language,
                model=task.model,
                status=task.status,
                progress=task.progress,
                priority=task.priority,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at
            )
            for task in tasks
        ]
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """获取任务详情"""
    task = task_service.get_task(task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        filename=task.filename,
        language=task.language,
        model=task.model,
        status=task.status,
        progress=task.progress,
        priority=task.priority,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
def get_task_status(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """获取任务状态"""
    try:
        status = task_service.get_task_status(task_id, current_user.id)
        return TaskStatusResponse(
            task_id=status["task_id"],
            status=status["status"],
            progress=status["progress"],
            created_at=status["created_at"],
            updated_at=status["updated_at"],
            completed_at=status["completed_at"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{task_id}/priority", response_model=TaskResponse)
def update_task_priority(
    task_id: int,
    priority_update: TaskPriorityUpdate,
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """更新任务优先级"""
    try:
        task = task_service.update_task_priority(task_id, current_user.id, priority_update.priority)
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            filename=task.filename,
            language=task.language,
            model=task.model,
            status=task.status,
            progress=task.progress,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """取消任务"""
    try:
        task = task_service.cancel_task(task_id, current_user.id)
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            filename=task.filename,
            language=task.language,
            model=task.model,
            status=task.status,
            progress=task.progress,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """删除任务"""
    try:
        task_service.delete_task(task_id, current_user.id)
        return {"message": "Task deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )