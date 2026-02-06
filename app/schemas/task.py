from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TaskBase(BaseModel):
    """任务基础模型"""
    language: str = "auto"
    model: str = "base"
    priority: int = 0


class TaskCreate(TaskBase):
    """任务创建模型"""
    pass


class TaskUpdate(BaseModel):
    """任务更新模型"""
    priority: Optional[int] = None


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int
    user_id: int
    filename: str
    status: TaskStatus
    progress: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int
    page: int
    limit: int
    tasks: List[TaskResponse]


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: int
    status: TaskStatus
    progress: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TaskPriorityUpdate(BaseModel):
    """任务优先级更新模型"""
    priority: int = Field(..., ge=0)


class TaskCreateResponse(BaseModel):
    """任务创建响应模型"""
    id: int
    user_id: int
    filename: str
    language: str
    model: str
    status: TaskStatus
    progress: int
    priority: int
    created_at: datetime