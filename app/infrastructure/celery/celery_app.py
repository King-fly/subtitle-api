from celery import Celery
from app.config import settings

# 创建Celery应用，暂时不使用结果后端
celery_app = Celery(
    "subtitle_api",
    broker=settings.CELERY_BROKER_URL,
    backend=None
)

# 配置Celery
celery_app.conf.update(
    task_serializer="pickle",
    accept_content=["pickle", "json"],
    result_serializer="pickle",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 任务超时时间（秒）
    task_soft_time_limit=3000,  # 任务软超时时间（秒）
    worker_prefetch_multiplier=1,  # 每个worker每次获取的任务数
    worker_max_tasks_per_child=100,  # 每个worker进程最多处理的任务数，超过后会重启
    # 配置结果序列化，确保异常能被正确处理
    result_extended=True,
    result_compression="gzip",
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.infrastructure.celery.tasks"])