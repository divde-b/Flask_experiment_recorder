"""
路由文件，蓝图
"""

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from pymysql import Error
from database import get_db_connection
import logging


logger = logging.getLogger(__name__)

experiments_bp = Blueprint('experiments', __name__, url_prefix='')


@experiments_bp.route('/')
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

@experiments_bp.route('/add', methods=['GET', 'POST'])
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
            return redirect(url_for('experiments.index'))
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

@experiments_bp.route('/delete/<int:exp_id>', methods=['POST'])
#删除路由
def delete(exp_id):
    #获取前端传来的密码
    password = request.form.get('password','')
    if password != current_app.config['ADMIN_PASSWORD']:
        logger.warning(f"尝试删除记录 ID={exp_id} 但密码错误")
        flash('密码错误删除失败','danger')
        #返回错误页面
        return redirect(url_for('experiments.index'))

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
    flash('记录已删除','success')
    return redirect(url_for('experiments.index'))
"""
RESTful路由设计
参数化查询防止SQL注入
完整的事务处理
详细的日志记录
错误处理机制
代码结构清晰
"""

@experiments_bp.route('/edit/<int:exp_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('experiments.index'))

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

@experiments_bp.route('/detail/<int:exp_id>')
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

@experiments_bp.route('/search')
#搜寻路由
def search():
    q = request.args.get('q','').strip()
    if not q:
        return redirect(url_for('experiments.index'))

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