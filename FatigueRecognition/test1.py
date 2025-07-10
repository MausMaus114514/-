from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlitecloud
from datetime import datetime, timezone
import pytz

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# SQLiteCloud连接配置
SQLITECLOUD_URL = "sqlitecloud://cd4niyefhk.g2.sqlite.cloud:8860/face-detection.db?apikey=fOB0qUqiLGWK1y8AU2W0NnNQGv2OXajLGg35bO2It8o"


# 创建数据库连接
def get_db_connection():
    try:
        conn = sqlitecloud.connect(SQLITECLOUD_URL)
        conn.row_factory = sqlitecloud.Row  # 返回字典形式的结果
        return conn
    except Exception as e:
        print(f"Error connecting to SQLiteCloud: {e}")
        raise


# 创建表（如果不存在）
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FatigueData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT '1',
            fatigue_level INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device_info TEXT
        )
    ''')
    conn.commit()
    conn.close()


# 上传疲劳检测结果
@app.route('/api/upload', methods=['POST'])
def upload_fatigue_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user_id = data.get('user_id', '1')
    fatigue_level = data.get('fatigue_level')
    device_info = data.get('device_info')

    # 使用UTC时间
    timestamp = datetime.now(timezone.utc).isoformat()

    if fatigue_level is None:
        return jsonify({"error": "fatigue_level is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO FatigueData (user_id, fatigue_level, timestamp, device_info)
               VALUES (?, ?, ?, ?)''',
            (user_id, fatigue_level, timestamp, device_info)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({"message": "Data uploaded successfully", "id": new_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# 获取疲劳预警信息
@app.route('/api/warnings', methods=['GET'])
def get_warnings():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''SELECT * FROM FatigueData 
               WHERE fatigue_level = 1 
               ORDER BY timestamp DESC'''
        )
        warnings = cursor.fetchall()

        result = []
        for row in warnings:
            # 将UTC时间转换为本地时间
            utc_time = datetime.fromisoformat(row['timestamp'])
            local_timezone = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(local_timezone)

            result.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'fatigue_level': row['fatigue_level'],
                'timestamp': local_time.strftime('%Y-%m-%d %H:%M:%S'),
                'device_info': row['device_info']
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# 获取疲劳警报信息
@app.route('/api/alarms', methods=['GET'])
def get_alarms():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''SELECT * FROM FatigueData 
               WHERE fatigue_level >= 2 
               ORDER BY timestamp DESC'''
        )
        alarms = cursor.fetchall()

        result = []
        for row in alarms:
            # 将UTC时间转换为本地时间
            utc_time = datetime.fromisoformat(row['timestamp'])
            local_timezone = pytz.timezone('Asia/Shanghai')
            local_time = utc_time.replace(tzinfo=timezone.utc).astimezone(local_timezone)

            result.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'fatigue_level': row['fatigue_level'],
                'timestamp': local_time.strftime('%Y-%m-%d %H:%M:%S'),
                'device_info': row['device_info']
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    # 启动时创建表
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)