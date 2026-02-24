"""
PythonAnywhere WSGI 配置文件
将此文件内容复制到 PythonAnywhere 的 WSGI 配置文件中
通常位于: /var/www/yourusername_pythonanywhere_com_wsgi.py
"""

import sys
import os

# 添加项目路径到 Python 路径
# 请将 'yourusername' 替换为你的 PythonAnywhere 用户名
project_home = '/home/yourusername/py-simple-chat'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 设置环境变量
os.environ['USE_MEMORY_STORAGE'] = '0'  # PythonAnywhere 支持文件存储
os.environ['SECRET_KEY'] = 'super_chat_123'  # 建议使用更安全的密钥

# 导入 Flask 应用和 SocketIO
from main import app, socketio

# PythonAnywhere 使用 WSGI，但 SocketIO 需要特殊处理
# 对于 Flask-SocketIO，我们需要使用 socketio.run() 的 WSGI 应用
application = socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)

# 如果上面的方式不工作，使用标准 Flask WSGI
# application = app
