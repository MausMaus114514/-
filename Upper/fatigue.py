import json
import random
import time
import os
from datetime import datetime
from typing import Dict

class FatigueDataSimulator:
    def __init__(self, device_id: str = "simulated_device_001"):
        """
        初始化模拟器
        :param device_id: 模拟设备ID
        """
        self.device_id = device_id
        self.status_map = {
            0: "正常",
            1: "轻微疲劳",
            2: "瞌睡"
        }
        # 状态转移概率矩阵 [当前状态][下一状态]
        self.transition_matrix = [
            [0.7, 0.25, 0.05],  # 从"正常"转移的概率
            [0.4, 0.4, 0.2],    # 从"轻微疲劳"转移的概率
            [0.1, 0.3, 0.6]     # 从"瞌睡"转移的概率
        ]
        self.current_status = 0  # 初始状态为"正常"

    def generate_status(self) -> int:
        """使用马尔可夫链模拟状态变化"""
        r = random.random()
        cumulative = 0.0
        for next_status, prob in enumerate(self.transition_matrix[self.current_status]):
            cumulative += prob
            if r < cumulative:
                self.current_status = next_status
                break
        return self.current_status

    def generate_data(self) -> Dict:
        """生成一条模拟数据"""
        status_code = self.generate_status()
        return {
            "device_id": self.device_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # 保留毫秒
            "status_code": status_code,
            "status_text": self.status_map[status_code],
            "is_alert": status_code >= 1,
            "blink_count": random.randint(0, 30) if status_code > 0 else random.randint(0, 10),
            "yawn_count": random.randint(0, 5) if status_code > 0 else random.randint(0, 2),
            "head_nod_count": random.randint(0, 8) if status_code > 0 else random.randint(0, 3)
        }

    def simulate_to_file(self, output_path: str, interval: float = 2.0, max_records: int = 100):
        """
        持续生成模拟数据并写入文件
        :param output_path: 输出文件路径
        :param interval: 生成间隔(秒)
        :param max_records: 最大生成条数
        """
        count = 0
        print(f"Starting fatigue data simulation. Outputting to: {output_path}")
        print("Press Ctrl+C to stop...")

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                while count < max_records:
                    data = self.generate_data()
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write('\n')  # 每条记录单独一行
                    count += 1
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")

if __name__ == "__main__":
    # 示例用法
    simulator = FatigueDataSimulator(device_id="simulated_driver_001")
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "info.json")
    
    # 每2秒生成一条数据，总共生成100条
    simulator.simulate_to_file(output_file, interval=2.0, max_records=100)