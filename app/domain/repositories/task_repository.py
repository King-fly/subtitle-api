from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.task import Task, TaskStatus


class TaskRepositoryInterface(ABC):
    """任务存储库接口"""
    
    @abstractmethod
    def create(self, task: Task) -> Task:
        """创建新任务"""
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取用户的任务列表"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """根据状态获取任务列表"""
        pass
    
    @abstractmethod
    def get_by_user_id_and_status(self, user_id: int, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """根据用户ID和状态获取任务列表"""
        pass
    
    @abstractmethod
    def update(self, task: Task) -> Task:
        """更新任务信息"""
        pass
    
    @abstractmethod
    def update_status(self, task_id: int, status: TaskStatus) -> bool:
        """更新任务状态"""
        pass
    
    @abstractmethod
    def update_progress(self, task_id: int, progress: int) -> bool:
        """更新任务进度"""
        pass
    
    @abstractmethod
    def update_priority(self, task_id: int, priority: int) -> bool:
        """更新任务优先级"""
        pass
    
    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """删除任务"""
        pass