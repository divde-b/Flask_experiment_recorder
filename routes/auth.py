from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from pymysql import Error
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.register'))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('用户名已存在', 'danger')
                conn.close()
                return redirect(url_for('auth.register'))

            password_hash = generate_password_hash(password)
            try:
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
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')  #获取‘记住我’复选框的值

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            if remember:
                session['remember'] = True
            logger.info(f"用户{username}登录成功")
            flash('登录成功', 'success')
            return redirect(url_for('experiments.index'))
        else:
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """用户登出"""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('已退出登录', 'info')
    return redirect(url_for('experiments.index'))