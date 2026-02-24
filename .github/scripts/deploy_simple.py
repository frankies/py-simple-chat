#!/usr/bin/env python3
"""
PythonAnywhere 简化部署脚本
使用 API 进行所有操作
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
    """执行 pa 命令（仅用于 reload）"""
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

def api_get(endpoint):
    """GET 请求"""
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}{endpoint}'
    headers = {'Authorization': f'Token {api_token}'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        return resp
    except Exception as e:
        log("❌", f"GET 请求失败: {e}")
        return None

def api_post(endpoint, data=None):
    """POST 请求 - 使用 form data"""
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}{endpoint}'
    headers = {'Authorization': f'Token {api_token}'}
    
    log("🔗", f"POST {url}")
    if data:
        log("📋", f"数据: {data}")
    
    try:
        # 使用 data 参数发送 form-encoded 数据
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        log("📊", f"状态: {resp.status_code}")
        if resp.status_code >= 400:
            log("⚠️", f"响应: {resp.text}")
        return resp
    except Exception as e:
        log("❌", f"POST 请求失败: {e}")
        return None

def execute_in_console(commands):
    """在 PythonAnywhere 控制台执行命令"""
    log("🖥️", "创建临时控制台...")
    
    # 创建控制台
    resp = api_post('/consoles/')
    if not resp or resp.status_code not in [200, 201]:
        log("❌", "无法创建控制台")
        return False
    
    console_id = resp.json().get('id')
    log("✅", f"控制台 ID: {console_id}")
    
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    base_url = f'https://www.pythonanywhere.com/api/v0/user/{username}'
    headers = {'Authorization': f'Token {api_token}'}
    
    try:
        # 发送命令
        for i, cmd in enumerate(commands, 1):
            log("📤", f"发送命令 {i}/{len(commands)}")
            
            # 将多行命令分行发送
            lines = cmd.strip().split('\n')
            for line in lines:
                if line.strip():  # 跳过空行
                    requests.post(
                        f'{base_url}/consoles/{console_id}/send_input/',
                        headers=headers,
                        data={'input': line + '\n'},
                        timeout=30
                    )
                    time.sleep(0.5)  # 短暂延迟
        
        # 等待命令执行
        log("⏳", "等待命令执行完成（最多30秒）...")
        
        # 轮询获取输出
        max_attempts = 10
        output_text = ""
        
        for attempt in range(max_attempts):
            time.sleep(3)
            
            resp = requests.get(
                f'{base_url}/consoles/{console_id}/get_latest_output/',
                headers=headers,
                timeout=30
            )
            
            if resp and resp.status_code == 200:
                new_output = resp.json().get('output', '')
                
                # 如果有新输出
                if new_output and new_output != output_text:
                    output_text = new_output
                    
                    # 检查是否完成
                    if '=== 设置完成 ===' in output_text:
                        log("✅", "检测到完成标记")
                        break
                    
                    log("�", f"获取输出中... ({attempt + 1}/{max_attempts})")
        
        # 显示输出
        if output_text:
            print("\n" + "="*70)
            print("PythonAnywhere 控制台输出:")
            print("="*70)
            print(output_text)
            print("="*70 + "\n")
            
            # 检查是否有错误
            if 'error' in output_text.lower() or 'failed' in output_text.lower():
                log("⚠️", "输出中可能包含错误，请检查")
        else:
            log("⚠️", "未获取到控制台输出")
            log("💡", "命令可能仍在执行，或执行时间过长")
        
        return True
        
    except Exception as e:
        log("❌", f"执行命令时出错: {e}")
        return False
    finally:
        # 删除控制台
        try:
       #  requests.delete(f'{base_url}/consoles/{console_id}/', headers=headers, timeout=30)
            log("🗑️", "控制台已清理")
        except:
            pass

def create_webapp_via_api(domain, python_version):
    """使用 API 创建 Web 应用"""
    log("🆕", f"通过 API 创建 Web 应用: {domain}")
    
    # Python 版本格式：python312, python310 等
    python_ver = f'python{python_version.replace(".", "")}'
    
    # 使用 form data
    data = {
        'domain_name': domain,
        'python_version': python_ver,
    }
    
    resp = api_post('/webapps/', data)
    
    if resp and resp.status_code in [200, 201]:
        log("✅", "Web 应用创建成功")
        return True
    else:
        log("❌", f"创建失败")
        return False

def update_webapp_config(domain, project_path):
    """更新 Web 应用配置"""
    log("⚙️", "更新 Web 应用配置...")
    
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain}/'
    headers = {'Authorization': f'Token {api_token}'}
    
    data = {
        'source_directory': project_path,
        'working_directory': project_path,
    }
    
    try:
        resp = requests.patch(url, headers=headers, json=data, timeout=30)
        if resp.status_code == 200:
            log("✅", "配置更新成功")
            return True
        else:
            log("⚠️", f"配置更新失败: {resp.text}")
            return False
    except Exception as e:
        log("❌", f"配置更新错误: {e}")
        return False

def update_wsgi_file(domain, project_path):
    """更新 WSGI 配置文件"""
    log("📝", "更新 WSGI 配置...")
    
    username = os.environ.get('PA_USERNAME')
    wsgi_path = f"/var/www/{domain.replace('.', '_')}_wsgi.py"
    
    wsgi_content = f"""import sys
