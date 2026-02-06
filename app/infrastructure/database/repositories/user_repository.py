from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepositoryInterface
from app.infrastructure.database.models.user import User as UserModel


class UserRepository(UserRepositoryInterface):
    """用户存储库实现"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """创建新用户"""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            api_key=user.api_key
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._map_to_entity(db_user)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None
    
    def get_by_api_key(self, api_key: str) -> Optional[User]:
        """根据API密钥获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.api_key == api_key).first()
        if db_user:
            return self._map_to_entity(db_user)
        return None
    
    def update(self, user: User) -> User:
        """更新用户信息"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            db_user.username = user.username
            db_user.email = user.email
            db_user.hashed_password = user.hashed_password
            db_user.api_key = user.api_key
            self.db.commit()
            self.db.refresh(db_user)
            return self._map_to_entity(db_user)
        raise ValueError(f"User with id {user.id} not found")
    
    def delete(self, user_id: int) -> bool:
        """删除用户"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    def _map_to_entity(self, db_user: UserModel) -> User:
        """将数据库模型映射到领域实体"""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            api_key=db_user.api_key,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )