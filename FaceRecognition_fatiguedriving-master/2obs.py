import json
import time
import os
import logging
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkobs.obs.client import ObsClient

class OBSUploader:
    """
    将本地JSON文件上传到华为云OBS（适配SDK 3.x版本）
    """
    
    def __init__(self, config: dict):
        """
        :param config: 包含ak, sk, endpoint, bucket_name
        """
        # 修改为（3.1.50版本）
        self.client = ObsClient(
          access_key_id=config['ak'],
          secret_access_key=config['sk'],
          server=config['endpoint']
        )
        self.bucket_name = config['bucket_name']
        self.folder = config.get('folder', 'fatigue_data/')
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('obs_uploader.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def upload_file(self, local_path: str) -> bool:
        """
        上传本地文件到OBS（SDK 3.x版本）
        :param local_path: 本地文件路径
        :return: 是否成功
        """
        try:
            # 验证文件存在
            if not os.path.exists(local_path):
                self.logger.error(f"File not found: {local_path}")
                return False
            
            # 读取文件内容
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 生成OBS对象键
            timestamp = data.get('timestamp', time.strftime("%Y-%m-%d_%H-%M-%S"))
            object_key = f"{self.folder}fatigue_{data.get('device_id', 'unknown')}_{timestamp.replace(':', '-')}.json"
            
            # 修改后（3.1.75版本方式）
            response = self.client.putObject(
              bucketName=self.bucket_name,
              objectKey=object_key,
              body=json.dumps(data, ensure_ascii=False)
            )
            
         
            
            if response.status < 300:
                self.logger.info(f"Successfully uploaded to obs://{self.bucket_name}/{object_key}")
                return True
            else:
                self.logger.error(f"Upload failed with status {response.status}: {response.reason}")
                return False
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Upload error: {str(e)}", exc_info=True)
            return False
    
    def monitor_and_upload(self, local_path: str, interval: float = 5.0):
        """
        监控本地文件变化并上传
        :param local_path: 要监控的本地文件路径
        :param interval: 检查间隔(秒)
        """
        last_modified = 0
        
        self.logger.info(f"Starting monitoring on {local_path}")
        self.logger.info(f"Target OBS location: obs://{self.bucket_name}/{self.folder}")
        
        try:
            while True:
                try:
                    current_modified = os.path.getmtime(local_path)
                    
                    if current_modified > last_modified:
                        self.logger.debug(f"Detected file modification at {time.ctime(current_modified)}")
                        
                        if self.upload_file(local_path):
                            last_modified = current_modified
                        else:
                            self.logger.warning("Upload failed, will retry after interval")
                    
                    time.sleep(interval)
                
                except FileNotFoundError:
                    self.logger.warning(f"File not found, retrying in {interval}s...")
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Monitoring error: {str(e)}", exc_info=True)
                    time.sleep(min(60, interval * 2))  # 错误时增加等待时间
                    
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.client.close()

if __name__ == "__main__":
    # 配置示例（实际应从环境变量或安全配置读取）
    OBS_CONFIG = {
        'ak': os.getenv('OBS_AK', 'HPUAEO42TXTDVUNMLVKF'),
        'sk': os.getenv('OBS_SK', 'jYNuSBCtlkryRcR58bidAVNd4y3vGgN8EER9anbs'),
        'endpoint': os.getenv('OBS_ENDPOINT', 'https://obs.cn-east-3.myhuaweicloud.com'),
        'bucket_name': os.getenv('OBS_BUCKET', 'obsmausmaus'),
        'folder': os.getenv('OBS_FOLDER', 'fatigue_data/')
    }
    
    # 安全警告检查
    if OBS_CONFIG['ak'].startswith('your-'):
        logging.warning("Using placeholder credentials! Replace with actual credentials in production.")
    
    uploader = OBSUploader(OBS_CONFIG)
    
    # 监控本地文件（示例路径，按需修改）
    DATA_FILE = os.path.join(os.path.dirname(__file__), './fatigue_data.json')
    uploader.monitor_and_upload(DATA_FILE, interval=10.0)
