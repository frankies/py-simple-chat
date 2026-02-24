# PythonAnywhere 手动设置指南

如果自动部署失败，请按照以下步骤手动设置 Web 应用。

## 为什么需要手动设置？

可能的原因：
1. **免费账户限制** - 免费账户只能创建 1 个 Web 应用
2. **API 限制** - 某些操作需要付费账户
3. **首次部署** - 首次部署时建议手动创建应用

## 手动设置步骤

### 1. 登录 PythonAnywhere

访问 https://www.pythonanywhere.com/ 并登录

### 2. 创建 Web 应用

1. 点击顶部的 **Web** 标签
2. 点击 **Add a new web app** 按钮
3. 选择域名（免费账户：`yourusername.pythonanywhere.com`）
4. 选择 **Manual configuration**（不要选择 Flask 等框架）
5. 选择 Python 版本：**Python 3.12**
6. 点击 **Next** 完成创建

### 3. 配置 WSGI 文件

在 Web 应用配置页面：

1. 找到 **Code** 部分
2. 点击 **WSGI configuration file** 链接（通常是 `/var/www/yourusername_pythonanywhere_com_wsgi.py`）
3. 删除所有内容，替换为：

```python
import sys
import os

# 替换为你的项目路径
project_home = '/home/yourusername/py-simple-chat'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
```

4. 点击 **Save** 保存

### 4. 设置源代码目录

在 Web 应用配置页面：

1. 找到 **Code** 部分
2. 在 **Source code** 输入框中输入：`/home/yourusername/py-simple-chat`
3. 在 **Working directory** 输入框中输入：`/home/yourusername/py-simple-chat`
4. 点击右侧的绿色勾号保存

### 5. 在控制台设置项目

1. 点击顶部的 **Consoles** 标签
2. 点击 **Bash** 创建新的 Bash 控制台
3. 执行以下命令：

```bash
# 克隆项目
cd ~
git clone https://github.com/你的用户名/py-simple-chat.git

# 进入项目目录
cd py-simple-chat

# 安装 uv
pip install --user uv

# 同步依赖
uv sync

# 初始化数据文件
touch users.json friends.json ip_limit.json banned.json
echo '{}' > users.json
echo '{}' > friends.json
echo '{}' > ip_limit.json
echo '{}' > banned.json
chmod 644 *.json
```

### 6. 重新加载应用

返回 **Web** 标签，点击页面顶部的绿色 **Reload** 按钮。

### 7. 测试应用

访问你的域名：`https://yourusername.pythonanywhere.com`

## 后续更新

手动设置完成后，GitHub Actions 可以自动更新代码和重新加载应用。

每次推送代码到 GitHub 时，CI/CD 会自动：
1. 更新代码（git pull）
2. 同步依赖（uv sync）
3. 重新加载应用

## 常见问题

### Q: 看到 "Something went wrong" 错误？

A: 检查以下内容：
1. WSGI 文件路径是否正确
2. 项目路径是否正确
3. main.py 文件是否存在
4. 依赖是否正确安装

查看错误日志：
- 在 Web 页面点击 **Log files**
- 查看 **Error log** 了解详细错误

### Q: 如何查看日志？

A: 在 Web 应用配置页面：
1. 点击 **Log files** 部分
2. 查看以下日志：
   - **Error log** - 应用错误
   - **Server log** - HTTP 请求
   - **Access log** - 访问记录

### Q: 如何更新代码？

A: 两种方式：

**方式 1: 自动更新（推荐）**
- 推送代码到 GitHub
- GitHub Actions 自动部署

**方式 2: 手动更新**
```bash
# 在 PythonAnywhere Bash 控制台
cd ~/py-simple-chat
git pull origin main
uv sync
```
然后在 Web 页面点击 **Reload** 按钮

### Q: SocketIO 不工作？

A: PythonAnywhere 免费账户不支持 WebSocket。

解决方案：
1. 在 `main.py` 中修改：
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
```

2. 前端使用长轮询：
```javascript
const socket = io({
    transports: ['polling']
});
```

### Q: 如何设置环境变量？

A: 在 WSGI 文件中添加：
```python
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['ADMIN_USERNAME'] = 'admin'
```

### Q: 如何使用自定义域名？

A: 
1. 升级到付费账户
2. 在 Web 页面添加自定义域名
3. 配置 DNS CNAME 记录

## 故障排除

### 应用无法启动

1. 检查 Error log
2. 验证 Python 版本
3. 确认所有依赖已安装
4. 检查文件权限

### 依赖安装失败

```bash
# 清除缓存重试
cd ~/py-simple-chat
rm -rf .venv
uv sync
```

### Git 拉取失败

```bash
# 重置本地更改
cd ~/py-simple-chat
git reset --hard origin/main
git pull
```

## 获取帮助

- [PythonAnywhere 帮助中心](https://help.pythonanywhere.com/)
- [PythonAnywhere 论坛](https://www.pythonanywhere.com/forums/)
- [Flask-SocketIO 文档](https://flask-socketio.readthedocs.io/)

## 下一步

设置完成后，查看 [DEPLOYMENT.md](../DEPLOYMENT.md) 了解更多配置选项。
