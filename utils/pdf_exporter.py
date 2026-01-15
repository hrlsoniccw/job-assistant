import os
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

try:
    from utils.file_parser import ResumeData
except ImportError:
    ResumeData = None


COLORS = {
    'primary': colors.HexColor('#667eea'),
    'secondary': colors.HexColor('#764ba2'),
    'dark': colors.HexColor('#1e293b'),
    'light': colors.HexColor('#f1f5f9'),
    'gray': colors.HexColor('#64748b'),
    'success': colors.HexColor('#10b981'),
    'white': colors.white,
    'background': colors.HexColor('#f8fafc'),
}


def get_base_styles():
    """获取基础样式表"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='ResumeTitle',
        parent=styles['Title'],
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=COLORS['primary'],
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=COLORS['secondary'],
        spaceAfter=12,
        spaceBefore=16,
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=COLORS['dark'],
        spaceAfter=8,
        spaceBefore=12,
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=COLORS['dark'],
        leading=14,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeNormalSmall',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=COLORS['gray'],
        leading=12,
        spaceAfter=3
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeBold',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=COLORS['dark'],
        leading=14,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeMeta',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=COLORS['gray'],
        alignment=TA_CENTER,
        spaceAfter=4
    ))
    
    return styles


def format_date(date_str: str) -> str:
    """标准化日期格式"""
    if not date_str:
        return ""
    date_str = date_str.strip()
    if date_str in ['至今', '现在', 'Present', 'Current']:
        return "至今"
    try:
        for fmt in ['%Y-%m', '%Y/%m', '%Y.%m', '%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y.%m')
            except ValueError:
                continue
        return date_str
    except:
        return date_str


class BaseResumeExporter:
    """简历导出器基类"""
    
    def __init__(self):
        self.styles = get_base_styles()
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        self.content_width = self.page_width - 2 * self.margin
    
    def generate(self, resume_data: Dict, output_path: str) -> bool:
        """生成PDF文件"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        story = self.build_content(resume_data)
        
        try:
            doc.build(story)
            return True
        except Exception as e:
            print(f"生成PDF失败: {e}")
            return False
    
    def generate_to_bytes(self, resume_data: Dict) -> bytes:
        """生成PDF到字节流"""
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        story = self.build_content(resume_data)
        doc.build(story)
        
        return buffer.getvalue()
    
    def build_content(self, resume_data: Dict) -> List:
        """构建PDF内容（子类实现）"""
        raise NotImplementedError
    
    def add_header(self, resume_data: Dict) -> List:
        """添加头部信息"""
        elements = []
        
        name = resume_data.get('name', '')
        job_title = resume_data.get('job_title', '')
        
        if name:
            elements.append(Paragraph(name, self.styles['ResumeTitle']))
        
        if job_title:
            elements.append(Paragraph(job_title, self.styles['ResumeMeta']))
        
        contact_info = []
        if resume_data.get('phone'):
            contact_info.append(f"📱 {resume_data['phone']}")
        if resume_data.get('email'):
            contact_info.append(f"✉️ {resume_data['email']}")
        if resume_data.get('location'):
            contact_info.append(f"📍 {resume_data['location']}")
        
        if contact_info:
            elements.append(Paragraph(" | ".join(contact_info), self.styles['ResumeMeta']))
        
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(
            width="30%",
            thickness=2,
            color=COLORS['primary'],
            spaceBefore=6,
            spaceAfter=12,
            hAlign='CENTER'
        ))
        
        return elements
    
    def add_section(self, title: str, content: List) -> List:
        """添加章节"""
        elements = []
        elements.append(Paragraph(title, self.styles['ResumeHeading1']))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS['light_gray'] if hasattr(colors, 'light_gray') else colors.HexColor('#e2e8f0'),
            spaceBefore=3,
            spaceAfter=8
        ))
        elements.extend(content)
        return elements


