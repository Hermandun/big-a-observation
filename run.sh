#!/bin/bash

# A股观察室启动脚本

echo "🚀 启动 A股观察室..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，从 .env.example 复制..."
    cp .env.example .env
    echo "请编辑 .env 文件配置你的 API Key"
    exit 1
fi

# 启动 Streamlit 应用
echo "✅ 启动应用..."
streamlit run src/streamlit_app.py --server.port 8501 --server.address localhost
