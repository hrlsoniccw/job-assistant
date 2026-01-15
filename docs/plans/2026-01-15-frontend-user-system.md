# Frontend User System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build frontend user authentication and profile management system (login/register, personal center, membership center).

**Architecture:** Single-page application with modal-based auth flows, JWT token management in localStorage, protected route handling with automatic redirect.

**Tech Stack:**
- HTML5 (inline styles in templates/index.html)
- Vanilla JavaScript (static/js/main.js)
- JWT token storage (localStorage)
- Fetch API for backend communication

---

## Task 1: Add JWT Token Management to main.js

**Files:**
- Modify: `static/js/main.js:1-5` (add after currentResumeId)

**Step 1: Write failing test (manual)**

Open browser console and verify:
```javascript
localStorage.getItem('token') === null
// Expected: null (no token exists)
```

**Step 2: Add token management functions**

Add to `static/js/main.js` after line 1:

```javascript
// Token management
let authToken = null;

function getToken() {
    if (!authToken) {
        authToken = localStorage.getItem('token');
    }
    return authToken;
}

function setToken(token) {
    authToken = token;
    localStorage.setItem('token', token);
}

function clearToken() {
    authToken = null;
    localStorage.removeItem('token');
}

function isAuthenticated() {
    return !!getToken();
}

// Add Authorization header to all fetch calls
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    const headers = options.headers || {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return fetch(url, {
        ...options,
        headers
    });
}

function handleApiError(response) {
    if (response.status === 401) {
        clearToken();
        showToast('登录已过期，请重新登录', 'error');
        showAuthModal();
    }
}
```

**Step 3: Run test (manual)**

Add to browser console after refresh:
```javascript
isAuthenticated()
// Expected: false (no login yet)

setToken('test-token')
isAuthenticated()
// Expected: true

clearToken()
isAuthenticated()
// Expected: false
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: add JWT token management functions"
```

---

## Task 2: Add Auth Modal HTML Structure

**Files:**
- Modify: `templates/index.html` (find </body> and add before it)

**Step 1: Write failing test**

Open browser and verify:
```javascript
document.getElementById('authModal') === null
// Expected: null (modal doesn't exist)
```

**Step 2: Add auth modal HTML**

Add before `</body>` tag in `templates/index.html`:

```html
<!-- Auth Modal -->
<div id="authModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2 id="authModalTitle">登录</h2>
            <button class="modal-close" onclick="closeAuthModal()">×</button>
        </div>

        <!-- Login Form -->
        <form id="loginForm" class="auth-form">
            <div class="form-group">
                <label class="form-label">邮箱</label>
                <input type="email" id="loginEmail" class="input-field" placeholder="请输入邮箱" required>
            </div>
            <div class="form-group">
                <label class="form-label">密码</label>
                <input type="password" id="loginPassword" class="input-field" placeholder="请输入密码" required>
            </div>
            <button type="submit" class="btn btn-primary btn-full">登录</button>
            <div class="auth-switch">
                还没有账号？<a href="#" onclick="showRegisterForm()">立即注册</a>
            </div>
        </form>

        <!-- Register Form -->
        <form id="registerForm" class="auth-form" style="display: none;">
            <div class="form-group">
                <label class="form-label">用户名</label>
                <input type="text" id="registerUsername" class="input-field" placeholder="2-50个字符" required minlength="2" maxlength="50">
            </div>
            <div class="form-group">
                <label class="form-label">邮箱</label>
                <input type="email" id="registerEmail" class="input-field" placeholder="请输入邮箱" required>
            </div>
            <div class="form-group">
                <label class="form-label">密码</label>
                <input type="password" id="registerPassword" class="input-field" placeholder="至少6位" required minlength="6">
            </div>
            <div class="form-group">
                <label class="form-label">手机号 (选填)</label>
                <input type="tel" id="registerPhone" class="input-field" placeholder="请输入手机号">
            </div>
            <button type="submit" class="btn btn-primary btn-full">注册</button>
            <div class="auth-switch">
                已有账号？<a href="#" onclick="showLoginForm()">立即登录</a>
            </div>
        </form>
    </div>
</div>
```

**Step 3: Run test**

Open browser and verify:
```javascript
document.getElementById('authModal') !== null
document.getElementById('loginForm') !== null
document.getElementById('registerForm') !== null
// Expected: true (all elements exist)
```

**Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat: add auth modal HTML structure"
```

---

## Task 3: Add Auth Modal CSS Styles

**Files:**
- Modify: `templates/index.html` (in <style> section)

**Step 1: Write failing test**

Open browser DevTools and verify:
```javascript
getComputedStyle(document.getElementById('authModal')).display === 'none'
// Expected: 'none' (hidden by default)
```

**Step 2: Add auth modal CSS**

Add to `<style>` section in `templates/index.html` after existing modal styles:

```css
/* Auth Modal */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.modal.active {
    display: flex;
}

.modal-content {
    background: var(--bg-card);
    border-radius: 20px;
    padding: 32px;
    width: 100%;
    max-width: 420px;
    border: 1px solid var(--border);
    position: relative;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.modal-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
}

.modal-close {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 2rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
}

.modal-close:hover {
    color: var(--text-primary);
}

.auth-form {
    display: block;
}

.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.input-field {
    width: 100%;
    padding: 14px 16px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--bg-dark);
    color: var(--text-primary);
    font-size: 1rem;
    font-family: inherit;
    transition: all 0.3s ease;
}

.input-field:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-full {
    width: 100%;
}

.auth-switch {
    text-align: center;
    margin-top: 16px;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.auth-switch a {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
}

.auth-switch a:hover {
    text-decoration: underline;
}
```

**Step 3: Run test**

Refresh browser and verify modal is properly styled:
```javascript
const modal = document.getElementById('authModal');
modal.classList.add('active');
// Verify: modal is visible, centered, with backdrop
modal.classList.remove('active');
```

**Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat: add auth modal CSS styles"
```

---

## Task 4: Implement Auth Modal Control Functions

**Files:**
- Modify: `static/js/main.js` (after existing modal functions)

**Step 1: Write failing test**

Open browser console and verify:
```javascript
typeof showAuthModal === 'undefined'
// Expected: 'undefined' (function doesn't exist yet)
```

**Step 2: Add auth modal functions**

Add to `static/js/main.js` after existing modal functions:

```javascript
function showAuthModal() {
    document.getElementById('authModal').classList.add('active');
    showLoginForm();
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('active');
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('authModalTitle').textContent = '登录';
}

function showRegisterForm() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('authModalTitle').textContent = '注册';
}
```

**Step 3: Run test**

Open browser console and verify:
```javascript
showAuthModal()
document.getElementById('authModal').classList.contains('active')
// Expected: true (modal is visible)

showRegisterForm()
document.getElementById('authModalTitle').textContent === '注册'
// Expected: true

closeAuthModal()
document.getElementById('authModal').classList.contains('active')
// Expected: false (modal is hidden)
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: add auth modal control functions"
```

---

## Task 5: Implement Login Functionality

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser, fill login form, and submit:
```javascript
// Submit should fail with "login function not defined" error
```

**Step 2: Add login function**

Add to `static/js/main.js`:

```javascript
// Initialize login form
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showToast('请填写邮箱和密码', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetchWithAuth('/api/user/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();

        if (result.success) {
            setToken(result.data.token);
            closeAuthModal();
            showToast('登录成功', 'success');
            loadUserProfile();
            updateHeaderUserStatus();
        } else {
            showToast(result.error || '登录失败', 'error');
        }
    } catch (error) {
        showToast('登录失败，请重试', 'error');
        console.error('Login error:', error);
    } finally {
        showLoading(false);
    }
});
```

**Step 3: Run test**

1. Register a test user via API (or use existing test data)
2. Fill login form with valid credentials
3. Submit form
4. Verify:
   - Token is saved to localStorage
   - Modal closes
   - Success toast appears

```javascript
localStorage.getItem('token') !== null
// Expected: true (token exists)
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: implement login functionality"
```

---

## Task 6: Implement Register Functionality

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser, fill register form, and submit:
```javascript
// Submit should fail with "register function not defined" error
```

**Step 2: Add register function**

Add to `static/js/main.js`:

```javascript
// Initialize register form
document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const username = document.getElementById('registerUsername').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const phone = document.getElementById('registerPhone').value.trim();

    // Validation
    if (username.length < 2 || username.length > 50) {
        showToast('用户名2-50个字符', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('密码至少6位', 'error');
        return;
    }

    const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
    if (!emailRegex.test(email)) {
        showToast('邮箱格式不正确', 'error');
        return;
    }

    showLoading(true);

    try {
        const response = await fetchWithAuth('/api/user/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, phone })
        });

        const result = await response.json();

        if (result.success) {
            setToken(result.data.token);
            closeAuthModal();
            showToast('注册成功', 'success');
            loadUserProfile();
            updateHeaderUserStatus();
        } else {
            showToast(result.error || '注册失败', 'error');
        }
    } catch (error) {
        showToast('注册失败，请重试', 'error');
        console.error('Register error:', error);
    } finally {
        showLoading(false);
    }
});
```

**Step 3: Run test**

1. Fill register form with valid data
2. Submit form
3. Verify:
   - User is created
   - Token is saved
   - Modal closes
   - Success toast appears

```javascript
localStorage.getItem('token') !== null
// Expected: true (token exists after registration)
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: implement register functionality"
```

---

## Task 7: Add User Profile Header Button

**Files:**
- Modify: `templates/index.html` (update header section)

**Step 1: Write failing test**

Open browser and verify:
```javascript
document.getElementById('userMenuButton') === null
// Expected: null (button doesn't exist)
```

**Step 2: Add user button to header**

Update header in `templates/index.html` (around line 1071):

```html
<header class="header">
    <h1>求职助手</h1>
    <p>AI 驱动 · 简历分析 · 面试准备 · 一站式求职解决方案</p>
    <div class="user-nav">
        <button id="userMenuButton" class="btn btn-secondary btn-sm" onclick="toggleUserMenu()">
            <span id="userMenuLabel">登录</span>
        </button>
        <div id="userDropdown" class="user-dropdown" style="display: none;">
            <div id="userDropdownContent"></div>
        </div>
    </div>
</header>
```

**Step 3: Add CSS for user nav**

Add to `<style>` section in `templates/index.html`:

```css
.user-nav {
    position: absolute;
    top: 40px;
    right: 24px;
}

.user-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    min-width: 200px;
    margin-top: 8px;
    box-shadow: var(--shadow-lg);
    z-index: 1001;
}

.user-dropdown.active {
    display: block;
}

.user-dropdown-item {
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.2s ease;
    border-bottom: 1px solid var(--border);
}

.user-dropdown-item:last-child {
    border-bottom: none;
}

.user-dropdown-item:hover {
    background: var(--bg-card-hover);
}

.user-dropdown-item.logout {
    color: var(--danger);
}
```

**Step 4: Run test**

Refresh browser and verify:
```javascript
document.getElementById('userMenuButton') !== null
document.getElementById('userDropdown') !== null
// Expected: true (both elements exist)
```

**Step 5: Commit**

```bash
git add templates/index.html
git commit -m "feat: add user profile header button"
```

---

## Task 8: Implement User Menu and Profile Loading

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser console and verify:
```javascript
typeof toggleUserMenu === 'undefined'
typeof loadUserProfile === 'undefined'
// Expected: 'undefined' (functions don't exist)
```

**Step 2: Add user menu functions**

Add to `static/js/main.js`:

```javascript
let userProfile = null;

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('active');
}

function updateHeaderUserStatus() {
    const button = document.getElementById('userMenuButton');
    const label = document.getElementById('userMenuLabel');

    if (isAuthenticated()) {
        label.textContent = userProfile ? userProfile.username : '个人中心';
        button.onclick = toggleUserMenu;
    } else {
        label.textContent = '登录';
        button.onclick = showAuthModal;
        document.getElementById('userDropdown').style.display = 'none';
    }
}

async function loadUserProfile() {
    if (!isAuthenticated()) {
        userProfile = null;
        renderUserDropdown();
        return;
    }

    try {
        const response = await fetchWithAuth('/api/user/profile');
        const result = await response.json();

        if (result.success) {
            userProfile = result.data;
            updateHeaderUserStatus();
            renderUserDropdown();
        } else {
            handleApiError(response);
        }
    } catch (error) {
        console.error('Load profile error:', error);
    }
}

function renderUserDropdown() {
    const content = document.getElementById('userDropdownContent');

    if (!userProfile) {
        content.innerHTML = `
            <div class="user-dropdown-item" onclick="showAuthModal()">
                <span>登录 / 注册</span>
            </div>
        `;
        return;
    }

    content.innerHTML = `
        <div class="user-dropdown-item" onclick="showPersonalCenter()">
            <span>👤 个人中心</span>
        </div>
        <div class="user-dropdown-item" onclick="showMembershipCenter()">
            <span>👑 会员中心</span>
        </div>
        <div class="user-dropdown-item logout" onclick="logout()">
            <span>🚪 退出登录</span>
        </div>
    `;
}
```

**Step 3: Run test**

1. Login to get authenticated
2. Click user menu button
3. Verify dropdown appears with menu items

```javascript
document.getElementById('userDropdown').classList.contains('active')
// Expected: true after clicking button
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: implement user menu and profile loading"
```

---

## Task 9: Implement Logout Functionality

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser console and verify:
```javascript
typeof logout === 'undefined'
// Expected: 'undefined' (function doesn't exist)
```

**Step 2: Add logout function**

Add to `static/js/main.js`:

```javascript
function logout() {
    if (!confirm('确定要退出登录吗？')) {
        return;
    }

    clearToken();
    userProfile = null;
    updateHeaderUserStatus();
    showToast('已退出登录', 'success');
}
```

**Step 3: Run test**

1. Login to get authenticated
2. Click logout
3. Verify:
   - Token is cleared from localStorage
   - User menu shows "登录"
   - Success toast appears

```javascript
localStorage.getItem('token') === null
// Expected: true (token cleared after logout)
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: implement logout functionality"
```

---

## Task 10: Create Personal Center Modal HTML

**Files:**
- Modify: `templates/index.html` (before </body>)

**Step 1: Write failing test**

Open browser and verify:
```javascript
document.getElementById('personalModal') === null
// Expected: null (modal doesn't exist)
```

**Step 2: Add personal center modal**

Add before `</body>` in `templates/index.html`:

```html
<!-- Personal Center Modal -->
<div id="personalModal" class="modal">
    <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
            <h2>个人中心</h2>
            <button class="modal-close" onclick="closePersonalModal()">×</button>
        </div>

        <form id="profileForm" class="auth-form">
            <div class="form-group">
                <label class="form-label">用户名</label>
                <input type="text" id="profileUsername" class="input-field" placeholder="2-50个字符" required minlength="2" maxlength="50">
            </div>
            <div class="form-group">
                <label class="form-label">邮箱 (只读)</label>
                <input type="email" id="profileEmail" class="input-field" readonly style="background: var(--bg-dark); opacity: 0.6;">
            </div>
            <div class="form-group">
                <label class="form-label">手机号</label>
                <input type="tel" id="profilePhone" class="input-field" placeholder="请输入手机号">
            </div>
            <div class="form-group">
                <label class="form-label">头像URL</label>
                <input type="url" id="profileAvatar" class="input-field" placeholder="https://...">
            </div>

            <!-- User Info Display -->
            <div id="userInfoDisplay" style="margin-top: 24px; padding: 20px; background: var(--bg-dark); border-radius: 12px;">
                <div style="margin-bottom: 12px;">
                    <span style="color: var(--text-muted);">会员等级：</span>
                    <span id="profileMembership" style="font-weight: 600; color: var(--primary);">免费用户</span>
                </div>
                <div style="margin-bottom: 12px;">
                    <span style="color: var(--text-muted);">注册时间：</span>
                    <span id="profileCreated">-</span>
                </div>
            </div>

            <button type="submit" class="btn btn-primary btn-full">保存修改</button>
        </form>
    </div>
</div>
```

**Step 3: Run test**

Open browser and verify:
```javascript
document.getElementById('personalModal') !== null
document.getElementById('profileForm') !== null
// Expected: true (elements exist)
```

**Step 4: Commit**

```bash
git add templates/index.html
git commit -m "feat: add personal center modal HTML"
```

---

## Task 11: Implement Personal Center Logic

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser console and verify:
```javascript
typeof showPersonalCenter === 'undefined'
typeof closePersonalModal === 'undefined'
// Expected: 'undefined' (functions don't exist)
```

**Step 2: Add personal center functions**

Add to `static/js/main.js`:

```javascript
function showPersonalCenter() {
    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }

    document.getElementById('userDropdown').classList.remove('active');

    // Populate form with current profile data
    if (userProfile) {
        document.getElementById('profileUsername').value = userProfile.username || '';
        document.getElementById('profileEmail').value = userProfile.email || '';
        document.getElementById('profilePhone').value = userProfile.phone || '';
        document.getElementById('profileAvatar').value = userProfile.avatar_url || '';

        // Display user info
        const membershipLevels = ['免费用户', '专业版', '尊享版'];
        const levelIndex = userProfile.membership_level || 0;
        document.getElementById('profileMembership').textContent = membershipLevels[levelIndex] || '免费用户';
        document.getElementById('profileCreated').textContent = userProfile.created_at || '-';
    }

    document.getElementById('personalModal').classList.add('active');
}

function closePersonalModal() {
    document.getElementById('personalModal').classList.remove('active');
}

// Initialize profile form
document.getElementById('profileForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }

    const username = document.getElementById('profileUsername').value.trim();
    const phone = document.getElementById('profilePhone').value.trim();
    const avatarUrl = document.getElementById('profileAvatar').value.trim();

    showLoading(true);

    try {
        const updateData = {};
        if (username) updateData.username = username;
        if (phone !== undefined) updateData.phone = phone;
        if (avatarUrl !== undefined) updateData.avatar_url = avatarUrl;

        const response = await fetchWithAuth('/api/user/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });

        const result = await response.json();

        if (result.success) {
            showToast('保存成功', 'success');
            loadUserProfile(); // Reload profile data
        } else {
            showToast(result.error || '保存失败', 'error');
        }
    } catch (error) {
        showToast('保存失败，请重试', 'error');
        console.error('Update profile error:', error);
    } finally {
        showLoading(false);
    }
});
```

**Step 3: Run test**

1. Login and open personal center
2. Modify profile data
3. Save
4. Verify:
   - Data is saved
   - Success toast appears
   - Profile is reloaded

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: implement personal center logic"
```

---

## Task 12: Create Membership Center Modal HTML

**Files:**
- Modify: `templates/index.html` (before </body>)

**Step 1: Write failing test**

Open browser and verify:
```javascript
document.getElementById('membershipModal') === null
// Expected: null (modal doesn't exist)
```

**Step 2: Add membership center modal**

Add before `</body>` in `templates/index.html`:

```html
<!-- Membership Center Modal -->
<div id="membershipModal" class="modal">
    <div class="modal-content" style="max-width: 700px;">
        <div class="modal-header">
            <h2>会员中心</h2>
            <button class="modal-close" onclick="closeMembershipModal()">×</button>
        </div>

        <!-- Current Membership Info -->
        <div id="currentMembership" style="margin-bottom: 32px; padding: 24px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); border-radius: 16px; border: 1px solid var(--border);">
            <h3 style="margin-bottom: 16px;">当前会员</h3>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);" id="currentMembershipLevel">免费用户</div>
            <div style="margin-top: 8px; color: var(--text-muted);" id="currentMembershipExpire"></div>
            <div style="margin-top: 16px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;" id="membershipStats"></div>
        </div>

        <!-- Membership Packages -->
        <h3 style="margin-bottom: 20px;">升级会员</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
            <div class="membership-card">
                <div class="membership-badge">月卡</div>
                <div class="membership-price">¥19.9<span style="font-size: 0.9rem; font-weight: 400;">/月</span></div>
                <ul class="membership-features">
                    <li>✓ 简历无限分析</li>
                    <li>✓ 15道面试题</li>
                    <li>✓ PDF导出</li>
                    <li>✓ 定制自我介绍</li>
                </ul>
                <button class="btn btn-primary btn-full" onclick="createOrder(1)">购买</button>
            </div>
            <div class="membership-card featured">
                <div class="membership-badge">年卡</div>
                <div class="membership-price">¥199.0<span style="font-size: 0.9rem; font-weight: 400;">/年</span></div>
                <div class="membership-save">省39.8元</div>
                <ul class="membership-features">
                    <li>✓ 简历无限分析</li>
                    <li>✓ 15道面试题</li>
                    <li>✓ PDF导出</li>
                    <li>✓ 定制自我介绍</li>
                    <li>✓ AI模拟面试</li>
                    <li>✓ 薪资预测</li>
                </ul>
                <button class="btn btn-primary btn-full" onclick="createOrder(2)">购买</button>
            </div>
            <div class="membership-card">
                <div class="membership-badge">终身卡</div>
                <div class="membership-price">¥499.0<span style="font-size: 0.9rem; font-weight: 400;">/终身</span></div>
                <div class="membership-save">超值</div>
                <ul class="membership-features">
                    <li>✓ 所有功能永久使用</li>
                    <li>✓ 专属客服</li>
                    <li>✓ 简历托管</li>
                    <li>✓ 优先内推</li>
                </ul>
                <button class="btn btn-primary btn-full" onclick="createOrder(3)">购买</button>
            </div>
        </div>
    </div>
