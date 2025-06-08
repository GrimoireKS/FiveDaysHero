from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from api import register_blueprints
from utils.cleanup_tasks import start_cleanup_tasks
import atexit

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# 配置CORS，允许所有来源的请求
CORS(app, resources={r"/*": {"origins": "*"}})

# 注册所有API蓝图
register_blueprints(app)

# 启动清理任务
start_cleanup_tasks()

# 注册应用退出时的清理函数
@atexit.register
def cleanup():
    from utils.cleanup_tasks import stop_cleanup_tasks
    stop_cleanup_tasks()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
