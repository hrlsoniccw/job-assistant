import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ComparisonResult:
    """对比结果"""
    overall_score: int
    skill_comparison: Dict
    experience_comparison: Dict
    education_comparison: Dict
    recommendations: List[str]
    strengths: List[str]
    weaknesses: List[str]


class ResumeComparator:
    """简历对比分析器"""
    
    SKILL_WEIGHTS = {
        '编程语言': ['Python', 'Java', 'JavaScript', 'Go', 'C++', 'Rust', 'TypeScript', 'PHP', 'Ruby', 'Swift', 'Kotlin'],
        '前端框架': ['React', 'Vue', 'Angular', 'Next.js', 'Svelte', 'jQuery', 'Bootstrap', 'Tailwind'],
        '后端框架': ['Django', 'Flask', 'FastAPI', 'Spring Boot', 'Express', 'NestJS', 'Gin', 'Laravel'],
        '数据库': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server'],
        '云和DevOps': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'Terraform'],
        '数据科学': ['Pandas', 'NumPy', 'Spark', 'Hadoop', 'TensorFlow', 'PyTorch', 'Scikit-learn'],
    }
    
    def __init__(self):
        self.all_skills = set()
        for skills in self.SKILL_WEIGHTS.values():
            self.all_skills.update(skills)
    
    def compare(self, resume1_data: Dict, resume2_data: Dict, jd_text: str = '') -> ComparisonResult:
        """对比两份简历"""
        skill_comp = self._compare_skills(resume1_data, resume2_data)
        exp_comp = self._compare_experience(resume1_data, resume2_data)
        edu_comp = self._compare_education(resume1_data, resume2_data)
        
        all_strengths = skill_comp['strengths'] + exp_comp['strengths'] + edu_comp['strengths']
        all_weaknesses = skill_comp['weaknesses'] + exp_comp['weaknesses'] + edu_comp['weaknesses']
        
        recommendations = self._generate_recommendations(
            resume1_data, resume2_data, skill_comp, exp_comp, jd_text
        )
        
        overall_score = self._calculate_overall_score(skill_comp, exp_comp, edu_comp)
        
        return ComparisonResult(
            overall_score=overall_score,
            skill_comparison=skill_comp,
            experience_comparison=exp_comp,
            education_comparison=edu_comp,
            recommendations=recommendations,
            strengths=all_strengths[:5],
            weaknesses=all_weaknesses[:5]
        )
    
    def _compare_skills(self, r1: Dict, r2: Dict) -> Dict:
        """对比技能"""
        skills1 = set(s.strip() for s in r1.get('skills', []) if s.strip())
        skills2 = set(s.strip() for s in r2.get('skills', []) if s.strip())
        
        common = skills1 & skills2
        only_in_1 = skills1 - skills2
        only_in_2 = skills2 - skills1
        
        skill_score1 = len(common) / max(len(skills1), 1) * 50 + 50
        skill_score2 = len(common) / max(len(skills2), 1) * 50 + 50
        
        return {
            'resume1_skills': list(skills1),
            'resume2_skills': list(skills2),
            'common_skills': list(common),
            'only_in_resume1': list(only_in_1),
            'only_in_resume2': list(only_in_2),
            'resume1_score': round(skill_score1),
            'resume2_score': round(skill_score2),
            'strengths': [
                f"简历1拥有 {len(only_in_1)} 项独特技能",
                f"简历2拥有 {len(only_in_2)} 项独特技能"
            ] if only_in_1 or only_in_2 else [],
            'weaknesses': [
                f"两份简历技能重复率 {len(common) / max(len(skills1 | skills2), 1) * 100:.0f}%"
            ] if skills1 and skills2 else []
        }
    
    def _compare_experience(self, r1: Dict, r2: Dict) -> Dict:
        """对比工作经验"""
        exp1 = r1.get('work_experience', [])
        exp2 = r2.get('work_experience', [])
        
        companies1 = [e.get('company', '') for e in exp1 if e.get('company')]
        companies2 = [e.get('company', '') for e in exp2 if e.get('company')]
        
        total_exp1 = sum(self._calculate_exp_years(e) for e in exp1)
        total_exp2 = sum(self._calculate_exp_years(e) for e in exp2)
        
        achievements1 = sum(len(e.get('achievements', [])) for e in exp1)
        achievements2 = sum(len(e.get('achievements', [])) for e in exp2)
        
        score1 = min(100, total_exp1 * 10 + achievements1 * 5)
        score2 = min(100, total_exp2 * 10 + achievements2 * 5)
        
        return {
            'resume1_experiences': len(exp1),
            'resume2_experiences': len(exp2),
            'resume1_years': total_exp1,
            'resume2_years': total_exp2,
            'resume1_companies': companies1,
            'resume2_companies': companies2,
            'resume1_achievements': achievements1,
            'resume2_achievements': achievements2,
            'resume1_score': round(score1),
            'resume2_score': round(score2),
            'strengths': [
                f"简历1: {total_exp1:.1f}年经验, {achievements1}个可量化成果",
                f"简历2: {total_exp2:.1f}年经验, {achievements2}个可量化成果"
            ],
            'weaknesses': [
                "经验年限较短" if total_exp1 < 3 else "",
                "成果描述不足" if achievements1 < 2 else ""
            ]
        }
    
    def _calculate_exp_years(self, exp: Dict) -> float:
        """计算工作经验年限"""
        start = exp.get('start_date', '')
        end = exp.get('end_date', '')
        
        if not start:
            return 0
        
        try:
            if start:
                year = int(start.split('-')[0][:4]) if '-' in start else int(start[:4])
                start_year = year
            else:
                start_year = 2020
            
            if end in ['至今', '现在', 'Present', 'Current']:
                end_year = 2025
            elif end:
                year = int(end.split('-')[0][:4]) if '-' in end else int(end[:4])
                end_year = year
            else:
                end_year = 2025
            
            return max(0, end_year - start_year)
        except:
            return 0
    
    def _compare_education(self, r1: Dict, r2: Dict) -> Dict:
        """对比教育背景"""
        edu1 = r1.get('education', [])
        edu2 = r2.get('education', [])
        
        schools1 = [e.get('school', '') for e in edu1 if e.get('school')]
        schools2 = [e.get('school', '') for e in edu2 if e.get('school')]
        
        degrees1 = [e.get('degree', '') for e in edu1 if e.get('degree')]
        degrees2 = [e.get('degree', '') for e in edu2 if e.get('degree')]
        
        score1 = self._edu_score(edu1)
        score2 = self._edu_score(edu2)
        
        return {
            'resume1_schools': schools1,
            'resume2_schools': schools2,
            'resume1_degrees': degrees1,
            'resume2_degrees': degrees2,
            'resume1_score': score1,
            'resume2_score': score2,
            'strengths': [
                f"简历1: {schools1[0] if schools1 else '未披露'} - {degrees1[0] if degrees1 else '未披露'}" if edu1 else "",
                f"简历2: {schools2[0] if schools2 else '未披露'} - {degrees2[0] if degrees2 else '未披露'}" if edu2 else ""
            ],
            'weaknesses': ["教育信息不完整"] if not edu1 or not edu2 else []
        }
    
    def _edu_score(self, education: List[Dict]) -> int:
        """计算教育背景评分"""
        if not education:
            return 50
        
        score = 60
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            if '博士' in degree or 'PhD' in degree:
                score += 20
            elif '硕士' in degree or 'Master' in degree:
                score += 15
            elif 'MBA' in degree:
                score += 15
            
            school = edu.get('school', '').lower()
            top_schools = ['清华', '北大', '复旦', '上交', '浙大', '哈佛', 'MIT', '斯坦福']
            if any(s in school for s in top_schools):
                score += 10
        
        return min(100, score)
    
    def _calculate_overall_score(self, skill_comp: Dict, exp_comp: Dict, edu_comp: Dict) -> int:
        """计算综合评分"""
        score1 = (skill_comp.get('resume1_score', 0) * 0.3 + 
                  exp_comp.get('resume1_score', 0) * 0.5 + 
                  edu_comp.get('resume1_score', 0) * 0.2)
        score2 = (skill_comp.get('resume2_score', 0) * 0.3 + 
                  exp_comp.get('resume2_score', 0) * 0.5 + 
                  edu_comp.get('resume2_score', 0) * 0.2)
        
        return round((score1 + score2) / 2)
    
    def _generate_recommendations(self, r1: Dict, r2: Dict, 
                                  skill_comp: Dict, exp_comp: Dict, 
                                  jd_text: str) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if skill_comp.get('only_in_resume1'):
            recommendations.append(f"建议简历2补充: {', '.join(skill_comp['only_in_resume1'][:3])}")
        
        if skill_comp.get('only_in_resume2'):
            recommendations.append(f"建议简历1补充: {', '.join(skill_comp['only_in_resume2'][:3])}")
        
        if exp_comp.get('resume1_years', 0) < exp_comp.get('resume2_years', 0):
            recommendations.append("简历1经验年限较短，建议突出项目经验和技能深度")
        
        if exp_comp.get('resume1_achievements', 0) < 2:
            recommendations.append("建议增加可量化的成果描述，如'提升效率30%'等")
        
        if jd_text:
            jd_skills = self._extract_jd_skills(jd_text)
            resume1_skills = set(r1.get('skills', []))
            resume2_skills = set(r2.get('skills', []))
            
            missing1 = jd_skills - resume1_skills
            missing2 = jd_skills - resume2_skills
            
            if missing1:
                recommendations.append(f"针对JD，简历1建议补充: {', '.join(list(missing1)[:3])}")
            if missing2:
                recommendations.append(f"针对JD，简历2建议补充: {', '.join(list(missing2)[:3])}")
        
        if not recommendations:
            recommendations.append("两份简历质量相近，建议根据目标岗位JD进行针对性调整")
        
        return recommendations[:5]
    
    def _extract_jd_skills(self, jd_text: str) -> set:
        """从JD中提取技能关键词"""
        skills = set()
        jd_lower = jd_text.lower()
        
        for category, skill_list in self.SKILL_WEIGHTS.items():
            for skill in skill_list:
                if skill.lower() in jd_lower:
                    skills.add(skill)
        
        return skills


def compare_resumes(resume1_id: int, resume2_id: int, jd_text: str = '') -> Dict:
    """对比两份简历"""
    from app import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume1_id,))
    r1 = cursor.fetchone()
    
    cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume2_id,))
    r2 = cursor.fetchone()
    
    conn.close()
    
    if not r1 or not r2:
        return {'success': False, 'error': '简历不存在'}
    
    def parse_resume_data(resume):
        data = {
            'skills': json.loads(resume['skills']) if resume['skills'] else [],
            'work_experience': [],
            'project_experience': [],
            'education': []
        }
        if resume['parsed_data']:
            try:
                parsed = json.loads(resume['parsed_data'])
                data.update(parsed)
            except:
                pass
        return data
    
    r1_data = parse_resume_data(r1)
    r2_data = parse_resume_data(r2)
    
    comparator = ResumeComparator()
    result = comparator.compare(r1_data, r2_data, jd_text)
    
    return {
        'success': True,
        'data': {
            'overall_score': result.overall_score,
            'skill_comparison': result.skill_comparison,
            'experience_comparison': result.experience_comparison,
            'education_comparison': result.education_comparison,
            'recommendations': result.recommendations,
            'strengths': result.strengths,
            'weaknesses': result.weaknesses
        }
    }
