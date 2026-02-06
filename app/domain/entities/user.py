from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户领域实体"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    api_key: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后的验证"""
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.email:
            raise ValueError("Email cannot be empty")
        if not self.hashed_password:
            raise ValueError("Password cannot be empty")