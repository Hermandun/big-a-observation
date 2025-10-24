# 部署到 Hugging Face Spaces

## 🚀 快速部署（3分钟）

### 步骤 1：创建 Space

1. 访问 https://huggingface.co/new-space
2. 登录你的账号
3. 填写信息：
   - **Space name**: `big-a-observation`
   - **License**: MIT
   - **Select the Space SDK**: 选择 **Streamlit**
   - **Space hardware**: CPU basic（免费）
   - **Visibility**: Public
4. 点击 **Create Space**

### 步骤 2：上传代码

在你创建的 Space 页面：

1. 点击 **Files** 标签
2. 点击 **Add file** → **Upload files**
3. 上传以下文件/文件夹：
   ```
   - app.py
   - requirements.txt
   - src/（整个文件夹）
   - .env.example
   - README.md
   - HYBRID_MODE_GUIDE.md
   ```

或者使用 Git：

```bash
# 克隆你的 Hugging Face Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/big-a-observation
cd big-a-observation

# 复制文件
cp -r "/Users/herman/Desktop/Dev/Big A Observation/app.py" .
cp -r "/Users/herman/Desktop/Dev/Big A Observation/requirements.txt" .
cp -r "/Users/herman/Desktop/Dev/Big A Observation/src" .
cp -r "/Users/herman/Desktop/Dev/Big A Observation/README.md" .

# 提交并推送
git add .
git commit -m "Initial deployment"
git push
```

### 步骤 3：配置 API Key

1. 在 Space 页面点击 **Settings** 标签
2. 找到 **Repository secrets** 部分
3. 点击 **New secret**
4. 添加：
   - **Name**: `DEEPSEEK_API_KEY`
   - **Value**: 你的 API Key（如：`sk-bzguagzymvuubepardjpxvqmbljfhxpmgceddsrqzjnouezw`）
5. 点击 **Add**
6. 重复添加：
   - **Name**: `DEEPSEEK_API_URL`
   - **Value**: `https://api.siliconflow.cn/v1`

### 步骤 4：等待部署

- Space 会自动构建和启动
- 查看 **Logs** 标签了解进度
- 看到 "You can now view your Streamlit app" 表示成功

### 步骤 5：访问应用

你的应用将在以下地址可用：
```
https://huggingface.co/spaces/YOUR_USERNAME/big-a-observation
```

默认登录账号：
- 用户名：`admin`
- 密码：`admin123`

## 🔄 更新代码

### 方式一：Web 界面上传
在 Space 的 **Files** 标签直接上传修改的文件

### 方式二：Git 推送
```bash
cd big-a-observation
# 修改代码
git add .
git commit -m "更新说明"
git push
```

### 方式三：从 GitHub 同步
1. 在 Space **Settings** 中
2. 找到 **Linked repositories**
3. 关联你的 GitHub 仓库：`https://github.com/hermandun/big-a-observation`
4. 每次推送到 GitHub 会自动同步到 Hugging Face

## 📝 注意事项

1. **数据库**：Hugging Face Spaces 重启会清空数据
   - 当前使用 SQLite，每次重启会重置用户数据
   - 如需持久化，考虑使用云数据库（如 MongoDB Atlas）

2. **性能**：免费版限制
   - CPU: 2 cores
   - RAM: 16GB
   - 建议使用 V3 模型以保证速度

3. **安全**：API Key 必须通过 Secrets 配置，不要提交到代码中

## 🆘 故障排查

### 应用无法启动
1. 查看 **Logs** 标签
2. 检查 requirements.txt 是否正确
3. 确认 API Key 已配置

### API 调用失败
1. 确认 Secrets 中的 API Key 正确
2. 检查 API 配额是否用完
3. 查看日志中的错误信息

## 📚 相关链接

- [你的 GitHub 仓库](https://github.com/hermandun/big-a-observation)
- [Hugging Face Spaces 文档](https://huggingface.co/docs/hub/spaces)
- [Streamlit on Spaces](https://huggingface.co/docs/hub/spaces-sdks-streamlit)

---

**准备就绪！** 现在就去 https://huggingface.co/new-space 创建你的 Space 吧！
