"""
数据库连接配置模块
责任：管理数据库连接参数，提供统一的数据库连接函数
"""

import pymysql#连接数据库
from pymysql import Error
import logging#日志
from pymysql.cursors import DictCursor
from config import Config

logger = logging.getLogger(__name__)

#数据库连接配置（从Config类读取，避免硬编码）
db_config = {
    'host': Config.DB_HOST,    #数据库主机
    'user': Config.DB_USER,    #用户名
    'password': Config.DB_PASSWORD,   #密码
    'database': Config.DB_NAME,    #数据库名
    'cursorclass': DictCursor   #返回字典格式结果
}

def get_db_connection():
    """
    创建并返回数据库连接对象
    如果连接失败，记录错误并返回None
    调用方需自行关闭连接
    """
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Error as e:
        logger.error(f"数据库连接失败： {e}")  #使用日志返回信息更贴切
        return None