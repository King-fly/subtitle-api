from dataclasses import dataclass
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


@dataclass
class Task:
    """任务领域实体"""
    id: Optional[int] = None
    user_id: int = 0
    file_path: str = ""
    filename: str = ""
    language: str = "auto"
    model: str = "base"
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    priority: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后的验证"""
        if not self.file_path:
            raise ValueError("File path cannot be empty")
        if not self.filename:
            raise ValueError("Filename cannot be empty")
        if self.progress < 0 or self.progress > 100:
            raise ValueError("Progress must be between 0 and 100")