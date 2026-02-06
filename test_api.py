#!/usr/bin/env python3
"""
API测试脚本
用于验证字幕生成API的功能
"""
import os
import sys
import time
import json
import requests
import argparse
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000/api"
HEALTH_URL = "http://localhost:8000/health"


def print_step(step):
    """打印步骤信息"""
    print(f"\n{'=' * 50}")
    print(f"STEP: {step}")
    print('=' * 50)


def print_response(response):
    """打印响应信息"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response Body:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print("Response Body:")
        print(response.text)


def test_health():
    """测试健康检查端点"""
    print_step("Testing Health Check Endpoint")
    response = requests.get(HEALTH_URL)
    print_response(response)
    return response.status_code == 200


def register_user(username, email, password):
    """注册新用户"""
    print_step("Registering New User")
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    print_response(response)
    
    if response.status_code == 201:
        return response.json()
    return None


def login_user(email, password):
    """用户登录"""
    print_step("Logging In User")
    url = f"{BASE_URL}/auth/login/json"
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    return None


def create_task(token, file_path, language="auto", model="base", priority=0):
    """创建字幕生成任务"""
    print_step("Creating Subtitle Generation Task")
    url = f"{BASE_URL}/tasks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return None
    
    # 获取文件名
    filename = os.path.basename(file_path)
    
    # 准备文件
    files = {
        "file": (filename, open(file_path, "rb"))
    }
    
    # 准备表单数据
    data = {
        "language": language,
        "model": model,
        "priority": str(priority)
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    print_response(response)
    
    if response.status_code == 201:
        return response.json()
    return None


def get_task_status(token, task_id):
    """获取任务状态"""
    print_step(f"Getting Task Status for Task ID: {task_id}")
    url = f"{BASE_URL}/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    return None


def wait_for_task_completion(token, task_id, max_wait=300, check_interval=10):
    """等待任务完成"""
    print_step(f"Waiting for Task Completion (Task ID: {task_id})")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        task = get_task_status(token, task_id)
        if task:
            status = task.get("status")
            progress = task.get("progress", 0)
            print(f"Current Status: {status}, Progress: {progress}%")
            
            if status == "completed":
                print("Task completed successfully!")
                return True
            elif status == "failed":
                print("Task failed!")
                return False
        
        print(f"Waiting {check_interval} seconds...")
        time.sleep(check_interval)
    
    print("Timeout: Task did not complete within the specified time.")
    return False


def get_task_subtitles(token, task_id):
    """获取任务的字幕列表"""
    print_step(f"Getting Subtitles for Task ID: {task_id}")
    url = f"{BASE_URL}/tasks/{task_id}/subtitles"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    return None


def download_subtitle(token, subtitle_id, output_dir="."):
    """下载字幕文件"""
    print_step(f"Downloading Subtitle for Subtitle ID: {subtitle_id}")
    url = f"{BASE_URL}/subtitles/{subtitle_id}/download"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # 获取文件名
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[1].strip('"')
        
        if not filename:
            filename = f"subtitle_{subtitle_id}.srt"
        
        # 保存文件
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"Subtitle downloaded successfully: {output_path}")
        return output_path
    else:
        print_response(response)
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Subtitle API Test Script")
    parser.add_argument("file", help="Path to audio/video file for testing")
    parser.add_argument("--username", default="testuser", help="Username for testing")
    parser.add_argument("--email", default="test@example.com", help="Email for testing")
    parser.add_argument("--password", default="testpassword", help="Password for testing")
    parser.add_argument("--language", default="auto", help="Language for subtitle generation")
    parser.add_argument("--model", default="base", help="Whisper model to use")
    parser.add_argument("--priority", type=int, default=0, help="Task priority")
    parser.add_argument("--max-wait", type=int, default=300, help="Maximum wait time for task completion (seconds)")
    
    args = parser.parse_args()
    
    # 测试健康检查
    if not test_health():
        print("Health check failed. Exiting...")
        sys.exit(1)
    
    # 注册用户
    user = register_user(args.username, args.email, args.password)
    if not user:
        print("User registration failed. Exiting...")
        sys.exit(1)
    
    # 登录用户
    login = login_user(args.email, args.password)
    if not login:
        print("User login failed. Exiting...")
        sys.exit(1)
    
    access_token = login.get("access_token")
    if not access_token:
        print("Failed to get access token. Exiting...")
        sys.exit(1)
    
    # 创建任务
    task = create_task(access_token, args.file, args.language, args.model, args.priority)
    if not task:
        print("Task creation failed. Exiting...")
        sys.exit(1)
    
    task_id = task.get("id")
    if not task_id:
        print("Failed to get task ID. Exiting...")
        sys.exit(1)
    
    # 等待任务完成
    if not wait_for_task_completion(access_token, task_id, args.max_wait):
        print("Task did not complete successfully. Exiting...")
        sys.exit(1)
    
    # 获取字幕列表
    subtitles = get_task_subtitles(access_token, task_id)
    if not subtitles:
        print("Failed to get subtitles. Exiting...")
        sys.exit(1)
    
    # 下载字幕文件
    if subtitles:
        # 创建输出目录
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        for subtitle in subtitles:
            subtitle_id = subtitle.get("id")
            if subtitle_id:
                download_subtitle(access_token, subtitle_id, output_dir)
    
    print_step("API Test Completed Successfully!")


if __name__ == "__main__":
    main()