class ModernMinimalExporter(BaseResumeExporter):
    """现代简约风格 - 清新简洁"""
    
    def __init__(self):
        super().__init__()
        self.margin = 15 * mm
    
    def build_content(self, resume_data: Dict) -> List:
        story = []
        
        story.extend(self.add_header(resume_data))
        
        if resume_data.get('self_introduction'):
            story.extend(self.add_introduction(resume_data['self_introduction']))
        
        if resume_data.get('skills'):
            story.extend(self.add_skills(resume_data['skills']))
        
        if resume_data.get('work_experience'):
            story.extend(self.add_work_experience(resume_data['work_experience']))
        
        if resume_data.get('project_experience'):
            story.extend(self.add_project_experience(resume_data['project_experience']))
        
        if resume_data.get('education'):
            story.extend(self.add_education(resume_data['education']))
        
        if resume_data.get('certificates'):
            story.extend(self.add_certificates(resume_data['certificates']))
        
        if resume_data.get('awards'):
            story.extend(self.add_awards(resume_data['awards']))
        
        return story
    
    def add_introduction(self, intro: str) -> List:
        elements = []
        elements.append(Paragraph("个人简介", self.styles['ResumeHeading2']))
        elements.append(Paragraph(intro.strip(), self.styles['ResumeNormal']))
        elements.append(Spacer(1, 10))
        return elements
    
    def add_skills(self, skills: List) -> List:
        elements = []
        elements.append(Paragraph("专业技能", self.styles['ResumeHeading2']))
        
        if len(skills) <= 10:
            skills_text = " | ".join(skills)
        else:
            skills_text = " | ".join(skills[:10]) + "..."
        
        elements.append(Paragraph(skills_text, self.styles['ResumeNormal']))
        elements.append(Spacer(1, 10))
        return elements
    
    def add_work_experience(self, experiences: List) -> List:
        elements = []
        elements.append(Paragraph("工作经历", self.styles['ResumeHeading2']))
        
        for exp in experiences:
            elements.extend(self.format_work_item(exp))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def format_work_item(self, exp: Dict) -> List:
        items = []
        
        title_row = []
        if exp.get('company'):
            title_row.append(Paragraph(exp['company'], self.styles['ResumeBold']))
        if exp.get('position'):
            date = f"{format_date(exp.get('start_date', ''))} - {format_date(exp.get('end_date', ''))}"
            title_row.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        if title_row:
            title_table = Table([title_row], colWidths=[None, 100])
            title_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            items.append(title_table)
        
        if exp.get('position'):
            items.append(Paragraph(exp['position'], self.styles['ResumeNormalSmall']))
        
        if exp.get('description'):
            desc = exp['description']
            if len(desc) > 500:
                desc = desc[:500] + "..."
            items.append(Paragraph(desc, self.styles['ResumeNormal']))
        
        if exp.get('achievements'):
            for ach in exp['achievements'][:3]:
                items.append(Paragraph(f"• {ach}", self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_project_experience(self, projects: List) -> List:
        elements = []
        elements.append(Paragraph("项目经历", self.styles['ResumeHeading2']))
        
        for proj in projects:
            elements.extend(self.format_project_item(proj))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def format_project_item(self, proj: Dict) -> List:
        items = []
        
        title_row = []
        if proj.get('name'):
            title_row.append(Paragraph(proj['name'], self.styles['ResumeBold']))
        date = f"{format_date(proj.get('start_date', ''))} - {format_date(proj.get('end_date', ''))}"
        title_row.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        if title_row:
            title_table = Table([title_row], colWidths=[None, 100])
            title_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            items.append(title_table)
        
        if proj.get('role'):
            items.append(Paragraph(f"职责: {proj['role']}", self.styles['ResumeNormalSmall']))
        
        if proj.get('tech_stack'):
            items.append(Paragraph(f"技术: {' | '.join(proj['tech_stack'][:8])}", self.styles['ResumeNormalSmall']))
        
        if proj.get('description'):
            desc = proj['description']
            if len(desc) > 300:
                desc = desc[:300] + "..."
            items.append(Paragraph(desc, self.styles['ResumeNormal']))
        
        return items
    
    def add_education(self, education: List) -> List:
        elements = []
        elements.append(Paragraph("教育背景", self.styles['ResumeHeading2']))
        
        for edu in education:
            elements.extend(self.format_education_item(edu))
            elements.append(Spacer(1, 6))
        
        return elements
    
    def format_education_item(self, edu: Dict) -> List:
        items = []
        
        title_row = []
        if edu.get('school'):
            title_row.append(Paragraph(edu['school'], self.styles['ResumeBold']))
        date = f"{format_date(edu.get('start_date', ''))} - {format_date(edu.get('end_date', ''))}"
        title_row.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        if title_row:
            title_table = Table([title_row], colWidths=[None, 100])
            title_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            items.append(title_table)
        
        if edu.get('degree') or edu.get('major'):
            degree_major = []
            if edu.get('degree'):
                degree_major.append(edu['degree'])
            if edu.get('major'):
                degree_major.append(edu['major'])
            items.append(Paragraph(" | ".join(degree_major), self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_certificates(self, certificates: List) -> List:
        if not certificates:
            return []
        
        elements = []
        elements.append(Paragraph("证书资质", self.styles['ResumeHeading2']))
        cert_text = " | ".join(certificates[:6])
        elements.append(Paragraph(cert_text, self.styles['ResumeNormal']))
        elements.append(Spacer(1, 8))
        return elements
    
    def add_awards(self, awards: List) -> List:
        if not awards:
            return []
        
        elements = []
        elements.append(Paragraph("荣誉奖励", self.styles['ResumeHeading2']))
        for award in awards[:5]:
            elements.append(Paragraph(f"• {award}", self.styles['ResumeNormal']))
        elements.append(Spacer(1, 8))
        return elements


class BusinessProfessionalExporter(BaseResumeExporter):
    """商务专业风格 - 经典稳重"""
    
    def __init__(self):
        super().__init__()
        self.margin = 18 * mm
    
    def build_content(self, resume_data: Dict) -> List:
        story = []
        
        story.extend(self.add_header(resume_data))
        story.append(Spacer(1, 15))
        
        if resume_data.get('work_experience'):
            story.extend(self.add_work_experience(resume_data['work_experience']))
        
        if resume_data.get('project_experience'):
            story.extend(self.add_project_experience(resume_data['project_experience']))
        
        if resume_data.get('education'):
            story.extend(self.add_education(resume_data['education']))
        
        if resume_data.get('skills'):
            story.extend(self.add_skills(resume_data['skills']))
        
        if resume_data.get('certificates') or resume_data.get('awards'):
            story.extend(self.add_additional_info(resume_data))
        
        return story
    
    def add_work_experience(self, experiences: List) -> List:
        elements = []
        elements.append(Paragraph("工作经历", self.styles['ResumeHeading1']))
        
        for exp in experiences:
            elements.extend(self.format_work_item(exp))
            elements.append(Spacer(1, 12))
        
        return elements
    
    def format_work_item(self, exp: Dict) -> List:
        items = []
        
        if exp.get('company'):
            items.append(Paragraph(exp['company'], self.styles['ResumeBold']))
        
        if exp.get('position'):
            date = f"{format_date(exp.get('start_date', ''))} - {format_date(exp.get('end_date', ''))}"
            items.append(Paragraph(f"{exp['position']} | {date}", self.styles['ResumeNormalSmall']))
        elif exp.get('start_date'):
            date = f"{format_date(exp.get('start_date', ''))} - {format_date(exp.get('end_date', ''))}"
            items.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        if exp.get('description'):
            items.append(Paragraph(exp['description'].strip(), self.styles['ResumeNormal']))
        
        if exp.get('achievements'):
            for ach in exp['achievements']:
                items.append(Paragraph(f"◆ {ach}", self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_project_experience(self, projects: List) -> List:
        elements = []
        elements.append(Paragraph("项目经验", self.styles['ResumeHeading1']))
        
        for proj in projects:
            elements.extend(self.format_project_item(proj))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def format_project_item(self, proj: Dict) -> List:
        items = []
        
        if proj.get('name'):
            items.append(Paragraph(proj['name'], self.styles['ResumeBold']))
        
        role_date = []
        if proj.get('role'):
            role_date.append(proj['role'])
        if proj.get('start_date'):
            date = f"{format_date(proj.get('start_date', ''))} - {format_date(proj.get('end_date', ''))}"
            role_date.append(date)
        if role_date:
            items.append(Paragraph(" | ".join(role_date), self.styles['ResumeNormalSmall']))
        
        if proj.get('tech_stack'):
            items.append(Paragraph(f"技术栈：{' | '.join(proj['tech_stack'][:6])}", self.styles['ResumeNormalSmall']))
        
        if proj.get('description'):
            items.append(Paragraph(proj['description'].strip(), self.styles['ResumeNormal']))
        
        return items
    
    def add_education(self, education: List) -> List:
        elements = []
        elements.append(Paragraph("教育背景", self.styles['ResumeHeading1']))
        
        for edu in education:
            elements.extend(self.format_education_item(edu))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def format_education_item(self, edu: Dict) -> List:
        items = []
        
        if edu.get('school'):
            items.append(Paragraph(edu['school'], self.styles['ResumeBold']))
        
        info = []
        if edu.get('degree'):
            info.append(edu['degree'])
        if edu.get('major'):
            info.append(edu['major'])
        if info:
            items.append(Paragraph(" | ".join(info), self.styles['ResumeNormalSmall']))
        
        if edu.get('start_date'):
            date = f"{format_date(edu.get('start_date', ''))} - {format_date(edu.get('end_date', ''))}"
            items.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_skills(self, skills: List) -> List:
        elements = []
        elements.append(Paragraph("专业技能", self.styles['ResumeHeading1']))
        
        chunk_size = 6
        for i in range(0, len(skills), chunk_size):
            chunk = skills[i:i+chunk_size]
            elements.append(Paragraph(" • ".join(chunk), self.styles['ResumeNormal']))
        
        elements.append(Spacer(1, 10))
        return elements
    
    def add_additional_info(self, resume_data: Dict) -> List:
        elements = []
        elements.append(Paragraph("其他信息", self.styles['ResumeHeading1']))
        
        if resume_data.get('certificates'):
            elements.append(Paragraph("证书：", self.styles['ResumeBold']))
            for cert in resume_data['certificates'][:4]:
                elements.append(Paragraph(f"• {cert}", self.styles['ResumeNormalSmall']))
        
        if resume_data.get('awards'):
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("荣誉：", self.styles['ResumeBold']))
            for award in resume_data['awards'][:4]:
                elements.append(Paragraph(f"• {award}", self.styles['ResumeNormalSmall']))
        
        return elements


class CreativeDesignExporter(BaseResumeExporter):
    """创意设计风格 - 突出个性"""
    
    def __init__(self):
        super().__init__()
        self.margin = 15 * mm
        self.sidebar_width = 60 * mm
        self.main_width = self.page_width - self.margin * 2 - self.sidebar_width - 5 * mm
    
    def build_content(self, resume_data: Dict) -> List:
        story = []
        
        story.extend(self.add_creative_header(resume_data))
        
        table = Table(
            [[self.build_sidebar(resume_data), self.build_main_content(resume_data)]],
            colWidths=[self.sidebar_width, self.main_width]
        )
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ]))
        
        story.append(table)
        
        return story
    
    def add_creative_header(self, resume_data: Dict) -> List:
        elements = []
        
        name = resume_data.get('name', '')
        if name:
            elements.append(Paragraph(
                name.upper(),
                ParagraphStyle(
                    name='CreativeName',
                    fontSize=28,
                    fontName='Helvetica-Bold',
                    textColor=COLORS['white'],
                    spaceAfter=8
                )
            ))
        
        job_title = resume_data.get('job_title', '')
        if job_title:
            elements.append(Paragraph(
                job_title,
                ParagraphStyle(
                    name='CreativeTitle',
                    fontSize=14,
                    fontName='Helvetica',
                    textColor=COLORS['light'],
                    spaceAfter=0
                )
            ))
        
        return elements
    
    def build_sidebar(self, resume_data: Dict) -> List:
        elements = []
        
        elements.append(Spacer(1, 20))
        
        contact_title = Paragraph("联系方式", self.styles['ResumeHeading2'])
        elements.append(contact_title)
        
        if resume_data.get('phone'):
            elements.append(Paragraph(f"📱 {resume_data['phone']}", self.styles['ResumeNormalSmall']))
        if resume_data.get('email'):
            elements.append(Paragraph(f"✉️ {resume_data['email']}", self.styles['ResumeNormalSmall']))
        if resume_data.get('location'):
            elements.append(Paragraph(f"📍 {resume_data['location']}", self.styles['ResumeNormalSmall']))
        
        elements.append(Spacer(1, 20))
        
        if resume_data.get('skills'):
            elements.append(Paragraph("技能专长", self.styles['ResumeHeading2']))
            for skill in resume_data['skills'][:12]:
                elements.append(Paragraph(f"▸ {skill}", self.styles['ResumeNormalSmall']))
        
        elements.append(Spacer(1, 20))
        
        if resume_data.get('certificates'):
            elements.append(Paragraph("证书资质", self.styles['ResumeHeading2']))
            for cert in resume_data['certificates'][:5]:
                elements.append(Paragraph(f"▸ {cert}", self.styles['ResumeNormalSmall']))
        
        elements.append(Spacer(1, 20))
        
        if resume_data.get('awards'):
            elements.append(Paragraph("荣誉奖励", self.styles['ResumeHeading2']))
            for award in resume_data['awards'][:5]:
                elements.append(Paragraph(f"★ {award}", self.styles['ResumeNormalSmall']))
        
        return elements
    
    def build_main_content(self, resume_data: Dict) -> List:
        elements = []
        
        if resume_data.get('self_introduction'):
            elements.append(Paragraph("关于我", self.styles['ResumeHeading1']))
            elements.append(Paragraph(resume_data['self_introduction'].strip(), self.styles['ResumeNormal']))
            elements.append(Spacer(1, 15))
        
        if resume_data.get('work_experience'):
            elements.append(Paragraph("工作经历", self.styles['ResumeHeading1']))
            for exp in resume_data['work_experience'][:4]:
                elements.extend(self.format_work_item(exp))
                elements.append(Spacer(1, 10))
            elements.append(Spacer(1, 10))
        
        if resume_data.get('project_experience'):
            elements.append(Paragraph("项目作品", self.styles['ResumeHeading1']))
            for proj in resume_data['project_experience'][:4]:
                elements.extend(self.format_project_item(proj))
                elements.append(Spacer(1, 8))
            elements.append(Spacer(1, 10))
        
        if resume_data.get('education'):
            elements.append(Paragraph("教育背景", self.styles['ResumeHeading1']))
            for edu in resume_data['education'][:2]:
                elements.extend(self.format_education_item(edu))
                elements.append(Spacer(1, 6))
        
        return elements
    
    def format_work_item(self, exp: Dict) -> List:
        items = []
        
        if exp.get('company'):
            items.append(Paragraph(exp['company'], self.styles['ResumeBold']))
        
        if exp.get('position'):
            date = f"{format_date(exp.get('start_date', ''))} - {format_date(exp.get('end_date', ''))}"
            items.append(Paragraph(f"{exp['position']} | {date}", self.styles['ResumeNormalSmall']))
        
        if exp.get('description'):
            desc = exp['description'][:300]
            items.append(Paragraph(desc, self.styles['ResumeNormal']))
        
        return items
    
    def format_project_item(self, proj: Dict) -> List:
        items = []
        
        if proj.get('name'):
            items.append(Paragraph(proj['name'], self.styles['ResumeBold']))
        
        if proj.get('role'):
            items.append(Paragraph(proj['role'], self.styles['ResumeNormalSmall']))
        
        if proj.get('tech_stack'):
            items.append(Paragraph(f"[{' | '.join(proj['tech_stack'][:5])}]", self.styles['ResumeNormalSmall']))
        
        if proj.get('description'):
            desc = proj['description'][:200]
            items.append(Paragraph(desc, self.styles['ResumeNormal']))
        
        return items
    
    def format_education_item(self, edu: Dict) -> List:
        items = []
        
        if edu.get('school'):
            items.append(Paragraph(edu['school'], self.styles['ResumeBold']))
        
        info = []
        if edu.get('degree'):
            info.append(edu['degree'])
        if edu.get('major'):
            info.append(edu['major'])
        if info:
            items.append(Paragraph(" | ".join(info), self.styles['ResumeNormalSmall']))
        
        return items


class ClassicTraditionalExporter(BaseResumeExporter):
    """经典传统风格 - 正式稳重"""
    
    def __init__(self):
        super().__init__()
        self.margin = 20 * mm
    
    def build_content(self, resume_data: Dict) -> List:
        story = []
        
        story.extend(self.add_header(resume_data))
        story.append(Spacer(1, 20))
        
        if resume_data.get('self_introduction'):
            story.extend(self.add_introduction(resume_data['self_introduction']))
        
        if resume_data.get('education'):
            story.extend(self.add_education(resume_data['education']))
        
        if resume_data.get('work_experience'):
            story.extend(self.add_work_experience(resume_data['work_experience']))
        
        if resume_data.get('project_experience'):
            story.extend(self.add_projects(resume_data['project_experience']))
        
        if resume_data.get('skills'):
            story.extend(self.add_skills(resume_data['skills']))
        
        return story
    
    def add_header(self, resume_data: Dict) -> List:
        elements = []
        
        name = resume_data.get('name', '')
        if name:
            elements.append(Paragraph(
                name,
                ParagraphStyle(
                    name='ClassicName',
                    fontSize=22,
                    fontName='Times-Bold',
                    textColor=colors.black,
                    alignment=TA_CENTER,
                    spaceAfter=10
                )
            ))
        
        job_title = resume_data.get('job_title', '')
        if job_title:
            elements.append(Paragraph(
                job_title,
                ParagraphStyle(
                    name='ClassicTitle',
                    fontSize=12,
                    fontName='Times-Roman',
                    textColor=colors.darkgray,
                    alignment=TA_CENTER,
                    spaceAfter=8
                )
            ))
        
        contact_info = []
        if resume_data.get('phone'):
            contact_info.append(f"电话: {resume_data['phone']}")
        if resume_data.get('email'):
            contact_info.append(f"邮箱: {resume_data['email']}")
        if resume_data.get('location'):
            contact_info.append(f"地点: {resume_data['location']}")
        
        if contact_info:
            elements.append(Paragraph(" | ".join(contact_info), self.styles['ResumeMeta']))
        
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black,
            spaceBefore=5,
            spaceAfter=10
        ))
        
        return elements
    
    def add_introduction(self, intro: str) -> List:
        elements = []
        elements.append(Paragraph("个人概述", self.styles['ResumeHeading2']))
        elements.append(Paragraph(intro.strip(), self.styles['ResumeNormal']))
        elements.append(Spacer(1, 12))
        return elements
    
    def add_education(self, education: List) -> List:
        elements = []
        elements.append(Paragraph("教育经历", self.styles['ResumeHeading2']))
        
        for edu in education:
            elements.extend(self.format_edu_item(edu))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def format_edu_item(self, edu: Dict) -> List:
        items = []
        
        school = edu.get('school', '')
        degree_major = []
        if edu.get('degree'):
            degree_major.append(edu['degree'])
        if edu.get('major'):
            degree_major.append(edu['major'])
        
        if school:
            items.append(Paragraph(f"{school} {' | '.join(degree_major)}", self.styles['ResumeBold']))
        
        date = f"{format_date(edu.get('start_date', ''))} - {format_date(edu.get('end_date', ''))}"
        if date:
            items.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_work_experience(self, experiences: List) -> List:
        elements = []
        elements.append(Paragraph("工作经验", self.styles['ResumeHeading2']))
        
        for exp in experiences:
            elements.extend(self.format_work_item(exp))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def format_work_item(self, exp: Dict) -> List:
        items = []
        
        company = exp.get('company', '')
        position = exp.get('position', '')
        date = f"{format_date(exp.get('start_date', ''))} - {format_date(exp.get('end_date', ''))}"
        
        if company:
            header = f"{company} | {position}" if position else company
            items.append(Paragraph(header, self.styles['ResumeBold']))
        
        if date:
            items.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        if exp.get('description'):
            items.append(Paragraph(exp['description'].strip(), self.styles['ResumeNormal']))
        
        return items
    
    def add_projects(self, projects: List) -> List:
        elements = []
        elements.append(Paragraph("项目经验", self.styles['ResumeHeading2']))
        
        for proj in projects[:4]:
            elements.extend(self.format_project_item(proj))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def format_project_item(self, proj: Dict) -> List:
        items = []
        
        name = proj.get('name', '')
        role = proj.get('role', '')
        date = f"{format_date(proj.get('start_date', ''))} - {format_date(proj.get('end_date', ''))}"
        
        if name:
            header = f"{name} ({role})" if role else name
            items.append(Paragraph(header, self.styles['ResumeBold']))
        
        if date:
            items.append(Paragraph(date, self.styles['ResumeNormalSmall']))
        
        if proj.get('description'):
            desc = proj['description'][:400]
            items.append(Paragraph(desc, self.styles['ResumeNormal']))
        
        return items
    
    def add_skills(self, skills: List) -> List:
        elements = []
        elements.append(Paragraph("专业技能", self.styles['ResumeHeading2']))
        
        for i in range(0, len(skills), 8):
            chunk = skills[i:i+8]
            elements.append(Paragraph(" • ".join(chunk), self.styles['ResumeNormal']))
        
        elements.append(Spacer(1, 10))
        return elements


