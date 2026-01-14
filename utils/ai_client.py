import json
import requests
from datetime import datetime
from typing import Optional
from config import get_api_config

api_stats = {
    "total_calls": 0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_tokens": 0,
    "last_call_time": None,
    "provider": "",
    "model": ""
}

SYSTEM_PROMPT = """You are a senior career development consultant and recruitment expert, proficient in job market trends, resume optimization, interview techniques, and career planning.

## Working Principles
1. Professional yet understandable: Analyze from HR perspective, but use easy-to-understand language
2. Get to the point: Identify core issues directly, provide actionable suggestions
3. Data-driven: Support suggestions with specific data and cases
4. User-centric: Think from job seeker's perspective to help them find satisfactory positions quickly

## Output Style
- Start with core观点 directly
- Each suggestion should be specific and actionable
- Present important information in concise bullet points
- End with clear action items

## Your Goals
Help job seekers:
- Discover and optimize resume issues
- Match with the most suitable job opportunities
- Prepare targeted interview answers
- Present their best selves
- Get satisfactory offers quickly"""


class AIClient:
    def __init__(self):
        self.api_config = get_api_config()
        self.update_headers()
        api_stats['provider'] = self.api_config['provider_name']
        api_stats['model'] = self.api_config['model_name']
    
    def update_headers(self):
        self.api_url = f"{self.api_config['api_base_url']}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_config['api_key']}",
            "Content-Type": "application/json"
        }
    
    def refresh_config(self):
        self.api_config = get_api_config()
        self.update_headers()
        api_stats['provider'] = self.api_config['provider_name']
        api_stats['model'] = self.api_config['model_name']
    
    def chat(self, messages: list, temperature: float = 0.7, system_prompt: Optional[str] = None) -> Optional[str]:
        chat_messages = messages.copy()
        if system_prompt is None:
            system_prompt = SYSTEM_PROMPT
        
        chat_messages.insert(0, {"role": "system", "content": system_prompt})
        
        payload = {
            "model": self.api_config['model_name'],
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                usage = result.get('usage', {})
                api_stats['total_calls'] += 1
                api_stats['total_prompt_tokens'] += usage.get('prompt_tokens', 0)
                api_stats['total_completion_tokens'] += usage.get('completion_tokens', 0)
                api_stats['total_tokens'] += usage.get('total_tokens', 0)
                api_stats['last_call_time'] = str(datetime.now())
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"API request failed: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
                print(error_msg)
                return None
                
        except requests.exceptions.Timeout:
            print("API request timeout")
            return None
        except Exception as e:
            print(f"API request error: {e}")
            return None
    
    def analyze_resume(self, resume_text: str) -> dict:
        prompt = f"""作为资深HR专家，请对以下简历进行全面分析评估。

【简历内容】
{resume_text[:8000]}

【分析要求】
请从以下6个维度进行评估：

1. **完整性** - 基本信息（姓名、联系方式、教育、工作经历）是否齐全
2. **格式规范性** - 格式是否统一、专业、易读
3. **内容质量** - 描述是否清晰、有说服力、无废话
4. **可量化成果** - 是否有具体数据支撑（提升X%、节省Y时间等）
5. **关键词匹配** - 识别硬技能（技术/工具）和软技能
6. **ATS友好度** - 是否容易被招聘系统识别（关键词布局、格式简洁度）

【输出要求】
请严格按照以下JSON格式返回，只返回JSON：
{{
    "score": 85,
    "overall_assessment": "一句话总体评价",
    "dimensions": {{
        "completeness": {{
            "score": 80,
            "issues": ["缺失的问题1"],
            "suggestions": ["改进建议1"]
        }},
        "format": {{
            "score": 85,
            "issues": ["格式问题1"],
            "suggestions": ["格式改进建议1"]
        }},
        "content": {{
            "score": 82,
            "issues": ["内容问题1"],
            "suggestions": ["内容改进建议1"]
        }},
        "quantifiable": {{
            "score": 75,
            "issues": ["可量化问题1"],
            "suggestions": ["如何量化成果"]
        }},
        "keywords": {{
            "hard_skills": ["硬技能1", "硬技能2"],
            "soft_skills": ["软技能1", "软技能2"],
            "missing_keywords": ["缺失的关键词1"],
            "suggestions": ["关键词优化建议"]
        }},
        "ats_friendly": {{
            "score": 78,
            "issues": ["ATS问题1"],
            "suggestions": ["ATS优化建议"]
        }}
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["问题1", "问题2"],
    "suggestions": ["可执行的改进建议1", "可执行的改进建议2"],
    "recommended_positions": ["适合的岗位方向1", "适合的岗位方向2"],
    "priority_actions": ["最优先做的1件事", "最优先做的2件事"]
}}

【评分标准】
- 90+：可直接投递大厂核心岗位
- 75-89：优化后可投递，适合大多数岗位
- 60-74：需要重点改进，建议针对性优化
- <60：建议大改或重写"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_analysis()
    
    def generate_optimization_suggestions(self, resume_text: str, analysis: dict) -> dict:
        """根据分析结果生成具体的简历优化建议"""
        prompt = f"""根据以下简历分析结果，生成具体的优化建议。

【原始简历摘要】
{resume_text[:4000]}

【分析结果】
{json.dumps(analysis, ensure_ascii=False, indent=2)}

【任务要求】
请生成具体可执行的简历优化建议，包括：
1. 每一条工作经历的改进建议（针对STAR法则）
2. 如何量化成果（给出具体的量化方法）
3. 如何补充缺失的关键词
4. 格式优化建议

【输出格式】
JSON格式：
{{
    "work_experience_suggestions": [
        {{
            "company": "公司名称",
            "original_description": "原始描述",
            "optimized_description": "优化后的描述",
            "improvement_points": ["改进点1", "改进点2"]
        }}
    ],
    "quantification_suggestions": [
        "如何量化成果的建议1",
        "如何量化成果的建议2"
    ],
    "keyword_suggestions": {{
        "to_add": ["需要添加的关键词1"],
        "to_highlight": ["需要突出显示的关键词1"]
    }},
    "format_suggestions": [
        "格式改进建议1"
    ],
    "overall_improvement_plan": "整体改进计划（100字以内）"
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.6)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def predict_interview_rate(self, resume_text: str, jd_text: str = None) -> dict:
        """预测简历通过面试筛选的概率"""
        prompt = f"""请评估这份简历通过面试筛选的概率。

【简历内容】
{resume_text[:6000]}

{'【目标岗位JD】' + jd_text[:2000] if jd_text else ''}

【评估维度】
1. 硬性条件匹配度（学历、经验年限、技能要求）
2. 软性条件匹配度（沟通、团队、抗压等）
3. 简历呈现效果（描述清晰度、重点突出度）
4. 与目标岗位的契合度

【输出格式】
JSON格式：
{{
    "interview_rate": 75,
    "interview_rate_label": "较高",
    "passing_factors": ["通过因素1", "通过因素2"],
    "risk_factors": ["风险因素1", "风险因素2"],
    "improvement_to_increase_rate": ["提升通过率的建议1"],
    "similar_success_cases": "类似背景候选人成功案例参考"
}}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def match_jd(self, resume_text: str, jd_text: str) -> dict:
        prompt = f"""[Precise Job Matching Analysis]

[Resume Summary]
{resume_text[:6000]}

[Target Job Description]
{jd_text[:4000]}

[Matching Analysis Requirements]
Please quickly evaluate:

1. **Matching Score** (0-100):
   - 90+: Highly matching, strongly recommend applying
   - 75-89: Basic matching, can apply
   - 60-74: Partial matching, resume needs targeted optimization
   - <60: Not recommended, continue applying for other positions

2. **Matched Items** (required by JD and present in resume)
3. **Missing Items** (required by JD but missing in resume, distinguish: trainable vs. hard requirement)
4. **Targeted Suggestions** (how to optimize resume to improve matching, max 3)

[Output Format]
Return JSON:
{{
    "match_score": 75,
    "matched_skills": ["matched skill 1", "matched skill 2"],
    "missing_skills": ["missing skill 1 (trainable/hard requirement)"],
    "matched_experiences": ["related experience"],
    "suggestions": ["specific improvement suggestion 1", "specific improvement suggestion 2"],
    "match_details": "one sentence summary of matching situation"
}}

[Important]
- Missing skills: mark "trainable" if can be learned through study; "hard requirement" if mandatory
- Suggestions should be specific and actionable, not empty words"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_match()
    
    def generate_interview_questions(self, resume_text: str, jd_text: str) -> dict:
        prompt = f"""[Interview Prep] - Generate questions based on your resume and target position

[Resume Highlights]
{resume_text[:6000]}

[Target Position]
{jd_text[:4000]}

[Generation Requirements]
As a senior interviewer, generate 12-15 high-frequency and precise interview questions:

**Question Distribution (must follow)**
- Self-introduction: 1 question (mandatory, 1-minute version)
- Job motivation: 2 questions (why choose us/this position)
- Deep dive: 3-4 questions (targeting resume projects and achievements)
- Technical/Ability: 3-4 questions (core skills required by position)
- Behavioral: 2 questions (teamwork/conflict handling/stress management)
- Open questions: 1 question (career planning/ask interviewer)

**Quality Standards**
Each question must include:
1. **question**: Real interview question
2. **answer_points**: 3-4 answer points (STAR method: Situation-Task-Action-Result)
3. **sample_answer**: Complete reference answer over 150 characters (customized for this candidate)
4. **tips**: 1 key interview tip

[Output Format]
JSON only:
{{
    "interview_questions": [
        {{
            "type": "Self-introduction",
            "question": "Please introduce yourself in 1 minute",
            "answer_points": ["background one sentence", "core competency", "matching point with position", "job motivation"],
            "sample_answer": "Hello, I am XX, graduated from XX University XX major. Past X years working/studying in XX field. My core competency is XX (related to position), achieved XX results in XX project using XX method (quantified). I am very interested in your company's XX business, believe my experience can bring XX value to the team.",
            "tips": "Keep under 1 minute, don't repeat resume content, highlight matching points with position"
        }}
    ]
}}

[Important]
- Reference answers must be customized for this candidate, not generic templates
- Technical questions should combine with specific technologies mentioned in resume
- Behavioral questions should combine with specific experiences in resume"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.7)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_questions()
    
    def generate_self_introduction(self, resume_text: str, jd_text: str) -> dict:
        prompt = f"""[Self-Introduction Customization] - Optimized for target position

[Your Resume]
{resume_text[:6000]}

[Target Position]
{jd_text[:4000]}

[Writing Requirements]
As a career consultant, generate 2 versions of self-introduction:

**1-Minute Concise Version (150-200 characters)**
- Opening: Name+current position/identity (1 sentence)
- Middle: Most relevant 2-3 experiences + core achievements (quantified), highlight matching points with target position (3-4 sentences)
- Closing: Job motivation + why choose this company/position (1-2 sentences)
- Goal: Make interviewer remember you, want to follow up

**3-Minute Detailed Version (400-600 characters)**
- Opening: Name+education background (1 sentence)
- Work experience: Timeline or skill-based, focus on experiences relevant to target position (5-6 sentences)
- Core abilities: Explain with specific cases (3-4, each with STAR method)
- Achievement display: Quantified data support (2-3 key achievements)
- Closing: Career planning + job motivation (2 sentences)

**Core Selling Points (3-5)**
Summarize 3-5 key selling points in self-introduction

[Output Format]
JSON:
{{
    "one_minute": "1-minute version (must be concise and powerful)",
    "three_minutes": "3-minute version (detailed experience showcase)",
    "key_points": ["core selling point 1", "core selling point 2", "core selling point 3"]
}}

[Important]
- Don't repeat resume, "add" resume information
- Every sentence should answer "why choose you"
- Use conversational language, suitable for interview delivery
- Should be able to speak naturally after memorizing, not like reciting"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.7)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_introduction()
    
    def _parse_json_response(self, response: str) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'interview_questions"\s*:\s*\[([\s\S]*?)\]', response)
            if json_match:
                try:
                    questions_str = "[" + json_match.group(1) + "]"
                    questions = json.loads(questions_str)
                    return {"interview_questions": questions}
                except json.JSONDecodeError:
                    pass
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            return {}
    
    def _get_default_analysis(self) -> dict:
        return {
            "score": 70,
            "strengths": ["Resume structure is clear"],
            "weaknesses": ["Consider adding more quantified data"],
            "suggestions": ["Optimize job descriptions", "Add project experience"],
            "recommended_positions": ["Suggest consulting specific position direction"]
        }
    
    def _get_default_match(self) -> dict:
        return {
            "match_score": 60,
            "matched_skills": [],
            "missing_skills": ["Please re-analyze after uploading resume and JD"],
            "matched_experiences": [],
            "suggestions": ["Ensure resume and JD information is complete"],
            "match_details": "Information incomplete, cannot accurately match"
        }
    
    def _get_default_questions(self) -> dict:
        return {
            "interview_questions": [
                {
                    "type": "自我介绍",
                    "question": "请简单介绍一下你自己",
                    "answer_points": ["基本信息", "工作经历", "核心竞争力"],
                    "sample_answer": "您好，我叫XXX，有X年工作经验...",
                    "tips": "简明扼要，突出与岗位的匹配度"
                }
            ]
        }
    
    def _get_default_introduction(self) -> dict:
        return {
            "one_minute": "请上传简历后生成自我介绍",
            "three_minutes": "请上传简历后生成自我介绍",
            "key_points": ["基本信息", "核心能力", "求职意向"]
        }


def get_api_stats() -> dict:
    config = get_api_config()
    return {
        "provider": api_stats['provider'] or config['provider_name'],
        "model": api_stats['model'] or config['model_name'],
        "total_calls": api_stats['total_calls'],
        "total_prompt_tokens": api_stats['total_prompt_tokens'],
        "total_completion_tokens": api_stats['total_completion_tokens'],
        "total_tokens": api_stats['total_tokens'],
        "last_call_time": api_stats['last_call_time'],
        "is_custom_key": config['is_custom']
    }


def reset_api_stats() -> dict:
    stats = api_stats.copy()
    api_stats['total_calls'] = 0
    api_stats['total_prompt_tokens'] = 0
    api_stats['total_completion_tokens'] = 0
    api_stats['total_tokens'] = 0
    api_stats['last_call_time'] = None
    return stats


def test_api_key(api_key: str, api_base_url: str = "", model_name: str = "") -> dict:
    test_url = api_base_url if api_base_url else "https://api.siliconflow.cn/v1"
    test_model = model_name if model_name else "Qwen/Qwen2.5-72B-Instruct"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": test_model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            f"{test_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return {"success": True, "message": "API Key is valid"}
        else:
            error_msg = "API Key is invalid"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
            except:
                error_msg = f"Error code: {response.status_code}"
            return {"success": False, "message": error_msg}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


ai_client = None


def get_ai_client() -> AIClient:
    """Get AI client singleton"""
    global ai_client
    if ai_client is None:
        ai_client = AIClient()
    else:
        ai_client.refresh_config()
    return ai_client
