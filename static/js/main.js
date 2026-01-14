let currentResumeId = null;

const jobTips = [
    { icon: '📝', title: '简历优化', desc: '使用STAR法则描述项目经历：情境-任务-行动-结果', tag: '简历技巧' },
    { icon: '🎯', title: '精准投递', desc: '根据JD关键词定制简历，提高ATS通过率', tag: '投递策略' },
    { icon: '💼', title: '面试着装', desc: '根据公司文化选择着装，金融正装，互联网商务休闲', tag: '形象管理' },
    { icon: '🗣️', title: '自我介绍', desc: '控制在一分钟内，突出与岗位匹配的核心能力', tag: '面试技巧' },
    { icon: '🔍', title: '公司调研', desc: '了解公司业务、文化、创始人，准备2-3个问题反问面试官', tag: '面试准备' },
    { icon: '⭐', title: 'STAR法则', desc: '用具体案例证明能力，数据化成果（提升30%、节省2小时等）', tag: '表达技巧' },
    { icon: '🤝', title: '行为面试', desc: '准备团队合作、冲突处理、压力应对的具体案例', tag: '面试技巧' },
    { icon: '💰', title: '薪资谈判', desc: '先让面试官出价，了解市场行情，准备最低可接受薪资', tag: '谈判技巧' },
    { icon: '📊', title: '作品集', desc: '准备1-2个最能体现能力的项目作品，现场展示效果更好', tag: '加分项' },
    { icon: '🎓', title: '持续学习', desc: '关注行业动态，学习新技术，展现学习能力和上进心', tag: '职业发展' },
    { icon: '🌐', title: '英语能力', desc: '外企或大厂必备，练习技术英语口语和专业术语', tag: '技能提升' },
    { icon: '📱', title: '作品链接', desc: 'GitHub、技术博客、LinkedIn等链接添加到简历', tag: '简历技巧' },
    { icon: '⏰', title: '时间管理', desc: '面试迟到是大忌，提前15分钟到达，熟悉路线', tag: '面试细节' },
    { icon: '📋', title: '带齐材料', desc: '纸质简历、作品集、笔记本、笔等备份材料', tag: '面试准备' },
    { icon: '🙋', title: '主动提问', desc: '询问团队情况、技术栈、发展空间、反馈时间等', tag: '面试技巧' },
    { icon: '🔄', title: '及时跟进', desc: '面试后24小时内发送感谢信，表达强烈兴趣', tag: '跟进技巧' }
];

document.addEventListener('DOMContentLoaded', function() {
    initTipsCarousel();
    initJobsCarousel();
    initUpload();
    initTabs();
    loadResumes();
    refreshApiStatus();
});

function initTipsCarousel() {
    const track = document.getElementById('tipsTrack');
    
    let tipsHTML = '';
    jobTips.forEach(function(tip) {
        tipsHTML += 
            '<div class="tip-item">' +
            '<span class="tip-icon">' + tip.icon + '</span>' +
            '<div class="tip-content">' +
            '<div class="tip-title">' + tip.title + '</div>' +
            '<div class="tip-desc">' + tip.desc + '</div>' +
            '<span class="tip-tag">' + tip.tag + '</span>' +
            '</div>' +
            '</div>';
    });
    
    track.innerHTML = tipsHTML + tipsHTML;
}

function initJobsCarousel() {
    fetchHotJobs();
}

async function fetchHotJobs() {
    try {
        const response = await fetch('/api/jobs/hot');
        const result = await response.json();
        
        if (result.success) {
            renderJobs(result.data);
        }
    } catch (error) {
        console.error('获取热门职位失败:', error);
        document.getElementById('jobsCount').textContent = '加载失败';
    }
}