</div>
```

**Step 3: Add membership card CSS**

Add to `<style>` section in `templates/index.html`:

```css
.membership-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}

.membership-card:hover {
    border-color: var(--primary);
    transform: translateY(-4px);
}

.membership-card.featured {
    border-color: var(--primary);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), var(--bg-card));
}

.membership-badge {
    display: inline-block;
    padding: 6px 16px;
    background: var(--primary);
    color: white;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 16px;
}

.membership-price {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.membership-save {
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 16px;
}

.membership-features {
    list-style: none;
    padding: 0;
    margin-bottom: 24px;
    text-align: left;
}

.membership-features li {
    padding: 8px 0;
    color: var(--text-secondary);
}
```

**Step 4: Run test**

Open browser and verify:
```javascript
document.getElementById('membershipModal') !== null
document.querySelectorAll('.membership-card').length === 3
// Expected: true
```

**Step 5: Commit**

```bash
git add templates/index.html
git commit -m "feat: add membership center modal HTML"
```

---

## Task 13: Implement Membership Center Logic

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser console and verify:
```javascript
typeof showMembershipCenter === 'undefined'
typeof loadMembershipInfo === 'undefined'
typeof createOrder === 'undefined'
// Expected: 'undefined' (functions don't exist)
```

**Step 2: Add membership functions**

Add to `static/js/main.js`:

```javascript
let membershipInfo = null;

function showMembershipCenter() {
    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }

    document.getElementById('userDropdown').classList.remove('active');
    loadMembershipInfo();
    document.getElementById('membershipModal').classList.add('active');
}

