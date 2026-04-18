"""
Flask应用主入口
负责创建应用实例、配置、注册蓝图、配置日志。
"""
from flask import Flask
from routes.experiments import experiments_bp
import logging
import os
from logging.handlers import RotatingFileHandler
from config import Config
from routes.auth import auth_bp
from routes.docs import docs_bp

#-----------日志配置----------
#确保日志目录存在
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

#配置日志格式
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#文件处理器: 按大小轮转，保留5个备份，每个最大1MB
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=1024*1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)  #文件记录 INFO 及以上级别

#控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)  #控制台输出 DEBUG 及以上级别

#配置根日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler],
)

#获取当前模块的logger
logger = logging.getLogger(__name__)

#----------FLask应用---------

#创建Flask应用实例
app = Flask(__name__)
app.config.from_object(Config)  #从config.py加载配置（包含SECRET_KEY、ADMIN_PASSWORD 等）

#注册蓝图
app.register_blueprint(experiments_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(docs_bp)

#提升安全性
app.config.update(
    SESSION_COOKIE_SECURE=True,  #仅通过 HTTPS 传输cookie
    SESSION_COOKIE_HTTPONLY=True,  #默认开启，确保为True
    SESSION_COOKIE_SAMESITEASK='Lax',  #防止 CSRF 攻击
)

#----------启动----------
if __name__ == '__main__':
    #开发模式，启用调试
    #生产环境使用 gunicorn 等服务器，并关闭debug
    app.run(debug=True)
