# PythonAnywhere API 权限说明

## API 权限限制

PythonAnywhere 的 API 在免费账户和付费账户之间有不同的权限限制。

### 免费账户限制

免费账户的 API 可能无法执行以下操作：

1. **创建 Web 应用**
   - 状态码：400 或 403
   - 错误：权限不足或参数错误
   - 解决：手动在 Web 界面创建

2. **重新加载 Web 应用**
   - 状态码：403
   - 错误：`You do not have permission to perform this action`
   - 解决：手动点击 Reload 按钮

3. **修改某些配置**
   - 某些高级配置可能受限
   - 需要通过 Web 界面操作

### 可用的 API 操作

即使是免费账户，以下操作通常也可用：

✅ **Consoles API**
- 创建控制台
- 发送命令
- 获取输出
- 删除控制台

✅ **Files API**
- 上传文件
- 下载文件
- 删除文件
- 列出目录

✅ **Webapps API（部分）**
- 列出应用
- 获取应用信息
- 更新配置（PATCH）

## 实际影响

### 对 CI/CD 的影响

**完全自动化的部分：**
- ✅ 代码更新（git pull）
- ✅ 依赖安装（uv sync）
- ✅ 文件操作
- ✅ 配置更新

**需要手动的部分：**
- ⚠️ 首次创建 Web 应用
- ⚠️ 重新加载应用（某些账户）

### 工作流程

**首次部署：**
1. 手动创建 Web 应用（5分钟）
2. 配置 GitHub Secrets/Variables
3. 推送代码触发自动部署
4. 代码和依赖自动更新
5. 手动点击 Reload（如果需要）

**后续更新：**
1. 推送代码到 GitHub
2. 自动更新代码和依赖
3. 手动点击 Reload（如果需要）

## 解决方案

### 方案 1: 手动 Reload（推荐）

**优点：**
- 简单可靠
- 不需要额外配置
- 适合所有账户类型

**步骤：**
1. 推送代码
2. 等待 GitHub Actions 完成
3. 登录 PythonAnywhere
4. 点击 Reload 按钮

### 方案 2: 升级到付费账户

**优点：**
- 完全自动化
- 更多 API 权限
- 更好的性能

**费用：**
- 查看 [PythonAnywhere 定价](https://www.pythonanywhere.com/pricing/)

### 方案 3: 使用 Webhook

某些情况下可以配置 webhook 来触发重新加载，但这需要额外的设置。

## API 权限对照表

| 操作 | 免费账户 | 付费账户 | 替代方案 |
|------|----------|----------|----------|
| 列出 webapps | ✅ | ✅ | - |
| 获取 webapp 信息 | ✅ | ✅ | - |
| 创建 webapp | ❌ | ✅ | 手动创建 |
| 重新加载 webapp | ❌ | ✅ | 手动 Reload |
| 更新 webapp 配置 | ✅ | ✅ | - |
| 创建控制台 | ✅ | ✅ | - |
| 执行命令 | ✅ | ✅ | - |
| 上传文件 | ✅ | ✅ | - |

## 错误代码说明

### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**原因：**
- API Token 权限不足
- 免费账户限制
- 操作不允许

**解决：**
- 检查账户类型
- 手动执行操作
- 考虑升级账户

### 400 Bad Request

```json
{
  "status": "ERROR",
  "error_type": "missing_domain_name_error",
  "error_message": "Please specify a domain in the domain_name parameter"
}
```

**原因：**
- 参数格式错误
- 缺少必需参数
- 数据格式不正确

**解决：**
- 检查 API 调用参数
- 使用正确的数据格式（form data vs JSON）
- 查看 API 文档

### 404 Not Found

**原因：**
- Web 应用不存在
- 路径错误
- 资源已删除

**解决：**
- 确认 Web 应用已创建
- 检查域名是否正确
- 验证资源路径

## 最佳实践

### 1. 接受限制

免费账户的限制是正常的，不要试图绕过。

### 2. 混合方式

- 自动化能自动化的部分
- 手动处理受限的操作
- 这是最实用的方案

### 3. 清晰的文档

- 告诉用户哪些需要手动
- 提供清晰的步骤
- 设置合理的期望

### 4. 监控和日志

- 记录 API 响应
- 提供友好的错误信息
- 帮助用户理解问题

## 常见问题

### Q: 为什么不能自动 reload？

A: 免费账户的 API Token 可能没有 reload 权限。这是 PythonAnywhere 的限制。

### Q: 手动 reload 麻烦吗？

A: 不麻烦，只需：
1. 登录 PythonAnywhere
2. 点击 Web 标签
3. 点击 Reload 按钮（1秒）

### Q: 有办法完全自动化吗？

A: 
- 升级到付费账户
- 或接受手动 reload
- 这是 PythonAnywhere 的设计

### Q: 其他部署平台呢？

A: 如果需要完全自动化，可以考虑：
- Heroku
- Railway
- Render
- Vercel（需要适配）
- 自己的 VPS

但 PythonAnywhere 的优势是：
- 简单易用
- 免费额度足够
- 专为 Python 优化

## 总结

PythonAnywhere 免费账户的 API 限制是合理的：
- ✅ 核心功能可用（代码更新、依赖安装）
- ⚠️ 某些操作需要手动（创建应用、重新加载）
- 💡 这是一个实用的折衷方案

对于个人项目和学习用途，这个限制是可以接受的。如果需要完全自动化，可以考虑升级账户或使用其他平台。

## 相关资源

- [PythonAnywhere API 文档](https://help.pythonanywhere.com/pages/API/)
- [PythonAnywhere 定价](https://www.pythonanywhere.com/pricing/)
- [手动设置指南](MANUAL_SETUP.md)
- [部署状态说明](DEPLOYMENT_STATUS.md)