function closeMembershipModal() {
    document.getElementById('membershipModal').classList.remove('active');
}

async function loadMembershipInfo() {
    if (!isAuthenticated()) {
        membershipInfo = null;
        renderCurrentMembership();
        return;
    }

    try {
        const response = await fetchWithAuth('/api/user/membership');
        const result = await response.json();

        if (result.success) {
            membershipInfo = result.data;
            renderCurrentMembership();
        } else {
            handleApiError(response);
        }
    } catch (error) {
        console.error('Load membership error:', error);
    }
}

function renderCurrentMembership() {
    const levels = ['免费用户', '专业版', '尊享版'];
    const levelIndex = membershipInfo ? membershipInfo.level : 0;

    document.getElementById('currentMembershipLevel').textContent = levels[levelIndex];

    const expireEl = document.getElementById('currentMembershipExpire');
    if (membershipInfo && membershipInfo.expire_time) {
        const expireDate = new Date(membershipInfo.expire_time);
        const now = new Date();
        if (expireDate > now) {
            expireEl.textContent = `到期时间：${expireDate.toLocaleDateString()}`;
        } else {
            expireEl.textContent = '会员已过期';
        }
    } else {
        expireEl.textContent = '';
    }

    // Render usage stats
    loadUsageStats();
}

async function loadUsageStats() {
    try {
        const response = await fetchWithAuth('/api/user/usage');
        const result = await response.json();

        if (result.success) {
            renderUsageStats(result.data);
        }
    } catch (error) {
        console.error('Load usage error:', error);
    }
}

