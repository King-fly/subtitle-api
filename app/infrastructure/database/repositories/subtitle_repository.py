from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.entities.subtitle import Subtitle
from app.domain.repositories.subtitle_repository import SubtitleRepositoryInterface
from app.infrastructure.database.models.subtitle import Subtitle as SubtitleModel


class SubtitleRepository(SubtitleRepositoryInterface):
    """字幕存储库实现"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, subtitle: Subtitle) -> Subtitle:
        """创建新字幕"""
        db_subtitle = SubtitleModel(
            task_id=subtitle.task_id,
            format=subtitle.format,
            content=subtitle.content
        )
        self.db.add(db_subtitle)
        self.db.commit()
        self.db.refresh(db_subtitle)
        return self._map_to_entity(db_subtitle)
    
    def get_by_id(self, subtitle_id: int) -> Optional[Subtitle]:
        """根据ID获取字幕"""
        db_subtitle = self.db.query(SubtitleModel).filter(SubtitleModel.id == subtitle_id).first()
        if db_subtitle:
            return self._map_to_entity(db_subtitle)
        return None
    
    def get_by_task_id(self, task_id: int) -> List[Subtitle]:
        """根据任务ID获取字幕列表"""
        db_subtitles = self.db.query(SubtitleModel).filter(
            SubtitleModel.task_id == task_id
        ).order_by(
            SubtitleModel.created_at.desc()
        ).all()
        return [self._map_to_entity(db_subtitle) for db_subtitle in db_subtitles]
    
    def get_by_task_id_and_format(self, task_id: int, format: str) -> Optional[Subtitle]:
        """根据任务ID和格式获取字幕"""
        db_subtitle = self.db.query(SubtitleModel).filter(
            SubtitleModel.task_id == task_id,
            SubtitleModel.format == format
        ).first()
        if db_subtitle:
            return self._map_to_entity(db_subtitle)
        return None
    
    def update(self, subtitle: Subtitle) -> Subtitle:
        """更新字幕信息"""
        db_subtitle = self.db.query(SubtitleModel).filter(SubtitleModel.id == subtitle.id).first()
        if db_subtitle:
            db_subtitle.format = subtitle.format
            db_subtitle.content = subtitle.content
            self.db.commit()
            self.db.refresh(db_subtitle)
            return self._map_to_entity(db_subtitle)
        raise ValueError(f"Subtitle with id {subtitle.id} not found")
    
    def delete(self, subtitle_id: int) -> bool:
        """删除字幕"""
        db_subtitle = self.db.query(SubtitleModel).filter(SubtitleModel.id == subtitle_id).first()
        if db_subtitle:
            self.db.delete(db_subtitle)
            self.db.commit()
            return True
        return False
    
    def _map_to_entity(self, db_subtitle: SubtitleModel) -> Subtitle:
        """将数据库模型映射到领域实体"""
        return Subtitle(
            id=db_subtitle.id,
            task_id=db_subtitle.task_id,
            format=db_subtitle.format,
            content=db_subtitle.content,
            created_at=db_subtitle.created_at,
            updated_at=db_subtitle.updated_at
        )