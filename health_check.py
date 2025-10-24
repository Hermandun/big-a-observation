#!/usr/bin/env python3
"""快速健康检查"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🏥 系统健康检查")
print("=" * 60)

# 1. 检查Streamlit
import subprocess
result = subprocess.run(['curl', '-s', 'http://localhost:8501/_stcore/health'], 
                       capture_output=True, text=True)
if result.returncode == 0 and 'ok' in result.stdout:
    print("✅ Streamlit 服务正常运行")
else:
    print("❌ Streamlit 服务未运行")
    sys.exit(1)

# 2. 检查新闻抓取
from services.realtime_manager import RealTimeManager
rt = RealTimeManager()
news = rt.fetch_latest_news(page=1, page_size=1)
if news and len(news) > 0:
    print(f"✅ 新闻抓取正常 (获取到 {len(news)} 条)")
else:
    print("⚠️ 新闻抓取异常")

# 3. 检查环境变量
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key and len(api_key) > 10:
    print(f"✅ DeepSeek API密钥已配置 ({api_key[:8]}...)")
else:
    print("❌ DeepSeek API密钥未配置")

# 4. 检查数据库
if os.path.exists('stock_analysis.db'):
    print("✅ SQLite数据库文件存在")
else:
    print("⚠️ SQLite数据库文件不存在（首次登录时会创建）")

print("=" * 60)
print()
print("🎉 系统就绪！")
print()
print("📱 打开浏览器访问: http://localhost:8501")
print("🔑 使用 admin/admin123 登录")
print()
print("🔍 观察要点：")
print("  1. 登录后，右上角会显示 '刷新次数'")
print("  2. 中间日志面板会显示处理步骤")
print("  3. 如果出错，会在页面顶部显示红色/黄色提示框")
print("  4. 每10秒自动刷新一次")
print()
