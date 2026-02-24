# PythonAnywhere CLI (pa) 命令使用指南

## 简介

`pa` 是 PythonAnywhere 官方提供的命令行工具，用于管理 PythonAnywhere 服务。它基于 `pythonanywhere` Python 包。

## 安装

### 在 PythonAnywhere 上

```bash
pip3.10 install --user pythonanywhere
```

### 在本地机器上

```bash
pip install pythonanywhere
# 或使用 pipx
pipx install pythonanywhere
```

## 环境变量配置

在本地机器上使用 `pa` 命令时，需要设置以下环境变量：

```bash
# API Token（必需）
export API_TOKEN="your_api_token_here"

# 用户名（如果本地用户名与 PythonAnywhere 用户名不同）
export USER="your_pythonanywhere_username"

# PythonAnywhere 站点（默认为 www.pythonanywhere.com）
export PYTHONANYWHERE_SITE="www.pythonanywhere.com"
# 或欧洲站点
# export PYTHONANYWHERE_SITE="eu.pythonanywhere.com"
```

### 获取 API Token

1. 登录 PythonAnywhere
2. 访问 Account 页面
3. 点击 "API token" 标签
4. 点击 "Create a new API token"
5. 复制生成的 token

## 主要命令

### 1. webapp - Web 应用管理

```bash
# 列出所有 web 应用
pa webapp list

# 创建新的 web 应用
pa webapp create --domain yourusername.pythonanywhere.com --python-version 3.12

# 重新加载 web 应用
pa webapp reload yourusername.pythonanywhere.com

# 删除 web 应用
pa webapp delete yourusername.pythonanywhere.com

# 获取 web 应用信息
pa webapp get yourusername.pythonanywhere.com
```

### 2. path - 文件操作

```bash
# 获取文件内容
pa path get /home/yourusername/file.txt

# 列出目录内容
pa path get /home/yourusername/myproject

# 删除文件
pa path delete /home/yourusername/old_file.txt

# 删除目录
pa path delete /home/yourusername/old_directory

# 上传文件内容
pa path upload /home/yourusername/file.txt --contents local_file.txt

# 创建共享链接
pa path share /home/yourusername/file.txt

# 检查共享链接状态
pa path share /home/yourusername/file.txt --check

# 取消共享
pa path unshare /home/yourusername/file.txt

# 显示目录树
pa path tree /home/yourusername/myproject
```

### 3. schedule - 定时任务管理

```bash
# 列出所有定时任务
pa schedule list

# 创建新的定时任务
pa schedule create --command "python /home/yourusername/script.py" \
  --hour 14 --minute 30

# 删除定时任务
pa schedule delete TASK_ID

# 获取定时任务详情
pa schedule get TASK_ID
```

### 4. django - Django 项目部署

```bash
# 自动配置 Django 项目
pa django autoconfigure https://github.com/username/repo.git

# 指定 Python 版本
pa django autoconfigure --python 3.12 https://github.com/username/repo.git

# 指定域名
pa django autoconfigure --domain yourusername.pythonanywhere.com \
  https://github.com/username/repo.git
```

## 在 GitHub Actions 中使用

### 设置环境变量

```yaml
- name: Deploy to PythonAnywhere
  env:
    API_TOKEN: ${{ secrets.PA_API_TOKEN }}
    USER: ${{ secrets.PA_USERNAME }}
  run: |
    pa webapp reload ${{ secrets.PA_DOMAIN }}
```

### 使用 PythonAnywhere API

由于 `pa` 命令不支持执行远程 bash 命令，在 CI/CD 中需要使用 PythonAnywhere API：

```python
import requests

# 创建控制台
response = requests.post(
    f'https://www.pythonanywhere.com/api/v0/user/{username}/consoles/',
    headers={'Authorization': f'Token {api_token}'}
)
console_id = response.json()['id']

# 发送命令
requests.post(
    f'https://www.pythonanywhere.com/api/v0/user/{username}/consoles/{console_id}/send_input/',
    headers={'Authorization': f'Token {api_token}'},
    json={'input': 'cd ~/project && git pull\n'}
)
```