function renderUsageStats(data) {
    const statsEl = document.getElementById('membershipStats');

    if (!data) {
        statsEl.innerHTML = '';
        return;
    }

    statsEl.innerHTML = `
        <div style="text-align: center;">
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">${data.today_count || 0}</div>
            <div style="color: var(--text-muted); font-size: 0.875rem;">今日分析</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--accent);">${data.remaining || 0}</div>
            <div style="color: var(--text-muted); font-size: 0.875rem;">剩余次数</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.25rem; font-weight: 700;">${data.daily_limit || 3}</div>
            <div style="color: var(--text-muted); font-size: 0.875rem;">每日限制</div>
        </div>
    `;
}

async function createOrder(productType) {
    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }

    showLoading(true);

    try {
        const response = await fetchWithAuth('/api/payment/create-order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_type: productType,
                pay_type: 0  // 0: 微信支付, 1: 支付宝
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(`订单创建成功：${result.data.order_no}`, 'success');
            // TODO: Integrate with actual payment flow
            console.log('Order created:', result.data);
            alert(`订单创建成功！\n订单号：${result.data.order_no}\n金额：¥${result.data.amount}\n\n请在后续版本完成支付集成`);
        } else {
            showToast(result.error || '创建订单失败', 'error');
        }
    } catch (error) {
        showToast('创建订单失败，请重试', 'error');
        console.error('Create order error:', error);
    } finally {
        showLoading(false);
    }
}
```

**Step 3: Run test**

1. Login and open membership center
2. Verify:
   - Current membership displays
   - Usage stats load
   - Clicking purchase buttons shows order creation

```javascript
document.getElementById('currentMembershipLevel').textContent === '免费用户'
// Expected: true for free user
```

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: implement membership center logic"
```

