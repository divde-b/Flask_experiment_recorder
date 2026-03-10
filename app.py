from flask import Flask, render_template, request, redirect, url_for
import pymysql
from pymysql import Error
from pymysql.cursors import DictCursor

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
    conn = get_db_connection()
    if not conn:
        return "数据库连接失败，请检查配置。"
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM experiments ORDER BY exp_date DESC")
        experiments = cursor.fetchall()
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
            except Error as e:
                conn.rollback()
                return f"插入失败: {e}"
            conn.close()
            return redirect(url_for('index'))
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)
