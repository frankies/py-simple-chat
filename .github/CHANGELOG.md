# 部署配置更新日志

## 2024 - 配置优化

### 变更内容

将 GitHub Actions 配置从全部使用 Secrets 改为 Secrets + Variables 混合模式。

### 变更原因

1. **安全性优化**
   - 只有敏感信息（API Token）需要加密
   - 非敏感信息使用普通变量更方便管理

2. **可维护性提升**
   - Variables 可以直接查看和编辑
   - 便于调试和验证配置

3. **最佳实践**
   - 遵循 GitHub Actions 推荐做法
   - 区分敏感和非敏感信息

### 配置对比

#### 之前（全部使用 Secrets）

```yaml
env:
  PA_API_TOKEN: ${{ secrets.PA_API_TOKEN }}
  PA_USERNAME: ${{ secrets.PA_USERNAME }}
  PA_DOMAIN: ${{ secrets.PA_DOMAIN }}
  PA_PROJECT_PATH: ${{ secrets.PA_PROJECT_PATH }}
```

**问题：**
- ❌ 所有值都被加密，无法查看
- ❌ 用户名、域名等非敏感信息也被隐藏
- ❌ 调试困难，日志中全是 `***`

#### 之后（Secrets + Variables）

```yaml
env:
  PA_API_TOKEN: ${{ secrets.PA_API_TOKEN }}      # Secret（加密）
  PA_USERNAME: ${{ vars.PA_USERNAME }}           # Variable（明文）
  PA_DOMAIN: ${{ vars.PA_DOMAIN }}               # Variable（明文）
  PA_PROJECT_PATH: ${{ vars.PA_PROJECT_PATH }}   # Variable（明文）
```

**优势：**
- ✅ API Token 加密保护
- ✅ 用户名、域名可见，便于验证
- ✅ 日志中可以看到配置信息
- ✅ 更容易调试和排查问题

### 迁移指南

如果你已经配置了 Secrets，需要迁移到新的配置方式：

#### 步骤 1: 记录现有配置

在 Settings → Secrets and variables → Actions → Secrets 中：
- 记录 `PA_USERNAME` 的值
- 记录 `PA_DOMAIN` 的值
- 记录 `PA_PROJECT_PATH` 的值
- 保留 `PA_API_TOKEN`（不需要记录）

#### 步骤 2: 删除旧的 Secrets

删除以下 Secrets（保留 PA_API_TOKEN）：
- PA_USERNAME
- PA_DOMAIN
- PA_PROJECT_PATH

#### 步骤 3: 创建 Variables

在 Settings → Secrets and variables → Actions → Variables 中：
- 创建 `PA_USERNAME`
- 创建 `PA_DOMAIN`
- 创建 `PA_PROJECT_PATH`

#### 步骤 4: 验证配置

推送代码触发部署，检查是否正常工作。

### 配置清单

完成迁移后，你应该有：

**Secrets（1个）**
- ✅ PA_API_TOKEN

**Variables（3个）**
- ✅ PA_USERNAME
- ✅ PA_DOMAIN
- ✅ PA_PROJECT_PATH

### 相关文档

- [GitHub 配置指南](GITHUB_CONFIG.md) - 详细配置步骤
- [快速部署指南](DEPLOY_GUIDE.md) - 完整部署流程
- [部署状态说明](DEPLOYMENT_STATUS.md) - 技术实现细节

### 常见问题

#### Q: 为什么要区分 Secrets 和 Variables？

A: 
- Secrets 用于敏感信息（如密码、Token），会被加密
- Variables 用于非敏感配置（如用户名、域名），便于管理
- 这是 GitHub Actions 的最佳实践

#### Q: 旧的配置还能用吗？

A: 
- 可以，但不推荐
- 全部使用 Secrets 会导致调试困难
- 建议迁移到新的配置方式

#### Q: 如何验证配置是否正确？

A: 
1. 查看 Actions 日志
2. 日志中应该能看到用户名和域名
3. API Token 仍然显示为 `***`

#### Q: Variables 安全吗？

A: 
- Variables 不加密，但存储在 GitHub 服务器上
- 只有仓库协作者可以查看
- 不要在 Variables 中存储密码或 Token

### 安全提示

1. **只有 API Token 需要加密**
   - 用户名、域名是公开信息
   - 不需要过度保护

2. **定期检查配置**
   - 确保 API Token 在 Secrets 中
   - 确保其他配置在 Variables 中

3. **监控访问日志**
   - 定期检查 Actions 运行记录
   - 注意异常的部署活动

### 技术细节

#### GitHub Actions 变量类型

| 类型 | 用途 | 加密 | 可见性 | 日志显示 |
|------|------|------|--------|----------|
| Secrets | 敏感信息 | ✅ | 不可见 | `***` |
| Variables | 配置信息 | ❌ | 可见 | 完整显示 |
| Environment Variables | 运行时变量 | ❌ | 可见 | 完整显示 |

#### 访问方式

```yaml
# Secrets
${{ secrets.SECRET_NAME }}

# Variables
${{ vars.VARIABLE_NAME }}

# 环境变量
${{ env.ENV_NAME }}
```

### 更新历史

- **2024-XX-XX**: 初始版本，全部使用 Secrets
- **2024-XX-XX**: 优化配置，区分 Secrets 和 Variables

### 反馈

如果你在迁移过程中遇到问题，请：
1. 查看 [GitHub 配置指南](GITHUB_CONFIG.md)
2. 检查 Actions 日志
3. 提交 Issue 反馈
