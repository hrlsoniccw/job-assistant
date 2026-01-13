from utils.file_parser import (
    parse_resume,
    extract_contact_info,
    extract_skills,
    suggest_job_positions
)
from utils.ai_client import get_ai_client


DEFAULT_INTERVIEW_QUESTIONS = [
    {
        "type": "自我介绍",
        "question": "请简单介绍一下你自己，包括你的教育背景和工作经历。",
        "answer_points": ["姓名和学历", "工作年限和主要经历", "核心技能和优势", "为什么适合这个岗位"],
        "sample_answer": "您好，我叫XXX，毕业于XX大学XX专业，拥有X年工作经验。在之前的工作中，我主要负责XX工作，使用XX技术/技能完成了XX项目，取得了XX成果。我对这个岗位很感兴趣，因为我的背景和经验与贵公司的需求非常匹配。",
        "tips": "控制在一分钟以内，突出与岗位相关的经历，避免重复简历内容"
    },
    {
        "type": "岗位相关性",
        "question": "你为什么对我们公司这个岗位感兴趣？",
        "answer_points": ["对公司的了解", "岗位与个人发展的契合", "能为公司带来的价值"],
        "sample_answer": "我对贵公司一直有关注，贵公司在XX领域的发展非常迅速。我对这个岗位很感兴趣，因为该岗位的工作内容与我的专业背景和工作经验高度契合。我希望能加入贵公司，与团队一起创造更大的价值。",
        "tips": "展示对公司的了解，结合自己的职业规划回答"
    },
    {
        "type": "岗位相关性",
        "question": "你对这个岗位的工作内容有什么了解？",
        "answer_points": ["岗位职责的理解", "关键工作内容", "可能面临的挑战"],
        "sample_answer": "根据我对岗位JD的理解，该岗位主要负责XX工作，需要具备XX能力。核心工作包括XX、XX等。这个岗位的挑战在于需要平衡XX和XX，我相信凭借我的经验能够胜任。",
        "tips": "结合JD内容回答，展示你的认真准备"
    },
    {
        "type": "工作经历",
        "question": "请描述你最有成就感的一个项目或工作成果。",
        "answer_points": ["项目背景", "具体行动", "量化结果"],
        "sample_answer": "在XX项目中，我负责XX工作。面对XX挑战，我采用了XX方法，最终帮助团队实现了XX成果，为公司带来了XX价值。这个项目让我学会了XX，提升了XX能力。",
        "tips": "使用STAR法则（情境-任务-行动-结果），突出自己的贡献"
    },
    {
        "type": "工作经历",
        "question": "在你过去的工作中，遇到最大的挑战是什么？如何克服的？",
        "answer_points": ["挑战的具体描述", "采取的解决方案", "最终结果和学到的经验"],
        "sample_answer": "在之前的工作中，我遇到的最大挑战是XX。面对这个挑战，我通过XX方式来解决，包括XX和XX。最终不仅解决了问题，还为公司带来了XX收益。这个经历让我学会了XX。",
        "tips": "选择有代表性的挑战，展示你的问题解决能力"
    },
    {
        "type": "工作经历",
        "question": "请介绍一下你负责的最复杂的项目，你是如何协调资源和管理时间的？",
        "answer_points": ["项目复杂度", "资源协调方法", "时间管理策略"],
        "sample_answer": "我负责的XX项目涉及XX方面，是一个比较复杂的项目。为了确保项目顺利进行，我采用了XX方法进行资源协调，通过XX工具进行时间管理。最终项目按时交付，达到了XX目标。",
        "tips": "展示项目管理能力和执行力"
    },
    {
        "type": "技术能力",
        "question": "请介绍一下你最擅长的技术或技能，以及你是如何提升的？",
        "answer_points": ["技术名称和掌握程度", "学习途径", "实际应用案例"],
        "sample_answer": "我最擅长的技术是XX。我通过XX方式学习这门技术，包括XX课程、XX项目实践等。在实际工作中，我运用这项技术完成了XX任务，解决了XX问题。",
        "tips": "结合实际案例，展示你的学习能力和应用能力"
    },
    {
        "type": "技术能力",
        "question": "当你遇到不熟悉的技术或问题时，你会如何解决？",
        "answer_points": ["问题解决方法", "学习新技能的途径", "寻求帮助的方式"],
        "sample_answer": "遇到不熟悉的技术时，我会首先通过官方文档和教程了解基础知识，然后通过小项目进行实践。如果遇到难点，我会查阅技术博客、社区讨论，或者向有经验的同事请教。我的原则是先理解原理，再动手实践。",
        "tips": "展示你的学习能力和主动性"
    },
    {
        "type": "技术能力",
        "question": "你是如何保持技术更新和学习新知识的？",
        "answer_points": ["学习方法和渠道", "时间分配", "学习成果"],
        "sample_answer": "我通过多种方式保持技术更新：1）订阅技术博客和公众号；2）每周阅读技术书籍或文档；3）参与开源项目或技术社区；4）参加技术分享会和培训课程。我每周会花XX时间学习新技术。",
        "tips": "展示你的学习习惯和自律性"
    },
    {
        "type": "行为面试",
        "question": "请描述一次你与团队成员意见不合的经历，你是如何处理的？",
        "answer_points": ["冲突情境", "处理方式", "最终结果和反思"],
        "sample_answer": "在XX项目中，我与同事在XX问题上意见不合。我首先认真听取对方的观点，然后表达了我的想法和理由。最终我们通过讨论达成了一致，项目也顺利推进。这个经历让我学会了换位思考和有效沟通。",
        "tips": "展示你的沟通能力和团队协作精神"
    },
    {
        "type": "行为面试",
        "question": "请描述一次你工作压力很大的时候，你是如何处理的？",
        "answer_points": ["压力来源", "应对方法", "结果和收获"],
        "sample_answer": "在XX期间，我面临很大的工作压力，需要同时处理XX、XX等多个任务。我通过制定优先级清单、合理分配时间、适当寻求帮助等方式来应对。最终所有任务都按时完成，我也学会了更高效的时间管理。",
        "tips": "展示你的抗压能力和自我管理能力"
    },
    {
        "type": "开放问题",
        "question": "你未来3-5年的职业规划是什么？",
        "answer_points": ["短期目标", "长期目标", "与应聘岗位的关系"],
        "sample_answer": "短期内，我希望能够在XX领域深耕，提升自己的专业能力，成为该领域的专家。长期来看，我希望能够承担更大的责任，带领团队完成更有挑战性的项目。贵公司的发展方向与我的职业规划非常契合，我希望能够在这里实现这些目标。",
        "tips": "展示你的职业规划清晰且与公司发展相符"
    },
    {
        "type": "开放问题",
        "question": "除了技术能力外，你认为自己还有哪些优点可以胜任这个岗位？",
        "answer_points": ["软技能", "个人特质", "与岗位的匹配"],
        "sample_answer": "除了技术能力外，我认为我的沟通能力、团队协作精神和学习能力是我的优势。我善于与不同背景的人沟通，能够有效协调团队资源。同时，我具有较强的学习能力，能够快速适应新环境和新要求。",
        "tips": "结合岗位需求展示你的综合素质"
    }
]


