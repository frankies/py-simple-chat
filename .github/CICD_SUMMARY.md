# CI/CD 部署方案总结

## 技术栈

- **包管理器**: uv（替代 pip + requirements.txt）
- **依赖定义**: pyproject.toml + uv.lock
- **部署平台**: PythonAnywhere
- **CI/CD**: GitHub Actions
- **部署工具**: pythonanywhere CLI (`pa` 命令)

## 架构设计

### 1. 依赖管理

使用 `uv` 而非传统的 `pip + requirements.txt`：

```
pyproject.toml  ← 依赖声明
uv.lock         ← 锁定版本（自动生成）
uv              ← 包管理工具
```

优势：
- 更快的安装速度（10-100x）
- 自动版本锁定，确保环境一致
- 更好的依赖解析

### 2. 部署流程

```
GitHub Push → GitHub Actions → PythonAnywhere
     ↓              ↓                ↓
   代码更新      自动化脚本      Web 应用更新
```

### 3. 自动化步骤

#### 首次部署（自动检测并执行）
1. ✅ 克隆 Git 仓库到 PythonAnywhere
2. ✅ 创建 Web 应用
3. ✅ 配置 WSGI 文件
4. ✅ 初始化数据文件（JSON）
5. ✅ 安装 uv
6. ✅ 同步依赖（uv sync）
7. ✅ 重新加载应用

#### 后续部署（增量更新）
1. ✅ Git pull 更新代码
2. ✅ uv sync 更新依赖
3. ✅ 重新加载应用

## 文件结构

```
.github/
├── workflows/
│   └── deploy.yml              # GitHub Actions 主配置
├── scripts/
│   └── deploy_to_pa.py         # Python 部署脚本
├── DEPLOY_GUIDE.md             # 快速部署指南
└── CICD_SUMMARY.md             # 本文档

pyproject.toml                  # 项目配置和依赖
uv.lock                         # 依赖版本锁定
uv.toml.example                 # uv 配置示例
UV_GUIDE.md                     # uv 使用指南

setup_pythonanywhere.sh         # 手动设置脚本
wsgi.py                         # WSGI 配置模板
DEPLOYMENT.md                   # 完整部署文档
```

## 核心文件说明

### 1. `.github/workflows/deploy.yml`

GitHub Actions 工作流配置：

```yaml
触发条件:
  - push to main 分支
  - 手动触发 (workflow_dispatch)

步骤:
  1. Checkout 代码
  2. 设置 Python 3.12
  3. 安装 uv
  4. 安装 pythonanywhere CLI
  5. 配置 PA API Token
  6. 执行部署脚本
  7. 显示部署状态
```

### 2. `.github/scripts/deploy_to_pa.py`

智能部署脚本，处理：

- 检测项目是否存在
- 检测 Web 应用是否存在
- 首次部署：完整初始化
- 后续部署：增量更新
- 使用 uv 管理依赖

关键函数：
- `check_project_exists()` - 检查项目目录
- `check_webapp_exists()` - 检查 Web 应用
- `clone_repository()` - 克隆仓库
- `create_webapp()` - 创建 Web 应用
- `install_dependencies()` - 使用 uv sync 安装依赖

### 3. `pyproject.toml`

项目配置文件：

```toml
[project]
name = "py-simple-chat"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "flask>=3.1.3",
    "gunicorn~=23.0.0",
    "flask-socketio>=5.6.1",
    "uv>=0.10.4",
]
```

## 环境变量（GitHub Secrets）

| 变量名 | 说明 | 示例 |
|--------|------|------|
| PA_API_TOKEN | PythonAnywhere API Token | `abc123...` |
| PA_USERNAME | PythonAnywhere 用户名 | `myusername` |
| PA_DOMAIN | Web 应用域名 | `myusername.pythonanywhere.com` |
| PA_PROJECT_PATH | 项目路径 | `/home/myusername/py-simple-chat` |

