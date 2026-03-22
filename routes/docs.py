"""
文档管理蓝图
提供技术文档的增删改查和详情页展示功能
所有路由都挂载在 /docs 路径下。
"""

from flask import Blueprint,render_template,request,session,redirect,url_for,flash
from pymysql import Error
from database import get_db_connection
import logging
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


logger = logging.getLogger(__name__)

docs_bp = Blueprint('docs',__name__,url_prefix='/docs')

#复用experiments中的login_required装饰器
#为了避免循环导入，直接在此处定义
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("请先登录",'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@docs_bp.route('/')
@login_required
def index():
    """显示当前用户的所有技术文档，按创建时间倒序排列"""
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败")
        return "数据库连接失败"
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT id, title, created_at, updated_at FROM docs WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            docs = cursor.fetchall()
            logger.debug(f"查询到{len(docs)}条文档")
        except Error as e:
            logger.exception("查询文档列表时发生异常")
            docs = []
    conn.close()
    return render_template("docs/index.html", docs=docs)
























