"""
使用Flask+Python+MySQL的全栈开发，用于记录网络实验。
"""

from flask import Flask, render_template, request, redirect, url_for
import pymysql
from pymysql import Error
from pymysql.cursors import DictCursor
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import flash
"""
使用Flask Web框架核心
pymysql mysql数据库连接库
logging 日志记录模块，用于记录运行信息
os 操作系统接口，用于文件路径操作
flash消息提示密码成功或错误
"""

#管理员密码
ADMIN_PASSWORD = 'Zls292524'

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

"""
创建logs目录（如果不存在）
配置日志格式
设置文件处理器，每个日志文件最大1MB，保留5个备份
设置控制台处理器
配置根日志记录器
"""

app = Flask(__name__)

"""
创建Flask应用实例
"""

#flash
app.secret_key = 'dakjgkjas4364'


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

@app.route('/')
#首页路由
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

"""
记录访问日志
连接数据库
查询所有实验记录，按日期降序排序
渲染index.html模板，传递试验记录数据
如果查询失败，返回错误信息
"""

@app.route('/add', methods=['GET', 'POST'])
#实验记录路由
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
                (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes, report)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                  """
            report = request.form.get('report')
            values = (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes, report)
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

"""
POST 请求处理（提交表单）
从表单获取数据
连接数据库
执行INSERT语句（插入）
提交事务
重定向到首页
GET请求 显示添加到表单页面
"""

@app.route('/delete/<int:exp_id>', methods=['POST'])
#删除路由
def delete(exp_id):
    #获取前端传来的密码
    password = request.form.get('password','')
    if password != ADMIN_PASSWORD:
        logger.warning(f"尝试删除记录 ID={exp_id} 但密码错误")
        flash('密码错误删除失败','danger')
        #返回错误页面
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        logger.error(f"删除实验 ID={exp_id} 时数据库连接失败")
        return "数据库连接失败"
    with conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM experiments WHERE id = %s", (exp_id,))
            conn.commit()
            logger.info(f"成功删除实验记录 ID={exp_id}")
        except Error as e:
            conn.rollback()
            logger.exception(f"删除实验 ID={exp_id} 时发生异常: {e}")
            return f"删除失败: {e}"
        finally:
            conn.close()
    flash('记录已删除','danger')
    return redirect(url_for('index'))

"""
RESTful路由设计
参数化查询防止SQL注入
完整的事务处理
详细的日志记录
错误处理机制
代码结构清晰
"""

@app.route('/edit/<int:exp_id>', methods=['GET', 'POST'])
#编辑路由
def edit(exp_id):
    """编辑试验记录"""
    conn = get_db_connection()
    if not conn:
        logger.error(f"编辑实验 ID={exp_id} 时数据库连接失败")
        return "数据库连接失败"

    if request.method == 'POST':
        #获取表单数据
        exp_name = request.form['exp_name']
        exp_date = request.form['exp_date']
        attacker_ip = request.form['attacker_ip']
        target_ip = request.form['target_ip']
        gateway_ip = request.form['gateway_ip']
        success = True if request.form.get('success') else False
        notes = request.form['notes']

        with conn.cursor() as cursor:
            report = request.form.get('report')
            sql = """
                UPDATE experiments
                SET exp_name = %s, exp_date = %s, attacker_ip = %s, target_ip = %s, gateway_ip = %s, success = %s, notes = %s, report = %s
                WHERE id=%s
            """
            values = (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes, report, exp_id)
            try:
                cursor.execute(sql, values)
                conn.commit()
                logger.info(f"成功更新实验记录 ID={exp_id}，新数据：{exp_name} / {exp_date}")
            except Error as e:
                conn.rollback()
                logger.exception(f"更新实验 ID={exp_id} 时发生异常: {e}")
                return f"更新失败: {e}"
            finally:
                conn.close()
        return redirect(url_for('index'))

    else:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM experiments WHERE id = %s", (exp_id,))
            exp = cursor.fetchone()
        conn.close()
        if not exp:
            logger.warning(f"尝试编辑不存在的实验记录 ID={exp_id}")
            return "记录不存在", 404
        logger.debug(f"加载编辑表单 ID={exp_id}")
        return render_template('edit.html', exp=exp)

"""
查看：首页列表
添加：新增记录
编辑：修改现有记录
删除：移除记录
"""

@app.route('/detail/<int:exp_id>')
#详情页路由
def detail(exp_id):
    """显示单条试验记录的详细信息"""
    conn = get_db_connection()
    if not conn:
        return "数据库连接失败"
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM experiments WHERE id = %s", (exp_id,))
        exp = cursor.fetchone()
    conn.close()
    if not exp:
        return "记录不存在", 404
    return render_template('detail.html', exp=exp)

"""
查看单条试验记录的完整信息
GET请求，通过ID查询单挑记录
简洁的只读展示页面
"""

@app.route('/search')
#搜寻路由
def search():
    q = request.args.get('q','').strip()
    if not q:
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        logger.error("搜索时连接数据库失败")
        return "数据库连接失败"

    with conn.cursor() as cursor:
        #使用LIKE模糊匹配多个字段
        sql = """
            SELECT * FROM experiments
            WHERE exp_name LIKE %s OR notes LIKE %s OR report LIKE %s
            ORDER BY exp_date DESC  
        """
        like_term = f"%{q}%"
        try:
            cursor.execute(sql, (like_term, like_term, like_term))
            experiments = cursor.fetchall()
            logger.info(f"搜索关键词 '{q}',找到{len(experiments)}条记录")
        except Error as e:
            logger.exception("搜索时发生异常")
            experiments = []
        finally:
            conn.close()
    return render_template('index.html', experiments=experiments, search_query=q)

"""
全文搜索，支持多个字段模糊匹配
GET请求，LIKE模糊查询
多字段搜索，结果按日期排序
"""


if __name__ == '__main__':
    app.run(debug=True) #启用调试模式
