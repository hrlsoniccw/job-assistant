import os
import sqlite3
import json
from datetime import datetime
from io import BytesIO
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# 使用硬编码的绝对路径避免编码问题
APP_ROOT = r"D:\VsCodeProjects\求职帮助系统"
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
DATABASE_PATH = os.path.join(APP_ROOT, 'data', 'jobhelper.db')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            raw_text TEXT,
            parsed_data TEXT,
            skills TEXT,
            user_id INTEGER,
            is_public INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            raw_text TEXT NOT NULL,
            resume_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            jd_id INTEGER,
            result_type TEXT,
            result_data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id),
            FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
        )
    ''')
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            avatar_url VARCHAR(500),
            membership_level INTEGER DEFAULT 0,
            membership_expire DATETIME,
            vip_code VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 会员订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no VARCHAR(64) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            product_type INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            pay_status INTEGER DEFAULT 0,
            pay_type INTEGER DEFAULT 0,
            transaction_id VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 使用记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            usage_type VARCHAR(50) NOT NULL,
            count INTEGER DEFAULT 0,
            date DATE DEFAULT CURRENT_DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

from utils.file_parser import parse_resume, allowed_file, extract_skills, parse_resume_full, resume_to_dict
from utils.analyzer import ResumeAnalyzer
analyzer = ResumeAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})
        
        file = request.files['file']

        if not file or not file.filename:
            return jsonify({'success': False, 'error': '没有选择文件'})

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'})

        filename = secure_filename(file.filename or '')
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        raw_text = parse_resume(file_path, filename)
        
        if not raw_text.strip():
            return jsonify({'success': False, 'error': '无法解析文件内容，请尝试其他格式'})
        
        skills = extract_skills(raw_text)
        
        resume_full = parse_resume_full(file_path, filename)
        resume_dict = resume_to_dict(resume_full)
        parsed_data_json = json.dumps(resume_dict, ensure_ascii=False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO resumes (filename, file_type, raw_text, parsed_data, skills) VALUES (?, ?, ?, ?, ?)',
            (filename, filename.rsplit('.', 1)[-1], raw_text, parsed_data_json, json.dumps(skills))
        )
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'resume_id': resume_id,
                'filename': filename,
                'skills': skills,
                'parsed_data': resume_dict,
                'text_preview': raw_text[:500] + '...' if len(raw_text) > 500 else raw_text
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    try:
        data = request.json
        resume_id = data.get('resume_id')
        
        if not resume_id:
            return jsonify({'success': False, 'error': '缺少resume_id'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        result = analyzer.analyze(resume['raw_text'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO analysis_results (resume_id, result_type, result_data) VALUES (?, ?, ?)',
            (resume_id, 'analyze', json.dumps(result, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/match', methods=['POST'])
def match_jd():
    try:
        data = request.json
        resume_id = data.get('resume_id')
        jd_text = data.get('jd_text')
        
        if not resume_id:
            return jsonify({'success': False, 'error': '缺少resume_id'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        if not jd_text:
            return jsonify({'success': False, 'error': '请提供岗位JD'})
        
        result = analyzer.match_with_jd(resume['raw_text'], jd_text)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO job_descriptions (raw_text, resume_id) VALUES (?, ?)',
            (jd_text, resume_id)
        )
        jd_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO analysis_results (resume_id, jd_id, result_type, result_data) VALUES (?, ?, ?, ?)',
            (resume_id, jd_id, 'match', json.dumps(result, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/interview', methods=['POST'])
def generate_interview():
    try:
        data = request.json
        resume_id = data.get('resume_id')
        jd_text = data.get('jd_text', '')
        
        if not resume_id:
            return jsonify({'success': False, 'error': '缺少resume_id'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        result = analyzer.generate_interview_questions(resume['raw_text'], jd_text)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO analysis_results (resume_id, result_type, result_data) VALUES (?, ?, ?)',
            (resume_id, 'interview', json.dumps(result, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/self-intro', methods=['POST'])
def generate_self_intro():
    try:
        data = request.json
        resume_id = data.get('resume_id')
        jd_text = data.get('jd_text', '')
        
        if not resume_id:
            return jsonify({'success': False, 'error': '缺少resume_id'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        result = analyzer.generate_self_introduction(resume['raw_text'], jd_text)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO analysis_results (resume_id, result_type, result_data) VALUES (?, ?, ?)',
            (resume_id, 'self-intro', json.dumps(result, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resumes', methods=['GET'])
def list_resumes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, filename, created_at, skills FROM resumes ORDER BY created_at DESC')
        resumes = cursor.fetchall()
        conn.close()
        
        result = []
        for resume in resumes:
            result.append({
                'id': resume['id'],
                'filename': resume['filename'],
                'created_at': resume['created_at'],
                'skills': json.loads(resume['skills']) if resume['skills'] else []
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/resumes/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM analysis_results WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM job_descriptions WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/resumes/<int:resume_id>/export', methods=['POST'])
def export_resume(resume_id):
    """导出简历为PDF"""
    try:
        from utils.pdf_exporter import export_resume_to_bytes, convert_resume_to_dict
        from utils.file_parser import parse_resume_full
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        data = request.json or {}
        template = data.get('template', 'modern')
        
        if template not in ['modern', 'business', 'creative']:
            template = 'modern'
        
        resume_data = {
            'name': resume['filename'].rsplit('.', 1)[0] if resume['filename'] else '',
            'skills': json.loads(resume['skills']) if resume['skills'] else [],
            'work_experience': [],
            'project_experience': [],
            'education': [],
            'certificates': [],
            'awards': [],
            'self_introduction': ''
        }
        
        if resume['parsed_data']:
            try:
                parsed = json.loads(resume['parsed_data'])
                resume_data.update(parsed)
            except json.JSONDecodeError:
                pass
        
        pdf_bytes = export_resume_to_bytes(resume_data, template)
        
        from flask import send_file
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'resume_{resume_id}_{template}.pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/resumes/<int:resume_id>/export-word', methods=['POST'])
def export_resume_word(resume_id):
    """导出简历为Word文档"""
    try:
        from utils.doc_exporter import WordExporter, convert_resume_to_dict
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        resume_data = {
            'name': resume['filename'].rsplit('.', 1)[0] if resume['filename'] else '',
            'skills': json.loads(resume['skills']) if resume['skills'] else [],
            'work_experience': [],
            'project_experience': [],
            'education': [],
            'certificates': [],
            'awards': [],
            'self_introduction': ''
        }
        
        if resume['parsed_data']:
            try:
                parsed = json.loads(resume['parsed_data'])
                resume_data.update(parsed)
            except json.JSONDecodeError:
                pass
        
        from flask import send_file
        import io
        
        doc_bytes = WordExporter.export_to_bytes(resume_data)
        
        return send_file(
            io.BytesIO(doc_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f'resume_{resume_id}.docx'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/resumes/<int:resume_id>/export-html', methods=['POST'])
def export_resume_html(resume_id):
    """导出简历为HTML文件"""
    try:
        from utils.doc_exporter import HTMLExporter, convert_resume_to_dict
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'success': False, 'error': '简历不存在'})
        
        resume_data = {
            'name': resume['filename'].rsplit('.', 1)[0] if resume['filename'] else '',
            'skills': json.loads(resume['skills']) if resume['skills'] else [],
            'work_experience': [],
            'project_experience': [],
            'education': [],
            'certificates': [],
            'awards': [],
            'self_introduction': ''
        }
        
        if resume['parsed_data']:
            try:
                parsed = json.loads(resume['parsed_data'])
                resume_data.update(parsed)
            except json.JSONDecodeError:
                pass
        
        from flask import send_file
        import io
        
        html_content = HTMLExporter.generate(resume_data)
        
        return send_file(
            io.BytesIO(html_content.encode('utf-8')),
            mimetype='text/html',
            as_attachment=True,
            download_name=f'resume_{resume_id}.html'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export-formats', methods=['GET'])
def get_export_formats():
    """获取可用的导出格式"""
    try:
        from utils.doc_exporter import get_available_export_formats
        
        formats = get_available_export_formats()
        
        return jsonify({
            'success': True,
            'data': formats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取可用的PDF模板列表"""
    try:
        from utils.pdf_exporter import get_available_templates
        
        templates = get_available_templates()
        
        return jsonify({
            'success': True,
            'data': templates
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/resumes/compare', methods=['POST'])
def compare_resumes():
    """对比两份简历"""
    try:
        from utils.comparator import compare_resumes
        
        data = request.json
        resume1_id = data.get('resume1_id')
        resume2_id = data.get('resume2_id')
        jd_text = data.get('jd_text', '')
        
        if not resume1_id or not resume2_id:
            return jsonify({'success': False, 'error': '请提供两份简历的ID'})
        
        if resume1_id == resume2_id:
            return jsonify({'success': False, 'error': '请选择两份不同的简历进行对比'})
        
        result = compare_resumes(resume1_id, resume2_id, jd_text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取API使用状态"""
    try:
        from utils.ai_client import get_api_stats, reset_api_stats, get_ai_client
        from config import get_api_config, save_user_config
        
        stats = get_api_stats()
        config = get_api_config()
        
        return jsonify({
            'success': True,
            'data': {
                'provider': stats['provider'],
                'model': stats['model'],
                'total_calls': stats['total_calls'],
                'prompt_tokens': stats['total_prompt_tokens'],
                'completion_tokens': stats['total_completion_tokens'],
                'total_tokens': stats['total_tokens'],
                'last_call_time': stats['last_call_time'],
                'is_custom_key': config['is_custom']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/status/reset', methods=['POST'])
def reset_status():
    """重置API使用统计"""
    try:
        from utils.ai_client import reset_api_stats
        
        old_stats = reset_api_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'message': '统计已重置',
                'cleared_stats': {
                    'total_calls': old_stats['total_calls'],
                    'total_tokens': old_stats['total_tokens']
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/config', methods=['GET'])
def get_api_config_info():
    """获取当前API配置信息"""
    try:
        from config import get_api_config
        
        config = get_api_config()
        
        return jsonify({
            'success': True,
            'data': {
                'api_base_url': config['api_base_url'],
                'api_key_masked': config['api_key'][:10] + '****' if config['api_key'] else '',
                'model_name': config['model_name'],
                'provider_name': config['provider_name'],
                'is_custom': config['is_custom']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/config/test', methods=['POST'])
def test_api_key_endpoint():
    """测试API Key是否有效"""
    try:
        from utils.ai_client import test_api_key
        
        data = request.json
        api_key = data.get('api_key', '').strip()
        api_base_url = data.get('api_base_url', '').strip()
        model_name = data.get('model_name', '').strip()
        
        if not api_key:
            return jsonify({'success': False, 'error': '请输入API Key'})
        
        result = test_api_key(api_key, api_base_url, model_name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/config/save', methods=['POST'])
def save_api_config():
    """保存用户API配置"""
    try:
        from config import save_user_config, load_user_config
        from utils.ai_client import get_ai_client
        
        data = request.json
        api_key = data.get('api_key', '').strip()
        api_base_url = data.get('api_base_url', '').strip() or 'https://api.siliconflow.cn/v1'
        model_name = data.get('model_name', '').strip() or 'Qwen/Qwen2.5-72B-Instruct'
        provider_name = data.get('provider_name', '').strip() or '自定义API'
        
        if not api_key:
            return jsonify({'success': False, 'error': '请输入API Key'})
        
        from utils.ai_client import test_api_key
        test_result = test_api_key(api_key, api_base_url, model_name)
        
        if not test_result['success']:
            return jsonify({
                'success': False, 
                'error': f'API Key测试失败: {test_result["message"]}'
            })
        
        user_config = {
            'api_key': api_key,
            'api_base_url': api_base_url,
            'model_name': model_name,
            'provider_name': provider_name
        }
        
        if save_user_config(user_config):
            get_ai_client()
            
            return jsonify({
                'success': True,
                'message': 'API配置已保存并生效'
            })
        else:
            return jsonify({'success': False, 'error': '保存配置失败'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/config/reset', methods=['POST'])
def reset_api_config():
    """重置为默认API配置"""
    try:
        from config import save_user_config, load_user_config
        from utils.ai_client import get_ai_client
        
        user_config = load_user_config()
        user_config.pop('api_key', None)
        user_config.pop('api_base_url', None)
        user_config.pop('model_name', None)
        user_config.pop('provider_name', None)
        
        save_user_config(user_config)
        get_ai_client()
        
        return jsonify({
            'success': True,
            'message': '已切换回默认API配置'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/jobs/hot')
def get_hot_jobs():
    """获取热门职位推荐"""
    try:
        from utils.job_client import get_hot_jobs
        
        jobs = get_hot_jobs()
        
        return jsonify({
            'success': True,
            'data': jobs
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/jobs/search')
def search_jobs():
    """搜索职位"""
    try:
        from utils.job_client import search_jobs
        
        keywords = request.args.get('keywords', '').strip()
        location = request.args.get('location', '').strip()
        category = request.args.get('category', 'all').strip()
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 50)
        
        jobs = search_jobs(keywords, location, category, page, limit)
        
        return jsonify({
            'success': True,
            'data': {
                'jobs': jobs,
                'page': page,
                'limit': limit,
                'total': len(jobs)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/jobs/parse-jd', methods=['POST'])
def parse_jd():
    """解析JD文本"""
    try:
        from utils.job_client import parse_job_description
        
        data = request.json
        jd_text = data.get('jd_text', '').strip()
        
        if not jd_text:
            return jsonify({'success': False, 'error': '请提供JD文本'})
        
        result = parse_job_description(jd_text)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================
# 用户系统 API
# ============================================

import hashlib
import jwt
import re
from datetime import datetime, timedelta
from functools import wraps

# JWT 配置
JWT_SECRET_KEY = os.urandom(24).hex()
JWT_EXPIRATION_HOURS = 24 * 7  # 7天过期


def generate_token(user_id: int) -> str:
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')


def decode_token(token: str) -> Optional[dict]:
    """解析JWT令牌"""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': '请先登录'})
        
        token = auth_header[7:]
        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'error': '登录已过期，请重新登录'})
        
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated


@app.route('/api/user/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        phone = data.get('phone', '').strip()
        
        # 验证必填字段
        if not all([username, email, password]):
            return jsonify({'success': False, 'error': '请填写完整信息'})
        
        # 验证邮箱格式
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return jsonify({'success': False, 'error': '邮箱格式不正确'})
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({'success': False, 'error': '密码至少6位'})
        
        # 验证用户名
        if len(username) < 2 or len(username) > 50:
            return jsonify({'success': False, 'error': '用户名2-50个字符'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查邮箱是否存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': '邮箱已被注册'})
        
        # 检查用户名是否存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': '用户名已被占用'})
        
        # 创建用户
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, phone) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, phone)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 生成token
        token = generate_token(user_id)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'membership_level': 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/user/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({'success': False, 'error': '请填写邮箱和密码'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'error': '邮箱或密码错误'})
        
        # 验证密码
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user['password_hash']:
            return jsonify({'success': False, 'error': '邮箱或密码错误'})
        
        # 生成token
        token = generate_token(user['id'])
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'phone': user['phone'],
                    'avatar_url': user['avatar_url'],
                    'membership_level': user['membership_level'],
                    'membership_expire': user['membership_expire']
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, phone, avatar_url, membership_level, membership_expire, created_at FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'})
        
        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'avatar_url': user['avatar_url'],
                'membership_level': user['membership_level'],
                'membership_expire': user['membership_expire'],
                'created_at': user['created_at']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户信息"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if data.get('username'):
            # 检查用户名是否被占用
            cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', (data['username'], request.user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'error': '用户名已被占用'})
            updates.append('username = ?')
            params.append(data['username'])
        
        if data.get('phone') is not None:
            updates.append('phone = ?')
            params.append(data['phone'])
        
        if data.get('avatar_url') is not None:
            updates.append('avatar_url = ?')
            params.append(data['avatar_url'])
        
        if updates:
            updates.append('updated_at = ?')
            params.append(datetime.now())
            params.append(request.user_id)
            
            cursor.execute(
                f'UPDATE users SET {", ".join(updates)} WHERE id = ?',
                params
            )
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '更新成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/user/membership', methods=['GET'])
@login_required
def get_membership():
    """获取会员信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT membership_level, membership_expire FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'})
        
        # 获取会员权限
        permissions = {
            0: ['basic_analysis', '3_interview_per_day'],
            1: ['unlimited_analysis', '15_interview_per_session', 'pdf_export', 'custom_intro'],
            2: ['unlimited_analysis', 'unlimited_interview', 'ai_mock_interview', 
                'pdf_export', 'salary_prediction', 'priority_support']
        }
        
        membership_info = {
            'level': user['membership_level'],
            'expire_time': user['membership_expire'],
            'permissions': permissions.get(user['membership_level'], []),
            'level_name': ['免费用户', '专业版', '尊享版'][user['membership_level']] if user['membership_level'] <= 2 else '未知'
        }
        
        return jsonify({
            'success': True,
            'data': membership_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/user/usage', methods=['GET'])
@login_required
def get_usage_stats():
    """获取使用统计"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取今日使用次数
        cursor.execute(
            'SELECT count FROM analysis_usage WHERE user_id = ? AND date = ? AND usage_type = ?',
            (request.user_id, today, 'analyze')
        )
        result = cursor.fetchone()
        today_count = result['count'] if result else 0
        
        # 获取用户会员等级
        cursor.execute('SELECT membership_level FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        conn.close()
        
        membership_level = user['membership_level'] if user else 0
        
        # 每日限制
        daily_limits = {
            0: {'limit': 3, 'remaining': max(0, 3 - today_count)},
            1: {'limit': 99999, 'remaining': 99999},
            2: {'limit': 99999, 'remaining': 99999}
        }
        
        limit_info = daily_limits.get(membership_level, daily_limits[0])
        
        return jsonify({
            'success': True,
            'data': {
                'today_count': today_count,
                'daily_limit': limit_info['limit'],
                'remaining': limit_info['remaining'],
                'membership_level': membership_level
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/user/usage', methods=['POST'])
@login_required
def record_usage():
    """记录使用次数"""
    try:
        data = request.json
        usage_type = data.get('usage_type', 'analyze')
        count = data.get('count', 1)
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查今日记录
        cursor.execute(
            'SELECT id, count FROM analysis_usage WHERE user_id = ? AND date = ? AND usage_type = ?',
            (request.user_id, today, usage_type)
        )
        result = cursor.fetchone()
        
        if result:
            cursor.execute(
                'UPDATE analysis_usage SET count = count + ? WHERE id = ?',
                (count, result['id'])
            )
        else:
            cursor.execute(
                'INSERT INTO analysis_usage (user_id, usage_type, count, date) VALUES (?, ?, ?, ?)',
                (request.user_id, usage_type, count, today)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '使用记录已保存'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ============================================
# 支付系统 API
# ============================================

@app.route('/api/payment/create-order', methods=['POST'])
@login_required
def create_payment_order():
    """创建支付订单"""
    try:
        from utils.payment_service import get_payment_service
        
        data = request.json
        product_type = data.get('product_type', 1)
        pay_type = data.get('pay_type', 0)  # 0:微信, 1:支付宝
        
        if product_type not in [1, 2, 3]:
            return jsonify({'success': False, 'error': '无效的产品类型'})
        
        # 创建订单并保存到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取会员套餐价格
        prices = {1: 19.9, 2: 199.0, 3: 499.0}
        amount = prices[product_type]
        
        # 生成订单号
        import random
        import time
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        order_no = f'JA{timestamp}{random.randint(1000, 9999)}'
        
        # 插入订单记录
        cursor.execute('''
            INSERT INTO orders (order_no, user_id, product_type, amount, pay_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_no, request.user_id, product_type, amount, pay_type))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 生成支付参数
        payment_service = get_payment_service()
        result = payment_service.create_order(request.user_id, product_type, pay_type)
        
        if not result.get('success'):
            return jsonify(result)
        
        return jsonify({
            'success': True,
            'data': {
                'order_id': order_id,
                'order_no': order_no,
                'product_name': result['data']['product_name'],
                'amount': result['data']['amount'],
                'pay_type': pay_type,
                'pay_params': result['data']['pay_params']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/payment/notify', methods=['POST'])
def payment_notify():
    """支付回调接口"""
    try:
        from utils.payment_service import get_payment_service
        
        # 获取回调数据
        # 根据支付方式不同，获取数据的方式不同
        # 这里需要根据微信支付或支付宝的要求解析
        notify_data = request.json if request.is_json else request.form.to_dict()
        
        # 处理回调
        payment_service = get_payment_service()
        result = payment_service.handle_notify(notify_data)
        
        if result.get('code') == 'SUCCESS':
            # 处理支付成功后的业务逻辑
            order_no = result.get('order_no', '')
            transaction_id = result.get('transaction_id', '')
            payment_service.handle_payment_success(order_no, transaction_id)
        
        # 返回给支付平台
        return jsonify({
            'code': result.get('code', 'FAIL'),
            'message': result.get('message', 'FAILED')
        })
        
    except Exception as e:
        return jsonify({'code': 'FAIL', 'message': str(e)})


@app.route('/api/payment/query-order/<order_no>', methods=['GET'])
def query_payment_order(order_no):
    """查询订单状态"""
    try:
        from utils.payment_service import get_payment_service
        
        payment_service = get_payment_service()
        result = payment_service.query_order(order_no)
        
        # 从数据库查询最新订单状态
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE order_no = ?', (order_no,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            return jsonify({'success': False, 'error': '订单不存在'})
        
        return jsonify({
            'success': True,
            'data': {
                'order_id': order['id'],
                'order_no': order['order_no'],
                'product_type': order['product_type'],
                'amount': order['amount'],
                'pay_status': order['pay_status'],
                'pay_type': order['pay_type'],
                'transaction_id': order['transaction_id'],
                'created_at': order['created_at'],
                'paid_at': order['paid_at']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/products', methods=['GET'])
def get_products():
    """获取会员套餐"""
    try:
        products = [
            {
                'id':1,
                'name': '月卡',
                'type':1,
                'price': 19.9,
                'description': '1个月专业版会员',
                'features': ['简历无限分析', '15道面试题', 'PDF导出', '定制自我介绍']
            },
            {
                'id': 2,
                'name': '年卡',
                'type': 2,
                'price': 199.0,
                'description': '12个月专业版会员',
                'features': ['简历无限分析', '15道面试题', 'PDF导出', '定制自我介绍', 'AI模拟面试', '薪资预测']
            },
            {
                'id': 3,
                'name': '终身卡',
                'type': 3,
                'price': 499.0,
                'description': '终身专业版会员',
                'features': ['所有功能永久使用', '专属客服', '简历托管', '优先内推']
            }
        ]
        
        return jsonify({
            'success': True,
            'data': products
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
