#!/usr/bin/env python3
"""
PythonAnywhere 自动部署脚本
使用 PythonAnywhere API 和 pa 命令
"""

import os
import sys
import subprocess
import requests
import time

def log(emoji, message):
    """打印日志"""
    print(f"{emoji} {message}")

def run_command(cmd, check=True):
    """执行本地命令"""
    log("🔧", f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        log("❌", f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result

def api_request(method, endpoint, data=None, files=None):
    """发送 API 请求"""
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    base_url = f'https://www.pythonanywhere.com/api/v0/user/{username}'
    
    url = f"{base_url}{endpoint}"
    headers = {'Authorization': f'Token {api_token}'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except Exception as e:
        log("❌", f"API 请求失败: {e}")
        return None

def create_console():
    """创建临时控制台"""
    log("🖥️", "创建临时控制台...")
    response = api_request('POST', '/consoles/')
    
    if response and response.status_code in [200, 201]:
        console_info = response.json()
        console_id = console_info.get('id')
        log("✅", f"控制台创建成功: {console_id}")
        return console_id
    
    log("❌", "控制台创建失败")
    return None

def send_console_input(console_id, command):
    """向控制台发送命令"""
    response = api_request('POST', f'/consoles/{console_id}/send_input/', {'input': command + '\n'})
    return response and response.status_code == 200

def get_console_output(console_id):
    """获取控制台输出"""
    response = api_request('GET', f'/consoles/{console_id}/get_latest_output/')
    if response and response.status_code == 200:
        return response.json().get('output', '')
    return ''

def delete_console(console_id):
    """删除控制台"""
    api_request('DELETE', f'/consoles/{console_id}/')

def execute_commands_in_console(commands):
    """在控制台中执行一系列命令"""
    console_id = create_console()
    if not console_id:
        return False
    
    try:
        for cmd in commands:
            log("📤", f"执行: {cmd}")
            send_console_input(console_id, cmd)
            time.sleep(3)  # 等待命令执行
        
        # 获取最终输出
        time.sleep(2)
        output = get_console_output(console_id)
        if output:
            print(output)
        
        return True
    finally:
        delete_console(console_id)

def check_webapp_exists(domain):
    """检查 Web 应用是否存在"""
    log("🔍", "检查 Web 应用...")
    response = api_request('GET', '/webapps/')
    
    if response and response.status_code == 200:
        webapps = response.json()
        for app in webapps:
            if app.get('domain_name') == domain:
                log("✅", f"Web 应用已存在: {domain}")
                return True
    
    log("�", "Web 应用不存在")
    return False

def create_webapp_via_pa(domain, python_version):
    """使用 pa 命令创建 Web 应用"""
    log("�", f"创建 Web 应用: {domain}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['API_TOKEN'] = env.get('PA_API_TOKEN')
    env['USER'] = env.get('PA_USERNAME')
    
    # 使用 pa webapp create 命令
    cmd = f'pa webapp create --domain {domain} --python {python_version}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    
    if result.returncode == 0:
        log("✅", "Web 应用创建成功")
        return True
    else:
        log("⚠️", f"Web 应用创建失败: {result.stderr}")
        # 尝试使用 API 创建
        return create_webapp_via_api(domain, python_version)

def create_webapp_via_api(domain, python_version):
    """使用 API 创建 Web 应用"""
    log("🔄", "尝试通过 API 创建...")
    
    data = {
        'domain_name': domain,
        'python_version': f'python{python_version.replace(".", "")}',
    }
    
    response = api_request('POST', '/webapps/', data)
    
    if response and response.status_code in [200, 201]:
        log("✅", "Web 应用创建成功")
        return True
    else:
        log("❌", f"创建失败: {response.text if response else 'No response'}")
        return False

def reload_webapp(domain):
    """重新加载 Web 应用"""
    log("🔄", "重新加载应用...")
    
    # 先尝试使用 pa 命令
    env = os.environ.copy()
    env['API_TOKEN'] = env.get('PA_API_TOKEN')
    env['USER'] = env.get('PA_USERNAME')
    
    cmd = f'pa webapp reload {domain}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    
    if result.returncode == 0:
        log("✅", "应用重新加载成功")
        return True
    
    # 如果 pa 命令失败，使用 API
    response = api_request('POST', f'/webapps/{domain}/reload/')
    
    if response and response.status_code == 200:
        log("✅", "应用重新加载成功")
        return True
    else:
        log("❌", f"重新加载失败: {response.text if response else 'No response'}")
        return False

def update_wsgi_file(domain, project_path):
    """更新 WSGI 配置文件"""
    log("📝", "更新 WSGI 配置...")
    
    username = os.environ.get('PA_USERNAME')
    wsgi_path = f"/var/www/{username.replace('.', '_')}_pythonanywhere_com_wsgi.py"
    
    wsgi_content = f"""import sys
import os

project_home = '{project_path}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
"""
    
    # 使用 files API 上传文件
    response = api_request('POST', f'/files/path{wsgi_path}', files={'content': wsgi_content})
    
    if response and response.status_code in [200, 201]:
        log("✅", "WSGI 文件更新成功")
        return True
    else:
        log("⚠️", "WSGI 文件更新失败，可能需要手动配置")
        return False

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
    
    log("🚀", "开始部署到 PythonAnywhere...")
    log("📋", f"用户名: {username}")
    log("📋", f"域名: {domain}")
    log("📋", f"项目路径: {project_path}")
    log("📋", f"仓库: {repo_url}")
    
    project_name = os.path.basename(project_path)
    
    # 1. 设置项目（通过控制台执行命令）
    log("📦", "设置项目环境...")
    
    commands = [
        f"cd ~",
        f"if [ -d {project_name} ]; then cd {project_name} && git pull origin main; else git clone {repo_url} {project_name}; fi",
        f"cd {project_name}",
        f"pip install --user uv",
        f"uv sync",
        f"touch users.json friends.json ip_limit.json banned.json",
        f"echo '{{}}' > users.json",
        f"echo '{{}}' > friends.json",
        f"echo '{{}}' > ip_limit.json",
        f"echo '{{}}' > banned.json",
        f"chmod 644 *.json",
    ]
    
    if not execute_commands_in_console(commands):
        log("⚠️", "项目设置可能未完全成功")
    
    # 2. 检查并创建 Web 应用
    webapp_exists = check_webapp_exists(domain)
    
    if not webapp_exists:
        if not create_webapp_via_pa(domain, python_version):
            log("❌", "Web 应用创建失败")
            sys.exit(1)
        time.sleep(2)
        
        # 更新 WSGI 文件
        update_wsgi_file(domain, project_path)
    
    # 3. 重新加载应用
    if not reload_webapp(domain):
        log("⚠️", "应用重新加载失败，可能需要手动重新加载")
    
    log("✅", "部署完成！")
    log("🌐", f"访问地址: https://{domain}")

if __name__ == '__main__':
    main()