class CompactConciseExporter(BaseResumeExporter):
    """紧凑简洁风格 - 信息密度高"""
    
    def __init__(self):
        super().__init__()
        self.margin = 12 * mm
        self.page_width, self.page_height = A4
    
    def build_content(self, resume_data: Dict) -> List:
        story = []
        
        story.extend(self.add_header(resume_data))
        
        if resume_data.get('skills'):
            story.extend(self.add_skills(resume_data['skills']))
        
        if resume_data.get('work_experience'):
            story.extend(self.add_work_experience(resume_data['work_experience']))
        
        if resume_data.get('project_experience'):
            story.extend(self.add_projects(resume_data['project_experience']))
        
        if resume_data.get('education'):
            story.extend(self.add_education(resume_data['education']))
        
        return story
    
    def add_header(self, resume_data: Dict) -> List:
        elements = []
        
        name = resume_data.get('name', '')
        job_title = resume_data.get('job_title', '')
        
        if name:
            elements.append(Paragraph(
                name.upper(),
                ParagraphStyle(
                    name='CompactName',
                    fontSize=20,
                    fontName='Helvetica-Bold',
                    textColor=COLORS['primary'],
                    spaceAfter=4
                )
            ))
        
        if job_title:
            elements.append(Paragraph(job_title, self.styles['ResumeNormalSmall']))
        
        contact = []
        if resume_data.get('phone'):
            contact.append(resume_data['phone'])
        if resume_data.get('email'):
            contact.append(resume_data['email'])
        if resume_data.get('location'):
            contact.append(resume_data['location'])
        
        if contact:
            elements.append(Paragraph(" | ".join(contact), self.styles['ResumeMeta']))
        
        elements.append(Spacer(1, 8))
        
        return elements
    
    def add_skills(self, skills: List) -> List:
        elements = []
        elements.append(Paragraph("【技能】" + " | ".join(skills[:15]), self.styles['ResumeNormal']))
        elements.append(Spacer(1, 6))
        return elements
    
    def add_work_experience(self, experiences: List) -> List:
        elements = []
        elements.append(Paragraph("【工作经历】", self.styles['ResumeBold']))
        
        for exp in experiences[:5]:
            elements.extend(self.format_work_item(exp))
            elements.append(Spacer(1, 4))
        
        return elements
    
    def format_work_item(self, exp: Dict) -> List:
        items = []
        
        company = exp.get('company', '')
        position = exp.get('position', '')
        date = f"{format_date(exp.get('start_date', ''))}-{format_date(exp.get('end_date', ''))}"
        
        header = []
        if company:
            header.append(company)
        if position:
            header.append(position)
        if date:
            header.append(date)
        
        if header:
            items.append(Paragraph(" • ".join(header), self.styles['ResumeNormalSmall']))
        
        if exp.get('achievements'):
            for ach in exp['achievements'][:2]:
                items.append(Paragraph(f"  ▶ {ach[:80]}", self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_projects(self, projects: List) -> List:
        elements = []
        elements.append(Paragraph("【项目经历】", self.styles['ResumeBold']))
        
        for proj in projects[:3]:
            elements.extend(self.format_project_item(proj))
            elements.append(Spacer(1, 4))
        
        return elements
    
    def format_project_item(self, proj: Dict) -> List:
        items = []
        
        name = proj.get('name', '')
        role = proj.get('role', '')
        
        if name:
            header = f"{name} ({role})" if role else name
            items.append(Paragraph(header, self.styles['ResumeNormalSmall']))
        
        if proj.get('tech_stack'):
            items.append(Paragraph(f"  [{', '.join(proj['tech_stack'][:4])}]", self.styles['ResumeNormalSmall']))
        
        return items
    
    def add_education(self, education: List) -> List:
        elements = []
        elements.append(Paragraph("【教育背景】", self.styles['ResumeBold']))
        
        for edu in education[:2]:
            school = edu.get('school', '')
            degree = edu.get('degree', '')
            major = edu.get('major', '')
            date = f"{format_date(edu.get('start_date', ''))}-{format_date(edu.get('end_date', ''))}"
            
            info = []
            if school:
                info.append(school)
            if degree or major:
                info.append(f"{degree} {major}" if degree else major)
            if date:
                info.append(date)
            
            if info:
                elements.append(Paragraph(" • ".join(info), self.styles['ResumeNormalSmall']))
        
        return elements


EXPORTERS = {
    'modern': ModernMinimalExporter,
    'business': BusinessProfessionalExporter,
    'creative': CreativeDesignExporter,
    'classic': ClassicTraditionalExporter,
    'compact': CompactConciseExporter,
}


def export_resume(resume_data: Dict, output_path: str, template: str = 'modern') -> bool:
    """导出简历为PDF"""
    exporter_class = EXPORTERS.get(template, EXPORTERS['modern'])
    exporter = exporter_class()
    return exporter.generate(resume_data, output_path)


def export_resume_to_bytes(resume_data: Dict, template: str = 'modern') -> bytes:
    """导出简历为PDF字节流"""
    exporter_class = EXPORTERS.get(template, EXPORTERS['modern'])
    exporter = exporter_class()
    return exporter.generate_to_bytes(resume_data)


def get_available_templates() -> List[Dict]:
    """获取可用模板列表"""
    return [
        {
            'id': 'modern',
            'name': '现代简约',
            'description': '清新简洁的设计，适合技术岗位',
            'preview': 'modern'
        },
        {
            'id': 'business',
            'name': '商务专业',
            'description': '经典稳重的设计，适合投行/咨询',
            'preview': 'business'
        },
        {
            'id': 'creative',
            'name': '创意设计',
            'description': '突出个性的设计，适合设计/产品',
            'preview': 'creative'
        },
        {
            'id': 'classic',
            'name': '经典传统',
            'description': '正式稳重风格，适合外企/国企',
            'preview': 'classic'
        },
        {
            'id': 'compact',
            'name': '紧凑简洁',
            'description': '信息密度高，适合经历丰富者',
            'preview': 'compact'
        }
    ]


def convert_resume_to_dict(resume: object) -> Dict:
    """将ResumeData对象转换为字典"""
    if hasattr(resume, '__dict__'):
        return {
            'name': getattr(resume, 'name', ''),
            'phone': getattr(resume, 'phone', ''),
            'email': getattr(resume, 'email', ''),
            'location': getattr(resume, 'location', ''),
            'blog': getattr(resume, 'blog', ''),
            'github': getattr(resume, 'github', ''),
            'job_title': getattr(resume, 'job_title', ''),
            'expected_salary': getattr(resume, 'expected_salary', ''),
            'expected_city': getattr(resume, 'expected_city', ''),
            'job_type': getattr(resume, 'job_type', ''),
            'work_experience': getattr(resume, 'work_experience', []),
            'project_experience': getattr(resume, 'project_experience', []),
            'education': getattr(resume, 'education', []),
            'skills': getattr(resume, 'skills', []),
            'certificates': getattr(resume, 'certificates', []),
            'awards': getattr(resume, 'awards', []),
            'self_introduction': getattr(resume, 'self_introduction', ''),
            'raw_text': getattr(resume, 'raw_text', '')
        }
    elif isinstance(resume, dict):
        return resume
    else:
        return {}
