# GitHub Actions 部署到 PythonAnywhere - 快速指南

## 工作原理

本部署方案使用：
- `pa` 命令行工具（pythonanywhere 包提供）
- PythonAnywhere API Token 进行身份验证
- `uv` 管理 Python 依赖
- GitHub Actions 自动化部署流程

## 一、准备工作（3分钟）

### 1. 获取 PythonAnywhere API Token

1. 登录 https://www.pythonanywhere.com/
2. 访问 Account → API Token
3. 点击 "Create a new API token"
4. 复制 token（只显示一次）

### 2. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

Settings → Secrets and variables → Actions → New repository secret

| 名称 | 值 | 示例 |
|------|-----|------|
| PA_API_TOKEN | 你的 API Token | `1234abcd...` |
| PA_USERNAME | PythonAnywhere 用户名 | `myusername` |
| PA_DOMAIN | Web 应用域名 | `myusername.pythonanywhere.com` |
| PA_PROJECT_PATH | 项目路径 | `/home/myusername/py-simple-chat` |

注意：PA_PROJECT_PATH 使用你的用户名，项目名称保持 `py-simple-chat`

## 二、首次部署（自动完成）

推送代码触发自动部署：

```bash
git add .
git commit -m "Setup CI/CD"
git push origin main
```

GitHub Actions 会自动完成以下操作：
- ✅ 克隆仓库到 PythonAnywhere
- ✅ 创建 Web 应用
- ✅ 配置 WSGI 文件
- ✅ 初始化数据文件
- ✅ 安装依赖
- ✅ 启动应用

查看部署状态：GitHub → Actions 标签

## 三、验证部署

访问你的应用：https://yourusername.pythonanywhere.com

## 常见问题

### Q: pa 命令如何工作？

A: `pa` 是 PythonAnywhere 官方 CLI 工具，通过以下方式使用：

```bash
# 需要设置环境变量
export API_TOKEN="your_api_token"
export USER="your_username"

# 执行远程命令
pa exec "cd ~/project && git pull"

# 管理 webapp
pa webapp list
pa webapp create --domain yourusername.pythonanywhere.com --python 3.12
pa webapp reload yourusername.pythonanywhere.com

# 文件操作
pa path get /home/username/file.txt
pa path delete /home/username/old_file.txt
```

### Q: SocketIO 连接失败？

A: PythonAnywhere 免费账户不支持 WebSocket。在 `main.py` 中修改：

```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
```

### Q: 部署后看到 "Something went wrong"？

A: 检查错误日志：
1. PythonAnywhere Web 页面
2. 点击 "Log files"
3. 查看 Error log

### Q: 如何手动安装依赖？

A: 在 PythonAnywhere 控制台：

```bash
cd ~/py-simple-chat
pip install --user uv
uv sync
```

### Q: 如何手动触发部署？

A: GitHub → Actions → Deploy to PythonAnywhere → Run workflow

### Q: 文件写入失败？

A: 确保 JSON 文件有写入权限：

```bash
chmod 644 /home/yourusername/py-simple-chat/*.json
```

## 完整命令速查

```bash
# 在 PythonAnywhere 控制台

# 更新代码
cd ~/py-simple-chat && git pull

# 安装 uv（首次）
pip install --user uv

# 同步依赖
uv sync

# 重新加载应用（使用 pa 命令）
pa reload yourusername.pythonanywhere.com
```

## 需要帮助？

- PythonAnywhere 帮助：https://help.pythonanywhere.com/
- 查看完整文档：DEPLOYMENT.md
