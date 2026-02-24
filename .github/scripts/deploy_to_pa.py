#!/usr/bin/env python3
"""
PythonAnywhere 自动部署脚本
使用 pythonanywhere-core 库和 pa 命令行工具
"""

import os
import sys
import subprocess

def log(emoji, message):
    """打印日志"""
    print(f"{emoji} {message}")

def run_pa_command(command, check=True):
    """执行 pa 命令"""
    log("🔧", f"执行: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        log("❌", f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result

def main():
    """主函数"""
    # 从环境变量获取配置
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    domain = os.environ.get('PA_DOMAIN')
    project_path = os.environ.get('PA_PROJECT_PATH')
    repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}.git"
    python_version = os.environ.get('PYTHON_VERSION', '3.12')
    
    if not all([api_token, username, domain, project_path]):
        log("❌", "缺少必要的环境变量")
        sys.exit(1)
    
    log("�", "开始部署到 PythonAnywhere...")
    log("📋", f"用户名: {username}")
    log("📋", f"域名: {domain}")
    log("📋", f"项目路径: {project_path}")
    log("📋", f"仓库: {repo_url}")
    
    # 设置环境变量供 pa 命令使用
    env = os.environ.copy()
    env['API_TOKEN'] = api_token
    env['USER'] = username
    
    # 1. 检查项目是否存在，不存在则克隆
    log("📦", "检查并设置项目...")
    project_name = os.path.basename(project_path)
    
    check_cmd = f'pa exec "test -d {project_path} && echo EXISTS || echo NOT_EXISTS"'
    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, env=env)
    
    if "NOT_EXISTS" in result.stdout or result.returncode != 0:
        log("📥", "克隆仓库...")
        run_pa_command(f'pa exec "cd ~ && git clone {repo_url} {project_name}"', check=False)
        
        # 初始化数据文件
        log("📄", "初始化数据文件...")
        init_commands = [
            f'pa exec "cd {project_path} && touch users.json friends.json ip_limit.json banned.json"',
            f'pa exec "cd {project_path} && echo \'{{}}\' > users.json"',
            f'pa exec "cd {project_path} && echo \'{{}}\' > friends.json"',
            f'pa exec "cd {project_path} && echo \'{{}}\' > ip_limit.json"',
            f'pa exec "cd {project_path} && echo \'{{}}\' > banned.json"',
            f'pa exec "cd {project_path} && chmod 644 *.json"',
        ]
        for cmd in init_commands:
            run_pa_command(cmd, check=False)
    else:
        log("✅", "项目已存在，更新代码...")
        run_pa_command(f'pa exec "cd {project_path} && git pull origin main"', check=False)
    
    # 2. 安装 uv 和依赖
    log("📚", "安装 uv...")
    run_pa_command(f'pa exec "pip install --user uv"', check=False)
    
    log("📦", "同步依赖...")
    run_pa_command(f'pa exec "cd {project_path} && uv sync"', check=False)
    
    # 3. 检查并创建 Web 应用
    log("🌐", "检查 Web 应用...")
    check_webapp = f'pa webapp list'
    result = subprocess.run(check_webapp, shell=True, capture_output=True, text=True, env=env)
    
    if domain not in result.stdout:
        log("🆕", "创建 Web 应用...")
        # 使用 pa webapp create 命令
        create_cmd = f'pa webapp create --domain {domain} --python {python_version} --source-directory {project_path}'
        run_pa_command(create_cmd, check=False)
        
        # 配置 WSGI 文件
        log("⚙️", "配置 WSGI 文件...")
        wsgi_content = f"""import sys
import os

project_home = '{project_path}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
"""
        # 写入 WSGI 文件
        wsgi_path = f"/var/www/{username.replace('.', '_')}_pythonanywhere_com_wsgi.py"
        escaped_content = wsgi_content.replace("'", "'\\''")
        run_pa_command(f'pa exec "echo \'{escaped_content}\' > {wsgi_path}"', check=False)
    else:
        log("✅", "Web 应用已存在")
    
    # 4. 重新加载应用
    log("🔄", "重新加载应用...")
    reload_cmd = f'pa webapp reload {domain}'
    run_pa_command(reload_cmd, check=False)
    
    log("✅", "部署完成！")
    log("🌐", f"访问地址: https://{domain}")

if __name__ == '__main__':
    main()
