"""
实验记录管理蓝图
包含实验记录的增删改查、搜索、详情页展示功能。
所有路由都挂载在 / 路径下（无前缀）。
"""

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from pymysql import Error
from database import get_db_connection
import logging
from functools import wraps


logger = logging.getLogger(__name__)

#创建蓝图实例，url_pre==erfix=''表示无前缀，即路由直接挂载在根路径
experiments_bp = Blueprint('experiments', __name__, url_prefix='')

#登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录','warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@experiments_bp.route('/')
@login_required
def index():
    """
    显示所有试验记录，按日期倒序排序。
    如果数据库连接失败，返回错误提示信息
    :return:
    """
    user_id = session.get('user_id')
    connection = get_db_connection()
    logger.info("访问首页")
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败")
        return "数据库连接失败，请检查配置。"
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM experiments WHERE user_id = %s ORDER BY exp_date DESC", (user_id,))
            experiments = cursor.fetchall()
            logger.debug(f"查询到 {len(experiments)} 条记录")
        except Error as e:
            logger.exception("查询实验记录时发生异常")
            return "查询失败"
    conn.close()
    return render_template('index.html', experiments=experiments)

@experiments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    添加新实验记录
    GET:显示表单页面
    POST:获取表单数据，插入数据库，成功后重定向到首页。
    :return:
    """
    if request.method == 'POST':
        #获取表单数据（使用.get（）避免缺少字段报错）
        exp_name = request.form['exp_name']
        exp_date = request.form['exp_date']
        attacker_ip = request.form['attacker_ip']
        target_ip = request.form['target_ip']
        gateway_ip = request.form['gateway_ip']
        success = True if request.form.get('success') else False
        notes = request.form['notes']
        report = request.form.get('report','')  #实验报告（Markdown）

        user_id = session['user_id']

        conn = get_db_connection()
        if not conn:
            return "数据库连接失败"
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO experiments 
                (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes, report, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                  """
            report = request.form.get('report')
            values = (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes, report, user_id)
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
    #GET请求：显示添加表单
    return render_template('add.html')

@experiments_bp.route('/delete/<int:exp_id>', methods=['POST'])
@login_required
def delete(exp_id):
    """
    删除试验记录（需要提供管理员密码）
    前端通过隐藏表单提交密码，后端验证后执行删除。
    :param exp_id:
    :return:
    """
    user_id = session['user_id']
    #获取前端传来的密码
    """
    password = request.form.get('password','')
    if password != current_app.config['ADMIN_PASSWORD']:
        logger.warning(f"尝试删除记录 ID={exp_id} 但密码错误")
        flash('密码错误删除失败','danger')
        #返回错误页面
        return redirect(url_for('experiments.index'))
    """
    conn = get_db_connection()
    if not conn:
        logger.error(f"删除实验 ID={exp_id} 时数据库连接失败")
        return "数据库连接失败"
    with conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM experiments WHERE id = %s AND user_id = %s", (exp_id,user_id))
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

@experiments_bp.route('/edit/<int:exp_id>', methods=['GET', 'POST'])
@login_required
def edit(exp_id):
    """
    编辑试验记录
    GET: 根据ID查询现有数据并填充表单
    POST: 更新数据库
    :param exp_id:
    :return:
    """
    user_id = session['user_id']
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
                WHERE id= %s AND user_id = %s
            """
            values = (exp_name, exp_date, attacker_ip, target_ip, gateway_ip, success, notes, report, exp_id, user_id)
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

    else:  #GET请求
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM experiments WHERE id = %s AND user_id = %s", (exp_id,user_id))
            exp = cursor.fetchone()
        conn.close()
        if not exp:
            logger.warning(f"尝试编辑不存在的实验记录 ID={exp_id}")
            return "记录不存在", 404
        logger.debug(f"加载编辑表单 ID={exp_id}")
        return render_template('edit.html', exp=exp)

@experiments_bp.route('/detail/<int:exp_id>')
@login_required
def detail(exp_id):
    """
    显示单条试验记录的详细信息
    包括所有字段，实验报告呢欧容使用Markdown渲染
    :param exp_id:
    :return:
    """
    user_id = session['user_id']
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

@experiments_bp.route('/search')
@login_required
def search():
    """
    搜索试验记录（模糊匹配）
    支持在实验名称、备注、报告内容中查找关键词
    搜索结果干日期倒叙排序。
    :return:
    """
    user_id = session['user_id']
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
            WHERE (exp_name LIKE %s OR notes LIKE %s OR report LIKE %s) AND user_id = %s
            ORDER BY exp_date DESC
        """
        like_term = f"%{q}%"
        try:
            cursor.execute(sql, (like_term, like_term, like_term, user_id))
            experiments = cursor.fetchall()
            logger.info(f"搜索关键词 '{q}',找到{len(experiments)}条记录")
        except Error as e:
            logger.exception("搜索时发生异常")
            experiments = []
        finally:
            conn.close()
    return render_template('index.html', experiments=experiments, search_query=q)
