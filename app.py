from flask import Flask, render_template, request, redirect, url_for
import pymysql
from pymysql import Error
from pymysql.cursors import DictCursor

import logging
from logging.handlers import RotatingFileHandler
import os

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


app = Flask(__name__)

#数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'zls29252431233',
    'database': 'experiment_db',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Error as e:
        print(f"连接失败: {e}")
        return None

@app.route('/')
def index():
    logger.info("访问首页")
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败")
        return "数据库连接失败，请检查配置。"
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM experiments ORDER BY exp_date DESC")
            experiments = cursor.fetchall()
            logger.debug(f"查询到 {len(experiments)} 条记录")
        except Error as e:
            logger.exception("查询实验记录时发生异常")
            return "查询失败"
    conn.close()
    return render_template('index.html', experiments=experiments)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        exp_name = request.form['exp_name']
        exp_date = request.form['exp_date']
        attacker_ip = request.form['attacker_ip']
        target_ip = request.form['target_ip']
        gateway_ip = request.form['gateway_ip']
        success = True if request.form.get('success') else False
        notes = request.form['notes']

        conn = get_db_connection()
        if not conn:
            return "数据库连接失败"
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO experiments 
                (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                  """
            values = (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes)
            try:
                cursor.execute(sql, values)
                conn.commit()
                logger.info(f"新增试验记录: {exp_name} - {exp_date}")
            except Error as e:
                conn.rollback()
                logger.exception("插入实验记录失败")
                return f"插入失败: {e}"
            conn.close()
            return redirect(url_for('index'))
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)
