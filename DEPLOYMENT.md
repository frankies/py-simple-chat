# PythonAnywhere 部署指南

本项目使用 GitHub Actions 自动部署到 PythonAnywhere。

## 前置准备

### 1. PythonAnywhere 账号设置

1. 注册 PythonAnywhere 账号：https://www.pythonanywhere.com/
2. 获取 API Token：
   - 登录后访问：https://www.pythonanywhere.com/user/{your_username}/account/#api_token
   - 点击 "Create a new API token"
   - 复制生成的 token

### 2. GitHub Secrets 配置

在 GitHub 仓库中设置以下 Secrets（Settings → Secrets and variables → Actions → New repository secret）：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `PA_API_TOKEN` | PythonAnywhere API Token | `abcd1234efgh5678...` |
| `PA_USERNAME` | PythonAnywhere 用户名 | `yourusername` |
| `PA_DOMAIN` | Web 应用域名 | `yourusername.pythonanywhere.com` |
| `PA_PROJECT_PATH` | 项目在 PA 上的路径 | `/home/yourusername/py-simple-chat` |

### 3. PythonAnywhere Web 应用配置

#### 方式一：通过 Web 界面配置

1. 登录 PythonAnywhere
2. 进入 "Web" 标签页
3. 点击 "Add a new web app"
4. 选择 Flask 框架和 Python 版本（3.12）
5. 设置项目路径：`/home/yourusername/py-simple-chat`
6. 配置 WSGI 文件（见下方）

#### 方式二：使用 pa 命令行工具

```bash
# 安装 pa 工具
pip install pythonanywhere

# 设置 API token
pa --set-token YOUR_API_TOKEN

# 创建 web 应用
pa create webapp --domain yourusername.pythonanywhere.com --python 3.12

# 设置项目路径
pa set webapp --domain yourusername.pythonanywhere.com --source-directory /home/yourusername/py-simple-chat
```

### 4. WSGI 配置文件

在 PythonAnywhere 的 Web 配置页面，编辑 WSGI 配置文件（通常在 `/var/www/yourusername_pythonanywhere_com_wsgi.py`）：

```python
import sys
import os

# 添加项目路径
project_home = '/home/yourusername/py-simple-chat'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 设置环境变量（可选）
os.environ['USE_MEMORY_STORAGE'] = '0'  # PythonAnywhere 支持文件存储

# 导入 Flask 应用
from main import app as application
```

### 5. 静态文件配置（可选）

在 PythonAnywhere Web 配置页面的 "Static files" 部分添加：

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/py-simple-chat/static/` |
| `/favicon.ico` | `/home/yourusername/py-simple-chat/public/favicon.ico` |

## 部署流程

### 自动部署

推送代码到 `main` 分支时自动触发部署：

```bash
git add .
git commit -m "Update application"
git push origin main
```

### 手动部署

在 GitHub Actions 页面手动触发 "Deploy to PythonAnywhere" workflow。

## 本地测试

部署前建议本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

访问 http://localhost:5000 测试功能。

## 常见问题

### 1. SocketIO 连接问题

PythonAnywhere 免费账户不支持 WebSocket。需要配置 Flask-SocketIO 使用长轮询：

在 `main.py` 中修改：

```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
```

前端连接时指定传输方式：

```javascript
const socket = io({
    transports: ['polling', 'websocket']
});
```

### 2. 文件权限问题

确保应用有权限写入 JSON 文件：

```bash
chmod 644 /home/yourusername/py-simple-chat/*.json
```

### 3. 依赖安装失败

在 PythonAnywhere 控制台手动安装：

```bash
cd /home/yourusername/py-simple-chat
pip install --user uv
uv sync
```

### 4. 查看日志

- 错误日志：PythonAnywhere Web 页面 → "Log files" → Error log
- 服务器日志：PythonAnywhere Web 页面 → "Log files" → Server log

## 进阶配置

### 使用 Git 部署（推荐）

1. 在 PythonAnywhere 控制台克隆仓库：

```bash
cd ~
git clone https://github.com/yourusername/py-simple-chat.git
```

2. 修改 GitHub Actions 脚本使用 git pull：

```yaml
- name: Deploy via Git
  run: |
    pa exec "cd $PA_PROJECT_PATH && git pull origin main"
```

### 环境变量配置

在 WSGI 文件中添加环境变量：

```python
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['ADMIN_USERNAME'] = 'admin'
```

## 监控和维护

- 定期检查应用状态：https://www.pythonanywhere.com/user/{username}/webapps/
- 查看 CPU 和流量使用情况
- 免费账户有每日 CPU 限制，注意优化性能

## 参考资源

- [PythonAnywhere 官方文档](https://help.pythonanywhere.com/)
- [Flask-SocketIO 文档](https://flask-socketio.readthedocs.io/)
- [pa CLI 工具文档](https://github.com/pythonanywhere/helper_scripts)
