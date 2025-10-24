#!/usr/bin/env python3
"""
全自动 Hugging Face Space 部署
直接创建、初始化并上传所有文件
"""

from huggingface_hub import HfApi, login
from pathlib import Path
import shutil
import subprocess
import os
import time

def main():
    print("🚀 全自动部署 A股观察室到 Hugging Face Space\n")
    
    api = HfApi()
    current_dir = Path(__file__).parent
    
    # 你已登录的信息
    username = "Ayar1111"
    space_name = "big-a-observation"
    repo_id = f"{username}/{space_name}"
    
    print(f"目标 Space: {repo_id}\n")
    
    # 步骤 1: 创建 Space
    print("📋 步骤 1: 创建 Space...")
    try:
        # 尝试使用 Gradio SDK（更稳定）
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            exist_ok=True,
            space_sdk="gradio"
        )
        print("  ✅ Space 创建成功！")
        print(f"  URL: https://huggingface.co/spaces/{repo_id}\n")
        time.sleep(2)  # 等待仓库创建完成
    except Exception as e:
        print(f"  ⚠️  创建 Space 时出错: {e}")
        print(f"  尝试继续...\n")
    
    # 步骤 2: 准备文件
    print("📦 步骤 2: 准备文件...")
    temp_dir = current_dir / "hf_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 复制必要文件
    files_to_copy = {
        "app.py": "app.py",
        "requirements.txt": "requirements.txt",
        "src": "src"
    }
    
    for src, dst in files_to_copy.items():
        src_path = current_dir / src
        dst_path = temp_dir / dst
        
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, 
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
            print(f"  ✅ {src}/")
        elif src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"  ✅ {src}")
    
    # 创建 README.md
    readme = temp_dir / "README.md"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write("""---
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
""")
    print(f"  ✅ README.md")
    
    # 创建 .gitignore
    gitignore = temp_dir / ".gitignore"
    with open(gitignore, 'w') as f:
        f.write("*.db\n*.sqlite\n.env\n__pycache__/\n*.pyc\n.DS_Store\n*.log\ntest_*.py\n")
    print(f"  ✅ .gitignore\n")
    
    # 步骤 3: 使用 Git 上传
    print("🔧 步骤 3: 初始化 Git 并上传...")
    try:
        os.chdir(temp_dir)
        
        # Git 初始化
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit: A股观察室"], 
                      check=True, capture_output=True)
        print("  ✅ Git 仓库初始化完成")
        
        # 配置远程仓库
        remote_url = f"https://huggingface.co/spaces/{repo_id}"
        subprocess.run(["git", "remote", "add", "origin", remote_url], 
                      check=True, capture_output=True)
        print(f"  ✅ 配置远程仓库: {remote_url}")
        
        # 获取凭证
        whoami = api.whoami()
        token = whoami.get('auth', {}).get('accessToken', {}).get('displayName', '')
        
        if not token:
            print("\n  ⚠️  无法获取 token，请手动推送")
            print(f"\n  请运行以下命令：")
            print(f"  cd {temp_dir}")
            print(f"  git push https://Ayar1111:YOUR_TOKEN@huggingface.co/spaces/{repo_id} main")
        else:
            # 推送
            push_url = f"https://Ayar1111:{token}@huggingface.co/spaces/{repo_id}"
            result = subprocess.run(
                ["git", "push", push_url, "main"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✅ 文件上传成功！\n")
            else:
                print(f"  ⚠️  推送出错: {result.stderr}")
                print(f"\n  请手动推送：")
                print(f"  cd {temp_dir}")
                print(f"  git push https://Ayar1111:YOUR_TOKEN@huggingface.co/spaces/{repo_id} main\n")
        
    except Exception as e:
        print(f"  ❌ Git 操作失败: {e}\n")
    finally:
        os.chdir(current_dir)
    
    # 步骤 4: 配置提醒
    print("=" * 60)
    print("⚙️ 重要：配置 API Key")
    print("=" * 60)
    print(f"\n请访问: https://huggingface.co/spaces/{repo_id}/settings")
    print(f"\n在 'Variables and secrets' 部分添加：")
    print(f"\n  1. Secret name: DEEPSEEK_API_KEY")
    print(f"     Secret value: sk-bzguagzymvuubepardjpxvqmbljfhxpmgceddsrqzjnouezw")
    print(f"\n  2. Secret name: DEEPSEEK_API_URL")
    print(f"     Secret value: https://api.siliconflow.cn/v1")
    
    # 完成
    print("\n" + "=" * 60)
    print("🎉 部署完成！")
    print("=" * 60)
    print(f"\n📱 应用地址: https://huggingface.co/spaces/{repo_id}")
    print(f"⚙️  设置页面: https://huggingface.co/spaces/{repo_id}/settings")
    print(f"📋 查看日志: https://huggingface.co/spaces/{repo_id}/logs")
    print(f"\n🔐 默认登录:")
    print(f"   用户名: admin")
    print(f"   密码: admin123")
    print(f"\n⏳ 应用构建需要 2-3 分钟，配置 API Key 后会自动启动")
    print("=" * 60)
    
    # 清理
    print(f"\n🧹 清理临时文件...")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("  ✅ 完成")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  部署已取消")
        exit(0)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
