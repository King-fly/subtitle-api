from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepositoryInterface
from app.infrastructure.database.models.task import Task as TaskModel


class TaskRepository(TaskRepositoryInterface):
    """任务存储库实现"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, task: Task) -> Task:
        """创建新任务"""
        db_task = TaskModel(
            user_id=task.user_id,
            file_path=task.file_path,
            filename=task.filename,
            language=task.language,
            model=task.model,
            status=task.status.value,
            progress=task.progress,
            priority=task.priority
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return self._map_to_entity(db_task)
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            return self._map_to_entity(db_task)
        return None
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取用户的任务列表"""
        db_tasks = self.db.query(TaskModel).filter(
            TaskModel.user_id == user_id
        ).order_by(
            TaskModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        return [self._map_to_entity(db_task) for db_task in db_tasks]
    
    def get_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """根据状态获取任务列表"""
        db_tasks = self.db.query(TaskModel).filter(
            TaskModel.status == status.value
        ).order_by(
            TaskModel.priority.desc(),
            TaskModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        return [self._map_to_entity(db_task) for db_task in db_tasks]
    
    def get_by_user_id_and_status(self, user_id: int, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """根据用户ID和状态获取任务列表"""
        db_tasks = self.db.query(TaskModel).filter(
            TaskModel.user_id == user_id,
            TaskModel.status == status.value
        ).order_by(
            TaskModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        return [self._map_to_entity(db_task) for db_task in db_tasks]
    
    def update(self, task: Task) -> Task:
        """更新任务信息"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task.id).first()
        if db_task:
            db_task.user_id = task.user_id
            db_task.file_path = task.file_path
            db_task.filename = task.filename
            db_task.language = task.language
            db_task.model = task.model
            db_task.status = task.status.value
            db_task.progress = task.progress
            db_task.priority = task.priority
            db_task.completed_at = task.completed_at
            self.db.commit()
            self.db.refresh(db_task)
            return self._map_to_entity(db_task)
        raise ValueError(f"Task with id {task.id} not found")
    
    def update_status(self, task_id: int, status: TaskStatus) -> bool:
        """更新任务状态"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            db_task.status = status.value
            if status == TaskStatus.COMPLETED:
                from datetime import datetime
                db_task.completed_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def update_progress(self, task_id: int, progress: int) -> bool:
        """更新任务进度"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            db_task.progress = progress
            self.db.commit()
            return True
        return False
    
    def update_priority(self, task_id: int, priority: int) -> bool:
        """更新任务优先级"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            db_task.priority = priority
            self.db.commit()
            return True
        return False
    
    def delete(self, task_id: int) -> bool:
        """删除任务"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False
    
    def _map_to_entity(self, db_task: TaskModel) -> Task:
        """将数据库模型映射到领域实体"""
        return Task(
            id=db_task.id,
            user_id=db_task.user_id,
            file_path=db_task.file_path,
            filename=db_task.filename,
            language=db_task.language,
            model=db_task.model,
            status=TaskStatus(db_task.status),
            progress=db_task.progress,
            priority=db_task.priority,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            completed_at=db_task.completed_at
        )