function renderJobs(jobs) {
    const track = document.getElementById('jobsTrack');
    const countEl = document.getElementById('jobsCount');
    
    countEl.textContent = jobs.length + '个热门职位';
    
    let jobsHTML = '';
    jobs.forEach(function(job) {
        var tagsHTML = '';
        job.tags.forEach(function(tag) {
            tagsHTML += '<span class="job-tag">' + tag + '</span>';
        });
        
        jobsHTML += 
            '<div class="job-card" data-category="' + job.category + '">' +
            '<div class="job-header">' +
            '<div class="job-title">' + job.title + '</div>' +
            '<div class="job-salary">' + job.salary + '</div>' +
            '</div>' +
            '<div class="job-company">🏢 ' + job.company + '</div>' +
            '<div class="job-tags">' + tagsHTML + '</div>' +
            '<div class="job-meta">' +
            '<div class="job-location">📍 ' + job.location + '</div>' +
            '<button class="job-apply-btn" onclick="openJobLink(\'' + job.source + '\')">投递</button>' +
            '</div>' +
            '</div>';
    });
    
    track.innerHTML = jobsHTML + jobsHTML;
    initJobFilters();
}

function initJobFilters() {
    var filterBtns = document.querySelectorAll('.job-filter-btn');
    var jobCards = document.querySelectorAll('.job-card');
    
    filterBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var filter = btn.dataset.filter;
            
            filterBtns.forEach(function(b) {
                b.classList.remove('active');
            });
            btn.classList.add('active');
            
            jobCards.forEach(function(card) {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

function openJobLink(source) {
    var links = {
        'BOSS直聘': 'https://www.zhipin.com',
        '猎聘': 'https://www.liepin.com',
        '前程无忧': 'https://www.51job.com'
    };
    
    showToast('正在跳转到 ' + source + '...', 'success');
    
    setTimeout(function() {
        window.open(links[source], '_blank');
    }, 1000);
}

function initUpload() {
    var uploadZone = document.getElementById('uploadZone');
    var fileInput = document.getElementById('resumeInput');
    var analyzeBtn = document.getElementById('analyzeBtn');
    
    uploadZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadResume(e.target.files[0]);
        }
    });
    
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', function() {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadResume(e.dataTransfer.files[0]);
        }
    });
    
    analyzeBtn.addEventListener('click', analyzeAll);
}

async function uploadResume(file) {
    var formData = new FormData();
    formData.append('file', file);
    
    showLoading(true);
    
    try {
        var response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        var result = await response.json();
        
        if (result.success) {
            currentResumeId = result.data.resume_id;
            showToast('简历上传成功', 'success');
            loadResumes();
            document.getElementById('analyzeBtn').disabled = false;
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        showToast('上传失败，请重试', 'error');
        console.error('Upload error:', error);
    } finally {
        showLoading(false);
    }
}

async function loadResumes() {
    try {
        var response = await fetch('/api/resumes');
        var result = await response.json();
        
        if (result.success) {
            renderResumeList(result.data);
        }
    } catch (error) {
        console.error('Load resumes error:', error);
    }
}

function renderResumeList(resumes) {
    var container = document.getElementById('resumeList');
    
    if (resumes.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    var html = '';
    resumes.forEach(function(resume) {
        var skillsHTML = '';
        resume.skills.slice(0, 5).forEach(function(s) {
            skillsHTML += '<span class="skill-tag">' + s + '</span>';
        });
        
        html += 
            '<div class="resume-item">' +
            '<div class="resume-icon">📄</div>' +
            '<div class="resume-info">' +
            '<div class="resume-name">' + resume.filename + '</div>' +
            '<div class="resume-date">上传时间：' + resume.created_at + '</div>' +
            '<div class="skills-container" style="margin-top: 8px;">' + (skillsHTML || '<span style="color: var(--text-muted); font-size: 0.875rem;">未识别到技能</span>') + '</div>' +
            '</div>' +
            '<div class="resume-actions">' +
            '<button class="btn btn-secondary btn-sm" onclick="selectResume(' + resume.id + ')">选择</button>' +
            '<button class="btn btn-secondary btn-sm" onclick="deleteResume(' + resume.id + ')">删除</button>' +
            '</div>' +
            '</div>';
    });
    
    container.innerHTML = html;
}

function selectResume(resumeId) {
    currentResumeId = resumeId;
    document.getElementById('analyzeBtn').disabled = false;
    showToast('已选择简历', 'success');
}

async function deleteResume(resumeId) {
    if (!confirm('确定要删除这份简历吗？')) return;
    
    try {
        var response = await fetch('/api/resumes/' + resumeId, {
            method: 'DELETE'
        });
        
        var result = await response.json();
        
        if (result.success) {
            showToast('删除成功', 'success');
            loadResumes();
            if (currentResumeId === resumeId) {
                currentResumeId = null;
                document.getElementById('analyzeBtn').disabled = true;
            }
        }
    } catch (error) {
        showToast('删除失败', 'error');
    }
}

async function analyzeAll() {
    if (!currentResumeId) {
        showToast('请先上传简历', 'error');
        return;
    }
    
    var jdText = document.getElementById('jdInput').value.trim();
    
    showLoading(true);
    
    try {
        await analyzeResume();
        
        if (jdText) {
            await matchJob(jdText);
        }
        
        await generateInterview(jdText);
        await generateSelfIntro(jdText);
        
        document.getElementById('resultSection').classList.add('active');
        document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
        
        showToast('分析完成', 'success');
    } catch (error) {
        showToast('分析失败，请重试', 'error');
        console.error('Analyze error:', error);
    } finally {
        showLoading(false);
    }
}

async function analyzeResume() {
    var response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: currentResumeId })
    });
    
    var result = await response.json();
    
    if (result.success) {
        renderResumeAnalysis(result.data);
    }
}

