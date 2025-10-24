#!/usr/bin/env python3
"""
检查 Hugging Face Space 状态和日志
"""

from huggingface_hub import HfApi
import requests

def main():
    print("🔍 检查 Space 状态\n")
    
    api = HfApi()
    repo_id = "Ayar1111/big-a-observation"
    
    try:
        # 获取 Space 信息
        space_info = api.space_info(repo_id=repo_id)
        
        print("=" * 60)
        print("Space 基本信息")
        print("=" * 60)
        print(f"名称: {space_info.id}")
        print(f"SDK: {space_info.sdk}")
        print(f"状态: {space_info.runtime.get('stage', 'unknown') if hasattr(space_info, 'runtime') else 'unknown'}")
        
        # 检查文件
        print("\n" + "=" * 60)
        print("已上传的文件")
        print("=" * 60)
        
        files = api.list_repo_files(repo_id=repo_id, repo_type="space")
        for f in sorted(files):
            print(f"  ✅ {f}")
        
        # 检查是否有 app.py
        if "app.py" not in files:
            print("\n⚠️  警告：缺少 app.py 文件！")
        
        # 检查 SDK 配置
        print("\n" + "=" * 60)
        print("SDK 配置检查")
        print("=" * 60)
        
        if hasattr(space_info, 'sdk'):
            print(f"SDK: {space_info.sdk}")
            if space_info.sdk != 'streamlit':
                print(f"⚠️  SDK 不是 Streamlit，当前是: {space_info.sdk}")
                print(f"建议：需要修改 README.md 中的 sdk 配置")
        
    except Exception as e:
        print(f"❌ 获取 Space 信息失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("建议检查")
    print("=" * 60)
    print(f"1. 查看日志: https://huggingface.co/spaces/{repo_id}/logs")
    print(f"2. 查看设置: https://huggingface.co/spaces/{repo_id}/settings")
    print(f"3. 查看文件: https://huggingface.co/spaces/{repo_id}/tree/main")

if __name__ == "__main__":
    main()