---

## Task 14: Initialize Auth State on Page Load

**Files:**
- Modify: `static/js/main.js` (update DOMContentLoaded event)

**Step 1: Write failing test**

Refresh page and verify:
```javascript
typeof loadUserProfile === 'undefined'
// Expected: function exists but not called on load
```

**Step 2: Update initialization**

Update DOMContentLoaded event in `static/js/main.js` (around line 22):

```javascript
document.addEventListener('DOMContentLoaded', function() {
    initTipsCarousel();
    initJobsCarousel();
    initUpload();
    initTabs();
    loadResumes();
    refreshApiStatus();

    // Initialize auth state
    loadUserProfile();
    updateHeaderUserStatus();

    // Add click outside to close dropdowns
    document.addEventListener('click', function(e) {
        const userDropdown = document.getElementById('userDropdown');
        const userButton = document.getElementById('userMenuButton');
        if (userDropdown && userButton) {
            if (!userDropdown.contains(e.target) && !userButton.contains(e.target)) {
                userDropdown.classList.remove('active');
            }
        }
    });
});
```

**Step 3: Run test**

1. Refresh page
2. Verify:
   - If logged in previously, user profile loads
   - Header shows correct user status

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: initialize auth state on page load"
```

---

## Task 15: Add Protected Route Handling

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open browser, try to access functions without login:
```javascript
localStorage.removeItem('token')
showPersonalCenter()
// Expected: Shows auth modal instead of personal center
```

**Step 2: Add protected route check**

Update protected functions in `static/js/main.js`:

```javascript
function showPersonalCenter() {
    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }
    // ... rest of function
}