async function matchJob(jdText) {
    var response = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            resume_id: currentResumeId,
            jd_text: jdText
        })
    });
    
    var result = await response.json();
    
    if (result.success) {
        renderJobMatch(result.data);
    }
}

async function generateInterview(jdText) {
    var response = await fetch('/api/interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            resume_id: currentResumeId,
            jd_text: jdText || ''
        })
    });
    
    var result = await response.json();
    
    if (result.success) {
        renderInterview(result.data);
    }
}

async function generateSelfIntro(jdText) {
    var response = await fetch('/api/self-intro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            resume_id: currentResumeId,
            jd_text: jdText || ''
        })
    });
    
    var result = await response.json();
    
    if (result.success) {
        renderSelfIntro(result.data);
    }
}

function renderResumeAnalysis(data) {
    var container = document.getElementById('resumeAnalysisContent');
    var analysis = data.analysis || {};
    
    var score = analysis.score || 70;
    var scoreClass = score >= 80 ? 'score-high' : (score >= 60 ? 'score-medium' : 'score-low');
    
    var strengths = analysis.strengths || [];
    var weaknesses = analysis.weaknesses || [];
    var suggestions = analysis.suggestions || [];
    var positions = analysis.recommended_positions || [];
    var skills = data.skills || [];
    
    var skillsHTML = '';
    if (skills.length > 0) {
        skillsHTML = 
            '<div style="margin-top: 24px;">' +
            '<h4 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 12px;">识别到的技能</h4>' +
            '<div class="skills-container">';
        skills.forEach(function(s) {
            skillsHTML += '<span class="skill-tag">' + s + '</span>';
        });
        skillsHTML += '</div></div>';
    }
    
    var strengthsHTML = '';
    if (strengths.length > 0) {
        strengths.forEach(function(s) {
            strengthsHTML += '<li style="padding: 8px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + s + '</li>';
        });
    } else {
        strengthsHTML = '<li style="color: var(--text-muted);">暂无明显优势</li>';
    }
    
    var weaknessesHTML = '';
    if (weaknesses.length > 0) {
        weaknesses.forEach(function(w) {
            weaknessesHTML += '<li style="padding: 8px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + w + '</li>';
        });
    } else {
        weaknessesHTML = '<li style="color: var(--text-muted);">未发现明显问题</li>';
    }
    
    var suggestionsHTML = '';
    if (suggestions.length > 0) {
        suggestions.forEach(function(s) {
            suggestionsHTML += '<li style="padding: 10px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + s + '</li>';
        });
    } else {
        suggestionsHTML = '<li style="color: var(--text-muted);">暂无建议</li>';
    }
    
    var positionsHTML = '';
    if (positions.length > 0) {
        positions.forEach(function(p) {
            positionsHTML += '<li style="padding: 10px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + (p.position || p) + '</li>';
        });
    } else {
        positionsHTML = '<li style="color: var(--text-muted);">根据简历内容分析</li>';
    }
    
    container.innerHTML = 
        '<div class="score-card">' +
        '<div class="score-header">' +
        '<div>' +
        '<h3 style="font-size: 1.25rem; margin-bottom: 8px;">简历综合评分</h3>' +
        '<p style="color: var(--text-muted); font-size: 0.9rem;">基于完整性、格式、内容质量、可量化性等维度评估</p>' +
        '</div>' +
        '<div class="score-circle ' + scoreClass + '">' + score + '<span style="font-size: 0.9rem; margin-left: 2px;">分</span></div>' +
        '</div>' +
        skillsHTML +
        '</div>' +
        
        '<div class="results-grid">' +
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #10b981, #059669);">💪</div>' +
        '<div class="card-title">简历优势</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + strengthsHTML + '</ul>' +
        '</div>' +
        
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706);">⚠️</div>' +
        '<div class="card-title">待改进项</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + weaknessesHTML + '</ul>' +
        '</div>' +
        '</div>' +
        
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #6366f1, #4f46e5);">📝</div>' +
        '<div class="card-title">优化建议</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + suggestionsHTML + '</ul>' +
        '</div>' +
        
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">💼</div>' +
        '<div class="card-title">推荐岗位方向</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + positionsHTML + '</ul>' +
        '</div>';
}

