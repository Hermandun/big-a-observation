# A股观察室 - 实时智能分析系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50.0-FF4B4B.svg)
![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**基于 Python + Streamlit + DeepSeek AI 的 A股实时新闻分析和投资推荐系统**

[功能特性](#-核心功能) | [快速开始](#-快速开始) | [部署指南](#-部署到-github-copilot-spaces)

</div>

---

## 🎯 核心功能

1. **实时新闻监控**：自动抓取新浪财经7x24小时实时新闻
2. **智能影响分析**：使用 DeepSeek-R1 模型进行两级分析
   - 一级分析：快速判断新闻是否对A股特定板块产生显著影响
   - 二级分析：提供具体股票操作建议（买入时机、价格、止损点等）
3. **实时行情整合**：通过 AkShare 获取A股实时数据
4. **三面板展示**：
   - 左侧：实时新闻流
   - 中间：DeepSeek 分析日志
   - 右侧：操作建议和推荐股票
5. **自动刷新**：每10秒自动刷新，保持登录状态

## 📁 项目结构

```
Big A Observation/
├── src/
│   ├── streamlit_app.py          # Streamlit 主应用
│   ├── services/
│   │   ├── realtime_manager.py   # 新闻抓取 + DeepSeek分析 + 股票筛选
│   │   └── auth_service.py       # SQLite 身份验证
│   └── models/
│       └── database.py            # 数据库模型
├── .env                           # API密钥配置
├── stock_analysis.db              # SQLite 数据库
├── test_flow.py                   # 完整流程测试脚本
└── README.md                      # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd "/Users/herman/Desktop/Dev/Big A Observation"
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动应用

```bash
streamlit run src/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

### 3. 访问应用

- **本地访问**：http://localhost:8501
- **局域网访问**：http://192.168.31.51:8501

### 4. 登录

- **用户名**：`admin`
- **密码**：`admin123`

## 🧪 测试

运行完整流程测试：

```bash
python test_flow.py
```

## 📊 工作流程

```
新浪7x24新闻
    ↓
[一级分析] DeepSeek-R1
    ├─ 无显著影响 → 继续监控
    └─ 有显著影响 →
        ↓
    AkShare 筛选候选股票
        ↓
    [二级分析] DeepSeek-R1
        ↓
    生成具体操作建议
```

## 🔧 技术栈

- **前端框架**：Streamlit 1.50.0
- **AI模型**：DeepSeek-R1 (via SiliconFlow API)
- **数据源**：新浪财经 7x24 API + AkShare
- **数据库**：SQLite 3
- **身份验证**：Passlib (bcrypt)

## 🔄 当前状态

### ✅ 已完成
- [x] 项目结构搭建
- [x] SQLite 数据库和身份验证
- [x] Streamlit 三面板界面
- [x] 10秒自动刷新（保持登录）
- [x] 新浪财经7x24新闻抓取
- [x] DeepSeek 一级和二级分析
- [x] AkShare A股数据集成

---

## 🌐 部署到 GitHub Copilot Spaces

### 方法 1: 通过 GitHub Web 界面

1. **创建 GitHub 仓库**
   - 访问 https://github.com/new
   - 仓库名：`big-a-observation`
   - 设置为 Public 或 Private

2. **推送代码**
   ```bash
   cd "/Users/herman/Desktop/Dev/Big A Observation"
   git init
   git add .
   git commit -m "Initial commit: A股观察室"
   git branch -M main
   git remote add origin https://github.com/你的用户名/big-a-observation.git
   git push -u origin main
   ```

3. **部署到 Copilot Spaces**
   - 访问 https://github.com/copilot/spaces
   - 点击 "New Space"
   - 选择你的仓库 `big-a-observation`
   - 配置 Secrets:
     - 名称: `DEEPSEEK_API_KEY`
     - 值: 你的 DeepSeek API Key
   - 点击 "Deploy"

### 方法 2: 使用命令行

```bash
# 1. 安装 GitHub CLI (如果未安装)
brew install gh  # macOS

# 2. 登录 GitHub
gh auth login

# 3. 创建仓库并推送
cd "/Users/herman/Desktop/Dev/Big A Observation"
git init
git add .
git commit -m "Initial commit"
gh repo create big-a-observation --public --source=. --remote=origin --push

# 4. 配置 Secret
gh secret set DEEPSEEK_API_KEY

# 5. 部署到 Copilot Spaces (需要通过 Web 界面)
```

## 🔐 环境变量配置

在 GitHub Copilot Spaces 中需要配置以下 Secret：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxx...` |

## 📊 混合模式架构

详见 [HYBRID_MODE_GUIDE.md](HYBRID_MODE_GUIDE.md)

### 性能优势

- **一级分析**: V3快速模型（5-10秒） - 持续监控
- **二级分析**: R1推理模型（30-120秒） - 深度分析
- **10分钟覆盖**: 60条一级分析 + 后台R1深度推荐

---

<div align="center">

**最后更新**：2025-01-24  
**版本**：v0.2.0  
**状态**：✅ 生产就绪

Made with ❤️ by A股观察室团队

**如果这个项目对你有帮助，请给个 ⭐ Star！**

</div>