import os
import json

# 应用根目录 - 使用os.path.abspath确保路径正确
APP_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CONFIG_FILE = os.path.join(APP_DIR, 'user_config.json')

# 默认API配置
DEFAULT_API_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
DEFAULT_PROVIDER_NAME = "硅基流动 (SiliconFlow)"

# 读取用户配置
def load_user_config():
    """加载用户配置"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
    return {}

# 保存用户配置
def save_user_config(config):
    """保存用户配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

# 获取当前API配置
def get_api_config():
    """获取当前使用的API配置"""
    user_config = load_user_config()
    
    # 优先使用用户配置
    if user_config.get('api_key'):
        return {
            'api_base_url': user_config.get('api_base_url', DEFAULT_API_BASE_URL),
            'api_key': user_config.get('api_key'),
            'model_name': user_config.get('model_name', DEFAULT_MODEL_NAME),
            'provider_name': user_config.get('provider_name', DEFAULT_PROVIDER_NAME),
            'is_custom': True
        }
    
    # 使用默认配置
    return {
        'api_base_url': DEFAULT_API_BASE_URL,
        'api_key': os.environ.get('API_KEY', ''),
        'model_name': DEFAULT_MODEL_NAME,
        'provider_name': DEFAULT_PROVIDER_NAME,
        'is_custom': False
    }

# 应用配置
SECRET_KEY = os.urandom(24)
DEBUG = True

# 文件上传配置
UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'}

# 数据库配置
DATABASE_PATH = os.path.join(APP_DIR, 'data', 'jobhelper.db')

# AI配置
AI_TIMEOUT = 60  # API超时时间（秒）
AI_MAX_TOKENS = 4000
