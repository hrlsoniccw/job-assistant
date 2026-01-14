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
        prompt = f"""Please analyze the resume as a senior HR expert.

[Resume Content]
{resume_text[:8000]}

[Analysis Requirements]
Please evaluate quickly from 5 dimensions:

1. **Completeness** (2 seconds): Basic info complete (name, contact, education, work experience)
2. **Format Standards**: Unified, professional, easy to read
3. **Content Quality**: Clear, persuasive, no fluff
4. **Quantifiable Results**: Specific data support (e.g., improved X%, saved Y time)
5. **Keyword Matching**: Identify hard skills (technologies/tools) and soft skills

[Output Format]
Return JSON only, no other content:
{{
    "score": 85,
    "strengths": ["specific strength 1", "specific strength 2"],
    "weaknesses": ["specific issue 1", "specific issue 2"],
    "suggestions": ["actionable suggestion 1", "actionable suggestion 2"],
    "recommended_positions": ["matching position 1", "matching position 2"]
}}

[Scoring Standards]
- 90+: Ready for core positions at top companies
- 75-89: Ready to apply after optimization
- 60-74: Need key improvements, suggest targeted optimization
- <60: Major revision or rewrite recommended"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_analysis()
    
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
