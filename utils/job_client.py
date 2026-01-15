import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class JobPosition:
    """职位数据模型"""
    id: str
    title: str
    company: str
    salary: str
    location: str
    tags: List[str] = field(default_factory=list)
    category: str = 'tech'
    source: str = ''
    requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    posted_time: str = ''
    url: str = ''


class JobAPIClient:
    """招聘API客户端基类"""
    
    def search_jobs(self, keywords: str = '', location: str = '', 
                    category: str = '', page: int = 1, limit: int = 10) -> List[JobPosition]:
        raise NotImplementedError
    
    def get_hot_jobs(self) -> List[JobPosition]:
        raise NotImplementedError
    
    def parse_jd(self, jd_text: str) -> Dict:
        raise NotImplementedError


class MockJobClient(JobAPIClient):
    """模拟招聘数据客户端（用于演示和测试）"""
    
    def __init__(self):
        self.job_database = self._init_job_database()
    
    def _init_job_database(self) -> List[Dict]:
        """初始化职位数据库"""
        return [
            {
                'id': '1',
                'title': '高级Python开发工程师',
                'company': '字节跳动',
                'salary': '25K-45K',
                'location': '北京',
                'tags': ['Python', 'Django', 'Go'],
                'category': 'tech',
                'source': 'BOSS直聘',
                'requirements': ['3年以上Python开发经验', '熟悉Django或Flask框架', '熟悉MySQL、Redis'],
                'responsibilities': ['负责后端系统设计和开发', '优化系统性能', '参与技术方案设计']
            },
            {
                'id': '2',
                'title': '前端开发工程师',
                'company': '阿里巴巴',
                'salary': '20K-35K',
                'location': '杭州',
                'tags': ['React', 'Vue', 'TypeScript'],
                'category': 'tech',
                'source': '猎聘',
                'requirements': ['2年以上前端开发经验', '熟悉React或Vue', '熟悉TypeScript'],
                'responsibilities': ['负责前端页面开发', '优化用户体验', '参与组件库建设']
            },
            {
                'id': '3',
                'title': '产品经理',
                'company': '腾讯科技',
                'salary': '22K-40K',
                'location': '深圳',
                'tags': ['C端产品', '用户增长', '数据分析'],
                'category': 'product',
                'source': '前程无忧',
                'requirements': ['3年以上产品经验', '熟悉产品设计流程', '数据分析能力强'],
                'responsibilities': ['负责产品规划', '需求分析和管理', '协调开发团队']
            },
            {
                'id': '4',
                'title': 'Java开发工程师',
                'company': '美团',
                'salary': '20K-38K',
                'location': '北京',
                'tags': ['Java', 'Spring Boot', '微服务'],
                'category': 'tech',
                'source': 'BOSS直聘',
                'requirements': ['3年以上Java开发经验', '熟悉Spring Boot', '熟悉微服务架构'],
                'responsibilities': ['负责后端系统开发', '参与架构设计', '优化系统性能']
            },
            {
                'id': '5',
                'title': '数据分析师',
                'company': '京东集团',
                'salary': '18K-30K',
                'location': '北京',
                'tags': ['SQL', 'Python', 'Tableau'],
                'category': 'tech',
                'source': '猎聘',
                'requirements': ['2年以上数据分析经验', '熟悉SQL和Python', '熟练使用BI工具'],
                'responsibilities': ['负责数据分析报告', '支持业务决策', '建设数据指标体系']
            },
            {
                'id': '6',
                'title': '用户运营经理',
                'company': '小红书',
                'salary': '18K-28K',
                'location': '上海',
                'tags': ['用户增长', '活动策划', '数据分析'],
                'category': '运营',
                'source': '前程无忧',
                'requirements': ['3年以上运营经验', '用户增长经验', '数据分析能力'],
                'responsibilities': ['制定运营策略', '策划用户活动', '提升用户活跃度']
            },
            {
                'id': '7',
                'title': 'Go后端开发',
                'company': '快手科技',
                'salary': '24K-42K',
                'location': '北京',
                'tags': ['Go', 'Kubernetes', '微服务'],
                'category': 'tech',
                'source': 'BOSS直聘',
                'requirements': ['3年以上Go开发经验', '熟悉Kubernetes', '微服务架构经验'],
                'responsibilities': ['负责后端开发', '优化系统性能', '参与架构设计']
            },
            {
                'id': '8',
                'title': '移动端开发工程师',
                'company': '网易',
                'salary': '20K-35K',
                'location': '杭州',
                'tags': ['iOS', 'Android', 'Flutter'],
                'category': 'tech',
                'source': '猎聘',
                'requirements': ['2年以上移动端开发经验', '熟悉iOS或Android', 'Flutter经验优先'],
                'responsibilities': ['负责移动端开发', '优化应用性能', '参与技术选型']
            },
            {
                'id': '9',
                'title': '算法工程师',
                'company': '百度',
                'salary': '30K-60K',
                'location': '北京',
                'tags': ['机器学习', '深度学习', 'NLP'],
                'category': 'tech',
                'source': '前程无忧',
                'requirements': ['硕士及以上学历', '机器学习算法经验', '深度学习框架熟练'],
                'responsibilities': ['负责算法研发', '优化模型效果', '落地业务场景']
            },
            {
                'id': '10',
                'title': '内容运营',
                'company': 'B站',
                'salary': '15K-25K',
                'location': '上海',
                'tags': ['内容策划', '短视频', '社区运营'],
                'category': '运营',
                'source': 'BOSS直聘',
                'requirements': ['2年以上运营经验', '内容策划能力', '社区运营经验'],
                'responsibilities': ['策划内容活动', '运营社区', '数据分析']
            },
            {
                'id': '11',
                'title': '高级产品经理',
                'company': '拼多多',
                'salary': '28K-50K',
                'location': '上海',
                'tags': ['B端产品', '供应链', 'ERP'],
                'category': 'product',
                'source': '猎聘',
                'requirements': ['5年以上产品经验', 'B端产品经验', '供应链领域经验'],
                'responsibilities': ['负责B端产品规划', '优化供应链系统', '提升业务效率']
            },
            {
                'id': '12',
                'title': 'DevOps工程师',
                'company': '滴滴出行',
                'salary': '22K-38K',
                'location': '北京',
                'tags': ['Docker', 'Jenkins', 'CI/CD'],
                'category': 'tech',
                'source': '前程无忧',
                'requirements': ['3年以上DevOps经验', '熟悉CI/CD流程', 'Docker和Kubernetes经验'],
                'responsibilities': ['负责CI/CD流程', '优化运维效率', '建设监控体系']
            },
            {
                'id': '13',
                'title': '新媒体运营',
                'company': '抖音',
                'salary': '16K-26K',
                'location': '北京',
                'tags': ['社交媒体', '内容营销', '直播运营'],
                'category': '运营',
                'source': 'BOSS直聘',
                'requirements': ['2年以上新媒体运营经验', '内容创作能力', '直播运营经验'],
                'responsibilities': ['运营社交媒体账号', '策划内容营销', '直播运营']
            },
            {
                'id': '14',
                'title': '安全工程师',
                'company': '华为',
                'salary': '25K-45K',
                'location': '深圳',
                'tags': ['网络安全', '渗透测试', '安全开发'],
                'category': 'tech',
                'source': '猎聘',
                'requirements': ['3年以上安全经验', '渗透测试能力', '安全开发经验'],
                'responsibilities': ['负责安全测试', '安全开发', '安全体系建设']
            },
            {
                'id': '15',
                'title': 'UI/UX设计师',
                'company': '小米',
                'salary': '18K-30K',
                'location': '北京',
                'tags': ['Figma', 'UI设计', '用户体验'],
                'category': 'product',
                'source': '前程无忧',
                'requirements': ['3年以上设计经验', '熟练使用Figma', '用户体验设计能力'],
                'responsibilities': ['负责产品设计', '优化用户体验', '设计规范制定']
            },
            {
                'id': '16',
                'title': '大数据开发工程师',
                'company': '蚂蚁集团',
                'salary': '28K-50K',
                'location': '杭州',
                'tags': ['Hadoop', 'Spark', 'Flink'],
                'category': 'tech',
                'source': 'BOSS直聘',
                'requirements': ['3年以上大数据开发经验', '熟悉Hadoop生态', 'Spark或Flink经验'],
                'responsibilities': ['负责大数据平台开发', '数据仓库建设', '实时计算开发']
            },
            {
                'id': '17',
                'title': 'SRE工程师',
                '公司': '阿里云',
                'salary': '25K-45K',
                'location': '杭州',
                'tags': ['Linux', 'Kubernetes', '监控'],
                'category': 'tech',
                'source': '猎聘',
                'requirements': ['3年以上SRE经验', 'Linux系统精通', 'Kubernetes经验'],
                'responsibilities': ['负责系统稳定性', '建设监控体系', '故障响应处理']
            },
            {
                'id': '18',
                'title': '测试开发工程师',
                'company': 'Shopee',
                'salary': '20K-35K',
                'location': '深圳',
                'tags': ['自动化测试', 'Selenium', '性能测试'],
                'category': 'tech',
                'source': '前程无忧',
                'requirements': ['2年以上测试开发经验', '自动化测试能力', '性能测试经验'],
                'responsibilities': ['负责自动化测试', '性能测试', '测试平台建设']
            },
            {
                'id': '19',
                'title': '技术专家',
                'company': '腾讯云',
                'salary': '35K-60K',
                'location': '深圳',
                'tags': ['云原生', '高并发', '架构设计'],
                'category': 'tech',
                'source': 'BOSS直聘',
                'requirements': ['5年以上开发经验', '架构设计能力', '云原生技术熟练'],
                'responsibilities': ['负责架构设计', '技术难点攻关', '团队技术指导']
            },
            {
                'id': '20',
                'title': '项目经理',
                'company': '华为',
                'salary': '20K-35K',
                'location': '深圳',
                'tags': ['PMP', '敏捷开发', '团队管理'],
                'category': 'product',
                'source': '猎聘',
                'requirements': ['5年以上项目管理经验', 'PMP认证', '敏捷开发经验'],
                'responsibilities': ['负责项目管理', '团队协调', '进度控制']
            }
        ]
    
    def search_jobs(self, keywords: str = '', location: str = '',
                    category: str = '', page: int = 1, limit: int = 10) -> List[JobPosition]:
        """搜索职位"""
        results = []
        
        for job in self.job_database:
            # 关键词匹配
            if keywords:
                keyword_lower = keywords.lower()
                match = (
                    keyword_lower in job['title'].lower() or
                    keyword_lower in job['company'].lower() or
                    keyword_lower in ' '.join(job['tags']).lower()
                )
                if not match:
                    continue
            
            # 地点匹配
            if location and location not in job['location']:
                continue
            
            # 类别匹配
            if category and category != 'all' and job['category'] != category:
                continue
            
            results.append(JobPosition(
                id=job['id'],
                title=job['title'],
                company=job['company'],
                salary=job['salary'],
                location=job['location'],
                tags=job['tags'],
                category=job['category'],
                source=job['source'],
                requirements=job.get('requirements', []),
                responsibilities=job.get('responsibilities', []),
                posted_time='3天前',
                url=f"https://example.com/job/{job['id']}"
            ))
        
        # 分页
        start = (page - 1) * limit
        end = start + limit
        return results[start:end]
    
    def get_hot_jobs(self) -> List[JobPosition]:
        """获取热门职位"""
        return self.search_jobs(limit=16)
    
    def parse_jd(self, jd_text: str) -> Dict:
        """解析JD文本"""
        result = {
            'title': '',
            'company': '',
            'salary': '',
            'location': '',
            'requirements': [],
            'responsibilities': [],
            'skills': []
        }
        
        # 提取职位名称
        title_patterns = [
            r'职位[：:\s]*([^\n]+)',
            r'岗位[：:\s]*([^\n]+)',
            r'招聘[：:\s]*([^\n]+)',
            r'(?:高级|资深|中级)?(?:Python|Java|前端|后端|产品|运营|算法|测试)[^\n]+'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, jd_text)
            if match:
                result['title'] = match.group(1).strip()
                break
        
        # 提取公司名称
        company_patterns = [
            r'公司[：:\s]*([^\n]+)',
            r'(?:字节跳动|阿里巴巴|腾讯|美团|京东|百度|华为|网易)[^\n]*'
        ]
        for pattern in company_patterns:
            match = re.search(pattern, jd_text)
            if match:
                result['company'] = match.group(1).strip()
                break
        
        # 提取薪资
        salary_pattern = r'(\d+K-\d+K|\d+K-\d+万|\d+-\d+K)'
        salary_match = re.search(salary_pattern, jd_text)
        if salary_match:
            result['salary'] = salary_match.group(1)
        
        # 提取地点
        location_patterns = [r'地点[：:\s]*([^\n]+)', r'(北京|上海|深圳|杭州|广州)[^\n]*']
        for pattern in location_patterns:
            match = re.search(pattern, jd_text)
            if match:
                result['location'] = match.group(1).strip()
                break
        
        # 提取任职要求
        req_section = re.search(r'任职[要求|资格][：:\n]*([\s\S]*?)(?:职责|工作内容|联系方式|$)', jd_text)
        if req_section:
            req_lines = req_section.group(1).split('\n')
            for line in req_lines:
                line = line.strip()
                if line and len(line) > 5:
                    result['requirements'].append(line)
        
        # 提取岗位职责
        resp_section = re.search(r'职责[：:\n]*([\s\S]*?)(?:要求|任职|资格|联系方式|$)', jd_text)
        if resp_section:
            resp_lines = resp_section.group(1).split('\n')
            for line in resp_lines:
                line = line.strip()
                if line and len(line) > 5:
                    result['responsibilities'].append(line)
        
        # 提取技能关键词
        skill_keywords = [
            'Python', 'Java', 'Go', 'JavaScript', 'TypeScript', 'C++',
            'React', 'Vue', 'Angular', 'Node.js',
            'Django', 'Flask', 'Spring Boot', 'FastAPI',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'AWS', 'Azure', 'GCP',
            '机器学习', '深度学习', 'TensorFlow', 'PyTorch',
            'NLP', '计算机视觉', '算法'
        ]
        for skill in skill_keywords:
            if skill in jd_text:
                result['skills'].append(skill)
        
        return result


# 单例实例
_job_client = None


def get_job_client() -> JobAPIClient:
    """获取招聘API客户端单例"""
    global _job_client
    if _job_client is None:
        _job_client = MockJobClient()
    return _job_client


def search_jobs(keywords: str = '', location: str = '',
                category: str = '', page: int = 1, limit: int = 10) -> List[Dict]:
    """搜索职位"""
    client = get_job_client()
    jobs = client.search_jobs(keywords, location, category, page, limit)
    return [job.__dict__ for job in jobs]


def get_hot_jobs() -> List[Dict]:
    """获取热门职位"""
    client = get_job_client()
    jobs = client.get_hot_jobs()
    return [job.__dict__ for job in jobs]


def parse_job_description(jd_text: str) -> Dict:
    """解析JD文本"""
    client = get_job_client()
    return client.parse_jd(jd_text)
