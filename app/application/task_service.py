import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.config import settings
from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepositoryInterface
from app.infrastructure.celery.tasks.subtitle_tasks import generate_subtitles_task, cancel_task_task


class TaskService:
    """任务服务"""
    
    def __init__(self, task_repository: TaskRepositoryInterface):
        self.task_repository = task_repository
    
    def create_task(
        self, 
        user_id: int, 
        file_path: str, 
        filename: str, 
        language: str = "auto", 
        model: str = "base",
        priority: int = 0
    ) -> Task:
        """
        创建新的字幕生成任务
        
        Args:
            user_id: 用户ID
            file_path: 文件路径
            filename: 文件名
            language: 语言代码
            model: Whisper模型名称
            priority: 任务优先级
        
        Returns:
            创建的任务
        """
        # 验证文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # 验证文件大小
        file_size = os.path.getsize(file_path)
        if file_size > settings.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes")
        
        # 创建任务
        task = Task(
            user_id=user_id,
            file_path=file_path,
            filename=filename,
            language=language,
            model=model,
            status=TaskStatus.PENDING,
            progress=0,
            priority=priority
        )
        
        # 保存任务
        task = self.task_repository.create(task)
        
        # 发送任务到Celery队列
        generate_subtitles_task.apply_async(
            args=[task.id],
            priority=priority
        )
        
        return task
    
    def get_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            任务，如果不存在则返回None
        """
        task = self.task_repository.get_by_id(task_id)
        if task and task.user_id == user_id:
            return task
        return None
    
    def get_tasks(
        self, 
        user_id: int, 
        status: Optional[TaskStatus] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """
        获取用户的任务列表
        
        Args:
            user_id: 用户ID
            status: 任务状态过滤
            skip: 跳过的任务数
            limit: 返回的最大任务数
        
        Returns:
            任务列表
        """
        if status:
            return self.task_repository.get_by_user_id_and_status(user_id, status, skip, limit)
        else:
            return self.task_repository.get_by_user_id(user_id, skip, limit)
    
    def update_task_priority(self, task_id: int, user_id: int, priority: int) -> Task:
        """
        更新任务优先级
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
            priority: 新的优先级
        
        Returns:
            更新后的任务
        
        Raises:
            ValueError: 如果任务不存在或不属于该用户
        """
        task = self.get_task(task_id, user_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # 只有待处理或处理中的任务可以更新优先级
        if task.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            raise ValueError(f"Cannot update priority for task in {task.status} status")
        
        # 更新优先级
        self.task_repository.update_priority(task_id, priority)
        
        # 重新获取任务
        task = self.task_repository.get_by_id(task_id)
        
        return task
    
    def cancel_task(self, task_id: int, user_id: int) -> Task:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            取消后的任务
        
        Raises:
            ValueError: 如果任务不存在或不属于该用户
        """
        task = self.get_task(task_id, user_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # 只有待处理或处理中的任务可以取消
        if task.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            raise ValueError(f"Cannot cancel task in {task.status} status")
        
        # 发送取消任务到Celery队列
        cancel_task_task.apply_async(args=[task_id])
        
        # 更新任务状态
        self.task_repository.update_status(task_id, TaskStatus.CANCELED)
        
        # 重新获取任务
        task = self.task_repository.get_by_id(task_id)
        
        return task
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            是否成功删除
        
        Raises:
            ValueError: 如果任务不存在或不属于该用户
        """
        task = self.get_task(task_id, user_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # 删除任务文件
        if os.path.exists(task.file_path):
            os.remove(task.file_path)
        
        # 删除任务
        return self.task_repository.delete(task_id)
    
    def get_task_status(self, task_id: int, user_id: int) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            任务状态信息
        """
        task = self.get_task(task_id, user_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        return {
            "task_id": task.id,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at
        }