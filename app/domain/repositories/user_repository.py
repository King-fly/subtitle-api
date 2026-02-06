from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User


class UserRepositoryInterface(ABC):
    """用户存储库接口"""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """创建新用户"""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        pass
    
    @abstractmethod
    def get_by_api_key(self, api_key: str) -> Optional[User]:
        """根据API密钥获取用户"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """更新用户信息"""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """删除用户"""
        pass