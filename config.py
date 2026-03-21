"""
配置文件
"""

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dakjgkjas4364'  #flash
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Zls292524'  #管理员密码

    #数据库配置
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'zls29252431233'
    DB_NAME = 'expriment_db'
    DB_CURSORCLASS = 'pymysql.cursors.DictCursor'