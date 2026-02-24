#!/usr/bin/env python3
"""
PythonAnywhere 简化部署脚本
专注于核心部署功能
"""

import os
import sys
import subprocess
import requests
import time

def log(emoji, message):
    """打印日志"""
    print(f"{emoji} {message}")

def run_pa_command(cmd):
    """执行 pa 命令"""
    env = os.environ.copy()
    env['API_TOKEN'] = env.get('PA_API_TOKEN')
    env['USER'] = env.get('PA_USERNAME')
    
    log("🔧", f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0

def api_call(method, endpoint, data=None):
    """调用 PythonAnywhere API"""
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}{endpoint}'
    headers = {'Authorization': f'Token {api_token}'}
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        
        return resp
    except Exception as e:
        log("❌", f"API 错误: {e}")
        return None

def execute_in_console(commands):
    """在 PythonAnywhere 控制台执行命令"""
    log("🖥️", "创建临时控制台...")
    
    # 创建控制台
    resp = api_call('POST', '/consoles/')
    if not resp or resp.status_code not in [200, 201]:
        log("❌", "无法创建控制台")
        return False
    
    console_id = resp.json().get('id')
    log("✅", f"控制台 ID: {console_id}")
    
    try:
        # 执行命令
        for cmd in commands:
            log("📤", f"执行: {cmd}")
            api_call('POST', f'/consoles/{console_id}/send_input/', {'input': cmd + '\n'})
            time.sleep(2)
        
        # 等待执行完成
        time.sleep(3)
        
        # 获取输出
        resp = api_call('GET', f'/consoles/{console_id}/get_latest_output/')
        if resp and resp.status_code == 200:
            output = resp.json().get('output', '')
            if output:
                print("--- 控制台输出 ---")
                print(output)
                print("--- 输出结束 ---")
        
        return True
    finally:
        # 删除控制台
        api_call('POST', f'/consoles/{console_id}/', {})  # DELETE 用 POST
        log("🗑️", "控制台已清理")

def main():
    """主函数"""
    # 获取配置
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    domain = os.environ.get('PA_DOMAIN')
    project_path = os.environ.get('PA_PROJECT_PATH')
    repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}.git"
    python_version = os.environ.get('PYTHON_VERSION', '3.12')
    
    if not all([api_token, username, domain, project_path]):
        log("❌", "缺少必要的环境变量")
        sys.exit(1)
    
    log("🚀", "开始部署...")
    log("📋", f"域名: {domain}")
    log("📋", f"项目: {project_path}")
    
    project_name = os.path.basename(project_path)
    
    # 1. 设置项目代码
    log("📦", "设置项目...")
    commands = [
        f"cd ~",
        f"if [ -d {project_name} ]; then echo 'Updating...'; cd {project_name} && git pull origin main; else echo 'Cloning...'; git clone {repo_url} {project_name}; fi",
        f"cd {project_name}",
        f"pip install --user uv || echo 'uv already installed'",
        f"uv sync",
        f"touch users.json friends.json ip_limit.json banned.json || true",
        f"[ ! -s users.json ] && echo '{{}}' > users.json || true",
        f"[ ! -s friends.json ] && echo '{{}}' > friends.json || true",
        f"[ ! -s ip_limit.json ] && echo '{{}}' > ip_limit.json || true",
        f"[ ! -s banned.json ] && echo '{{}}' > banned.json || true",
        f"chmod 644 *.json || true",
        f"echo 'Setup complete'",
    ]
    
    if not execute_in_console(commands):
        log("⚠️", "项目设置可能未完全成功，继续...")
    
    # 2. 检查 webapp 是否存在
    log("🌐", "检查 Web 应用...")
    resp = api_call('GET', '/webapps/')
    webapp_exists = False
    
    if resp and resp.status_code == 200:
        webapps = resp.json()
        for app in webapps:
            if app.get('domain_name') == domain:
                webapp_exists = True
                log("✅", "Web 应用已存在")
                break
    
    # 3. 创建 webapp（如果不存在）
    if not webapp_exists:
        log("🆕", "创建 Web 应用...")
        
        # 尝试使用 pa 命令
        if run_pa_command(f'pa webapp create --domain {domain} --python-version {python_version}'):
            log("✅", "Web 应用创建成功")
            time.sleep(2)
            
            # 更新 WSGI 文件
            log("⚙️", "配置 WSGI...")
            wsgi_path = f"/var/www/{username.replace('.', '_')}_pythonanywhere_com_wsgi.py"
            wsgi_content = f"""import sys
import os

project_home = '{project_path}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
"""
            
            # 使用控制台写入 WSGI 文件
            wsgi_commands = [
                f"cat > {wsgi_path} << 'EOFWSGI'",
                wsgi_content,
                "EOFWSGI"
            ]
            execute_in_console(wsgi_commands)
        else:
            log("❌", "Web 应用创建失败")
            log("💡", "请手动在 PythonAnywhere Web 页面创建应用")
            sys.exit(1)
    
    # 4. 重新加载应用
    log("🔄", "重新加载应用...")
    if run_pa_command(f'pa webapp reload {domain}'):
        log("✅", "应用重新加载成功")
    else:
        log("⚠️", "重新加载失败，请手动重新加载")
    
    log("✅", "部署完成！")
    log("🌐", f"访问: https://{domain}")

if __name__ == '__main__':
    main()
