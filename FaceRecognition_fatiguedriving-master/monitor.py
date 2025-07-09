# monitor.py
import json
import time
import os
from datetime import datetime
from share_data import SharedData

class FatigueMonitor:
    def __init__(self, device_id="default_device"):
        """
        初始化疲劳监控器
        :param device_id: 设备/驾驶员ID
        """
        self.device_id = device_id
        self.shared_data = SharedData()
        self.status_map = {
            0: "正常",
            1: "轻微疲劳",
            2: "瞌睡"
        }
    
    def generate_data(self):
        """
        生成当前疲劳数据
        :return: 包含时间戳和状态的字典
        """
        status_code = self.shared_data.get_status()
        return {
            "device_id": self.device_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status_code": status_code,
            "status_text": self.status_map.get(status_code, "未知状态"),
            "is_alert": status_code >= 1  # 是否警报状态
        }
    
    def monitor_to_file(self, output_path: str, interval: float = 1.0, max_records: int = None):
        """
        持续监控并将数据写入JSON文件
        :param output_path: 输出文件路径
        :param interval: 检查间隔(秒)
        :param max_records: 最大记录条数,None表示无限
        """
        count = 0
        print(f"Starting fatigue monitoring. Outputting to: {output_path}")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                if max_records and count >= max_records:
                    break
                
                data = self.generate_data()
                
                # 写入JSON文件(每次覆盖)
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # 控制台输出状态信息
                if data["status_code"] == 1:
                    print(f"[警告] {data['timestamp']} 检测到轻微疲劳状态")
                elif data["status_code"] == 2:
                    print(f"[警报] {data['timestamp']} 检测到瞌睡状态！")
                
                count += 1
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
    
    def monitor_continuous(self, interval: float = 1.0):
        """
        持续监控并在控制台输出(不写入文件)
        :param interval: 检查间隔(秒)
        """
        print("Starting continuous fatigue monitoring...")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                data = self.generate_data()
                
                if data["status_code"] == 1:
                    print(f"[警告] {data['timestamp']} 检测到轻微疲劳状态")
                elif data["status_code"] == 2:
                    print(f"[警报] {data['timestamp']} 检测到瞌睡状态！")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    # 示例用法
    monitor = FatigueMonitor(device_id="driver_001")
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "./fatigue.json")
    
    # 方式1: 监控并写入文件(每1秒检查一次)
    monitor.monitor_to_file(output_file, interval=1.0)
    
    # 方式2: 仅控制台监控(不写入文件)
    # monitor.monitor_continuous(interval=1.0)

#JSON消息格式示例：
#    {
#      "device_id": "driver_001",
#      "timestamp": "2023-11-15 14:30:45",
#      "status_code": 2,
#      "status_text": "瞌睡",
#      "is_alert": true
#    }