import json
import time
import os
import logging
import requests
from requests.auth import HTTPBasicAuth

class DataUploader:
    """
    将本地JSON文件上传到华为云平台的上位机
    """

    def __init__(self, config: dict):
        """
        :param config: 包含ak, sk, api_endpoint
        """
        self.ak = config.get('ak')
        self.sk = config.get('sk')
        self.api_endpoint = config.get('api_endpoint', ' http://192.168.x.x:5000/upload ')

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('data_uploader.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 验证配置
        if not self.ak or not self.sk:
            self.logger.error("AK 和 SK 必须在配置中提供。")
            raise ValueError("AK 和 SK 是必需的。")
        if not self.api_endpoint:
            self.logger.error("API Endpoint 必须在配置中提供。")
            raise ValueError("API Endpoint 是必需的。")

    def read_json_file(self, local_path: str) -> dict:
        """
        读取并解析本地JSON文件
        :param local_path: 本地文件路径
        :return: 解析后的JSON数据
        """
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"成功读取文件: {local_path}")
            return data
        except FileNotFoundError:
            self.logger.error(f"文件未找到: {local_path}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {str(e)}")
            return {}

    def send_to_upper_computer(self, data: dict) -> bool:
        """
        将数据发送到上位机API
        :param data: 要发送的数据
        :return: 是否成功
        """
        try:
            headers = {'Content-Type': 'application/json'}
            # 使用HTTPBasicAuth进行基本认证
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                data=json.dumps(data),
                auth=HTTPBasicAuth(self.ak, self.sk)
            )

            if response.status_code < 300:
                self.logger.info(f"成功发送数据到上位机API: {self.api_endpoint}")
                return True
            else:
                self.logger.error(
                    f"发送数据到上位机API失败，状态码: {response.status_code}, 响应: {response.text}"
                )
                return False

        except requests.RequestException as e:
            self.logger.error(f"请求异常: {str(e)}")
            return False

    def monitor_and_upload(self, local_path: str, interval: float = 10.0):
        """
        监控本地文件变化并上传
        :param local_path: 要监控的本地文件路径
        :param interval: 检查间隔(秒)
        """
        self.logger.info(f"开始监控文件: {local_path}")
        self.logger.info(f"目标上位机API: {self.api_endpoint}")
        self.logger.info(f"监控间隔: {interval} 秒")

        last_modified = 0

        try:
            while True:
                try:
                    current_modified = os.path.getmtime(local_path)

                    if current_modified > last_modified:
                        self.logger.debug(f"检测到文件修改: {time.ctime(current_modified)}")
                        
                        data = self.read_json_file(local_path)
                        if data:
                            success = self.send_to_upper_computer(data)
                            if success:
                                last_modified = current_modified
                            else:
                                self.logger.warning("上传失败，将在下次检查时重试。")
                        else:
                            self.logger.warning("读取到的数据为空，跳过上传。")
                    
                    time.sleep(interval)

                except FileNotFoundError:
                    self.logger.warning(f"文件未找到，将在 {interval} 秒后重试...")
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"监控错误: {str(e)}", exc_info=True)
                    time.sleep(min(60, interval * 2))  # 错误时增加等待时间

        except KeyboardInterrupt:
            self.logger.info("监控已由用户停止。")
        except Exception as e:
            self.logger.error(f"致命错误: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # 配置示例（实际应从环境变量或安全配置读取）
    UPLOAD_CONFIG = {
        'ak': os.getenv('UPLOAD_AK', 'HPUAEO42TXTDVUNMLVKF'),
        'sk': os.getenv('UPLOAD_SK', 'jYNuSBCtlkryRcR58bidAVNd4y3vGgN8EER9anbs'),
        'api_endpoint': os.getenv('UPLOAD_API_ENDPOINT', ' http://192.168.x.x:5000/upload ')    #  modify 此处填写上位机的ip，端口暂时维持5000
    }

    # 安全警告检查
    if UPLOAD_CONFIG['ak'].startswith('YOUR_ACTUAL'):
        logging.warning("使用占位符凭证！请在生产环境中替换为实际凭证。")

    uploader = DataUploader(UPLOAD_CONFIG)

    # 监控本地文件（示例路径，按需修改）
    DATA_FILE = os.path.join(os.path.dirname(__file__), './fatigue.json')
    uploader.monitor_and_upload(DATA_FILE, interval=10.0)