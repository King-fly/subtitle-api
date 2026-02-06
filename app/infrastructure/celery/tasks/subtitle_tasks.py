import os
import tempfile
from datetime import datetime
from app.infrastructure.celery.celery_app import celery_app
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.database.repositories.task_repository import TaskRepository
from app.infrastructure.database.repositories.subtitle_repository import SubtitleRepository
from app.infrastructure.whisper.whisper_service import whisper_service
from app.domain.entities.task import TaskStatus
from app.domain.entities.subtitle import Subtitle
from app.config import settings

# 导入所有模型，确保它们被SQLAlchemy注册
from app.infrastructure.database.models import user, task, subtitle


@celery_app.task(bind=True)
def generate_subtitles_task(self, task_id: int):
    """
    生成字幕的Celery任务
    
    Args:
        task_id: 任务ID
    """
    # 获取数据库会话
    db = SessionLocal()
    try:
        # 获取任务存储库
        task_repo = TaskRepository(db)
        subtitle_repo = SubtitleRepository(db)
        
        # 获取任务
        task = task_repo.get_by_id(task_id)
        if not task:
            task_repo.update_status(task_id, TaskStatus.FAILED)
            raise ValueError(f"Task {task_id} not found")
        
        # 更新任务状态为处理中
        task_repo.update_status(task_id, TaskStatus.PROCESSING)
        
        # 定义进度回调函数
        def progress_callback(progress: float):
            """更新任务进度"""
            progress_percent = int(progress * 100)
            task_repo.update_progress(task_id, progress_percent)
            self.update_state(state="PROGRESS", meta={"progress": progress_percent})
        
        # 检查文件是否存在
        if not os.path.exists(task.file_path):
            task_repo.update_status(task_id, TaskStatus.FAILED)
            raise ValueError(f"File {task.file_path} not found")
        
        # 检查文件类型
        file_ext = os.path.splitext(task.file_path)[1].lower()
        audio_path = task.file_path
        
        # 如果是视频文件，提取音频
        if file_ext in [".mp4", ".avi", ".mov", ".mkv", ".wmv"]:
            # 创建临时音频文件
            temp_audio_fd, temp_audio_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_audio_fd)
            
            try:
                # 提取音频
                if not whisper_service.extract_audio(task.file_path, temp_audio_path):
                    task_repo.update_status(task_id, TaskStatus.FAILED)
                    raise ValueError("Failed to extract audio from video")
                
                audio_path = temp_audio_path
                
                # 生成字幕
                subtitles = whisper_service.generate_subtitles(
                    audio_path,
                    model_name=task.model,
                    language=task.language,
                    formats=["srt", "vtt", "txt"],
                    progress_callback=progress_callback
                )
                
                # 保存字幕
                for format, content in subtitles.items():
                    subtitle = subtitle_repo.create(
                        Subtitle(
                            task_id=task_id,
                            format=format,
                            content=content
                        )
                    )
            finally:
                # 清理临时文件
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
        else:
            # 直接处理音频文件
            subtitles = whisper_service.generate_subtitles(
                audio_path,
                model_name=task.model,
                language=task.language,
                formats=["srt", "vtt", "txt"],
                progress_callback=progress_callback
            )
            
            # 保存字幕
            for format, content in subtitles.items():
                subtitle = subtitle_repo.create(
                    Subtitle(
                        task_id=task_id,
                        format=format,
                        content=content
                    )
                )
        
        # 更新任务状态为完成
        task_repo.update_status(task_id, TaskStatus.COMPLETED)
        
        return {
            "status": "success",
            "task_id": task_id,
            "subtitles": list(subtitles.keys())
        }
    
    except Exception as e:
        # 更新任务状态为失败
        task_repo.update_status(task_id, TaskStatus.FAILED)
        self.update_state(state="FAILURE", meta={"error": str(e)})
        # 重新抛出异常，让Celery能够正确处理失败信息
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True)
def cancel_task_task(self, task_id: int):
    """
    取消任务的Celery任务
    
    Args:
        task_id: 任务ID
    """
    # 获取数据库会话
    db = SessionLocal()
    try:
        # 获取任务存储库
        task_repo = TaskRepository(db)
        
        # 获取任务
        task = task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # 检查任务状态
        if task.status not in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            raise ValueError(f"Task {task_id} cannot be canceled")
        
        # 更新任务状态为已取消
        task_repo.update_status(task_id, TaskStatus.CANCELED)
        
        return {"status": "success", "task_id": task_id}
    
    except Exception as e:
        # 重新抛出异常，让Celery能够正确处理失败信息
        raise
    
    finally:
        db.close()