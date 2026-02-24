#!/usr/bin/env python3
"""Upload current project (including .venv) to PythonAnywhere using `pa path upload`.

This script is intended to be run inside CI (GitHub Actions).
It assumes that:
- `uv sync` has already been run, so `.venv` exists.
- `pythonanywhere` CLI (`pa` command) is installed and on PATH.
- The following env vars are set:
  - API_TOKEN: PythonAnywhere API token
  - USER: PythonAnywhere username
  - PA_PROJECT_PATH: remote project directory on PythonAnywhere, e.g. /home/username/py-simple-chat
  - PA_DOMAIN: (optional) domain name for webapp reload

The script:
1. Walks the repository root.
2. Skips non-deployment directories like .git and .github.
3. For every file, calls `pa path upload <remote_path> --contents <local_file>`.
4. Optionally triggers `pa webapp reload` at the end.
"""

import os
import sys
import subprocess
from pathlib import Path


def log(prefix: str, message: str) -> None:
    print(f"{prefix} {message}")


def run_pa_command(args, check: bool = True) -> subprocess.CompletedProcess:
    """Run a `pa` CLI command with API_TOKEN/USER env wired."""
    env = os.environ.copy()
    if "API_TOKEN" not in env or "USER" not in env:
        log("❌", "环境变量 API_TOKEN 或 USER 未设置（PythonAnywhere 认证失败）")
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
    - __pycache__
    - *.pyc, *.pyo
    """
    skip_dirs = {".git", ".github", "__pycache__"}

    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Filter directories in-place
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            if filename.endswith((".pyc", ".pyo")):
                continue
            local_path = Path(dirpath) / filename
            upload_file(repo_root, local_path, remote_root)


def maybe_reload_webapp(domain: str) -> None:
    if not domain:
        return
    log("🔄", f"重新加载 Web 应用: {domain}")
    # best-effort reload; 不失败整个部署
    result = run_pa_command(["webapp", "reload", domain], check=False)
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

    # 可选：先清空远程目录（谨慎使用）
    # run_pa_command(["path", "delete", pa_project_path], check=False)

    upload_tree(repo_root, pa_project_path)

    maybe_reload_webapp(pa_domain)

    log("✅", "项目上传完成")


if __name__ == "__main__":
    main()