class ResumeAnalyzer:
    """简历分析器"""
    
    def __init__(self):
        self.ai = get_ai_client()
    
    def analyze(self, resume_text: str) -> dict:
        """
        完整分析简历
        
        Args:
            resume_text: 简历纯文本
        
        Returns:
            分析结果字典
        """
        skills = extract_skills(resume_text)
        ai_analysis = self.ai.analyze_resume(resume_text)
        contact_info = extract_contact_info(resume_text)
        recommended_positions = suggest_job_positions(skills, [])
        
        result = {
            'contact_info': contact_info,
            'skills': skills,
            'recommended_positions': recommended_positions,
            'analysis': ai_analysis
        }
        
        return result
    
    def match_with_jd(self, resume_text: str, jd_text: str) -> dict:
        """
        分析简历与岗位的匹配度
        
        Args:
            resume_text: 简历纯文本
            jd_text: 岗位JD文本
        
        Returns:
            匹配结果
        """
        return self.ai.match_jd(resume_text, jd_text)
    
    def generate_interview_questions(self, resume_text: str, jd_text: str) -> dict:
        """
        生成面试题
        
        Args:
            resume_text: 简历纯文本
            jd_text: 岗位JD文本
        
        Returns:
            面试题列表（至少12道）
        """
        result = self.ai.generate_interview_questions(resume_text, jd_text)
        
        questions = result.get('interview_questions', [])
        
        if not questions or len(questions) < 12:
            result['interview_questions'] = DEFAULT_INTERVIEW_QUESTIONS
        
        return result
    
    def generate_self_introduction(self, resume_text: str, jd_text: str) -> dict:
        """
        生成自我介绍
        
        Args:
            resume_text: 简历纯文本
            jd_text: 岗位JD文本
        
        Returns:
            自我介绍内容
        """
        return self.ai.generate_self_introduction(resume_text, jd_text)
