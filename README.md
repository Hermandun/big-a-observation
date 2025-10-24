# A股观察室 - 实时智能分析系统

基于 Python + Streamlit + DeepSeek AI 的 A股实时新闻分析和投资推荐系统。

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

### 1. 克隆项目

```bash
git clone https://github.com/hermandun/big-a-observation.git
cd big-a-observation
```

### 2. 配置环境

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key
```

### 3. 启动应用

**方式一：使用启动脚本（推荐）**
```bash
./run.sh
```

**方式二：手动启动**
```bash
streamlit run src/streamlit_app.py
```

### 4. 访问应用

- **本地访问**：http://localhost:8501
- **登录账号**：
  - 用户名：`admin`
  - 密码：`admin123`

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
- **AI模型**：DeepSeek-V3 (一级分析) + DeepSeek-R1 (二级分析)
- **数据源**：新浪财经 7x24 API + AkShare
- **数据库**：SQLite 3
- **身份验证**：Passlib (bcrypt)

## 🎨 混合模式架构

系统采用智能混合模式，兼顾速度与质量：

- **一级分析**：DeepSeek-V3 快速模型（5-10秒）
  - 持续监控新闻流
  - 快速判断影响
  - 不阻塞后续分析

- **二级分析**：DeepSeek-R1 推理模型（30-120秒）
  - 深度分析有影响新闻
  - 队列化处理
  - 高质量股票推荐

详见 [HYBRID_MODE_GUIDE.md](./HYBRID_MODE_GUIDE.md)

## ⚙️ 配置说明

### 环境变量 (.env)

```env
# DeepSeek API 配置（必填）
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_URL=https://api.siliconflow.cn/v1

# 数据库配置（可选，默认使用SQLite）
MONGO_URL=mongodb://localhost:27017
MONGO_DB=stock_analysis

# JWT 密钥（可选）
JWT_SECRET=your-secret-key-here
```

### 获取 DeepSeek API Key

1. 访问 [SiliconFlow](https://siliconflow.cn/)
2. 注册并获取 API Key
3. 将 Key 填入 `.env` 文件

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

**最后更新**：2025-10-24  
**版本**：v1.0  
**状态**：✅ 生产就绪