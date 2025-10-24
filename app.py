#!/usr/bin/env python3
"""
A股观察室 - Hugging Face Spaces 入口文件

这个文件是 Hugging Face Spaces 的入口点。
Spaces 会自动运行这个 app.py 文件来启动 Streamlit 应用。
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 从 Hugging Face Secrets 读取环境变量（如果存在）
try:
    if hasattr(st, 'secrets'):
        if 'DEEPSEEK_API_KEY' in st.secrets:
            os.environ['DEEPSEEK_API_KEY'] = st.secrets['DEEPSEEK_API_KEY']
        if 'DEEPSEEK_API_URL' in st.secrets:
            os.environ['DEEPSEEK_API_URL'] = st.secrets['DEEPSEEK_API_URL']
except Exception:
    pass

# 如果没有配置环境变量，使用默认值
if 'DEEPSEEK_API_URL' not in os.environ:
    os.environ['DEEPSEEK_API_URL'] = 'https://api.siliconflow.cn/v1'

# 导入主应用（这会执行 streamlit_app.py 中的所有代码）
if __name__ == "__main__":
    # 设置工作目录
    os.chdir(current_dir)
    
    # 导入并运行
    import streamlit_app
