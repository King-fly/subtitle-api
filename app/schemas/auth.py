from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    api_key: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
    email: Optional[str] = None