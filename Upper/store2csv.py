import json
import csv
import os
import time
from datetime import datetime

# 配置参数
JSON_FILE = './info.json'      # JSON文件路径
CSV_FILE = './info.csv'   # CSV文件路径
FIELDS = [
    "device_id",
    "timestamp",
    "status_code",
    "status_text",
    "is_alert",
    "blink_count",
    "yawn_count",
    "head_nod_count"
]

def initialize_csv():
    """初始化CSV文件，写入表头"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
            writer.writeheader()
            print(f"初始化CSV文件: {CSV_FILE}")

def append_to_csv(data):
    """将单条数据追加到CSV文件"""
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writerow(data)
        print(f"已追加数据到CSV: {data['timestamp']}")

def monitor_json(interval=2.0):
    """监控JSON文件，定期读取并追加到CSV"""
    initialize_csv()
    last_modified = os.path.getmtime(JSON_FILE) if os.path.exists(JSON_FILE) else 0
    print(f"开始监控JSON文件: {JSON_FILE}, 初始修改时间: {datetime.fromtimestamp(last_modified)}")
    
    try:
        while True:
            current_modified = os.path.getmtime(JSON_FILE)
            if current_modified > last_modified:
                last_modified = current_modified
                try:
                    with open(JSON_FILE, 'r', encoding='utf-8') as f:
                        new_data = json.load(f)
                    append_to_csv(new_data)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                except Exception as e:
                    print(f"读取JSON文件时出错: {e}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n监控已停止。")

if __name__ == "__main__":
    monitor_json(interval=2.0)