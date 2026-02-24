# GitHub Secrets 和 Variables 配置指南

## 为什么区分 Secrets 和 Variables？

- **Secrets（加密变量）**: 敏感信息，如 API Token、密码等，在日志中会被隐藏
- **Variables（普通变量）**: 非敏感信息，如用户名、域名等，可以在日志中显示

## 配置步骤

### 1. 进入仓库设置

1. 打开你的 GitHub 仓库
2. 点击顶部的 **Settings** 标签
3. 在左侧菜单找到 **Secrets and variables**
4. 点击 **Actions**

### 2. 配置 Secrets（加密变量）

1. 点击 **Secrets** 标签
2. 点击 **New repository secret** 按钮
3. 添加以下 Secret：

| Name | Value | 说明 |
|------|-------|------|
| `PA_API_TOKEN` | 你的 API Token | 从 PythonAnywhere Account 页面获取 |

**获取 API Token：**
1. 登录 https://www.pythonanywhere.com/
2. 点击右上角 Account
3. 点击 API token 标签
4. 点击 "Create a new API token"
5. 复制生成的 token

### 3. 配置 Variables（普通变量）

1. 点击 **Variables** 标签
2. 点击 **New repository variable** 按钮
3. 依次添加以下 Variables：

| Name | Value | 示例 |
|------|-------|------|
| `PA_USERNAME` | 你的 PythonAnywhere 用户名 | `myusername` |
| `PA_DOMAIN` | Web 应用域名 | `myusername.pythonanywhere.com` |
| `PA_PROJECT_PATH` | 项目在 PA 上的路径 | `/home/myusername/py-simple-chat` |

**注意事项：**
- PA_USERNAME: 你的 PythonAnywhere 登录用户名
- PA_DOMAIN: 
  - 免费账户：`yourusername.pythonanywhere.com`
  - 付费账户：可以是自定义域名
- PA_PROJECT_PATH: 
  - 格式：`/home/你的用户名/项目名称`
  - 项目名称通常与 GitHub 仓库名相同

## 配置示例

假设你的 PythonAnywhere 用户名是 `john`，GitHub 仓库是 `py-simple-chat`：

### Secrets
```
PA_API_TOKEN = "1234567890abcdef1234567890abcdef12345678"
```

### Variables
```
PA_USERNAME = "john"
PA_DOMAIN = "john.pythonanywhere.com"
PA_PROJECT_PATH = "/home/john/py-simple-chat"
```

## 验证配置

配置完成后，可以通过以下方式验证：

1. **查看 Secrets**
   - 在 Secrets 标签下应该看到 `PA_API_TOKEN`
   - 值会显示为 `***`（已加密）

2. **查看 Variables**
   - 在 Variables 标签下应该看到 3 个变量
   - 值会完整显示

3. **测试部署**
   - 推送代码到 main 分支
   - 查看 Actions 标签
   - 检查工作流是否成功运行

## 常见问题

### Q: 如何更新 Secret 或 Variable？

A: 
1. 进入 Settings → Secrets and variables → Actions
2. 点击对应的 Secret 或 Variable
3. 点击 "Update secret" 或 "Update variable"
4. 输入新值并保存

### Q: Secret 和 Variable 有什么区别？

A:
- **Secret**: 
  - 值被加密存储
  - 在日志中显示为 `***`
  - 适合存储敏感信息
  - 无法查看原始值（只能更新）

- **Variable**:
  - 值明文存储
  - 在日志中完整显示
  - 适合存储非敏感配置
  - 可以查看和编辑

### Q: 为什么 API Token 要用 Secret？

A: API Token 是敏感信息，如果泄露：
- 他人可以访问你的 PythonAnywhere 账户
- 可以修改你的应用
- 可以查看你的文件

使用 Secret 可以：
- 加密存储
- 在日志中隐藏
- 防止意外泄露

### Q: 可以在本地查看这些值吗？

A: 
- 不能直接查看 Secrets 的值
- Variables 可以在仓库设置中查看
- 如果忘记了 Secret 的值，需要重新生成

### Q: 多个分支可以使用不同的配置吗？

A: 
- Secrets 和 Variables 是仓库级别的
- 所有分支共享相同的配置
- 如果需要不同环境，可以：
  - 使用不同的仓库
  - 或在代码中根据分支名称选择配置

## 安全建议

1. **定期轮换 API Token**
   - 每 3-6 个月更新一次
   - 如果怀疑泄露，立即更新

2. **最小权限原则**
   - 只授予必要的权限
   - 不要共享 API Token

3. **监控使用情况**
   - 定期检查 Actions 日志
   - 注意异常的部署活动

4. **备份配置**
   - 记录配置信息（除了 Secret 值）
   - 便于恢复或迁移

## 相关文档

- [GitHub Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Variables 文档](https://docs.github.com/en/actions/learn-github-actions/variables)
- [PythonAnywhere API 文档](https://help.pythonanywhere.com/pages/API/)