function renderJobMatch(data) {
    var container = document.getElementById('jobMatchContent');
    
    var score = data.match_score || 0;
    var scoreClass = score >= 80 ? 'score-high' : (score >= 60 ? 'score-medium' : 'score-low');
    
    var matchedSkills = data.matched_skills || [];
    var missingSkills = data.missing_skills || [];
    var suggestions = data.suggestions || [];
    var details = data.match_details || '';
    
    var matchedHTML = '';
    if (matchedSkills.length > 0) {
        matchedSkills.forEach(function(s) {
            matchedHTML += '<li style="padding: 8px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + s + '</li>';
        });
    } else {
        matchedHTML = '<li style="color: var(--text-muted);">暂无匹配技能</li>';
    }
    
    var missingHTML = '';
    if (missingSkills.length > 0) {
        missingSkills.forEach(function(s) {
            missingHTML += '<li style="padding: 8px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + s + '</li>';
        });
    } else {
        missingHTML = '<li style="color: var(--text-muted);">没有明显缺失</li>';
    }
    
    var suggestionsHTML = '';
    if (suggestions.length > 0) {
        suggestions.forEach(function(s) {
            suggestionsHTML += '<li style="padding: 10px 0; color: var(--text-secondary); border-bottom: 1px solid var(--border);">• ' + s + '</li>';
        });
    } else {
        suggestionsHTML = '<li style="color: var(--text-muted);">暂无建议</li>';
    }
    
    container.innerHTML = 
        '<div class="score-card">' +
        '<div class="score-header">' +
        '<div>' +
        '<h3 style="font-size: 1.25rem; margin-bottom: 8px;">岗位匹配度</h3>' +
        '<p style="color: var(--text-muted); font-size: 0.9rem;">' + details + '</p>' +
        '</div>' +
        '<div class="score-circle ' + scoreClass + '">' + score + '<span style="font-size: 0.9rem; margin-left: 2px;">分</span></div>' +
        '</div>' +
        '</div>' +
        
        '<div class="results-grid">' +
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #10b981, #059669);">✅</div>' +
        '<div class="card-title">匹配项</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + matchedHTML + '</ul>' +
        '</div>' +
        
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626);">❌</div>' +
        '<div class="card-title">缺失项</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + missingHTML + '</ul>' +
        '</div>' +
        '</div>' +
        
        '<div class="card">' +
        '<div class="card-header" style="margin-bottom: 16px;">' +
        '<div class="card-icon" style="background: linear-gradient(135deg, #6366f1, #4f46e5);">📈</div>' +
        '<div class="card-title">提升建议</div>' +
        '</div>' +
        '<ul style="list-style: none; padding: 0;">' + suggestionsHTML + '</ul>' +
        '</div>';
}

