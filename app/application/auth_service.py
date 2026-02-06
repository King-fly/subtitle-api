import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepositoryInterface


class AuthService:
    """认证服务"""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_api_key(self) -> str:
        """创建API密钥"""
        return secrets.token_urlsafe(32)
    
    def register_user(self, username: str, email: str, password: str) -> User:
        """注册新用户"""
        # 检查用户名是否已存在
        if self.user_repository.get_by_username(username):
            raise ValueError("Username already registered")
        
        # 检查邮箱是否已存在
        if self.user_repository.get_by_email(email):
            raise ValueError("Email already registered")
        
        # 创建新用户
        hashed_password = self.get_password_hash(password)
        api_key = self.create_api_key()
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            api_key=api_key
        )
        
        return self.user_repository.create(user)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户"""
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """根据API密钥获取用户"""
        return self.user_repository.get_by_api_key(api_key)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.user_repository.get_by_id(user_id)
    
    def refresh_api_key(self, user_id: int) -> User:
        """刷新API密钥"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.api_key = self.create_api_key()
        return self.user_repository.update(user)