let currentResumeId = null;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    initUploadArea();
    initTabs();
    loadResumes();
    refreshApiStatus();
});

// 初始化上传区域
function initUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadResume(e.target.files[0]);
        }
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadResume(e.dataTransfer.files[0]);
        }
    });
    
    analyzeBtn.addEventListener('click', analyzeAll);
}

// 上传简历
async function uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentResumeId = result.data.resume_id;
            showToast('简历上传成功！', 'success');
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

// 加载简历列表
async function loadResumes() {
    try {
        const response = await fetch('/api/resumes');
        const result = await response.json();
        
        if (result.success) {
            renderResumeList(result.data);
        }
    } catch (error) {
        console.error('Load resumes error:', error);
    }
}

// 渲染简历列表
function renderResumeList(resumes) {
    const container = document.getElementById('resumeList');
    
    if (resumes.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无上传的简历</div>';
        return;
    }
    
    let html = '';
    resumes.forEach(resume => {
        const skills = resume.skills.slice(0, 5).map(s => 
            `<span class="skill-tag">${s}</span>`
        ).join('');
        
        html += `
            <div class="resume-item">
                <div class="resume-info">
                    <div class="resume-name">${resume.filename}</div>
                    <div class="resume-date">上传时间：${resume.created_at}</div>
                    <div style="margin-top: 10px;">${skills}</div>
                </div>
                <div class="resume-actions">
                    <button class="btn btn-primary" onclick="selectResume(${resume.id})">选择</button>
                    <button class="btn btn-secondary" onclick="deleteResume(${resume.id})">删除</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 选择简历
function selectResume(resumeId) {
    currentResumeId = resumeId;
    document.getElementById('analyzeBtn').disabled = false;
    showToast('已选择简历', 'success');
}

// 删除简历
async function deleteResume(resumeId) {
    if (!confirm('确定要删除这份简历吗？')) return;
    
    try {
        const response = await fetch(`/api/resumes/${resumeId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
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

// 分析所有功能
async function analyzeAll() {
    if (!currentResumeId) {
        showToast('请先上传简历', 'error');
        return;
    }
    
    const jdText = document.getElementById('jdInput').value.trim();
    
    showLoading(true);
    
    try {
        // 1. 分析简历
        await analyzeResume();
        
        // 2. 岗位匹配
        if (jdText) {
            await matchJob(jdText);
        }
        
        // 3. 生成面试题
        await generateInterview(jdText);
        
        // 4. 生成自我介绍
        await generateSelfIntro(jdText);
        
        // 显示结果区域
        document.getElementById('resultSection').style.display = 'block';
        
        // 滚动到结果区域
        document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
        
        showToast('分析完成！', 'success');
    } catch (error) {
        showToast('分析失败，请重试', 'error');
        console.error('Analyze error:', error);
    } finally {
        showLoading(false);
    }
}

// 分析简历
async function analyzeResume() {
    const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: currentResumeId })
    });
    
    const result = await response.json();
    
    if (result.success) {
        renderResumeAnalysis(result.data);
    }
}

// 岗位匹配
async function matchJob(jdText) {
    const response = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            resume_id: currentResumeId,
            jd_text: jdText
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        renderJobMatch(result.data);
    }
}

// 生成面试题
async function generateInterview(jdText) {
    const response = await fetch('/api/interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            resume_id: currentResumeId,
            jd_text: jdText || ''
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        renderInterview(result.data);
    }
}

// 生成自我介绍
async function generateSelfIntro(jdText) {
    const response = await fetch('/api/self-intro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            resume_id: currentResumeId,
            jd_text: jdText || ''
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        renderSelfIntro(result.data);
    }
}

