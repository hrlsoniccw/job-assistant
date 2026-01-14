import os
import sqlite3
import json
from datetime import datetime
from io import BytesIO
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        import random
        
        # 模拟热门职位数据（实际项目中可接入真实招聘API）
        hot_jobs = [
            {
                'id': 1,
                'title': '高级Python开发工程师',
                'company': '字节跳动',
                'salary': '25K-45K',
                'location': '北京',
                'tags': ['Python', 'Django', 'Go'],
                'category': 'tech',
                'source': 'BOSS直聘'
            },
            {
                'id': 2,
                'title': '前端开发工程师',
                'company': '阿里巴巴',
                'salary': '20K-35K',
                'location': '杭州',
                'tags': ['React', 'Vue', 'TypeScript'],
                'category': 'tech',
                'source': '猎聘'
            },
            {
                'id': 3,
                'title': '产品经理',
                'company': '腾讯科技',
                'salary': '22K-40K',
                'location': '深圳',
                'tags': ['C端产品', '用户增长', '数据分析'],
                'category': 'product',
                'source': '前程无忧'
            },
            {
                'id': 4,
                'title': 'Java开发工程师',
                'company': '美团',
                'salary': '20K-38K',
                'location': '北京',
                'tags': ['Java', 'Spring Boot', '微服务'],
                'category': 'tech',
                'source': 'BOSS直聘'
            },
            {
                'id': 5,
                'title': '数据分析师',
                'company': '京东集团',
                'salary': '18K-30K',
                'location': '北京',
                'tags': ['SQL', 'Python', 'Tableau'],
                'category': 'tech',
                'source': '猎聘'
            },
            {
                'id': 6,
                'title': '用户运营经理',
                'company': '小红书',
                'salary': '18K-28K',
                'location': '上海',
                'tags': ['用户增长', '活动策划', '数据分析'],
                'category': '运营',
                'source': '前程无忧'
            },
            {
                'id': 7,
                'title': 'Go后端开发',
                'company': '快手科技',
                'salary': '24K-42K',
                'location': '北京',
                'tags': ['Go', 'Kubernetes', '微服务'],
                'category': 'tech',
                'source': 'BOSS直聘'
            },
            {
                'id': 8,
                'title': '移动端开发工程师',
                'company': '网易',
                'salary': '20K-35K',
                'location': '杭州',
                'tags': ['iOS', 'Android', 'Flutter'],
                'category': 'tech',
                'source': '猎聘'
            },
            {
                'id': 9,
                'title': '算法工程师',
                'company': '百度',
                'salary': '30K-60K',
                'location': '北京',
                'tags': ['机器学习', '深度学习', 'NLP'],
                'category': 'tech',
                'source': '前程无忧'
            },
            {
                'id': 10,
                'title': '内容运营',
                'company': 'B站',
                'salary': '15K-25K',
                'location': '上海',
                'tags': ['内容策划', '短视频', '社区运营'],
                'category': '运营',
                'source': 'BOSS直聘'
            },
            {
                'id': 11,
                'title': '高级产品经理',
                'company': '拼多多',
                'salary': '28K-50K',
                'location': '上海',
                'tags': ['B端产品', '供应链', 'ERP'],
                'category': 'product',
                'source': '猎聘'
            },
            {
                'id': 12,
                'title': 'DevOps工程师',
                'company': '滴滴出行',
                'salary': '22K-38K',
                'location': '北京',
                'tags': ['Docker', 'Jenkins', 'CI/CD'],
                'category': 'tech',
                'source': '前程无忧'
            },
            {
                'id': 13,
                'title': '新媒体运营',
                'company': '抖音',
                'salary': '16K-26K',
                'location': '北京',
                'tags': ['社交媒体', '内容营销', '直播运营'],
                'category': '运营',
                'source': 'BOSS直聘'
            },
            {
                'id': 14,
                'title': '安全工程师',
                'company': '华为',
                'salary': '25K-45K',
                'location': '深圳',
                'tags': ['网络安全', '渗透测试', '安全开发'],
                'category': 'tech',
                'source': '猎聘'
            },
            {
                'id': 15,
                'title': 'UI/UX设计师',
                'company': '小米',
                'salary': '18K-30K',
                'location': '北京',
                'tags': ['Figma', 'UI设计', '用户体验'],
                'category': 'product',
                'source': '前程无忧'
            },
            {
                'id': 16,
                'title': '大数据开发工程师',
                'company': '蚂蚁集团',
                'salary': '28K-50K',
                'location': '杭州',
                'tags': ['Hadoop', 'Spark', 'Flink'],
                'category': 'tech',
                'source': 'BOSS直聘'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': hot_jobs
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