## 使用流程

### 开发者视角

1. **本地开发**
   ```bash
   uv sync              # 安装依赖
   uv run python main.py  # 运行应用
   ```

2. **提交代码**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

3. **自动部署**
   - GitHub Actions 自动触发
   - 查看部署状态：GitHub → Actions
   - 访问应用：https://yourusername.pythonanywhere.com

### 首次配置（一次性）

1. 获取 PythonAnywhere API Token
2. 在 GitHub 配置 4 个 Secrets
3. 推送代码，自动完成所有设置

## 优势

### 1. 零手动配置
- 不需要在 PythonAnywhere 上手动创建项目
- 不需要手动配置 WSGI
- 不需要手动安装依赖

### 2. 智能检测
- 自动识别首次部署 vs 更新部署
- 只执行必要的步骤
- 避免重复创建资源

### 3. 可靠性
- 使用 uv.lock 确保依赖版本一致
- 完整的错误处理
- 清晰的日志输出

### 4. 速度
- uv 比 pip 快 10-100 倍
- 增量更新只同步变更
- 并行处理多个步骤

## 故障排除

### 部署失败

1. 查看 GitHub Actions 日志
2. 检查 Secrets 配置是否正确
3. 验证 PythonAnywhere API Token 有效性

### 应用错误

1. 查看 PythonAnywhere Error Log
2. 检查 WSGI 配置
3. 验证依赖是否正确安装

### 手动干预

如需手动操作：

```bash
# SSH 到 PythonAnywhere（通过 Web 控制台）
cd ~/py-simple-chat

# 更新代码
git pull

# 重新安装依赖
uv sync

# 重新加载应用
pa reload yourusername.pythonanywhere.com
```

## 扩展性

### 添加测试

在 `.github/workflows/deploy.yml` 中添加：

```yaml
- name: Run Tests
  run: |
    uv run pytest
```

### 添加代码检查

```yaml
- name: Lint Code
  run: |
    uv run ruff check .
```

### 多环境部署

创建不同的 workflow 文件：
- `deploy-staging.yml` - 测试环境
- `deploy-production.yml` - 生产环境

### 通知集成

添加部署通知（Slack、Discord 等）：

```yaml
- name: Notify Deployment
  if: success()
  run: |
    curl -X POST ${{ secrets.WEBHOOK_URL }} \
      -d '{"text":"Deployment successful!"}'
```

## 安全考虑

1. **API Token 保护**
   - 使用 GitHub Secrets 存储
   - 不在代码中硬编码
   - 定期轮换 Token

2. **依赖安全**
   - uv.lock 锁定版本
   - 定期更新依赖
   - 使用 `uv lock --upgrade` 更新

3. **代码审查**
   - 保护 main 分支
   - 要求 PR 审查
   - 自动化测试

## 性能优化

1. **缓存依赖**
   GitHub Actions 可以缓存 uv 缓存：
   ```yaml
   - uses: actions/cache@v3
     with:
       path: ~/.cache/uv
       key: uv-${{ hashFiles('uv.lock') }}
   ```

2. **并行部署**
   如有多个应用，可以并行部署

3. **增量更新**
   只更新变更的文件和依赖

## 监控和日志

- GitHub Actions 日志：完整的部署过程
- PythonAnywhere Error Log：应用运行错误
- PythonAnywhere Server Log：HTTP 请求日志
- PythonAnywhere Access Log：访问统计

## 成本

- GitHub Actions：免费（公共仓库）
- PythonAnywhere：免费套餐可用
- uv：开源免费

## 总结

这套 CI/CD 方案提供了：

✅ 完全自动化的部署流程  
✅ 智能的首次部署和增量更新  
✅ 使用现代化的 uv 包管理器  
✅ 零手动配置  
✅ 清晰的文档和故障排除指南  
✅ 可扩展的架构设计  

开发者只需关注代码，推送后自动部署到生产环境。
