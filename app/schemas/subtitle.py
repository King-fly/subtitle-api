from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SubtitleBase(BaseModel):
    """字幕基础模型"""
    format: str = Field(..., pattern="^(srt|vtt|txt)$")


class SubtitleCreate(SubtitleBase):
    """字幕创建模型"""
    task_id: int
    content: str


class SubtitleUpdate(BaseModel):
    """字幕更新模型"""
    content: str


class SubtitleResponse(SubtitleBase):
    """字幕响应模型"""
    id: int
    task_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubtitleDetailResponse(SubtitleResponse):
    """字幕详情响应模型"""
    content: str


class SubtitleExportResponse(BaseModel):
    """字幕导出响应模型"""
    filename: str
    format: str
    content_type: str