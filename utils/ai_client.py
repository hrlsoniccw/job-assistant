import json
import requests
from datetime import datetime
from typing import Optional
from config import get_api_config

# 全局API统计
api_stats = {
    "total_calls": 0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_tokens": 0,
    "last_call_time": None,
    "provider": "",
    "model": ""
}


class AIClient:
    """AI客户端 - 支持动态API Key切换"""
    
    def __init__(self):
        self.api_config = get_api_config()
        self.update_headers()
        api_stats['provider'] = self.api_config['provider_name']
        api_stats['model'] = self.api_config['model_name']
    
    def update_headers(self):
        """更新请求头"""
        self.api_url = f"{self.api_config['api_base_url']}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_config['api_key']}",
            "Content-Type": "application/json"
        }
    
    def refresh_config(self):
        """刷新配置（用于切换API Key后）"""
        self.api_config = get_api_config()
        self.update_headers()
        api_stats['provider'] = self.api_config['provider_name']
        api_stats['model'] = self.api_config['model_name']
    
    def chat(self, messages: list, temperature: float = 0.7) -> Optional[str]:
        """
        发送聊天请求
        """
        payload = {
            "model": self.api_config['model_name'],
            "messages": messages,
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
                error_msg = f"API请求失败: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
                print(error_msg)
                return None
                
        except requests.exceptions.Timeout:
            print("API请求超时")
            return None
        except Exception as e:
            print(f"API请求异常: {e}")
            return None
    
    def analyze_resume(self, resume_text: str) -> dict:
        """分析简历"""
        prompt = f"""你是一个专业的HR和简历优化专家。请分析以下简历，找出其中的问题并提供改进建议。

简历内容：
{resume_text[:8000]}

请从以下几个维度进行分析：
1. 简历完整性：是否有缺失的重要信息
2. 格式规范性：格式是否统一、专业
3. 内容质量：描述是否清晰、有说服力
4. 可量化性：是否有具体的成果数据
5. 关键词匹配：简历中提到的技能和经验

请严格按照以下JSON格式返回分析结果（不要添加任何其他内容）：
{{
    "score": 85,
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "recommended_positions": ["适合的岗位方向1", "适合的岗位方向2"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_analysis()
    
    def match_jd(self, resume_text: str, jd_text: str) -> dict:
        """分析简历与岗位JD的匹配程度"""
        prompt = f"""你是一个专业的HR。请分析简历与岗位JD的匹配程度。

简历内容：
{resume_text[:6000]}

岗位JD：
{jd_text[:4000]}

请分析：
1. 匹配度评分（0-100）
2. 匹配项（简历中符合JD要求的点）
3. 缺失项（简历中缺少但JD要求的点）
4. 改进建议

请严格按照以下JSON格式返回：
{{
    "match_score": 75,
    "matched_skills": ["技能1", "技能2"],
    "missing_skills": ["技能3"],
    "matched_experiences": ["经验1"],
    "suggestions": ["建议1", "建议2"],
    "match_details": "详细说明匹配情况"
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.5)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_match()
    
    def generate_interview_questions(self, resume_text: str, jd_text: str) -> dict:
        """根据简历和岗位JD生成面试题"""
        prompt = f"""你是一个专业的面试官。请根据简历和岗位JD，生成12-15道面试题。

简历内容：
{resume_text[:6000]}

岗位JD：
{jd_text[:4000]}

请严格按照以下要求生成面试题：
1. 自我介绍（1道）
2. 岗位相关性（2-3道）
3. 工作经历（3-4道）
4. 技术/专业能力（3-4道）
5. 行为面试题（2-3道）
6. 开放问题（1-2道）

总共必须生成至少12道面试题，最多15道。

请严格按照以下JSON格式返回（必须返回完整的JSON数组）：
{{
    "interview_questions": [
        {{
            "type": "自我介绍",
            "question": "请简单介绍一下你自己",
            "answer_points": ["要点1", "要点2"],
            "sample_answer": "参考回答...",
            "tips": "注意事项"
        }},
        {{
            "type": "岗位相关性",
            "question": "你为什么对这个岗位感兴趣？",
            "answer_points": ["要点1", "要点2"],
            "sample_answer": "参考回答...",
            "tips": "注意事项"
        }}
    ]
}}

注意：
- interview_questions数组必须包含至少12个问题对象
- 每个问题必须有type、question、answer_points、sample_answer、tips这5个字段
- answer_points必须是数组格式["要点1", "要点2"]
- sample_answer要详细完整，至少100字以上
- tips要给出实用的面试技巧建议"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.7)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_questions()
    
    def generate_self_introduction(self, resume_text: str, jd_text: str) -> dict:
        """生成自我介绍"""
        prompt = f"""你是一个专业的职业顾问。请根据简历和岗位JD，生成一份专业的自我介绍。

简历内容：
{resume_text[:6000]}

岗位JD：
{jd_text[:4000]}

请生成两个版本的自我介绍：
1. 1分钟版本（200-300字）：简洁有力，突出与岗位的匹配度
2. 3分钟版本（500-800字）：详细展示经历和能力

请严格按照以下JSON格式返回：
{{
    "one_minute": "1分钟版本的自我介绍...",
    "three_minutes": "3分钟版本的自我介绍...",
    "key_points": ["核心要点1", "核心要点2"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.7)
        
        if response:
            return self._parse_json_response(response)
        return self._get_default_introduction()
    
    def _parse_json_response(self, response: str) -> dict:
        """解析JSON响应"""
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
            "strengths": ["简历结构清晰"],
            "weaknesses": ["建议添加更多量化数据"],
            "suggestions": ["建议优化工作描述", "建议补充项目经验"],
            "recommended_positions": ["建议咨询具体岗位方向"]
        }
    
    def _get_default_match(self) -> dict:
        return {
            "match_score": 60,
            "matched_skills": [],
            "missing_skills": ["请上传简历和JD后重新分析"],
            "matched_experiences": [],
            "suggestions": ["请确保简历和JD信息完整"],
            "match_details": "信息不完整，无法准确匹配"
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
    """获取API使用统计"""
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
    """重置API统计"""
    stats = api_stats.copy()
    api_stats['total_calls'] = 0
    api_stats['total_prompt_tokens'] = 0
    api_stats['total_completion_tokens'] = 0
    api_stats['total_tokens'] = 0
    api_stats['last_call_time'] = None
    return stats


def test_api_key(api_key: str, api_base_url: str = "", model_name: str = "") -> dict:
    """测试API Key是否有效"""
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
            return {"success": True, "message": "API Key有效"}
        else:
            error_msg = "API Key无效"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', response.text)
            except:
                error_msg = f"错误码: {response.status_code}"
            return {"success": False, "message": error_msg}
    except Exception as e:
        return {"success": False, "message": f"连接失败: {str(e)}"}


# 全局AI客户端实例
ai_client = None


def get_ai_client() -> AIClient:
    """获取AI客户端单例"""
    global ai_client
    if ai_client is None:
        ai_client = AIClient()
    else:
        ai_client.refresh_config()
    return ai_client
