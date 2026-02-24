#!/usr/bin/env python3
"""
PythonAnywhere 自动部署脚本
处理首次部署和后续更新
"""

import os
import sys
import subprocess
import json

def run_command(cmd, check=True):
    """执行命令并返回结果"""
    print(f"🔧 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ 错误: {result.stderr}")
        sys.exit(1)
    return result

def pa_exec(command):
    """在 PythonAnywhere 上执行命令"""
    return run_command(f'pa exec "{command}"', check=False)

def check_project_exists(project_path):
    """检查项目目录是否存在"""
    result = pa_exec(f"test -d {project_path}")
    return result.returncode == 0

def check_webapp_exists(domain):
    """检查 Web 应用是否存在"""
    result = run_command("pa webapps list", check=False)
    return domain in result.stdout

def clone_repository(repo_url, project_path):
    """克隆 Git 仓库"""
    print("📦 克隆仓库...")
    project_name = os.path.basename(project_path)
    pa_exec(f"cd ~ && git clone {repo_url} {project_name}")
    
    # 初始化数据文件
    print("📄 初始化数据文件...")
    for file in ['users.json', 'friends.json', 'ip_limit.json', 'banned.json']:
        pa_exec(f"cd {project_path} && echo '{{}}' > {file}")
    pa_exec(f"cd {project_path} && chmod 644 *.json")

def update_repository(project_path):
    """更新 Git 仓库"""
    print("🔄 更新代码...")
    pa_exec(f"cd {project_path} && git pull origin main")

def create_webapp(domain, python_version, project_path, username):
    """创建 Web 应用"""
    print("🌐 创建 Web 应用...")
    run_command(f"pa webapps create --domain {domain} --python {python_version}")
    
    # 配置 WSGI 文件
    print("⚙️  配置 WSGI 文件...")
    wsgi_path = f"/var/www/{username.replace('.', '_')}_pythonanywhere_com_wsgi.py"
    
    wsgi_content = f"""import sys
import os

project_home = '{project_path}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
"""
    
    # 写入 WSGI 文件
    escaped_content = wsgi_content.replace("'", "'\\''")
    pa_exec(f"echo '{escaped_content}' > {wsgi_path}")

def install_dependencies(project_path):
    """安装 Python 依赖"""
    print("📚 安装 uv...")
    pa_exec("pip install --user uv")
    
    print("📦 使用 uv 同步依赖...")
    pa_exec(f"cd {project_path} && uv sync")

def reload_webapp(domain):
    """重新加载 Web 应用"""
    print("🔄 重新加载应用...")
    run_command(f"pa reload {domain}")

def main():
    # 从环境变量获取配置
    username = os.environ.get('PA_USERNAME')
    domain = os.environ.get('PA_DOMAIN')
    project_path = os.environ.get('PA_PROJECT_PATH')
    repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}.git"
    python_version = os.environ.get('PYTHON_VERSION', '3.12')
    
    if not all([username, domain, project_path]):
        print("❌ 缺少必要的环境变量")
        sys.exit(1)
    
    print("🚀 开始部署到 PythonAnywhere...")
    print(f"   用户名: {username}")
    print(f"   域名: {domain}")
    print(f"   项目路径: {project_path}")
    
    # 1. 检查并设置项目
    if check_project_exists(project_path):
        print("✅ 项目已存在，更新代码...")
        update_repository(project_path)
    else:
        print("📦 首次部署，克隆仓库...")
        clone_repository(repo_url, project_path)
    
    # 2. 检查并创建 Web 应用
    if check_webapp_exists(domain):
        print("✅ Web 应用已存在")
    else:
        print("🆕 创建新的 Web 应用...")
        create_webapp(domain, python_version, project_path, username)
    
    # 3. 安装依赖
    install_dependencies(project_path)
    
    # 4. 重新加载应用
    reload_webapp(domain)
    
    print("✅ 部署成功！")
    print(f"🌐 访问地址: https://{domain}")

if __name__ == '__main__':
    main()