import os

project_home = '{project_path}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['USE_MEMORY_STORAGE'] = '0'

from main import app as application
"""
    
    # 使用 files API 上传文件
    api_token = os.environ.get('PA_API_TOKEN')
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path{wsgi_path}'
    headers = {'Authorization': f'Token {api_token}'}
    
    try:
        resp = requests.post(url, headers=headers, files={'content': wsgi_content}, timeout=30)
        
        if resp.status_code in [200, 201]:
            log("✅", "WSGI 文件更新成功")
            return True
        else:
            log("⚠️", f"WSGI 文件更新失败: {resp.text}")
            return False
    except Exception as e:
        log("❌", f"WSGI 文件更新错误: {e}")
        return False

def reload_webapp(domain):
    """重新加载 Web 应用"""
    log("🔄", "重新加载应用...")
    
    # 直接使用 API
    api_token = os.environ.get('PA_API_TOKEN')
    username = os.environ.get('PA_USERNAME')
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain}/reload/'
    headers = {'Authorization': f'Token {api_token}'}
    
    try:
        resp = requests.post(url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            log("✅", "应用重新加载成功")
            return True
        elif resp.status_code == 403:
            log("⚠️", "权限不足或应用不存在")
            log("💡", "可能的原因：")
            log("💡", "  1. Web 应用尚未创建")
            log("💡", "  2. API Token 权限不足")
            log("💡", "  3. 域名不正确")
            return False
        elif resp.status_code == 404:
            log("⚠️", "Web 应用不存在")
            log("💡", f"请先在 PythonAnywhere 创建应用: {domain}")
            return False
        else:
            log("⚠️", f"重新加载失败: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        log("❌", f"重新加载错误: {e}")
        return False

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
    log("📋", f"Python: {python_version}")
    
    project_name = os.path.basename(project_path)
    
    # 1. 设置项目代码
    log("📦", "设置项目...")
    
    # 将所有命令合并为一个脚本
    script = f"""
cd ~
if [ -d {project_name} ]; then
    echo "=== 更新现有项目 ==="
    cd {project_name}
    git pull origin main
else
    echo "=== 克隆新项目 ==="
    git clone {repo_url} {project_name}
    cd {project_name}
fi

echo "=== 安装 uv ==="
pip install --user uv || echo "uv 已安装"

echo "=== 同步依赖 ==="
uv sync

echo "=== 初始化数据文件 ==="
touch users.json friends.json ip_limit.json banned.json
[ ! -s users.json ] && echo '{{}}' > users.json || echo "users.json 已存在"
[ ! -s friends.json ] && echo '{{}}' > friends.json || echo "friends.json 已存在"
[ ! -s ip_limit.json ] && echo '{{}}' > ip_limit.json || echo "ip_limit.json 已存在"
[ ! -s banned.json ] && echo '{{}}' > banned.json || echo "banned.json 已存在"
chmod 644 *.json

echo "=== 设置完成 ==="
echo "项目路径: $(pwd)"
echo "Python 版本: $(python --version)"
echo "uv 版本: $(uv --version)"
"""
    
    commands = [script]
    
    if not execute_in_console(commands):
        log("⚠️", "项目设置可能未完全成功，继续...")
    
    # 2. 检查 webapp 是否存在
    log("🌐", "检查 Web 应用...")
    resp = api_get('/webapps/')
    webapp_exists = False
    
    if resp and resp.status_code == 200:
        webapps = resp.json()
        for app in webapps:
            if app.get('domain_name') == domain:
                webapp_exists = True
                log("✅", "Web 应用已存在")
                break
    
    # 3. 创建或更新 webapp
    if not webapp_exists:
        log("🆕", "创建 Web 应用...")
        
        if not create_webapp_via_api(domain, python_version):
            log("⚠️", "Web 应用创建失败")
            log("💡", "可能的原因：")
            log("💡", "  1. API Token 权限不足")
            log("💡", "  2. 域名已被使用")
            log("💡", "  3. 免费账户限制（最多1个应用）")
            log("💡", "")
            log("💡", "解决方案：")
            log("💡", f"  请手动在 PythonAnywhere Web 页面创建应用")
            log("💡", f"  域名: {domain}")
            log("💡", f"  Python 版本: {python_version}")
            log("💡", "")
            log("🔄", "继续尝试配置现有应用...")
        else:
            time.sleep(2)
    
    # 4. 更新配置（无论是否刚创建）
    update_webapp_config(domain, project_path)
    
    # 5. 更新 WSGI 文件
    update_wsgi_file(domain, project_path)
    
    # 6. 重新加载应用
    if not reload_webapp(domain):
        log("⚠️", "应用重新加载失败")
        log("💡", "如果应用不存在，请先手动创建")
    
    log("✅", "部署流程完成！")
    log("🌐", f"访问: https://{domain}")

if __name__ == '__main__':
    main()
