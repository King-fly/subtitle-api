# Subtitle API

基于 Whisper 的音视频字幕生成 API

[English Version](README.md)

## 项目概述

Subtitle API 是一个基于 FastAPI 和 OpenAI Whisper 的音视频字幕生成服务，支持多种格式的字幕生成（SRT、VTT、TXT），并提供异步任务处理功能。

## 功能特性

### 核心功能
- 🎯 音视频字幕自动生成
- 📝 支持多种字幕格式：SRT、VTT、TXT
- ⏱️ 异步任务处理
- 🔊 支持多种音频格式
- 📹 支持多种视频格式
- 🌐 多语言支持
- 🔒 安全的 API 认证

### 技术特性
- 🚀 高性能 FastAPI 框架
- 📦 模块化架构设计
- 📊 完整的 API 文档
- 📈 任务进度追踪
- 🔄 自动视频音频提取
- 🧠 基于 Whisper 的强大语音识别

## 技术栈

### 后端
- **Python 3.12** - 编程语言
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM 数据库框架
- **Celery** - 异步任务队列
- **Redis** - 任务队列和缓存

### 机器学习
- **OpenAI Whisper** - 语音识别模型
- **PyTorch** - 深度学习框架

### 数据库
- **SQLite** - 默认数据库（支持 MySQL/PostgreSQL）

### 工具
- **FFmpeg** - 音视频处理
- **Pydantic** - 数据验证
- **Passlib** - 密码加密
- **JWT** - 认证令牌

## 项目结构

```
app/
├── api/                 # API 路由
│   ├── auth.py         # 认证相关路由
│   ├── tasks.py        # 任务相关路由
│   ├── subtitles.py    # 字幕相关路由
│   └── task_subtitles.py # 任务字幕关联路由
├── application/        # 应用服务层
│   ├── auth_service.py
│   ├── subtitle_service.py
│   └── task_service.py
├── domain/             # 领域层
│   ├── entities/       # 领域实体
│   │   ├── subtitle.py
│   │   ├── task.py
│   │   └── user.py
│   └── repositories/   # 存储库接口
├── infrastructure/     # 基础设施层
│   ├── celery/         # Celery 配置和任务
│   ├── database/       # 数据库配置和实现
│   └── whisper/        # Whisper 服务实现
├── schemas/            # Pydantic 模型
├── config.py           # 应用配置
└── main.py             # 应用入口
```

## 安装

### 环境要求
- Python 3.12+
- FFmpeg
- Redis

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-repo/subtitle-api.git
   cd subtitle-api
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # 或在 Windows 上: .venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装 FFmpeg**
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt-get install ffmpeg`
   - Windows: 下载并安装 [FFmpeg](https://ffmpeg.org/download.html)

5. **启动 Redis**
   ```bash
   redis-server
   ```

## 配置

### 环境变量

创建 `.env` 文件并配置以下环境变量：

```env
# 数据库配置
DATABASE_URL=sqlite:///./subtitles.db

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Whisper 配置
WHISPER_MODEL_PATH=./models
WHISPER_MODEL=base

# API 配置
API_PREFIX=/api
DEBUG=True
```

## 使用

### 启动服务

1. **启动 API 服务**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **启动 Celery Worker**
   ```bash
   celery -A app.infrastructure.celery.celery_app.celery_app worker --loglevel=info
   ```

3. **启动 Celery Beat (可选)**
   ```bash
   celery -A app.infrastructure.celery.celery_app.celery_app beat --loglevel=info
   ```

### API 访问

- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 文档

API 提供以下主要功能：

### 认证 API
- `POST /api/token` - 获取访问令牌
- `GET /api/me` - 获取当前用户信息
- `POST /api/refresh-api-key` - 刷新 API 密钥

### 任务 API
- `POST /api/tasks` - 创建新任务
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/{task_id}` - 获取任务详情
- `DELETE /api/tasks/{task_id}` - 删除任务

### 字幕 API
- `GET /api/subtitles` - 获取字幕列表
- `GET /api/subtitles/{subtitle_id}` - 获取字幕详情
- `GET /api/subtitles/{subtitle_id}/content` - 获取字幕内容
- `DELETE /api/subtitles/{subtitle_id}` - 删除字幕

### 任务字幕 API
- `GET /api/tasks/{task_id}/subtitles` - 获取任务的字幕列表

## Celery 任务

### 主要任务
- `generate_subtitles_task` - 生成字幕的异步任务
- `cancel_task_task` - 取消任务的异步任务

### 任务状态
- `PENDING` - 任务待处理
- `PROCESSING` - 任务处理中
- `COMPLETED` - 任务完成
- `FAILED` - 任务失败
- `CANCELED` - 任务取消

## 数据库

### 主要模型
- **User** - 用户信息
- **Task** - 字幕生成任务
- **Subtitle** - 生成的字幕

### 关系
- 一个用户可以有多个任务
- 一个任务可以生成多个字幕
- 一个字幕属于一个任务

## 测试

### 运行测试

```bash
pytest
```

### 测试覆盖率

```bash
pytest --cov=app
```

## 部署

### Docker 部署

```bash
docker-compose up -d
```

### 生产部署

1. 使用 Gunicorn 作为 WSGI 服务器
2. 配置 Nginx 作为反向代理
3. 使用 Supervisor 管理进程
4. 配置 HTTPS

## 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，欢迎联系我们。

## 更新日志

### v1.0.0 (2024-02-06)
- 初始版本
- 支持基本字幕生成功能
- 支持异步任务处理
- 提供完整 API 文档

## 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [FastAPI](https://github.com/tiangolo/fastapi) - Web 框架
- [Celery](https://github.com/celery/celery) - 任务队列

## 故障排除

### 常见问题

1. **Whisper 模型下载失败**
   - 确保网络连接正常
   - 手动下载模型到 `models/` 目录

2. **FFmpeg 找不到**
   - 确保 FFmpeg 已正确安装
   - 将 FFmpeg 添加到系统环境变量

3. **Redis 连接失败**
   - 确保 Redis 服务已启动
   - 检查 Redis 配置

4. **任务处理失败**
   - 检查文件格式是否支持
   - 检查文件大小是否超过限制
   - 查看 Celery 日志获取详细错误信息

## 开发说明

### 代码风格
- 使用 PEP 8 代码风格
- 类型注解
- 模块化设计
- 详细的文档注释

### 开发流程
1. 编写代码
2. 运行测试
3. 检查代码风格
4. 提交更改
5. 创建 PR

---

**感谢使用 Subtitle API！**