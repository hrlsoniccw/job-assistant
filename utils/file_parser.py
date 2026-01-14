import os
import re
from typing import Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in {'txt', 'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'}


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def parse_resume(file_path: str, filename: str) -> str:
    """解析简历文件，返回纯文本内容"""
    ext = get_file_extension(filename)
    
    try:
        if ext == 'pdf':
            return parse_pdf(file_path)
        elif ext in ('docx', 'doc'):
            return parse_word(file_path)
        elif ext == 'txt':
            return parse_text(file_path)
        elif ext in ('jpg', 'jpeg', 'png'):
            return parse_image(file_path)
        else:
            return parse_text(file_path)
    except Exception as e:
        print(f"解析文件失败 {filename}: {e}")
        return ""


def parse_pdf(file_path: str) -> str:
    """解析PDF文件"""
    if pdfplumber is None:
        raise ImportError("请安装pdfplumber: pip install pdfplumber")
    
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def parse_word(file_path: str) -> str:
    """解析Word文件"""
    if Document is None:
        raise ImportError("请安装python-docx: pip install python-docx")
    
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    # 尝试提取表格内容
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text + " "
            text += "\n"
    
    return text


def parse_text(file_path: str) -> str:
    """解析文本文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_image(file_path: str) -> str:
    """解析图片文件（OCR识别）"""
    if Image is None:
        raise ImportError("请安装Pillow: pip install Pillow")
    if pytesseract is None:
        raise ImportError("请安装pytesseract: pip install pytesseract")
    
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        return text
    except Exception as e:
        print(f"OCR识别失败: {e}")
        # 如果OCR失败，返回空字符串而不是抛出异常
        return ""


def extract_contact_info(text: str) -> dict:
    """从简历文本中提取联系信息"""
    info = {
        'phone': '',
        'email': '',
        'name': ''
    }
    
    # 提取手机号
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    if phones:
        info['phone'] = phones[0]
    
    # 提取邮箱
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        info['email'] = emails[0]
    
    # 提取姓名（假设第一行是姓名）
    lines = text.strip().split('\n')
    if lines:
        info['name'] = lines[0].strip()
    
    return info


def extract_work_experience(text: str) -> dict:
    """提取工作经历"""
    experiences = []
    
    # 常见的章节标题
    work_section_patterns = [
        r'工作经历',
        r'工作经历：',
        r'工作经历:',
        r'职业经历',
        r'任职经历',
        r'专业经历'
    ]
    
    # 项目经历模式
    project_section_patterns = [
        r'项目经历',
        r'项目经验',
        r'项目经历：',
        r'项目经验:',
        r'项目背景'
    ]
    
    # 教育背景模式
    education_section_patterns = [
        r'教育背景',
        r'教育经历',
        r'教育背景：',
        r'教育经历:'
    ]
    
    # 技能模式
    skills_section_patterns = [
        r'专业技能',
        r'技能特长',
        r'技能清单',
        r'专业能力'
    ]
    
    return {
        'work': experiences,
        'projects': [],
        'education': [],
        'skills': []
    }


def extract_skills(text: str) -> list:
    """从简历中提取技能关键词"""
    skills = []
    
    # 常见技术关键词
    tech_keywords = [
        # 编程语言
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        # 前端
        'React', 'Vue', 'Angular', 'HTML', 'CSS', 'TypeScript', 'Node.js', 'jQuery', 'Bootstrap',
        # 后端
        'Django', 'Flask', 'Spring', 'Spring Boot', 'MyBatis', 'Hibernate', 'Express', 'FastAPI',
        # 数据库
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 'Elasticsearch',
        # 云和DevOps
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'Linux', 'Nginx',
        # 数据分析
        'Pandas', 'NumPy', 'Spark', 'Hadoop', 'Tableau', 'Excel', 'SQL',
        # AI/ML
        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'NLP', 'Computer Vision',
        # 其他
        'RESTful API', 'GraphQL', 'Microservices', 'Agile', 'Scrum'
    ]
    
    text_lower = text.lower()
    for keyword in tech_keywords:
        if keyword.lower() in text_lower:
            skills.append(keyword)
    
    return list(set(skills))


def suggest_job_positions(skills: list, work_experience: list) -> list:
    """根据技能和工作经验推荐合适的岗位方向"""
    positions = []
    
    # 技术岗位分类
    tech_positions = {
        '后端开发': ['Python', 'Java', 'Go', 'Spring', 'Django', 'Flask', 'MySQL', 'Redis'],
        '前端开发': ['React', 'Vue', 'HTML', 'CSS', 'JavaScript', 'TypeScript', 'Node.js'],
        '全栈开发': ['Python', 'JavaScript', 'React', 'Node.js', 'MySQL'],
        '数据分析': ['Python', 'Pandas', 'SQL', 'Excel', 'Tableau', 'Spark'],
        '机器学习': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'NLP'],
        'DevOps': ['Docker', 'Kubernetes', 'Jenkins', 'AWS', 'Linux', 'Git'],
        '移动开发': ['Swift', 'Kotlin', 'React Native', 'Android', 'iOS'],
        '产品经理': ['Axure', 'Figma', '需求分析', '产品设计', '用户研究']
    }
    
    for position, required_skills in tech_positions.items():
        match_count = sum(1 for skill in skills if skill in required_skills)
        if match_count >= 2:
            positions.append({
                'position': position,
                'match_score': match_count / len(required_skills),
                'matched_skills': [s for s in skills if s in required_skills]
            })
    
    # 按匹配度排序
    positions.sort(key=lambda x: x['match_score'], reverse=True)
    
    return positions[:5]  # 返回前5个推荐岗位
