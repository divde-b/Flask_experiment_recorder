"""
文档管理蓝图
提供技术文档的增删改查和详情页展示功能
所有路由都挂载在 /docs 路径下。
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from pymysql import Error
from database import get_db_connection
import logging
from functools import wraps

logger = logging.getLogger(__name__)

docs_bp = Blueprint('docs', __name__, url_prefix='/docs')

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("请先登录", 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@docs_bp.route('/')
@login_required
def index():
    """显示当前用户的所有技术文档，按更新时间倒序排列"""
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败")
        return "数据库连接失败"
    with conn.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT id, title, created_at, updated_at
                FROM docs
                WHERE user_id = %s
                ORDER BY updated_at DESC
            """, (user_id,))
            docs = cursor.fetchall()
            logger.debug(f"查询到 {len(docs)} 条文档")
        except Error as e:
            logger.exception("查询文档列表时发生异常")
            docs = []
    conn.close()
    return render_template("docs/index.html", docs=docs)


@docs_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加新文档"""
    if request.method == "POST":
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title:
            flash('标题不能为空', 'danger')
            return redirect(url_for('docs.add'))

        user_id = session['user_id']
        conn = get_db_connection()
        if not conn:
            return "数据库连接失败"
        with conn.cursor() as cursor:
            # 修正：INSERT INFO -> INSERT INTO
            sql = "INSERT INTO `docs` (`title`, `content`, `user_id`) VALUES (%s, %s, %s)"
            try:
                cursor.execute(sql, (title, content, user_id))
                conn.commit()
                logger.info(f"新增文档：{title}")
                flash('文档添加成功', 'success')
                return redirect(url_for('docs.index'))
            except Error as e:
                conn.rollback()
                logger.exception("插入文档失败")
                flash('文档添加失败', 'danger')
            finally:
                conn.close()
    return render_template("docs/add.html")


@docs_bp.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def edit(doc_id):
    """编辑文档"""
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return "数据库连接失败"

    if request.method == "POST":
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title:
            flash('标题不能为空', 'danger')
            return redirect(url_for('docs.edit', doc_id=doc_id))

        with conn.cursor() as cursor:
            # 修正：参数顺序正确，WHERE 条件同时检查 id 和 user_id
            sql = "UPDATE `docs` SET title = %s, content = %s WHERE id = %s AND user_id = %s"
            try:
                cursor.execute(sql, (title, content, doc_id, user_id))
                conn.commit()
                if cursor.rowcount == 0:
                    flash('文档不存在或无权限编辑', 'danger')
                else:
                    logger.info(f"更新文档 ID={doc_id}")
                    flash("文档更新成功", "success")
                return redirect(url_for('docs.index'))
            except Error as e:
                conn.rollback()
                logger.exception(f"更新文档 ID={doc_id} 失败")
                flash("文档更新失败", "danger")
            finally:
                conn.close()
    else:
        # GET 请求：加载文档内容
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, content FROM docs WHERE id = %s AND user_id = %s", (doc_id, user_id))
            doc = cursor.fetchone()
        conn.close()
        if not doc:
            flash('文档不存在', 'danger')
            return redirect(url_for('docs.index'))
        return render_template("docs/edit.html", doc=doc)


@docs_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    """删除文档"""
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return "数据库连接失败"
    with conn.cursor() as cursor:
        try:
            # 修正：条件顺序与参数一致
            cursor.execute("DELETE FROM docs WHERE id = %s AND user_id = %s", (doc_id, user_id))
            conn.commit()
            if cursor.rowcount == 0:
                flash('文档不存在或无权删除', 'danger')
            else:
                logger.info(f"删除文档 ID={doc_id}")
                flash("文档已删除", "success")
        except Error as e:
            conn.rollback()
            logger.exception(f"删除文档 ID={doc_id} 失败")
            flash('删除失败', 'danger')
        finally:
            conn.close()
    return redirect(url_for('docs.index'))


@docs_bp.route('/detail/<int:doc_id>')
@login_required
def detail(doc_id):
    """文档详情页，使用 Markdown 渲染内容"""
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return "数据库连接失败"
    with conn.cursor() as cursor:
        # 修正：条件顺序与参数一致
        cursor.execute("SELECT id, title, content, created_at, updated_at FROM docs WHERE id = %s AND user_id = %s", (doc_id, user_id))
        doc = cursor.fetchone()
    conn.close()
    if not doc:
        flash('文档不存在', 'danger')
        return redirect(url_for('docs.index'))
    return render_template("docs/detail.html", doc=doc)


@docs_bp.route('/search')
@login_required
def search():
    """搜索文档：按标题或内容模糊匹配"""
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('docs.index'))

    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        logger.error("搜索时数据库连接失败")
        return "数据库连接失败"

    with conn.cursor() as cursor:
        # 修正：使用参数化查询，LIKE %s 不需要额外引号
        sql = """
            SELECT id, title, created_at, updated_at
            FROM docs
            WHERE user_id = %s AND (title LIKE %s OR content LIKE %s)
            ORDER BY updated_at DESC
        """
        like_term = f"%{q}%"
        try:
            cursor.execute(sql, (user_id, like_term, like_term))
            docs = cursor.fetchall()
            logger.info(f"搜索关键词 '{q}'，找到 {len(docs)} 条文档")
        except Error as e:
            logger.exception("搜索文档时发生异常")
            docs = []
        finally:
            conn.close()
    return render_template("docs/index.html", docs=docs, search_query=q)