// 渲染简历分析结果
function renderResumeAnalysis(data) {
    const container = document.getElementById('resumeAnalysisContent');
    const analysis = data.analysis || {};
    
    const score = analysis.score || 70;
    const scoreClass = score >= 80 ? 'score-high' : (score >= 60 ? 'score-medium' : 'score-low');
    
    const strengths = analysis.strengths || [];
    const weaknesses = analysis.weaknesses || [];
    const suggestions = analysis.suggestions || [];
    const positions = analysis.recommended_positions || [];
    
    const skills = data.skills || [];
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h3>简历评分</h3>
                <span class="score-badge ${scoreClass}">${score}分</span>
            </div>
            
            <div class="result-section">
                <h4>🎯 提取的技能</h4>
                <div>
                    ${skills.length > 0 ? skills.map(s => `<span class="skill-tag">${s}</span>`).join('') : '未识别到技能关键词'}
                </div>
            </div>
            
            <div class="result-section">
                <h4>💪 简历优势</h4>
                <ul>
                    ${strengths.length > 0 ? strengths.map(s => `<li>${s}</li>`).join('') : '<li>暂无明显优势</li>'}
                </ul>
            </div>
            
            <div class="result-section">
                <h4>⚠️ 需要改进</h4>
                <ul>
                    ${weaknesses.length > 0 ? weaknesses.map(w => `<li>${w}</li>`).join('') : '<li>未发现明显问题</li>'}
                </ul>
            </div>
            
            <div class="result-section">
                <h4>📝 改进建议</h4>
                <ul>
                    ${suggestions.length > 0 ? suggestions.map(s => `<li>${s}</li>`).join('') : '<li>暂无建议</li>'}
                </ul>
            </div>
            
            <div class="result-section">
                <h4>💼 适合的岗位方向</h4>
                <ul>
                    ${positions.length > 0 ? positions.map(p => `<li>${p.position || p}</li>`).join('') : '<li>根据简历内容分析</li>'}
                </ul>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// 渲染岗位匹配结果
function renderJobMatch(data) {
    const container = document.getElementById('jobMatchContent');
    
    const score = data.match_score || 0;
    const scoreClass = score >= 80 ? 'score-high' : (score >= 60 ? 'score-medium' : 'score-low');
    
    const matchedSkills = data.matched_skills || [];
    const missingSkills = data.missing_skills || [];
    const suggestions = data.suggestions || [];
    const details = data.match_details || '';
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h3>匹配度评分</h3>
                <span class="score-badge ${scoreClass}">${score}分</span>
            </div>
            
            <p style="color: #666; margin-bottom: 20px;">${details}</p>
            
            <div class="result-section">
                <h4>✅ 匹配的技能和经验</h4>
                <ul>
                    ${matchedSkills.length > 0 ? matchedSkills.map(s => `<li>${s}</li>`).join('') : '<li>暂无匹配的技能</li>'}
                </ul>
            </div>
            
            <div class="result-section">
                <h4>❌ 缺失的技能和要求</h4>
                <ul>
                    ${missingSkills.length > 0 ? missingSkills.map(s => `<li>${s}</li>`).join('') : '<li>没有明显缺失</li>'}
                </ul>
            </div>
            
            <div class="result-section">
                <h4>📝 提升建议</h4>
                <ul>
                    ${suggestions.length > 0 ? suggestions.map(s => `<li>${s}</li>`).join('') : '<li>暂无建议</li>'}
                </ul>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// 渲染面试题
function renderInterview(data) {
    const container = document.getElementById('interviewContent');
    const questions = data.interview_questions || [];
    
    if (questions.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无面试题</div>';
        return;
    }
    
    let html = `
        <div style="margin-bottom: 20px; color: #666;">
            共生成 ${questions.length} 道面试题，建议认真准备
        </div>
    `;
    
    questions.forEach((q, index) => {
        html += `
            <div class="question-card">
                <span class="question-type">${q.type}</span>
                <div class="question-text">${index + 1}. ${q.question}</div>
                <div class="answer-section">
                    <h5>回答要点</h5>
                    <div class="answer-points">
                        ${(q.answer_points || []).map(p => `• ${p}`).join('<br>')}
                    </div>
                    <h5 style="margin-top: 15px;">参考回答</h5>
                    <div class="sample-answer">${q.sample_answer || '暂无参考回答'}</div>
                    ${q.tips ? `<div class="tips">💡 ${q.tips}</div>` : ''}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 渲染自我介绍
function renderSelfIntro(data) {
    const container = document.getElementById('selfIntroContent');
    
    const oneMinute = data.one_minute || '';
    const threeMinutes = data.three_minutes || '';
    const keyPoints = data.key_points || [];
    
    let html = `
        <div style="margin-bottom: 20px; color: #666;">
            核心要点：${keyPoints.join(' → ')}
        </div>
        
        <div class="self-intro">
            <h4>🗣️ 1分钟精简版</h4>
            <p>${oneMinute || '请上传简历后生成自我介绍'}</p>
        </div>
        
        <div class="self-intro">
            <h4>🗣️ 3分钟详细版</h4>
            <p>${threeMinutes || '请上传简历后生成自我介绍'}</p>
        </div>
    `;
    
    container.innerHTML = html;
}

// 初始化Tab切换
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 移除所有active
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // 添加active到当前
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });
}

// 显示/隐藏加载动画
function showLoading(show) {
    document.getElementById('loading').classList.toggle('active', show);
    document.getElementById('analyzeBtn').disabled = show;
}

// 显示Toast提示
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 获取API状态
async function refreshApiStatus() {
    try {
        const response = await fetch('/api/status');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            document.getElementById('apiCalls').textContent = data.total_calls || 0;
            document.getElementById('apiTokens').textContent = formatNumber(data.total_tokens || 0);
            document.getElementById('apiProvider').textContent = data.provider || '-';
            document.getElementById('apiModel').textContent = data.model ? 
                (data.model.length > 15 ? data.model.substring(0, 15) + '...' : data.model) : '-';
            
            // 显示/隐藏自定义标签
            const customBadge = document.getElementById('customBadge');
            customBadge.style.display = data.is_custom_key ? 'inline' : 'none';
            
            if (data.last_call_time) {
                const date = new Date(data.last_call_time);
                document.getElementById('apiLastTime').textContent = 
                    '最后调用：' + date.toLocaleString('zh-CN');
            } else {
                document.getElementById('apiLastTime').textContent = '最后调用：暂无';
            }
        }
    } catch (error) {
        console.error('获取API状态失败:', error);
        document.getElementById('apiCalls').textContent = '-';
        document.getElementById('apiTokens').textContent = '-';
        document.getElementById('apiProvider').textContent = '-';
        document.getElementById('apiModel').textContent = '-';
    }
}

// 切换API配置面板
function toggleApiConfig() {
    const panel = document.getElementById('apiConfigPanel');
    panel.classList.toggle('active');
    
    // 如果打开面板，加载当前配置
    if (panel.classList.contains('active')) {
        loadCurrentConfig();
    }
}

// 加载当前配置
async function loadCurrentConfig() {
    try {
        const response = await fetch('/api/config');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            document.getElementById('apiKeyInput').value = '';
            document.getElementById('apiUrlInput').value = data.api_base_url || '';
            document.getElementById('modelInput').value = data.model_name || '';
            document.getElementById('providerInput').value = data.provider_name || '';
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

// 测试API Key
async function testApiKey() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const apiUrl = document.getElementById('apiUrlInput').value.trim();
    const modelName = document.getElementById('modelInput').value.trim();
    const providerName = document.getElementById('providerInput').value.trim();
    
    if (!apiKey) {
        showToast('请输入API Key', 'error');
        return;
    }
    
    showLoading(true);
    document.getElementById('testResult').innerHTML = '<span style="color: #666;">测试中...</span>';
    
    try {
        const response = await fetch('/api/config/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_key: apiKey,
                api_base_url: apiUrl,
                model_name: modelName
            })
        });
        
        const result = await response.json();
        const testResult = document.getElementById('testResult');
        
        if (result.success) {
            testResult.className = 'test-result success';
            testResult.innerHTML = '✓ ' + result.message;
        } else {
            testResult.className = 'test-result error';
            testResult.innerHTML = '✗ ' + result.message;
        }
    } catch (error) {
        document.getElementById('testResult').className = 'test-result error';
        document.getElementById('testResult').innerHTML = '✗ 测试失败: ' + error.message;
    } finally {
        showLoading(false);
    }
}

// 保存API配置
async function saveApiConfig() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const apiUrl = document.getElementById('apiUrlInput').value.trim();
    const modelName = document.getElementById('modelInput').value.trim();
    const providerName = document.getElementById('providerInput').value.trim();
    
    if (!apiKey) {
        showToast('请输入API Key', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/config/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_key: apiKey,
                api_base_url: apiUrl,
                model_name: modelName,
                provider_name: providerName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            document.getElementById('apiConfigPanel').classList.remove('active');
            refreshApiStatus();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// 重置为默认配置
async function resetToDefault() {
    if (!confirm('确定要切换回默认API配置吗？当前的自定义配置将被清除。')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/config/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            document.getElementById('apiConfigPanel').classList.remove('active');
            refreshApiStatus();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        showToast('重置失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// 格式化数字
function formatNumber(num) {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万';
    }
    return num.toString();
}
