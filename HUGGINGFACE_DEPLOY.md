# Hugging Face Spaces 部署指南

如果你想将项目部署到 Hugging Face Spaces，请按照以下步骤操作：

## 📋 准备工作

### 1. 在 Hugging Face 创建 Space

1. 访问 https://huggingface.co/spaces
2. 点击 "Create new Space"
3. 配置：
   - **Owner**: 选择你的账号
   - **Space name**: `big-a-observation`
   - **License**: MIT
   - **Space SDK**: 选择 **Streamlit**
   - **Visibility**: Public 或 Private

### 2. 准备部署文件

项目需要以下文件（已包含）：

```
big-a-observation/
├── app.py                    # Hugging Face Spaces 入口文件
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量模板
├── src/                      # 源代码
└── README.md                 # 文档
```

## 🚀 部署步骤

### 方式一：通过 Git 推送（推荐）

```bash
# 1. 克隆你的 Hugging Face Space 仓库
git clone https://huggingface.co/spaces/YOUR_USERNAME/big-a-observation
cd big-a-observation

# 2. 从本地项目复制文件
cp -r /path/to/your/project/* .

# 3. 创建 app.py（Hugging Face Spaces 入口）
cat > app.py << 'EOF'
import streamlit as st
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入主应用
from streamlit_app import *

# Hugging Face Spaces 会自动运行这个文件
EOF

# 4. 配置 Secrets（环境变量）
# 在 Hugging Face Space 设置页面添加：
# - DEEPSEEK_API_KEY
# - DEEPSEEK_API_URL

# 5. 提交并推送
git add .
git commit -m "Initial deployment"
git push
```

### 方式二：通过 GitHub 同步

1. 在 Hugging Face Space 设置页面
2. 找到 "Repository" 部分
3. 点击 "Link to GitHub"
4. 选择你的 GitHub 仓库：`hermandun/big-a-observation`
5. 自动同步代码

## ⚙️ 配置环境变量

在 Hugging Face Space 设置页面：

1. 进入 "Settings" 标签
2. 找到 "Repository secrets"
3. 添加以下 secrets：

```
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_API_URL=https://api.siliconflow.cn/v1
```

## 📝 创建 app.py

在项目根目录创建 `app.py`（Hugging Face Spaces 入口文件）：

```python
#!/usr/bin/env python3
"""
A股观察室 - Hugging Face Spaces 入口文件
"""

import streamlit as st
import sys
import os

# 添加 src 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 从 Hugging Face Secrets 读取环境变量
if 'DEEPSEEK_API_KEY' in st.secrets:
    os.environ['DEEPSEEK_API_KEY'] = st.secrets['DEEPSEEK_API_KEY']
if 'DEEPSEEK_API_URL' in st.secrets:
    os.environ['DEEPSEEK_API_URL'] = st.secrets['DEEPSEEK_API_URL']

# 导入并运行主应用
from streamlit_app import render_login, render_main

# 配置页面（必须在最前面）
st.set_page_config(page_title="A股观察室", page_icon="📈", layout="wide")

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 渲染应用
if st.session_state.authenticated:
    render_main()
else:
    render_login()
```

## 🔧 requirements.txt 优化

Hugging Face Spaces 可能需要更轻量的依赖：

```txt
streamlit==1.50.0
streamlit-autorefresh==1.0.1
requests==2.32.5
python-dotenv==1.1.1
akshare==1.17.71
passlib==1.7.4
pandas==2.3.3
bcrypt==5.0.0
```

## ⚠️ 注意事项

### 1. 数据库问题

Hugging Face Spaces 的文件系统是临时的，每次重启会重置：

**解决方案**：
- 使用外部数据库（如 MongoDB Atlas）
- 或简化为无状态应用（每次启动初始化）

### 2. API Key 安全

**重要**：不要将 API Key 提交到 Git！

使用 Hugging Face Secrets：

```python
import streamlit as st

# 从 Secrets 读取
api_key = st.secrets.get("DEEPSEEK_API_KEY", None)
if not api_key:
    st.error("请配置 DEEPSEEK_API_KEY")
    st.stop()
```

### 3. 性能限制

Hugging Face Spaces 免费版限制：
- CPU: 2 cores
- RAM: 16GB
- 超时: 60秒

**优化建议**：
- 使用 V3 模型（更快）
- 减少并发请求
- 添加缓存机制

## 🎯 部署后测试

1. 访问你的 Space URL：
   ```
   https://huggingface.co/spaces/YOUR_USERNAME/big-a-observation
   ```

2. 测试功能：
   - [ ] 登录功能
   - [ ] 新闻抓取
   - [ ] V3 一级分析
   - [ ] R1 二级分析
   - [ ] 自动刷新

## 📚 相关链接

- [Hugging Face Spaces 文档](https://huggingface.co/docs/hub/spaces)
- [Streamlit on Spaces](https://huggingface.co/docs/hub/spaces-sdks-streamlit)
- [管理 Secrets](https://huggingface.co/docs/hub/spaces-overview#managing-secrets)

## 🆘 常见问题

### Q: 如何查看日志？
A: 在 Space 页面点击 "Logs" 标签

### Q: 如何更新代码？
A: 
- 方式一：`git push` 到 Hugging Face Space 仓库
- 方式二：如果关联了 GitHub，推送到 GitHub 即可自动同步

### Q: 如何重启应用？
A: 在 Space 设置页面点击 "Factory reboot"

---

**当前状态**：✅ 代码已推送到 GitHub，可以随时部署到 Hugging Face Spaces
