import sys
import os
import tempfile
import requests

# 创建一个临时的音频文件
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    # 写入一个简单的WAV文件头（虽然不是真实的音频数据，但足够用于测试）
    f.write(b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    temp_file_path = f.name

try:
    # 注册一个用户
    print("Registering user...")
    register_response = requests.post(
        "http://localhost:8000/api/auth/register",
        json={
            "username": "testuser_task",
            "email": "test_task@example.com",
            "password": "testpassword123"
        }
    )
    print(f"Register status: {register_response.status_code}")
    
    # 登录获取令牌
    print("\nLogging in...")
    login_response = requests.post(
        "http://localhost:8000/api/auth/login/json",
        json={
            "email": "test_task@example.com",
            "password": "testpassword123"
        }
    )
    print(f"Login status: {login_response.status_code}")
    token = login_response.json().get("access_token")
    
    if token:
        # 创建任务
        print("\nCreating task...")
        headers = {"Authorization": f"Bearer {token}"}
        with open(temp_file_path, "rb") as f:
            task_response = requests.post(
                "http://localhost:8000/api/tasks",
                headers=headers,
                files={"file": f},
                data={
                    "language": "auto",
                    "model": "base",
                    "priority": 0
                }
            )
        print(f"Task creation status: {task_response.status_code}")
        print(f"Task response: {task_response.json()}")
        
        # 获取任务ID
        task_id = task_response.json().get("id")
        if task_id:
            print(f"\nTask created successfully with ID: {task_id}")
            print("Task should now be processed by Celery worker.")
            
            # 检查任务状态
            print("\nChecking task status...")
            status_response = requests.get(
                f"http://localhost:8000/api/tasks/{task_id}",
                headers=headers
            )
            print(f"Task status: {status_response.status_code}")
            print(f"Task status response: {status_response.json()}")

except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # 清理临时文件
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    print("\nTest completed!")