function showMembershipCenter() {
    if (!isAuthenticated()) {
        showAuthModal();
        return;
    }
    // ... rest of function
}
```

**Step 3: Run test**

1. Clear token and refresh
2. Click personal center menu
3. Verify:
   - Auth modal shows instead of personal center
   - After login, personal center opens

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: add protected route handling"
```

---

## Task 16: Add Click Outside Modal Close

**Files:**
- Modify: `static/js/main.js`

**Step 1: Write failing test**

Open auth modal and click outside:
```javascript
document.getElementById('authModal').classList.add('active')
document.getElementById('authModal').click()
// Expected: Modal should close
```

**Step 2: Add click outside handlers**

Add to `static/js/main.js` after modal close functions:

```javascript
// Close modals when clicking outside
document.getElementById('authModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeAuthModal();
    }
});

document.getElementById('personalModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closePersonalModal();
    }
});

document.getElementById('membershipModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeMembershipModal();
    }
});
```

**Step 3: Run test**

1. Open each modal
2. Click outside the modal content
3. Verify:
   - Modal closes
   - No JavaScript errors

**Step 4: Commit**

```bash
git add static/js/main.js
git commit -m "feat: add click outside modal close"
```

---

## Task 17: Update analyzeResume to Use fetchWithAuth

**Files:**
- Modify: `static/js/main.js:310-322`

**Step 1: Write failing test**

Analyze resume while logged out:
```javascript
localStorage.removeItem('token')
analyzeResume()
// Expected: Should work (public endpoint)
```

**Step 2: Update analyze function**

Replace analyzeResume function to use fetchWithAuth:

```javascript
async function analyzeResume() {
    var response = await fetchWithAuth('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: currentResumeId })
    });

    var result = await response.json();
    handleApiError(response);

    if (result.success) {
        renderResumeAnalysis(result.data);
    }
}
```

**Step 3: Update all API calls**

Replace all fetch calls with fetchWithAuth for consistency:
- `matchJob` (line 324)
- `generateInterview` (line 341)
- `generateSelfIntro` (line 358)
- `loadResumes` (line 203)
- `loadUserProfile` (already updated)
- `loadMembershipInfo` (already updated)
- `loadUsageStats` (already updated)

