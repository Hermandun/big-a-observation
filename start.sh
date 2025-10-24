#!/bin/bash

# 启动 Python 后端服务
echo "启动后端服务..."
"/Users/herman/Desktop/Dev/Big A Observation/.venv/bin/python" src/main.py &

# 使用 Python 的 http.server 启动前端服务
echo "启动前端服务..."
cd frontend
python3 -m http.server 8080

# 当脚本被中断时，确保关闭后端服务
trap "pkill -f 'python src/main.py'" EXIT