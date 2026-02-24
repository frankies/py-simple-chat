#!/bin/bash

# PythonAnywhere 快速设置脚本
# 在 PythonAnywhere 的 Bash 控制台中运行此脚本

set -e

echo "🚀 开始设置 PythonAnywhere 环境..."

# 配置变量
REPO_URL="https://github.com/yourusername/py-simple-chat.git"  # 替换为你的仓库地址
PROJECT_NAME="py-simple-chat"
PYTHON_VERSION="3.12"

# 1. 克隆仓库
echo "📦 克隆代码仓库..."
cd ~
if [ -d "$PROJECT_NAME" ]; then
    echo "⚠️  项目目录已存在，正在更新..."
    cd $PROJECT_NAME
    git pull origin main
else
    git clone $REPO_URL
    cd $PROJECT_NAME
fi

# 2. 安装 uv
echo "📦 安装 uv..."
pip install --user uv

# 3. 安装依赖
echo "📚 使用 uv 同步依赖..."
uv sync

# 4. 创建必要的数据文件
echo "📄 初始化数据文件..."
touch users.json friends.json ip_limit.json banned.json
echo "{}" > users.json
echo "{}" > friends.json
echo "{}" > ip_limit.json
echo "{}" > banned.json

# 5. 设置文件权限
echo "🔐 设置文件权限..."
chmod 644 *.json

echo ""
echo "✅ 设置完成！"
echo ""
echo "📝 下一步操作："
echo "1. 在 PythonAnywhere Web 页面创建新的 Web 应用"
echo "2. 配置 WSGI 文件（参考 wsgi.py）"
echo "3. 设置静态文件路径"
echo "4. 重新加载 Web 应用"
echo ""
echo "🌐 访问地址: https://yourusername.pythonanywhere.com"
