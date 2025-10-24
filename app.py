#!/usr/bin/env python3
"""
A股观察室 - Hugging Face Spaces 入口文件
"""

import streamlit as st
import sys
import os
from pathlib import Path
import time

# ⚠️ 必须在最开始配置页面（在任何其他 Streamlit 命令之前）
st.set_page_config(page_title="A股观察室", page_icon="📈", layout="wide")

# 添加 src 目录到 Python 路径
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 从 Hugging Face Secrets 读取环境变量
try:
    if hasattr(st, 'secrets') and st.secrets:
        if 'DEEPSEEK_API_KEY' in st.secrets:
            os.environ['DEEPSEEK_API_KEY'] = st.secrets['DEEPSEEK_API_KEY']
        if 'DEEPSEEK_API_URL' in st.secrets:
            os.environ['DEEPSEEK_API_URL'] = st.secrets['DEEPSEEK_API_URL']
except Exception as e:
    # Secrets 未配置时不报错
    pass

# 设置默认值
if 'DEEPSEEK_API_URL' not in os.environ:
    os.environ['DEEPSEEK_API_URL'] = 'https://api.siliconflow.cn/v1'

# 检查 API Key
if 'DEEPSEEK_API_KEY' not in os.environ:
    st.error("⚠️ 未配置 DEEPSEEK_API_KEY")
    st.info("请在 Space Settings → Repository secrets 中添加 DEEPSEEK_API_KEY")
    st.stop()

# 导入其他必要的模块
try:
    from streamlit_autorefresh import st_autorefresh
    from services.realtime_manager import RealTimeManager
except ImportError as e:
    st.error(f"❌ 导入模块失败: {e}")
    st.info("请检查 requirements.txt 是否包含所有依赖")
    st.stop()

# 只在已登录状态下启用自动刷新
if 'authenticated' in st.session_state and st.session_state.authenticated:
    st_autorefresh(interval=10000, key="data_refresh")

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'rt_manager' not in st.session_state:
    st.session_state.rt_manager = RealTimeManager()
if 'last_seen_id' not in st.session_state:
    st.session_state.last_seen_id = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'use_reasoning_model' not in st.session_state:
    st.session_state.use_reasoning_model = False
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False
if 'analysis_start_time' not in st.session_state:
    st.session_state.analysis_start_time = None
if 'is_level2_analyzing' not in st.session_state:
    st.session_state.is_level2_analyzing = False
if 'level2_queue' not in st.session_state:
    st.session_state.level2_queue = []

# 登录页面
def render_login():
    st.title("A股观察室 — 实时推荐")
    
    st.markdown("### 🔐 用户登录")
    st.info("💡 默认账号: admin / admin123")
    
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")
        
        if submit:
            if username == "admin" and password == "admin123":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("✅ 登录成功！")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ 用户名或密码错误")

# 导入主渲染函数
try:
    # 直接导入 streamlit_app 模块中的函数
    # 需要临时移除 set_page_config 的调用
    import importlib.util
    spec = importlib.util.spec_from_file_location("streamlit_app", src_dir / "streamlit_app.py")
    streamlit_app_module = importlib.util.module_from_spec(spec)
    
    # 暂时覆盖 set_page_config 避免重复调用
    original_set_page_config = st.set_page_config
    st.set_page_config = lambda *args, **kwargs: None
    
    spec.loader.exec_module(streamlit_app_module)
    
    # 恢复原始函数
    st.set_page_config = original_set_page_config
    
    # 获取 render_main 函数
    render_main = streamlit_app_module.render_main
    process_news = streamlit_app_module.process_news
    
except Exception as e:
    st.error(f"❌ 加载主应用失败: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# 渲染应用
if st.session_state.authenticated:
    try:
        render_main()
    except Exception as e:
        st.error(f"❌ 应用运行出错: {e}")
        import traceback
        st.code(traceback.format_exc())
else:
    render_login()
