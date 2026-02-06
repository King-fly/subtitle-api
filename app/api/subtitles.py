from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List

from app.config import settings
from app.infrastructure.database.database import get_db
from app.infrastructure.database.repositories.subtitle_repository import SubtitleRepository
from app.infrastructure.database.repositories.task_repository import TaskRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.application.subtitle_service import SubtitleService
from app.application.auth_service import AuthService
from app.schemas.subtitle import (
    SubtitleResponse, SubtitleDetailResponse, SubtitleUpdate, SubtitleExportResponse
)
from app.schemas.auth import UserResponse
from app.api.tasks import get_current_user_from_api_key, get_current_user

# 创建路由器
router = APIRouter(prefix="/subtitles", tags=["subtitles"])


def get_subtitle_service(db: Session = Depends(get_db)) -> SubtitleService:
    """获取字幕服务"""
    subtitle_repository = SubtitleRepository(db)
    task_repository = TaskRepository(db)
    return SubtitleService(subtitle_repository, task_repository)


@router.get("/{subtitle_id}", response_model=SubtitleDetailResponse)
def get_subtitle(
    subtitle_id: int,
    current_user: UserResponse = Depends(get_current_user),
    subtitle_service: SubtitleService = Depends(get_subtitle_service)
):
    """获取字幕详情"""
    subtitle = subtitle_service.get_subtitle(subtitle_id, current_user.id)
    if not subtitle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtitle {subtitle_id} not found"
        )
    
    return SubtitleDetailResponse(
        id=subtitle.id,
        task_id=subtitle.task_id,
        format=subtitle.format,
        content=subtitle.content,
        created_at=subtitle.created_at,
        updated_at=subtitle.updated_at
    )


@router.put("/{subtitle_id}", response_model=SubtitleDetailResponse)
def update_subtitle(
    subtitle_id: int,
    subtitle_update: SubtitleUpdate,
    current_user: UserResponse = Depends(get_current_user),
    subtitle_service: SubtitleService = Depends(get_subtitle_service)
):
    """更新字幕内容"""
    try:
        subtitle = subtitle_service.update_subtitle(
            subtitle_id, subtitle_update.content, current_user.id
        )
        return SubtitleDetailResponse(
            id=subtitle.id,
            task_id=subtitle.task_id,
            format=subtitle.format,
            content=subtitle.content,
            created_at=subtitle.created_at,
            updated_at=subtitle.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{subtitle_id}", status_code=status.HTTP_200_OK)
def delete_subtitle(
    subtitle_id: int,
    current_user: UserResponse = Depends(get_current_user),
    subtitle_service: SubtitleService = Depends(get_subtitle_service)
):
    """删除字幕"""
    try:
        subtitle_service.delete_subtitle(subtitle_id, current_user.id)
        return {"message": "Subtitle deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{subtitle_id}/download")
def download_subtitle(
    subtitle_id: int,
    current_user: UserResponse = Depends(get_current_user),
    subtitle_service: SubtitleService = Depends(get_subtitle_service)
):
    """下载字幕文件"""
    try:
        export_data = subtitle_service.export_subtitle(subtitle_id, current_user.id)
        
        return Response(
            content=export_data["content"],
            media_type=export_data["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename={export_data['filename']}"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )