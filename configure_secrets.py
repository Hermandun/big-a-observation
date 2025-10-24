#!/usr/bin/env python3
"""
配置 Hugging Face Space Secrets
"""

from huggingface_hub import HfApi, add_space_secret

def main():
    print("🔐 配置 API Key Secrets\n")
    
    api = HfApi()
    repo_id = "Ayar1111/big-a-observation"
    
    secrets = {
        "DEEPSEEK_API_KEY": "sk-bzguagzymvuubepardjpxvqmbljfhxpmgceddsrqzjnouezw",
        "DEEPSEEK_API_URL": "https://api.siliconflow.cn/v1"
    }
    
    for key, value in secrets.items():
        try:
            add_space_secret(repo_id=repo_id, key=key, value=value)
            print(f"  ✅ {key}")
        except Exception as e:
            print(f"  ❌ {key}: {e}")
    
    print("\n✅ API Key 配置完成！")
    print(f"\n访问你的应用: https://huggingface.co/spaces/{repo_id}")
    print(f"查看构建日志: https://huggingface.co/spaces/{repo_id}/logs")

if __name__ == "__main__":
    main()
