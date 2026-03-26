"""
用户认证蓝图（auth）
处理用户注册、登录、登出功能没使用wekzeug进行密码哈希，
通过 session 维护登录状态
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from pymysql import Error
import logging

logger = logging.getLogger(__name__)

# 创建蓝图实例，所有前缀为 /auth
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册
    GET：显示注册表单
    POST：处理注册请求，验证数据、检查用户名唯一性，密码哈希后存入数据库
    :return:
    """
    if request.method == 'POST':
        # 获取表单数据，去除用户名首尾空格
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        # 简单验证，用户名和密码不能为空
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('auth.register'))

        # 验证两次密码是否一致
        if password != confirm:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.register'))

        #连接数据库
        conn = get_db_connection()
        with conn.cursor() as cursor:
            #检查用户名是否存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('用户名已存在', 'danger')
                conn.close()
                return redirect(url_for('auth.register'))
            #生成密码哈希（安全存储）
            password_hash = generate_password_hash(password)
            try:
                # 插入新用户
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                               (username, password_hash))
                conn.commit()
                logger.info(f"新用户注册：{username}")
                flash('注册成功，请登录', 'success')
                return redirect(url_for('auth.login'))
            except Error as e:
                conn.rollback()
                logger.exception(f"新用户{username}注册失败：{e}")
                flash('注册失败，请稍后重试', 'danger')
                return redirect(url_for('auth.register'))
            finally:
                conn.close()
    # GET 请求时返回注册页面
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    GET：显示登录表单
    POST:验证用户名和密码，成功则写入 session，可选“记住我”功能
    :return:
    """
    if request.method == 'POST':
        #获取表单数据
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')  #获取‘记住我’复选框的值

        # 连接数据库查询用户
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        conn.close()

        # 验证用户存在且密码正确
        if user and check_password_hash(user['password_hash'], password):
            # 写入session，记录用户登录状态
            session['user_id'] = user['id']
            session['username'] = username
            # 如果勾选了“记住我”，可设置session为永久
            if remember:
                session['remember'] = True
            logger.info(f"用户{username}登录成功")
            flash('登录成功', 'success')
            return redirect(url_for('experiments.index'))
        else:
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))
    # GET 请求时返回登录页面
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """
    用户登出
    清除session中的用户信息，并提示已退出
    :return:
    """
    session.pop('user_id', None)# 移除user_id，即使不存在也不报错
    session.pop('username', None)# 移除username
    flash('已退出登录', 'info')
    return redirect(url_for('experiments.index'))