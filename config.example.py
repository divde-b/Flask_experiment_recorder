"""
配置文件
"""

import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'  #flash
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'your-admin-password'  #管理员密码
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    #数据库配置
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'your-db-password'
    DB_NAME = 'experiment_db'
    DB_CURSORCLASS = 'pymysql.cursors.DictCursor'