from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Subtitle:
    """字幕领域实体"""
    id: Optional[int] = None
    task_id: int = 0
    format: str = "srt"  # srt, vtt, txt
    content: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后的验证"""
        if not self.content:
            raise ValueError("Subtitle content cannot be empty")
        if self.format not in ["srt", "vtt", "txt"]:
            raise ValueError("Unsupported subtitle format")