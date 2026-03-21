"""
数据库连接配置文件
"""
import pymysql#连接数据库
from pymysql import Error
import logging#日志
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)

#数据库连接配置
db_config = {
    'host': 'localhost',    #数据库主机
    'user': 'root',    #用户名
    'password': 'zls29252431233',   #密码
    'database': 'experiment_db',    #数据库名
    'cursorclass': pymysql.cursors.DictCursor   #返回字典格式结果
}

def get_db_connection():
    """
    创建数据库连接
    如果连接失败，记录错误并
    :return: None
    """
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Error as e:
        print(f"连接失败: {e}")
        return None