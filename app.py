"""
主文件，日志格式，操作系统文件，
"""

from flask import Flask
from routes.experiments import experiments_bp
import logging
import os
from logging.handlers import RotatingFileHandler
from config import Config

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
file_handler.setLevel(logging.INFO) #文件记录INFO及以上级别

#控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)

#配置根日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler],
)

#获取当前模块的logger
logger = logging.getLogger(__name__)

#创建Flask应用实例
app = Flask(__name__)
app.config.from_object(Config)

#注册蓝图
app.register_blueprint(experiments_bp)


if __name__ == '__main__':
    app.run(debug=True) #启用调试模式
