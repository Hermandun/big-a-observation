#!/bin/bash
# 部署到 GitHub 的脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署 A股观察室 到 GitHub..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -f "src/streamlit_app.py" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 获取 GitHub 用户名
echo -e "${YELLOW}📝 请输入你的 GitHub 用户名:${NC}"
read -p "用户名: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}❌ 用户名不能为空${NC}"
    exit 1
fi

REPO_NAME="big-a-observation"

echo -e "${GREEN}✅ 将创建仓库: https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"

# 检查是否已经初始化 git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 初始化 Git 仓库...${NC}"
    git init
    git branch -M main
else
    echo -e "${GREEN}✅ Git 仓库已存在${NC}"
fi

# 添加所有文件
echo -e "${YELLOW}📁 添加文件到 Git...${NC}"
git add .

# 检查是否有更改需要提交
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  没有新的更改需要提交${NC}"
else
    echo -e "${YELLOW}💾 提交更改...${NC}"
    git commit -m "Deploy: A股观察室 v0.2.0 - 混合模式架构"
fi

# 检查是否已添加 remote
if git remote | grep -q "^origin$"; then
    echo -e "${YELLOW}🔄 更新 remote URL...${NC}"
    git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
else
    echo -e "${YELLOW}🔗 添加 remote...${NC}"
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
fi

# 推送到 GitHub
echo -e "${YELLOW}⬆️  推送到 GitHub...${NC}"
echo -e "${YELLOW}注意：如果仓库不存在，请先在 GitHub 上创建仓库${NC}"
echo -e "${YELLOW}访问: https://github.com/new${NC}"
read -p "按回车继续推送..."

if git push -u origin main; then
    echo -e "${GREEN}✅ 成功推送到 GitHub!${NC}"
    echo ""
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo ""
    echo "📋 下一步："
    echo "1. 访问 https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "2. 进入 GitHub Copilot Spaces: https://github.com/copilot/spaces"
    echo "3. 点击 'New Space' 并选择你的仓库"
    echo "4. 配置 Secret: DEEPSEEK_API_KEY"
    echo "5. 点击 'Deploy'"
    echo ""
    echo -e "${YELLOW}🔐 别忘了配置 DEEPSEEK_API_KEY！${NC}"
else
    echo -e "${RED}❌ 推送失败${NC}"
    echo ""
    echo "💡 可能的原因："
    echo "1. 仓库不存在 - 请访问 https://github.com/new 创建仓库"
    echo "2. 没有权限 - 请检查 GitHub 认证"
    echo "3. 网络问题 - 请检查网络连接"
    echo ""
    echo "🔧 手动推送命令："
    echo "git push -u origin main"
    exit 1
fi
