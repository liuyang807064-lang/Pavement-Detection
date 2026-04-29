from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from pymysql.cursors import DictCursor
import re

app = Flask(__name__)
app.secret_key = 'graduation-design-secret-key'

# 数据库连接配置
DB_CONFIG = {
    'host': '101.200.144.25',
    'port': 3306,
    'user': 'liuyang',
    'password': '123456',
    'database': 'graduation_design',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def is_mobile_device(user_agent):
    """检测是否为移动设备"""
    mobile_patterns = [
        'Android',
        'iPhone',
        'iPad',
        'Mobile',
        'BlackBerry',
        'Windows Phone',
        'Opera Mini',
        'IEMobile',
        'Touch',
        'Mobi'
    ]
    
    user_agent = user_agent.lower()
    return any(pattern.lower() in user_agent for pattern in mobile_patterns)

@app.route('/')
def index():
    """首页路由 - 自动检测设备并跳转"""
    user_agent = request.headers.get('User-Agent', '')
    
    if is_mobile_device(user_agent):
        # 如果是移动设备，跳转到手机端页面
        return redirect(url_for('mobile_index'))
    else:
        # 如果是桌面设备，显示桌面版首页
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录功能"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, password))
                user = cursor.fetchone()
                
                if user:
                    session['username'] = username
                    session['is_admin'] = user['is_admin']
                    flash('登录成功！', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('用户名或密码错误！', 'error')
        except Exception as e:
            flash(f'数据库错误：{str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册功能"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('两次输入的密码不一致！', 'error')
            return render_template('index.html')
        
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # 检查用户名是否已存在
                check_sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(check_sql, (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    flash('用户名已存在！', 'error')
                else:
                    # 插入新用户
                    insert_sql = "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, 0)"
                    cursor.execute(insert_sql, (username, password))
                    conn.commit()
                    flash('注册成功！请登录。', 'success')
                    return redirect(url_for('index'))
        except Exception as e:
            flash(f'数据库错误：{str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('index.html')

@app.route('/logout')
def logout():
    """退出登录"""
    session.pop('username', None)
    flash('已退出登录！', 'info')
    return redirect(url_for('index'))

@app.route('/realtime-detection')
def realtime_detection():
    """实时路面检测与预警页面"""
    return render_template('realtime_detection.html')

@app.route('/models/<path:filename>')
def serve_model_files(filename):
    """提供模型文件访问"""
    from flask import send_from_directory
    return send_from_directory('models', filename)

@app.route('/map-view')
def map_view():
    """路面风险点地图页面"""
    return render_template('map_view.html')

@app.route('/statistics')
def statistics():
    """历史数据统计分析页面"""
    return render_template('statistics.html')

@app.route('/mobile')
def mobile_index():
    """手机端专用首页"""
    return render_template('mobile_index.html')

@app.route('/api/risks', methods=['GET'])
def get_risk_points():
    """获取所有已提交的路面风险点数据"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM road_risks WHERE is_submitted = 1"
            cursor.execute(sql)
            risks = cursor.fetchall()
            
            # 转换为列表
            risk_list = []
            for risk in risks:
                risk_list.append({
                    'id': risk['id'],
                    'latitude': float(risk['latitude']),
                    'longitude': float(risk['longitude']),
                    'risk_type': risk['risk_type']
                })
            
            return {'success': True, 'data': risk_list}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

@app.route('/api/risks/add', methods=['POST'])
def add_risk_point():
    """添加新的风险点"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        risk_type = data.get('risk_type')
        
        if not latitude or not longitude or not risk_type:
            return {'success': False, 'message': '参数不完整'}
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO road_risks (latitude, longitude, risk_type) VALUES (%s, %s, %s)"
            cursor.execute(sql, (latitude, longitude, risk_type))
            conn.commit()
            
            return {'success': True, 'message': '添加成功', 'id': cursor.lastrowid}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

@app.route('/api/statistics/summary', methods=['GET'])
def get_statistics_summary():
    """获取统计数据摘要"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 总数量
            cursor.execute("SELECT COUNT(*) as total FROM road_risks WHERE is_submitted = 1")
            total = cursor.fetchone()['total']
            
            # 按类型统计
            cursor.execute("""
                SELECT risk_type, COUNT(*) as count 
                FROM road_risks 
                WHERE is_submitted = 1 
                GROUP BY risk_type
            """)
            type_stats = cursor.fetchall()
            
            # 按日期统计 (最近 7 天)
            cursor.execute("""
                SELECT DATE(detection_time) as date, COUNT(*) as count 
                FROM road_risks 
                WHERE is_submitted = 1 
                AND detection_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(detection_time)
                ORDER BY date
            """)
            daily_stats = cursor.fetchall()
            
            return {
                'success': True,
                'data': {
                    'total': total,
                    'type_stats': type_stats,
                    'daily_stats': daily_stats
                }
            }
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

@app.route('/api/statistics/recent', methods=['GET'])
def get_recent_risks():
    """获取最近的检测记录"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, latitude, longitude, risk_type, detection_time 
                FROM road_risks 
                WHERE is_submitted = 1 
                ORDER BY detection_time DESC 
                LIMIT 50
            """)
            risks = cursor.fetchall()
            
            risk_list = []
            for risk in risks:
                risk_list.append({
                    'id': risk['id'],
                    'latitude': float(risk['latitude']),
                    'longitude': float(risk['longitude']),
                    'risk_type': risk['risk_type'],
                    'detection_time': risk['detection_time'].strftime('%Y-%m-%d %H:%M:%S') if risk['detection_time'] else ''
                })
            
            return {'success': True, 'data': risk_list}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

@app.route('/report')
def report_form():
    """危险路段上报页面"""
    return render_template('report_form.html')

@app.route('/api/report/submit', methods=['POST'])
def submit_report():
    """提交风险点上报"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        risk_type = data.get('risk_type')
        risk_level = data.get('risk_level', 'medium')
        description = data.get('description', '')
        contact = data.get('contact', '')
        
        if not latitude or not longitude or not risk_type:
            return {'success': False, 'message': '参数不完整'}
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 插入新的风险点，is_submitted 默认为 0（待审核）
            sql = """INSERT INTO road_risks 
                    (latitude, longitude, risk_type, risk_level, description, contact, is_submitted) 
                    VALUES (%s, %s, %s, %s, %s, %s, 0)"""
            cursor.execute(sql, (latitude, longitude, risk_type, risk_level, description, contact))
            conn.commit()
            
            return {'success': True, 'message': '上报成功，等待审核', 'id': cursor.lastrowid}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

@app.route('/api/report/history', methods=['GET'])
def get_report_history():
    """获取用户的上报历史记录"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 如果用户已登录，只获取该用户的记录
            # 目前简化处理，获取所有记录（实际应该根据用户 ID 过滤）
            sql = """SELECT id, latitude, longitude, risk_type, risk_level, 
                           description, contact, is_submitted, detection_time 
                    FROM road_risks 
                    ORDER BY detection_time DESC 
                    LIMIT 50"""
            cursor.execute(sql)
            risks = cursor.fetchall()
            
            risk_list = []
            for risk in risks:
                risk_list.append({
                    'id': risk['id'],
                    'latitude': float(risk['latitude']),
                    'longitude': float(risk['longitude']),
                    'risk_type': risk['risk_type'],
                    'risk_level': risk.get('risk_level', 'medium'),
                    'description': risk.get('description', ''),
                    'contact': risk.get('contact', ''),
                    'is_submitted': risk['is_submitted'],
                    'detection_time': risk['detection_time'].strftime('%Y-%m-%d %H:%M:%S') if risk['detection_time'] else ''
                })
            
            return {'success': True, 'data': risk_list}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

@app.route('/admin/review')
def admin_review():
    """管理员审核页面"""
    # TODO: 添加管理员权限验证
    # if not session.get('is_admin'):
    #     flash('需要管理员权限', 'error')
    #     return redirect(url_for('login'))
    return render_template('admin_review.html')

@app.route('/api/report/approve/<int:report_id>', methods=['POST'])
def approve_report(report_id):
    """审核上报数据（通过/拒绝）"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'reject'
        
        if action not in ['approve', 'reject']:
            return {'success': False, 'message': '无效的操作'}
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if action == 'approve':
                # 通过审核，设置 is_submitted = 1
                sql = "UPDATE road_risks SET is_submitted = 1 WHERE id = %s"
            else:
                # 拒绝，设置 is_submitted = -1
                sql = "UPDATE road_risks SET is_submitted = -1 WHERE id = %s"
            
            cursor.execute(sql, (report_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return {'success': True, 'message': f'操作成功：{"已通过" if action == "approve" else "已拒绝"}'}
            else:
                return {'success': False, 'message': '未找到对应的记录'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)