# 快速参考

## GitHub 配置速查

### Secrets（加密）
```
PA_API_TOKEN = "你的API Token"
```

### Variables（明文）
```
PA_USERNAME = "你的用户名"
PA_DOMAIN = "你的用户名.pythonanywhere.com"
PA_PROJECT_PATH = "/home/你的用户名/py-simple-chat"
```

## 配置位置

```
GitHub 仓库
  └─ Settings
      └─ Secrets and variables
          └─ Actions
              ├─ Secrets 标签 → 添加 PA_API_TOKEN
              └─ Variables 标签 → 添加其他 3 个
```

## 部署流程

### 首次部署
1. ✅ 获取 API Token
2. ✅ 配置 GitHub Secrets + Variables
3. ✅ 手动创建 PythonAnywhere Web 应用
4. ✅ 推送代码

### 后续更新
```bash
git push origin main
```
自动完成！

## 常用命令

### 本地开发
```bash
uv sync              # 安装依赖
uv run python main.py  # 运行应用
```

### PythonAnywhere 控制台
```bash
cd ~/py-simple-chat
git pull             # 更新代码
uv sync              # 同步依赖
```

### 手动重新加载
在 PythonAnywhere Web 页面点击 **Reload** 按钮

## 文档导航

| 文档 | 用途 |
|------|------|
| [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) | 快速部署指南 |
| [MANUAL_SETUP.md](MANUAL_SETUP.md) | 手动设置步骤 |
| [GITHUB_CONFIG.md](GITHUB_CONFIG.md) | GitHub 配置详解 |
| [PA_COMMAND_GUIDE.md](PA_COMMAND_GUIDE.md) | PA 命令使用 |
| [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) | 部署状态说明 |
| [CHANGELOG.md](CHANGELOG.md) | 配置更新日志 |

## 故障排除

### 问题：部署失败
1. 检查 Actions 日志
2. 验证配置是否正确
3. 查看 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

### 问题：应用无法访问
1. 检查 Web 应用是否创建
2. 查看 Error log
3. 查看 [MANUAL_SETUP.md](MANUAL_SETUP.md)

### 问题：依赖安装失败
```bash
cd ~/py-simple-chat
rm -rf .venv
uv sync
```

## 获取帮助

- [PythonAnywhere 帮助](https://help.pythonanywhere.com/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [uv 文档](https://docs.astral.sh/uv/)
