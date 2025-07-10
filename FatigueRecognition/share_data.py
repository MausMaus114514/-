# share_data.py
import multiprocessing

class SharedData:
    def __init__(self):
        self.fatigue_status = multiprocessing.Value('i', 0)  # 0:正常, 1:轻微疲劳, 2:瞌睡
        self.lock = multiprocessing.Lock()
    
    def update_status(self, status):
        with self.lock:
            if status == "正常":
                self.fatigue_status.value = 0
            elif status == "轻微疲劳":
                self.fatigue_status.value = 1
            elif status == "瞌睡":
                self.fatigue_status.value = 2
    
    def get_status(self):
        with self.lock:
            return self.fatigue_status.value
        
# 创建全局共享实例
shared_data = SharedData()