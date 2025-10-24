# 🚀 快速部署指南

## 方式一：一键部署脚本 (推荐)

```bash
cd "/Users/herman/Desktop/Dev/Big A Observation"
./deploy.sh
```

按提示输入你的 GitHub 用户名，脚本会自动完成：
1. ✅ 初始化 Git
2. ✅ 提交所有文件
3. ✅ 推送到 GitHub

## 方式二：手动步骤

### 第一步：创建 GitHub 仓库

访问 https://github.com/new 创建新仓库：
- 仓库名：`big-a-observation`
- 描述：A股观察室 - 实时智能分析系统
- 可见性：Public（公开）或 Private（私有）
- ❌ 不要勾选 "Add a README file"

### 第二步：推送代码

```bash
cd "/Users/herman/Desktop/Dev/Big A Observation"

# 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit: A股观察室 v0.2.0"

# 添加 GitHub 远程仓库（替换为你的用户名）
git remote add origin https://github.com/你的用户名/big-a-observation.git
git branch -M main
git push -u origin main
```

### 第三步：部署到 Copilot Spaces

1. 访问 https://github.com/copilot/spaces
2. 点击 **"New Space"**
3. 选择仓库：`big-a-observation`
4. 配置 **Secrets**：
   - 点击 "Settings" → "Secrets"
   - 添加新 Secret：
     - Name: `DEEPSEEK_API_KEY`
     - Value: `你的DeepSeek API Key`
5. 点击 **"Deploy"**

## 🔐 获取 DeepSeek API Key

1. 访问 https://cloud.siliconflow.cn/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 Key（格式：`sk-xxx...`）

## ✅ 部署成功后

访问你的 Space URL，例如：
```
https://github.com/你的用户名/big-a-observation
```

登录信息：
- 用户名：`admin`
- 密码：`admin123`

## 🐛 常见问题

### 问题 1: 推送失败 "repository not found"
**解决**：确保已在 GitHub 上创建仓库

### 问题 2: 认证失败
**解决**：配置 GitHub 认证
```bash
# 使用 Personal Access Token
git config --global credential.helper store
git push  # 输入用户名和 Token
```

### 问题 3: Space 启动失败
**解决**：检查 Secret 配置
- 确保 `DEEPSEEK_API_KEY` 已正确配置
- 检查 API Key 是否有效

### 问题 4: 端口冲突
**解决**：Copilot Spaces 会自动处理端口，无需手动配置

## 📝 部署后维护

### 更新代码
```bash
cd "/Users/herman/Desktop/Dev/Big A Observation"
git add .
git commit -m "更新说明"
git push
```

Copilot Spaces 会自动检测更新并重新部署。

### 查看日志
在 Copilot Spaces 界面点击 "Logs" 查看运行日志

### 重启应用
在 Copilot Spaces 界面点击 "Restart"

## 🎉 完成！

现在你的 A股观察室已经在云端运行了！
分享你的 Space URL 给朋友使用吧！
