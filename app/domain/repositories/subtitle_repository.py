from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.subtitle import Subtitle


class SubtitleRepositoryInterface(ABC):
    """字幕存储库接口"""
    
    @abstractmethod
    def create(self, subtitle: Subtitle) -> Subtitle:
        """创建新字幕"""
        pass
    
    @abstractmethod
    def get_by_id(self, subtitle_id: int) -> Optional[Subtitle]:
        """根据ID获取字幕"""
        pass
    
    @abstractmethod
    def get_by_task_id(self, task_id: int) -> List[Subtitle]:
        """根据任务ID获取字幕列表"""
        pass
    
    @abstractmethod
    def get_by_task_id_and_format(self, task_id: int, format: str) -> Optional[Subtitle]:
        """根据任务ID和格式获取字幕"""
        pass
    
    @abstractmethod
    def update(self, subtitle: Subtitle) -> Subtitle:
        """更新字幕信息"""
        pass
    
    @abstractmethod
    def delete(self, subtitle_id: int) -> bool:
        """删除字幕"""
        pass