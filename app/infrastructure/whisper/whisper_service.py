import os
import whisper
import ffmpeg
from typing import Dict, List, Optional, Tuple
from app.config import settings


class WhisperService:
    """Whisper语音识别服务"""
    
    def __init__(self):
        self.model_path = settings.WHISPER_MODEL_PATH
        self.default_model = settings.WHISPER_MODEL
        self.models = {}  # 缓存已加载的模型
    
    def load_model(self, model_name: str) -> whisper.Whisper:
        """加载Whisper模型"""
        if model_name not in self.models:
            # 检查模型是否已下载
            model_path = os.path.join(self.model_path, model_name)
            if not os.path.exists(model_path):
                # 模型不存在，让whisper自动下载
                self.models[model_name] = whisper.load_model(model_name)
            else:
                # 从本地加载模型
                self.models[model_name] = whisper.load_model(model_path)
        return self.models[model_name]
    
    def transcribe(
        self, 
        audio_path: str, 
        model_name: str = None, 
        language: str = "auto",
        progress_callback = None
    ) -> Dict:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            model_name: Whisper模型名称 (tiny, base, small, medium, large)
            language: 语言代码，"auto"表示自动检测
            progress_callback: 进度回调函数，接收进度百分比
        
        Returns:
            转录结果字典
        """
        if model_name is None:
            model_name = self.default_model
        
        # 加载模型
        model = self.load_model(model_name)
        
        # 转录
        result = model.transcribe(
            audio_path,
            language=language if language != "auto" else None,
            verbose=True
        )
        
        return result
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """
        从视频文件中提取音频
        
        Args:
            video_path: 视频文件路径
            audio_path: 输出音频文件路径
        
        Returns:
            是否成功
        """
        try:
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec="pcm_s16le", ac=1, ar="16k")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return False
    
    def format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为SRT格式"""
        milliseconds = int(seconds * 1000)
        hours = milliseconds // 3600000
        milliseconds %= 3600000
        minutes = milliseconds // 60000
        milliseconds %= 60000
        seconds = milliseconds // 1000
        milliseconds %= 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def generate_srt(self, segments: List[Dict]) -> str:
        """生成SRT格式字幕"""
        srt_content = []
        for i, segment in enumerate(segments, 1):
            start_time = self.format_timestamp(segment["start"])
            end_time = self.format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            srt_content.append(str(i))
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")
        
        return "\n".join(srt_content)
    
    def generate_vtt(self, segments: List[Dict]) -> str:
        """生成VTT格式字幕"""
        vtt_content = ["WEBVTT", ""]
        for i, segment in enumerate(segments, 1):
            start_time = self.format_timestamp(segment["start"]).replace(",", ".")
            end_time = self.format_timestamp(segment["end"]).replace(",", ".")
            text = segment["text"].strip()
            
            vtt_content.append(f"{i}")
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(text)
            vtt_content.append("")
        
        return "\n".join(vtt_content)
    
    def generate_txt(self, segments: List[Dict]) -> str:
        """生成纯文本格式字幕"""
        return "\n".join(segment["text"].strip() for segment in segments)
    
    def generate_subtitles(
        self, 
        audio_path: str, 
        model_name: str = None, 
        language: str = "auto",
        formats: List[str] = None,
        progress_callback = None
    ) -> Dict[str, str]:
        """
        生成多种格式的字幕
        
        Args:
            audio_path: 音频文件路径
            model_name: Whisper模型名称
            language: 语言代码
            formats: 要生成的字幕格式列表，默认["srt", "vtt", "txt"]
            progress_callback: 进度回调函数
        
        Returns:
            格式到字幕内容的映射字典
        """
        if formats is None:
            formats = ["srt", "vtt", "txt"]
        
        # 转录音频
        result = self.transcribe(audio_path, model_name, language, progress_callback)
        
        # 生成字幕
        subtitles = {}
        if "srt" in formats:
            subtitles["srt"] = self.generate_srt(result["segments"])
        if "vtt" in formats:
            subtitles["vtt"] = self.generate_vtt(result["segments"])
        if "txt" in formats:
            subtitles["txt"] = self.generate_txt(result["segments"])
        
        return subtitles


# 创建全局Whisper服务实例
whisper_service = WhisperService()