## 常见使用场景

### 场景 1: 首次部署（使用 API）

由于 `pa` 命令不支持远程命令执行，需要使用 PythonAnywhere API：

```python
import requests

api_token = "your_token"
username = "your_username"
base_url = f"https://www.pythonanywhere.com/api/v0/user/{username}"
headers = {"Authorization": f"Token {api_token}"}

# 1. 创建控制台
console_response = requests.post(f"{base_url}/consoles/", headers=headers)
console_id = console_response.json()['id']

# 2. 执行命令
commands = [
    "cd ~ && git clone https://github.com/user/repo.git myproject",
    "cd ~/myproject && pip install --user -r requirements.txt"
]

for cmd in commands:
    requests.post(
        f"{base_url}/consoles/{console_id}/send_input/",
        headers=headers,
        json={"input": cmd + "\n"}
    )
    time.sleep(2)

# 3. 删除控制台
requests.delete(f"{base_url}/consoles/{console_id}/", headers=headers)
```

### 场景 2: 使用 pa 命令管理 webapp

```bash
# 创建 web 应用
pa webapp create --domain yourusername.pythonanywhere.com --python-version 3.12

# 重新加载应用
pa webapp reload yourusername.pythonanywhere.com
```

### 场景 3: 文件操作

```bash
# 上传配置文件
pa path upload /home/yourusername/myproject/config.py --contents local_config.py

# 查看日志
pa path get /var/log/yourusername.pythonanywhere.com.error.log

# 删除旧文件
pa path delete /home/yourusername/old_backup
```

## 错误处理

### 常见错误

1. **No such command 'exec'**
   - 原因：`pa` 命令不支持 `exec` 子命令
   - 解决：使用 PythonAnywhere API 的 consoles 端点执行远程命令

2. **Authentication failed**
   - 原因：API Token 无效或未设置
   - 解决：检查 `API_TOKEN` 环境变量

3. **Command timeout**
   - 原因：命令执行时间过长
   - 解决：将长时间命令拆分为多个短命令

4. **Permission denied**
   - 原因：文件权限问题
   - 解决：使用 `pa exec "chmod +x file"` 修改权限

## 最佳实践

1. **使用环境变量**
   - 不要在脚本中硬编码 API Token
   - 使用 GitHub Secrets 存储敏感信息

2. **命令幂等性**
   - 确保命令可以重复执行
   - 使用条件判断避免重复操作

3. **错误处理**
   - 检查命令返回值
   - 提供清晰的错误信息

4. **日志记录**
   - 记录关键操作
   - 便于调试和追踪

5. **测试**
   - 在本地测试 pa 命令
   - 使用 `--help` 查看命令选项

## 参考资源

- [pythonanywhere PyPI](https://pypi.org/project/pythonanywhere/)
- [PythonAnywhere API 文档](https://help.pythonanywhere.com/pages/API/)
- [PythonAnywhere 帮助中心](https://help.pythonanywhere.com/)
- [helper_scripts GitHub](https://github.com/pythonanywhere/helper_scripts)

## 命令速查表

| 操作 | 命令 |
|------|------|
| 列出 webapps | `pa webapp list` |
| 创建 webapp | `pa webapp create --domain DOMAIN --python VERSION` |
| 重新加载 webapp | `pa webapp reload DOMAIN` |
| 执行远程命令 | `pa exec "COMMAND"` |
| 获取文件 | `pa path get PATH` |
| 删除文件 | `pa path delete PATH` |
| 列出定时任务 | `pa schedule list` |
| 创建定时任务 | `pa schedule create --command CMD --hour H --minute M` |
| Django 自动配置 | `pa django autoconfigure REPO_URL` |
