from typing import List, Optional, Dict, Any
from app.domain.entities.subtitle import Subtitle
from app.domain.entities.task import TaskStatus
from app.domain.repositories.subtitle_repository import SubtitleRepositoryInterface
from app.domain.repositories.task_repository import TaskRepositoryInterface


class SubtitleService:
    """字幕服务"""
    
    def __init__(
        self, 
        subtitle_repository: SubtitleRepositoryInterface,
        task_repository: TaskRepositoryInterface
    ):
        self.subtitle_repository = subtitle_repository
        self.task_repository = task_repository
    
    def get_subtitle(self, subtitle_id: int, user_id: int) -> Optional[Subtitle]:
        """
        获取字幕
        
        Args:
            subtitle_id: 字幕ID
            user_id: 用户ID
        
        Returns:
            字幕，如果不存在则返回None
        """
        subtitle = self.subtitle_repository.get_by_id(subtitle_id)
        if subtitle:
            # 检查字幕所属的任务是否属于该用户
            task = self.task_repository.get_by_id(subtitle.task_id)
            if task and task.user_id == user_id:
                return subtitle
        return None
    
    def get_subtitles_by_task_id(self, task_id: int, user_id: int) -> List[Subtitle]:
        """
        获取任务的所有字幕
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            字幕列表
        """
        # 检查任务是否属于该用户
        task = self.task_repository.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return []
        
        # 检查任务是否已完成
        if task.status != TaskStatus.COMPLETED:
            return []
        
        # 获取字幕
        return self.subtitle_repository.get_by_task_id(task_id)
    
    def get_subtitle_by_format(self, task_id: int, format: str, user_id: int) -> Optional[Subtitle]:
        """
        获取特定格式的字幕
        
        Args:
            task_id: 任务ID
            format: 字幕格式
            user_id: 用户ID
        
        Returns:
            字幕，如果不存在则返回None
        """
        # 检查任务是否属于该用户
        task = self.task_repository.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return None
        
        # 检查任务是否已完成
        if task.status != TaskStatus.COMPLETED:
            return None
        
        # 获取字幕
        return self.subtitle_repository.get_by_task_id_and_format(task_id, format)
    
    def update_subtitle(self, subtitle_id: int, content: str, user_id: int) -> Subtitle:
        """
        更新字幕内容
        
        Args:
            subtitle_id: 字幕ID
            content: 新的字幕内容
            user_id: 用户ID
        
        Returns:
            更新后的字幕
        
        Raises:
            ValueError: 如果字幕不存在或不属于该用户
        """
        subtitle = self.get_subtitle(subtitle_id, user_id)
        if not subtitle:
            raise ValueError(f"Subtitle not found: {subtitle_id}")
        
        # 更新字幕内容
        subtitle.content = content
        return self.subtitle_repository.update(subtitle)
    
    def delete_subtitle(self, subtitle_id: int, user_id: int) -> bool:
        """
        删除字幕
        
        Args:
            subtitle_id: 字幕ID
            user_id: 用户ID
        
        Returns:
            是否成功删除
        
        Raises:
            ValueError: 如果字幕不存在或不属于该用户
        """
        subtitle = self.get_subtitle(subtitle_id, user_id)
        if not subtitle:
            raise ValueError(f"Subtitle not found: {subtitle_id}")
        
        # 删除字幕
        return self.subtitle_repository.delete(subtitle_id)
    
    def export_subtitle(self, subtitle_id: int, user_id: int) -> Dict[str, Any]:
        """
        导出字幕
        
        Args:
            subtitle_id: 字幕ID
            user_id: 用户ID
        
        Returns:
            字幕导出信息，包含文件名和内容
        
        Raises:
            ValueError: 如果字幕不存在或不属于该用户
        """
        subtitle = self.get_subtitle(subtitle_id, user_id)
        if not subtitle:
            raise ValueError(f"Subtitle not found: {subtitle_id}")
        
        # 获取任务信息
        task = self.task_repository.get_by_id(subtitle.task_id)
        if not task:
            raise ValueError(f"Task not found for subtitle: {subtitle_id}")
        
        # 生成文件名
        base_filename = task.filename.rsplit(".", 1)[0]
        filename = f"{base_filename}.{subtitle.format}"
        
        return {
            "filename": filename,
            "content": subtitle.content,
            "format": subtitle.format,
            "content_type": self._get_content_type(subtitle.format)
        }
    
    def _get_content_type(self, format: str) -> str:
        """
        获取字幕格式对应的Content-Type
        
        Args:
            format: 字幕格式
        
        Returns:
            Content-Type
        """
        content_types = {
            "srt": "text/srt",
            "vtt": "text/vtt",
            "txt": "text/plain"
        }
        return content_types.get(format, "text/plain")