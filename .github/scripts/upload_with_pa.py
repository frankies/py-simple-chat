#!/usr/bin/env python3
"""Upload current project code to PythonAnywhere using `pa path upload`.

This script is intended to be run inside CI (GitHub Actions).
It assumes that:
- `uv sync` has already been run in CI（用于验证依赖，虚拟环境本身不会被上传）。
- `pythonanywhere` CLI (`pa` command) is installed and on PATH.
- The following env vars are set:
  - API_TOKEN: PythonAnywhere API token
  - USER: PythonAnywhere username
  - PA_PROJECT_PATH: remote project directory on PythonAnywhere, e.g. /home/username/py-simple-chat
  - PA_DOMAIN: (optional) domain name for webapp reload

The script:
1. Walks the repository root.
2. Skips non-deployment directories like .git, .github, .venv.
3. For every remaining file, calls `pa path upload <remote_path> --contents <local_file>`.
4. Optionally triggers `pa webapp reload` at the end.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

import requests


def log(prefix: str, message: str) -> None:
    print(f"{prefix} {message}")


def run_pa_command(args, check: bool = True) -> subprocess.CompletedProcess:
    """Run a `pa` CLI command with correct PA username and token.

    优先使用 PA_USERNAME + PA_API_TOKEN，其次回退到 USER + API_TOKEN。
    """
    env = os.environ.copy()

    # 统一用户名：优先 PA_USERNAME，其次 USER
    pa_username = env.get("PA_USERNAME") or env.get("USER")
    if not pa_username:
        log("❌", "缺少 PA_USERNAME/USER（PythonAnywhere 用户名）")
        sys.exit(1)

    # 强制覆盖 USER，并设置 PYTHONANYWHERE_USERNAME，避免继续使用 GitHub runner 的默认用户名
    env["USER"] = pa_username
    env["PYTHONANYWHERE_USERNAME"] = pa_username

    api_token = env.get("PA_API_TOKEN") or env.get("API_TOKEN")
    if not api_token:
        log("❌", "缺少 PA_API_TOKEN/API_TOKEN（PythonAnywhere API token）")
        sys.exit(1)

    cmd = ["pa"] + list(args)
    log("🔧", "执行: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # pa 某些正常输出会走 stderr，这里只在失败时标红
        stream = sys.stderr if result.returncode != 0 else sys.stdout
        print(result.stderr, file=stream)

    if check and result.returncode != 0:
        log("❌", f"命令失败，退出码: {result.returncode}")
        sys.exit(result.returncode)

    return result


def api_request(method: str, endpoint: str, data=None):
    """Call PythonAnywhere API using token/username from env.

    Prefers PA_API_TOKEN/PA_USERNAME, falls back to API_TOKEN/USER.
    """
    env = os.environ.copy()
    api_token = env.get("PA_API_TOKEN") or env.get("API_TOKEN")
    # 与 run_pa_command 保持一致：优先 PA_USERNAME
    username = env.get("PA_USERNAME") or env.get("USER")
    host = os.environ.get("PYTHONANYWHERE_SITE", "www.pythonanywhere.com")

    if not api_token or not username:
        log("⚠️", "缺少 API token 或用户名，无法调用 PythonAnywhere API 创建 Web 应用")
        return None

    base_url = f"https://{host}/api/v0/user/{username}"
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Token {api_token}"}

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            # 使用 form-data 以兼容 webapps 创建接口
            resp = requests.post(url, headers=headers, data=data, timeout=30)
        elif method == "PATCH":
            # 对配置更新，官方示例使用 JSON
            resp = requests.patch(url, headers=headers, json=data, timeout=30)
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")
        return resp
    except Exception as exc:  # 网络错误等
        log("❌", f"API 请求失败: {exc}")
        return None


def upload_file(local_root: Path, local_file: Path, remote_root: str) -> None:
    """Upload a single file using `pa path upload`.

    remote_root: e.g. /home/username/py-simple-chat
    """
    rel = local_file.relative_to(local_root)
    # Normalize to POSIX-style paths for PythonAnywhere
    remote_path = str(Path(remote_root) / rel).replace("\\", "/")

    # Ensure parent directories are implicitly created by files API
    run_pa_command(["path", "upload", remote_path, "--contents", str(local_file)])


def upload_tree(repo_root: Path, remote_root: str) -> None:
    """Walk repo_root and upload all files to remote_root.

    Skips:
    - .git
    - .github
    - .venv
    - __pycache__
    - *.pyc, *.pyo
    """
    skip_dirs = {".git", ".github", ".venv", "__pycache__"}

    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Filter directories in-place
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            if filename.endswith((".pyc", ".pyo")):
                continue
            local_path = Path(dirpath) / filename
            upload_file(repo_root, local_path, remote_root)


def ensure_remote_directory(remote_root: str) -> None:
    """Ensure that remote_root directory exists on PythonAnywhere.

    If it does not exist, create it by uploading then deleting a dummy file.
    """
    log("🔍", f"检查远程目录是否存在: {remote_root}")

    # If path exists (file or dir), pa path get will succeed
    result = run_pa_command(["path", "get", remote_root], check=False)
    if result.returncode == 0:
        log("✅", "远程目录已存在")
        return

    log("📁", "远程目录不存在，准备创建...")

    dummy_remote = str(Path(remote_root) / ".pa_dir_init").replace("\\", "/")

    # Create a temporary empty local file, upload it, then delete it remotely
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        run_pa_command(["path", "upload", dummy_remote, "--contents", str(tmp_path)])
        # Remove dummy file but keep directory
        run_pa_command(["path", "delete", dummy_remote], check=False)
        log("✅", "远程目录已创建")
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except OSError:
                pass


def ensure_webapp(domain: str) -> None:
    """Ensure that the webapp for given domain exists; create via API if missing."""
    if not domain:
        return

    log("🌐", f"检查 Web 应用是否存在: {domain}")

    resp = api_request("GET", "/webapps/")
    if not resp:
        log("⚠️", "无法获取 Web 应用列表（可能是 API 权限或网络问题）")
        return

    if resp.status_code == 200:
        try:
            webapps = resp.json()
        except Exception:
            webapps = []

        for app in webapps:
            if app.get("domain_name") == domain:
                log("✅", "Web 应用已存在")
                return
    else:
        log("⚠️", f"获取 Web 应用列表失败: {resp.status_code} - {resp.text[:200]}")
        return

    log("🆕", "Web 应用不存在，尝试创建...")

    python_version = os.environ.get("PYTHON_VERSION", "3.12")
    python_ver = f"python{python_version.replace('.', '')}"

    data = {
        "domain_name": domain,
        "python_version": python_ver,
    }

    create_resp = api_request("POST", "/webapps/", data=data)
    if not create_resp:
        log("❌", "创建 Web 应用失败（API 无响应）")
        return

    if create_resp.status_code in (200, 201):
        log("✅", "Web 应用创建成功")
    else:
        log("❌", f"Web 应用创建失败: {create_resp.status_code} - {create_resp.text[:300]}")


def update_webapp_config(domain: str, project_path: str) -> None:
    """Update webapp config: source_directory & virtualenv_path.

    - source_directory: 指向代码所在目录（PA_PROJECT_PATH）
    - virtualenv_path: 指向虚拟环境目录，约定为 <PA_PROJECT_PATH>/.venv
    """
    if not domain or not project_path:
        return

    log("⚙️", f"更新 Web 应用配置: {domain}")

    data = {
        "source_directory": project_path,
        "virtualenv_path": f"{project_path}/.venv",
    }

    resp = api_request("PATCH", f"/webapps/{domain}/", data=data)
    if not resp:
        log("⚠️", "更新 Web 应用配置失败（API 无响应）")
        return

    if resp.status_code == 200:
        log("✅", "Web 应用配置更新成功")
    else:
        log("⚠️", f"Web 应用配置更新失败: {resp.status_code} - {resp.text[:300]}")


def update_wsgi_file(project_path: str) -> None:
    """Update /var/www/<username>_pythonanywhere_com_wsgi.py to point to project_path."""
    if not project_path:
        return

    env = os.environ.copy()
    username = env.get("PA_USERNAME") or env.get("USER")
    api_token = env.get("PA_API_TOKEN") or env.get("API_TOKEN")
    host = env.get("PYTHONANYWHERE_SITE", "www.pythonanywhere.com")

    if not username or not api_token:
        log("⚠️", "缺少用户名或 API token，跳过更新 WSGI 文件")
        return

    wsgi_path = f"/var/www/{username}_pythonanywhere_com_wsgi.py"

    wsgi_content = f"""import sys
