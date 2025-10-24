#!/usr/bin/env python3
"""
使用 HF API 直接上传文件（不使用 Git）
"""

from huggingface_hub import HfApi
from pathlib import Path
import time

def main():
    print("🚀 使用 API 直接上传文件到 Hugging Face Space\n")
    
    api = HfApi()
    current_dir = Path(__file__).parent
    
    username = "Ayar1111"
    space_name = "big-a-observation"
    repo_id = f"{username}/{space_name}"
    
    print(f"目标: {repo_id}\n")
    
    # 上传单个文件
    files_to_upload = [
        ("app.py", "app.py"),
        ("requirements.txt", "requirements.txt"),
    ]
    
    print("📤 上传主文件...")
    for src, dst in files_to_upload:
        src_path = current_dir / src
        if src_path.exists():
            try:
                api.upload_file(
                    path_or_fileobj=str(src_path),
                    path_in_repo=dst,
                    repo_id=repo_id,
                    repo_type="space",
                )
                print(f"  ✅ {dst}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  ❌ {dst}: {e}")
    
    # 上传 src 目录
    print("\n📤 上传 src/ 目录...")
    src_dir = current_dir / "src"
    if src_dir.exists():
        try:
            api.upload_folder(
                folder_path=str(src_dir),
                path_in_repo="src",
                repo_id=repo_id,
                repo_type="space",
                ignore_patterns=["__pycache__", "*.pyc", ".DS_Store"]
            )
            print(f"  ✅ src/")
        except Exception as e:
            print(f"  ❌ src/: {e}")
    
    # 创建并上传 README
    print("\n📤 上传 README.md...")
    readme_content = """---
title: A股观察室
emoji: 📈
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.50.0
app_file: app.py
pinned: false
license: mit
---

# A股观察室 - 实时智能分析系统

基于 DeepSeek AI 的 A股实时新闻分析和投资推荐系统。

## 功能特点

- 🔍 实时监控新浪财经7x24新闻
- 🤖 AI智能影响分析（DeepSeek-V3 + R1混合模式）
- 📊 自动推荐股票操作策略
- ⚡ 每10秒自动刷新

## 使用说明

默认登录账号：
- 用户名：`admin`
- 密码：`admin123`

## 配置

需要在 Settings → Repository secrets 中配置：
- `DEEPSEEK_API_KEY`: 你的 DeepSeek API Key
- `DEEPSEEK_API_URL`: `https://api.siliconflow.cn/v1`

## 项目地址

GitHub: https://github.com/Hermandun/big-a-observation
"""
    
    try:
        api.upload_file(
            path_or_fileobj=readme_content.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="space",
        )
        print(f"  ✅ README.md")
    except Exception as e:
        print(f"  ❌ README.md: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 文件上传完成！")
    print("=" * 60)
    print(f"\n📱 Space: https://huggingface.co/spaces/{repo_id}")
    print(f"\n⚠️  下一步：配置 API Key")
    print(f"访问: https://huggingface.co/spaces/{repo_id}/settings")
    print(f"\n添加 Secrets:")
    print(f"  DEEPSEEK_API_KEY = sk-bzguagzymvuubepardjpxvqmbljfhxpmgceddsrqzjnouezw")
    print(f"  DEEPSEEK_API_URL = https://api.siliconflow.cn/v1")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