**Step 4: Run test**

1. Login
2. Upload and analyze resume
3. Verify:
   - Analysis completes successfully
   - Token is sent in Authorization header

**Step 5: Commit**

```bash
git add static/js/main.js
git commit -m "refactor: use fetchWithAuth for all API calls"
```

---

## Task 18: Test Complete User Flow

**Files:**
- Test: Manual browser testing

**Step 1: Test Registration Flow**

1. Open application
2. Click "登录" button in header
3. Click "立即注册"
4. Fill registration form with valid data
5. Submit
6. Verify:
   - Success toast appears
   - User menu shows username
   - Token is in localStorage

**Step 2: Test Login Flow**

1. Logout (if logged in)
2. Click "登录" button
3. Fill login form with valid credentials
4. Submit
5. Verify:
   - Success toast appears
   - User profile loads
   - Header updates

**Step 3: Test Personal Center**

1. Click personal center from menu
2. Modify profile data
3. Save
4. Verify:
   - Changes persist
   - Success toast appears

**Step 4: Test Membership Center**

1. Click membership center from menu
2. Verify:
   - Current membership displays
   - Usage stats show
   - Package cards render

**Step 5: Test Protected Routes**

1. Logout
2. Try to open personal center/membership center
3. Verify:
   - Auth modal appears
   - Original modal doesn't open

**Step 6: Test Auto-Login**

1. Login successfully
2. Refresh page
3. Verify:
   - User remains logged in
   - Profile loads automatically
   - Header shows correct state

**Step 7: Test Logout**

1. Click logout
2. Verify:
   - Token cleared
   - Header shows "登录"
   - User menu hides

**Step 8: Test Error Handling**

1. Login with invalid credentials
2. Register with existing email
3. Verify:
   - Appropriate error messages
   - Form doesn't submit invalid data

**Step 9: Document Results**

Create test results file:

```bash
cat > docs/plans/frontend-user-system-test-results.md << 'EOF'
# Frontend User System Test Results

**Test Date:** 2026-01-15
**Tester:** [Name]

## Test Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Registration | ✅/❌ | |
| Login | ✅/❌ | |
| Auto-login on refresh | ✅/❌ | |
| Personal Center | ✅/❌ | |
| Profile Update | ✅/❌ | |
| Membership Center | ✅/❌ | |
| Usage Stats | ✅/❌ | |
| Protected Routes | ✅/❌ | |
| Logout | ✅/❌ | |
| Error Handling | ✅/❌ | |

## Issues Found

1. [Description]
2. [Description]

## Recommendations

1. [Recommendation]
2. [Recommendation]
EOF
```

**Step 10: Commit**

```bash
git add docs/plans/frontend-user-system-test-results.md
git commit -m "test: add frontend user system test results"
```

---

## Summary

This implementation plan adds the following features:

1. **JWT Token Management**
   - Token storage in localStorage
   - Automatic token injection in API calls
   - Token validation and cleanup

2. **Authentication**
   - Login modal with email/password
   - Registration modal with validation
   - Auto-redirect to login for protected routes

3. **User Profile**
   - Personal center modal
   - Profile viewing and editing
   - Real-time updates

4. **Membership Center**
   - Current membership display
   - Usage statistics
   - Package comparison and purchase

5. **UI/UX**
   - Header user menu
   - Modal-based interactions
   - Responsive design
   - Error handling

## Files Modified

| File | Changes |
|------|----------|
| `static/js/main.js` | Add auth functions, API calls, state management |
| `templates/index.html` | Add modal HTML, header button, CSS styles |

## New Functions

- `getToken()`, `setToken()`, `clearToken()`, `isAuthenticated()`
- `fetchWithAuth()`, `handleApiError()`
- `showAuthModal()`, `closeAuthModal()`
- `showLoginForm()`, `showRegisterForm()`
- `showPersonalCenter()`, `closePersonalCenter()`
- `showMembershipCenter()`, `closeMembershipCenter()`
- `loadUserProfile()`, `loadMembershipInfo()`, `loadUsageStats()`
- `toggleUserMenu()`, `renderUserDropdown()`
- `logout()`, `createOrder()`

## API Endpoints Used

- `POST /api/user/register`
- `POST /api/user/login`
- `GET /api/user/profile`
- `PUT /api/user/profile`
- `GET /api/user/membership`
- `GET /api/user/usage`
- `POST /api/payment/create-order`