function renderInterview(data) {
    var container = document.getElementById('interviewContent');
    var questions = data.interview_questions || [];
    
    if (questions.length === 0) {
        container.innerHTML = 
            '<div class="empty-state">' +
            '<div class="empty-icon">📋</div>' +
            '<p>暂无面试题</p>' +
            '</div>';
        return;
    }
    
    var html = 
        '<div style="margin-bottom: 24px; padding: 16px 20px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border);">' +
        '<span style="color: var(--primary); font-weight: 600;">共 ' + questions.length + ' 道面试题</span>' +
        '<span style="color: var(--text-muted); margin-left: 16px;">建议认真准备每一道题</span>' +
        '</div>';
    
    questions.forEach(function(q, index) {
        var pointsHTML = '';
        if (q.answer_points && q.answer_points.length > 0) {
            q.answer_points.forEach(function(p) {
                pointsHTML += '• ' + p + '<br>';
            });
        }
        
        html += 
            '<div class="question-card">' +
            '<div class="question-header">' +
            '<span class="question-type">' + q.type + '</span>' +
            '<span style="color: var(--text-muted); font-size: 0.875rem;">#' + (index + 1) + '</span>' +
            '</div>' +
            '<div class="question-text">' + q.question + '</div>' +
            '<div class="answer-block">' +
            '<div class="answer-label">回答要点</div>' +
            '<div class="answer-content">' + pointsHTML + '</div>' +
            '</div>' +
            '<div class="answer-block" style="margin-top: 12px;">' +
            '<div class="answer-label">参考回答</div>' +
            '<div class="answer-content">' + (q.sample_answer || '暂无参考回答') + '</div>' +
            '</div>';
        
        if (q.tips) {
            html += 
                '<div style="margin-top: 12px; padding: 12px 16px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 3px solid var(--warning);">' +
                '<span style="color: var(--warning); font-weight: 600;">💡 </span>' +
                '<span style="color: var(--text-secondary);">' + q.tips + '</span>' +
                '</div>';
        }
        
        html += '</div>';
    });
    
    container.innerHTML = html;
}

function renderSelfIntro(data) {
    var container = document.getElementById('selfIntroContent');
    
    var oneMinute = data.one_minute || '';
    var threeMinutes = data.three_minutes || '';
    var keyPoints = data.key_points || [];
    
    container.innerHTML = 
        '<div style="margin-bottom: 24px; padding: 16px 20px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">' +
        '<span style="color: var(--primary); font-weight: 600;">核心卖点：</span>' +
        '<span style="color: var(--text-secondary);">' + keyPoints.join(' → ') + '</span>' +
        '</div>' +
        
        '<div class="intro-card" style="position: relative;">' +
        '<div class="intro-title">🗣️ 1分钟精简版</div>' +
        '<div class="intro-content">' + (oneMinute || '请上传简历后生成自我介绍') + '</div>' +
        '</div>' +
        
        '<div class="intro-card" style="position: relative;">' +
        '<div class="intro-title">🗣️ 3分钟详细版</div>' +
        '<div class="intro-content">' + (threeMinutes || '请上传简历后生成自我介绍') + '</div>' +
        '</div>';
}

