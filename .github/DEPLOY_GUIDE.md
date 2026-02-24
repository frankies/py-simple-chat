# GitHub Actions 部署到 PythonAnywhere - 快速指南

## 重要说明

### pa 命令的限制

`pa` 命令行工具有以下限制：

1. **webapp create 命令只能在 PythonAnywhere 上运行**
   - 需要 `WORKON_HOME` 环境变量
   - 该变量只在 PythonAnywhere 服务器上存在
   - 在本地或 CI/CD 中无法使用

2. **可以在本地/CI/CD 中使用的命令**
   - `pa webapp list` - 列出应用
   - `pa webapp reload` - 重新加载应用
   - `pa path` - 文件操作
   - `pa schedule` - 定时任务

3. **需要使用 API 的操作**
   - 创建 Web 应用
   - 执行远程命令
   - 更新 WSGI 配置

## 一、准备工作（3分钟）

### 1. 获取 PythonAnywhere API Token

1. 登录 https://www.pythonanywhere.com/
2. 访问 Account → API Token
3. 点击 "Create a new API token"
4. 复制 token（只显示一次）

### 2. 配置 GitHub Secrets 和 Variables

在 GitHub 仓库中配置以下内容：

**Secrets（加密变量）** - Settings → Secrets and variables → Actions → Secrets

| 名称 | 值 | 示例 |
|------|-----|------|
| PA_API_TOKEN | PythonAnywhere API Token | `abc123...` |

**Variables（普通变量）** - Settings → Secrets and variables → Actions → Variables

| 名称 | 值 | 示例 |
|------|-----|------|
| PA_USERNAME | PythonAnywhere 用户名 | `myusername` |
| PA_DOMAIN | Web 应用域名 | `myusername.pythonanywhere.com` |
| PA_PROJECT_PATH | 项目路径 | `/home/myusername/py-simple-chat` |

**详细配置步骤：** 查看 [GitHub 配置指南](GITHUB_CONFIG.md)

**配置步骤：**

1. 进入 GitHub 仓库
2. 点击 Settings → Secrets and variables → Actions
3. 点击 **Secrets** 标签
   - 点击 "New repository secret"
   - 添加 `PA_API_TOKEN`
4. 点击 **Variables** 标签
   - 点击 "New repository variable"
   - 依次添加 `PA_USERNAME`、`PA_DOMAIN`、`PA_PROJECT_PATH`

注意：PA_PROJECT_PATH 使用你的用户名，项目名称保持 `py-simple-chat`

## 二、首次部署

### 选项 A: 自动部署（推荐尝试）

推送代码触发自动部署：

```bash
git add .
git commit -m "Setup CI/CD"
git push origin main
```

GitHub Actions 会尝试自动完成所有操作。

查看部署状态：GitHub → Actions 标签

### 选项 B: 手动设置（如果自动失败）

如果自动部署失败（常见于免费账户），请按照 [手动设置指南](.github/MANUAL_SETUP.md) 操作。

**为什么可能失败？**
- 免费账户只能创建 1 个 Web 应用
- API 创建应用可能需要付费账户
- 首次部署建议手动创建

**手动设置后的好处：**
- 后续推送代码会自动更新
- 自动同步依赖
- 自动重新加载应用

## 三、验证部署

访问你的应用：https://yourusername.pythonanywhere.com

## 常见问题

### Q: 自动部署失败，显示 "Web 应用创建失败"？

A: 这是正常的，特别是免费账户。解决方案：

1. **手动创建应用**（推荐）
   - 按照 [手动设置指南](.github/MANUAL_SETUP.md) 操作
   - 只需设置一次
   - 后续推送会自动更新

2. **检查账户限制**
   - 免费账户只能创建 1 个 Web 应用
   - 如果已有应用，需要先删除

3. **验证 API Token**
   - 确保 Token 有效
   - 重新生成 Token 并更新 GitHub Secrets

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
