from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
from datetime import timedelta

from app.config import settings
from app.infrastructure.database.database import get_db
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.application.auth_service import AuthService
from app.schemas.auth import UserCreate, UserResponse, Token, TokenData, UserLogin

# 创建路由器
router = APIRouter(prefix="/auth", tags=["auth"])

# HTTP Bearer认证
token_bearer = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务"""
    user_repository = UserRepository(db)
    return AuthService(user_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(token_bearer),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = auth_service.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        created_at=user.created_at
    )


def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """获取当前活跃用户"""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """注册新用户"""
    try:
        db_user = auth_service.register_user(user.username, user.email, user.password)
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            api_key=db_user.api_key,
            created_at=db_user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登录"""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
def login_json(
    user: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登录（JSON格式）"""
    user = auth_service.authenticate_user(user.email, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/refresh-api-key", response_model=UserResponse)
def refresh_api_key(
    current_user: UserResponse = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """刷新API密钥"""
    user = auth_service.refresh_api_key(current_user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        created_at=user.created_at
    )