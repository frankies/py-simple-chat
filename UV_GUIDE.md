# uv 使用指南

本项目使用 [uv](https://github.com/astral-sh/uv) 作为 Python 包管理工具，它比传统的 pip 更快、更可靠。

## 为什么使用 uv？

- ⚡ 速度快：比 pip 快 10-100 倍
- 🔒 可靠：使用 `uv.lock` 确保依赖版本一致
- 🎯 简单：统一的命令行接口
- 🔄 兼容：完全兼容 pip 和 PyPI

## 安装 uv

### Windows

```bash
pip install uv
```

或使用 PowerShell：

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux

```bash
pip install uv
```

或使用 curl：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 基本使用

### 1. 同步依赖

从 `pyproject.toml` 和 `uv.lock` 安装所有依赖：

```bash
uv sync
```

这会：
- 创建虚拟环境（如果不存在）
- 安装 `pyproject.toml` 中定义的所有依赖
- 使用 `uv.lock` 确保版本一致

### 2. 添加新依赖

```bash
# 添加生产依赖
uv add flask-cors

# 添加开发依赖
uv add --dev pytest
```

### 3. 移除依赖

```bash
uv remove package-name
```

### 4. 运行 Python 脚本

```bash
# 在 uv 管理的虚拟环境中运行
uv run python main.py

# 或运行任何命令
uv run flask run
```

### 5. 更新依赖

```bash
# 更新所有依赖到最新版本
uv lock --upgrade

# 更新特定包
uv lock --upgrade-package flask
```

## 配置镜像源（中国大陆用户）

创建 `uv.toml` 文件（已提供 `uv.toml.example` 模板）：

```toml
[pip]
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

或使用环境变量：

```bash
# Windows (PowerShell)
$env:UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

# macOS/Linux
export UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
```

可用的镜像源：
- 清华大学：`https://pypi.tuna.tsinghua.edu.cn/simple`
- 阿里云：`https://mirrors.aliyun.com/pypi/simple/`
- 腾讯云：`https://mirrors.cloud.tencent.com/pypi/simple`
- 华为云：`https://mirrors.huaweicloud.com/repository/pypi/simple`

## 常用命令对照

| 操作 | pip | uv |
|------|-----|-----|
| 安装依赖 | `pip install -r requirements.txt` | `uv sync` |
| 添加包 | `pip install flask` | `uv add flask` |
| 移除包 | `pip uninstall flask` | `uv remove flask` |
| 运行脚本 | `python main.py` | `uv run python main.py` |
| 创建虚拟环境 | `python -m venv .venv` | `uv venv` |
| 激活虚拟环境 | `source .venv/bin/activate` | 不需要（使用 `uv run`）|

## 虚拟环境管理

uv 会自动管理虚拟环境，但你也可以手动操作：

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境（可选）
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 在虚拟环境中使用 pip（不推荐）
uv pip install package-name
```

## 项目工作流

### 首次设置

```bash
# 1. 克隆项目
git clone <repo-url>
cd py-simple-chat

# 2. 安装 uv
pip install uv

# 3. 同步依赖
uv sync

# 4. 运行应用
uv run python main.py
```

### 日常开发

```bash
# 添加新依赖
uv add new-package

# 运行应用
uv run python main.py

# 运行测试
uv run pytest

# 提交更改（包括 uv.lock）
git add pyproject.toml uv.lock
git commit -m "Add new dependency"
```

## 在 PythonAnywhere 上使用

PythonAnywhere 部署时会自动：

1. 安装 uv：`pip install --user uv`
2. 同步依赖：`uv sync`
3. 使用虚拟环境中的 Python

## 故障排除

### 问题：uv sync 失败

```bash
# 清除缓存重试
uv cache clean
uv sync
```

### 问题：找不到 Python

```bash
# 指定 Python 版本
uv venv --python 3.12
uv sync
```

### 问题：依赖冲突

```bash
# 重新生成 lock 文件
rm uv.lock
uv lock
uv sync
```

### 问题：网络超时（中国大陆）

配置镜像源（见上文"配置镜像源"部分）

## 更多资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub 仓库](https://github.com/astral-sh/uv)
- [Python 打包指南](https://packaging.python.org/)

## 从 pip/requirements.txt 迁移

如果你之前使用 `requirements.txt`：

```bash
# uv 可以直接读取 requirements.txt
uv pip install -r requirements.txt

# 或者迁移到 pyproject.toml
# 手动将依赖添加到 pyproject.toml 的 dependencies 数组
# 然后运行
uv sync
```

本项目已经配置好 `pyproject.toml`，直接使用 `uv sync` 即可。
