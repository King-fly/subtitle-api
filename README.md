# Subtitle API

An audio/video subtitle generation API based on Whisper

[中文版本 (Chinese Version)](README.zh.md)

## Project Overview

Subtitle API is an audio/video subtitle generation service based on FastAPI and OpenAI Whisper, supporting multiple subtitle formats (SRT, VTT, TXT) and providing asynchronous task processing capabilities.

## Features

### Core Features
- 🎯 Automatic audio/video subtitle generation
- 📝 Support for multiple subtitle formats: SRT, VTT, TXT
- ⏱️ Asynchronous task processing
- 🔊 Support for multiple audio formats
- 📹 Support for multiple video formats
- 🌐 Multi-language support
- 🔒 Secure API authentication

### Technical Features
- 🚀 High-performance FastAPI framework
- 📦 Modular architecture design
- 📊 Complete API documentation
- 📈 Task progress tracking
- 🔄 Automatic video audio extraction
- 🧠 Powerful speech recognition based on Whisper

## Technology Stack

### Backend
- **Python 3.12** - Programming language
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM database framework
- **Celery** - Asynchronous task queue
- **Redis** - Task queue and cache

### Machine Learning
- **OpenAI Whisper** - Speech recognition model
- **PyTorch** - Deep learning framework

### Database
- **SQLite** - Default database (supports MySQL/PostgreSQL)

### Tools
- **FFmpeg** - Audio/video processing
- **Pydantic** - Data validation
- **Passlib** - Password encryption
- **JWT** - Authentication tokens

## Project Structure

```
app/
├── api/                 # API routes
│   ├── auth.py         # Authentication related routes
│   ├── tasks.py        # Task related routes
│   ├── subtitles.py    # Subtitle related routes
│   └── task_subtitles.py # Task-subtitle association routes
├── application/        # Application service layer
│   ├── auth_service.py
│   ├── subtitle_service.py
│   └── task_service.py
├── domain/             # Domain layer
│   ├── entities/       # Domain entities
│   │   ├── subtitle.py
│   │   ├── task.py
│   │   └── user.py
│   └── repositories/   # Repository interfaces
├── infrastructure/     # Infrastructure layer
│   ├── celery/         # Celery configuration and tasks
│   ├── database/       # Database configuration and implementation
│   └── whisper/        # Whisper service implementation
├── schemas/            # Pydantic models
├── config.py           # Application configuration
└── main.py             # Application entry point
```

## Installation

### Environment Requirements
- Python 3.12+
- FFmpeg
- Redis

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-repo/subtitle-api.git
   cd subtitle-api
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # Or on Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt-get install ffmpeg`
   - Windows: Download and install [FFmpeg](https://ffmpeg.org/download.html)

5. **Start Redis**
   ```bash
   redis-server
   ```

## Configuration

### Environment Variables

Create a `.env` file and configure the following environment variables:

```env
# Database configuration
DATABASE_URL=sqlite:///./subtitles.db

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# JWT configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Whisper configuration
WHISPER_MODEL_PATH=./models
WHISPER_MODEL=base

# API configuration
API_PREFIX=/api
DEBUG=True
```

## Usage

### Start Services

1. **Start API Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Celery Worker**
   ```bash
   celery -A app.infrastructure.celery.celery_app.celery_app worker --loglevel=info
   ```

3. **Start Celery Beat (Optional)**
   ```bash
   celery -A app.infrastructure.celery.celery_app.celery_app beat --loglevel=info
   ```

### API Access

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Documentation

The API provides the following main functions:

### Auth API
- `POST /api/token` - Get access token
- `GET /api/me` - Get current user information
- `POST /api/refresh-api-key` - Refresh API key

### Tasks API
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - Get task list
- `GET /api/tasks/{task_id}` - Get task details
- `DELETE /api/tasks/{task_id}` - Delete task

### Subtitles API
- `GET /api/subtitles` - Get subtitle list
- `GET /api/subtitles/{subtitle_id}` - Get subtitle details
- `GET /api/subtitles/{subtitle_id}/content` - Get subtitle content
- `DELETE /api/subtitles/{subtitle_id}` - Delete subtitle

### Task Subtitles API
- `GET /api/tasks/{task_id}/subtitles` - Get task's subtitle list

## Celery Tasks

### Main Tasks
- `generate_subtitles_task` - Asynchronous subtitle generation task
- `cancel_task_task` - Asynchronous task cancellation task

### Task Status
- `PENDING` - Task pending
- `PROCESSING` - Task processing
- `COMPLETED` - Task completed
- `FAILED` - Task failed
- `CANCELED` - Task canceled

## Database

### Main Models
- **User** - User information
- **Task** - Subtitle generation task
- **Subtitle** - Generated subtitles

### Relationships
- One user can have multiple tasks
- One task can generate multiple subtitles
- One subtitle belongs to one task

## Testing

### Run Tests

```bash
pytest
```

### Test Coverage

```bash
pytest --cov=app
```

## Deployment

### Docker Deployment

```bash
docker-compose up -d
```

### Production Deployment

1. Use Gunicorn as WSGI server
2. Configure Nginx as reverse proxy
3. Use Supervisor for process management
4. Configure HTTPS

## Contributing

Contributions are welcome! Please submit Issues and Pull Requests.

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or suggestions, please feel free to contact us.

## Changelog

### v1.0.0 (2024-02-06)
- Initial release
- Basic subtitle generation functionality
- Asynchronous task processing
- Complete API documentation

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [FastAPI](https://github.com/tiangolo/fastapi) - Web framework
- [Celery](https://github.com/celery/celery) - Task queue

## Troubleshooting

### Common Issues

1. **Whisper Model Download Failed**
   - Ensure network connection is normal
   - Manually download the model to `models/` directory

2. **FFmpeg Not Found**
   - Ensure FFmpeg is correctly installed
   - Add FFmpeg to system environment variables

3. **Redis Connection Failed**
   - Ensure Redis service is started
   - Check Redis configuration

4. **Task Processing Failed**
   - Check if file format is supported
   - Check if file size exceeds limit
   - Check Celery logs for detailed error information

## Development Notes

### Code Style
- Use PEP 8 code style
- Type annotations
- Modular design
- Detailed documentation comments

### Development Process
1. Write code
2. Run tests
3. Check code style
4. Commit changes
5. Create PR

---

**Thank you for using Subtitle API!**