function initTabs() {
    var tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            tabBtns.forEach(function(b) {
                b.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(function(c) {
                c.classList.remove('active');
            });
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });
}

function showLoading(show) {
    document.getElementById('loading').classList.toggle('active', show);
    document.getElementById('analyzeBtn').disabled = show;
}

function showToast(message, type) {
    var toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast ' + type + ' show';
    
    setTimeout(function() {
        toast.classList.remove('show');
    }, 3000);
}

async function refreshApiStatus() {
    try {
        var response = await fetch('/api/status');
        var result = await response.json();
        
        if (result.success) {
            var data = result.data;
            document.getElementById('apiCalls').textContent = data.total_calls || 0;
            document.getElementById('apiTokens').textContent = formatNumber(data.total_tokens || 0);
            document.getElementById('apiProvider').textContent = data.provider || '-';
            var modelText = data.model || '-';
            if (modelText.length > 15) {
                modelText = modelText.substring(0, 15) + '...';
            }
            document.getElementById('apiModel').textContent = modelText;
        }
    } catch (error) {
        console.error('获取API状态失败:', error);
    }
}

function openConfigModal() {
    document.getElementById('configModal').classList.add('active');
    loadCurrentConfig();
}

function closeConfigModal() {
    document.getElementById('configModal').classList.remove('active');
}

async function loadCurrentConfig() {
    try {
        var response = await fetch('/api/config');
        var result = await response.json();
        
        if (result.success) {
            var data = result.data;
            document.getElementById('apiKeyInput').value = '';
            document.getElementById('apiUrlInput').value = data.api_base_url || '';
            document.getElementById('modelInput').value = data.model_name || '';
            document.getElementById('providerInput').value = data.provider_name || '';
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

async function testApiKey() {
    var apiKey = document.getElementById('apiKeyInput').value.trim();
    var apiUrl = document.getElementById('apiUrlInput').value.trim();
    var modelName = document.getElementById('modelInput').value.trim();
    
    if (!apiKey) {
        showToast('请输入API Key', 'error');
        return;
    }
    
    var testResult = document.getElementById('testResult');
    testResult.innerHTML = '<span style="color: var(--text-muted);">测试中...</span>';
    
    try {
        var response = await fetch('/api/config/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_key: apiKey,
                api_base_url: apiUrl,
                model_name: modelName
            })
        });
        
        var result = await response.json();
        
        if (result.success) {
            testResult.innerHTML = '<div style="padding: 12px 16px; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border: 1px solid var(--accent); color: var(--accent);">✓ ' + result.message + '</div>';
        } else {
            testResult.innerHTML = '<div style="padding: 12px 16px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border: 1px solid var(--danger); color: var(--danger);">✗ ' + result.message + '</div>';
        }
    } catch (error) {
        testResult.innerHTML = '<div style="padding: 12px 16px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border: 1px solid var(--danger); color: var(--danger);">✗ 测试失败: ' + error.message + '</div>';
    }
}

async function saveApiConfig() {
    var apiKey = document.getElementById('apiKeyInput').value.trim();
    var apiUrl = document.getElementById('apiUrlInput').value.trim();
    var modelName = document.getElementById('modelInput').value.trim();
    var providerName = document.getElementById('providerInput').value.trim();
    
    if (!apiKey) {
        showToast('请输入API Key', 'error');
        return;
    }
    
    try {
        var response = await fetch('/api/config/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_key: apiKey,
                api_base_url: apiUrl,
                model_name: modelName,
                provider_name: providerName
            })
        });
        
        var result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            closeConfigModal();
            refreshApiStatus();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    }
}

function formatNumber(num) {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万';
    }
    return num.toString();
}

document.getElementById('configModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeConfigModal();
    }
});
