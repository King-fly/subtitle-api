from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database.database import get_db
from app.infrastructure.database.repositories.subtitle_repository import SubtitleRepository
from app.infrastructure.database.repositories.task_repository import TaskRepository
from app.application.subtitle_service import SubtitleService
from app.schemas.subtitle import SubtitleResponse
from app.schemas.auth import UserResponse
from app.api.tasks import get_current_user

# 创建路由器
router = APIRouter(tags=["task-subtitles"])


def get_subtitle_service(db: Session = Depends(get_db)) -> SubtitleService:
    """获取字幕服务"""
    subtitle_repository = SubtitleRepository(db)
    task_repository = TaskRepository(db)
    return SubtitleService(subtitle_repository, task_repository)


@router.get("/tasks/{task_id}/subtitles", response_model=List[SubtitleResponse])
def get_task_subtitles(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user),
    subtitle_service: SubtitleService = Depends(get_subtitle_service)
):
    """获取任务的所有字幕"""
    subtitles = subtitle_service.get_subtitles_by_task_id(task_id, current_user.id)
    
    return [
        SubtitleResponse(
            id=subtitle.id,
            task_id=subtitle.task_id,
            format=subtitle.format,
            created_at=subtitle.created_at,
            updated_at=subtitle.updated_at
        )
        for subtitle in subtitles
    ]