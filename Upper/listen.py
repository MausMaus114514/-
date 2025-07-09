from flask import Flask, request, jsonify
import json
import os
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_server.log')
    ]
)
logger = logging.getLogger(__name__)

# 定义保存JSON数据的文件路径
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE_PATH = os.path.join(UPLOAD_DIR, 'received_data.json')

@app.route('/upload', methods=['POST'])
def upload_data():
    """
    接收POST请求，解析JSON数据并保存到文件中。
    """
    logger.info("接收到上传请求。")
    try:
        # 检查请求是否包含JSON数据
        if not request.is_json:
            logger.error("请求中不包含JSON数据。")
            return jsonify({"error": "请求中不包含JSON数据"}), 400

        # 解析JSON数据
        data = request.get_json()
        logger.info(f"接收到的JSON数据: {data}")

        # 将JSON数据写入文件
        with open(SAVE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"JSON数据已成功保存到 {SAVE_FILE_PATH}")
        return jsonify({"message": "数据已成功接收并保存"}), 200

    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        return jsonify({"error": "内部服务器错误"}), 500

if __name__ == '__main__':
    # 获取主机地址和端口，可以从环境变量中读取，默认为主机192.168.5.15，端口5000,在实际开发中替换为和开发板的ip和端口信息保持一致
    HOST = os.getenv('API_HOST', '192.168.5.15')
    PORT = int(os.getenv('API_PORT', 5000))

    logger.info(f"API服务器正在启动，监听地址: {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)