import os

project_home = '{project_path}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
"""

    url = f"https://{host}/api/v0/user/{username}/files/path{wsgi_path}"
    headers = {"Authorization": f"Token {api_token}"}

    log("📝", f"更新 WSGI 文件: {wsgi_path}")
    try:
        resp = requests.post(url, headers=headers, files={"content": ("wsgi.py", wsgi_content)}, timeout=30)
    except Exception as exc:
        log("⚠️", f"更新 WSGI 文件请求失败: {exc}")
        return

    if resp.status_code in (200, 201):
        log("✅", "WSGI 文件更新成功")
    else:
        log("⚠️", f"WSGI 文件更新失败: {resp.status_code} - {resp.text[:300]}")


def run_remote_uv_sync(project_path: str) -> None:
    """Run `uv sync` on PythonAnywhere inside the project directory via Consoles API."""
    if not project_path:
        return

    env = os.environ.copy()
    username = env.get("PA_USERNAME") or env.get("USER")
    api_token = env.get("PA_API_TOKEN") or env.get("API_TOKEN")
    host = env.get("PYTHONANYWHERE_SITE", "www.pythonanywhere.com")

    if not username or not api_token:
        log("⚠️", "缺少用户名或 API token，跳过远程 uv sync")
        return

    base_url = f"https://{host}/api/v0/user/{username}"
    headers = {"Authorization": f"Token {api_token}"}

    log("🖥️", "创建远程 Bash 控制台以执行 uv sync...")
    try:
        resp = requests.post(
            f"{base_url}/consoles/",
            headers=headers,
            data={
                "executable": "/bin/bash",
                "arguments": "-l",
                "working_directory": project_path,
            },
            timeout=30,
        )
    except Exception as exc:
        log("⚠️", f"创建远程控制台失败: {exc}")
        return

    if resp.status_code not in (200, 201):
        log("⚠️", f"创建远程控制台失败: {resp.status_code} - {resp.text[:200]}")
        return

    try:
        console_id = resp.json().get("id")
    except Exception:
        console_id = None

    if not console_id:
        log("⚠️", "创建控制台响应中缺少 id，跳过 uv sync")
        return

    log("✅", f"控制台已创建，ID: {console_id}")

    # 在远程环境中安装 uv（如有需要）并执行 uv sync
    script = "pip install --user uv || echo 'uv maybe already installed'\nuv sync\n"

    try:
        requests.post(
            f"{base_url}/consoles/{console_id}/send_input/",
            headers=headers,
            data={"input": script},
            timeout=30,
        )
        log("📤", "已发送 uv sync 命令到远程控制台")

        # 简单轮询几次输出，方便在日志里看到执行情况
        for _ in range(6):  # 约 30 秒
            try:
                out_resp = requests.get(
                    f"{base_url}/consoles/{console_id}/get_latest_output/",
                    headers=headers,
                    timeout=30,
                )
            except Exception:
                break

            if out_resp.status_code != 200:
                break

            output = out_resp.json().get("output", "")
            if output:
                print(output)
            import time as _time
            _time.sleep(5)
    finally:
        # 结束并清理控制台（尽力而为）
        try:
            requests.delete(
                f"{base_url}/consoles/{console_id}/",
                headers=headers,
                timeout=30,
            )
        except Exception:
            pass


def maybe_reload_webapp(domain: str) -> None:
    if not domain:
        return
    log("🔄", f"重新加载 Web 应用: {domain}")
    # best-effort reload; 不失败整个部署
    result = run_pa_command(["webapp", "reload", "-d", domain], check=False)
    if result.returncode == 0:
        log("✅", "Web 应用重新加载成功")
    else:
        log("⚠️", "Web 应用重新加载失败（可以在控制台手动 Reload）")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    pa_project_path = os.environ.get("PA_PROJECT_PATH")
    pa_domain = os.environ.get("PA_DOMAIN", "")

    if not pa_project_path:
        log("❌", "缺少环境变量 PA_PROJECT_PATH")
        sys.exit(1)

    log("🚀", "开始使用 pa path upload 部署项目...")
    log("📁", f"本地根目录: {repo_root}")
    log("📂", f"远程目录: {pa_project_path}")

    # 1. 确保远程目录存在
    ensure_remote_directory(pa_project_path)

    # 2. 上传整个项目目录（不包含 .venv，只上传代码和资源）
    upload_tree(repo_root, pa_project_path)

    # 3. 在平台目录下执行一次 uv sync，确保依赖就绪
    run_remote_uv_sync(pa_project_path)
    
    # 4. 确保 Web 应用存在
    ensure_webapp(pa_domain)

    # 5. 更新 Web 应用配置：source_directory & virtualenv_path
    update_webapp_config(pa_domain, pa_project_path)

    # 6. 更新 WSGI 文件，使其指向新的 project_home
    update_wsgi_file(pa_project_path)

    
    # 7. 重载 Web 应用（尽力而为）
    maybe_reload_webapp(pa_domain)

    log("✅", "项目上传完成")


if __name__ == "__main__":
    main()
