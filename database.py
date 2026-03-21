"""
数据库连接配置文件
"""

import pymysql#连接数据库
from pymysql import Error
import logging#日志
from pymysql.cursors import DictCursor
from config import Config

logger = logging.getLogger(__name__)

#数据库连接配置
db_config = {
    'host': Config.DB_HOST,    #数据库主机
    'user': Config.DB_USER,    #用户名
    'password': Config.DB_PASSWORD,   #密码
    'database': Config.DB_NAME,    #数据库名
    'cursorclass': DictCursor   #返回字典格式结果
}

def get_db_connection():
    """
    创建数据库连接
    如果连接失败，记录错误
    :return: None
    """
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Error as e:
        logger.error(f"数据库连接失败： {e}")
        return None