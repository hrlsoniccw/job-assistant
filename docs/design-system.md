# 设计规范 - Job Assistant 求职助手

## 一、设计理念

参考 ResumeGPT 的设计风格：
- **极简** - 减少视觉干扰，聚焦内容
- **卡片式** - 每个功能块独立成卡片
- **深色主题** - 高级感、科技感
- **动画适度** - 加载、过渡有动画，其他保持静态

## 二、配色方案

### 主色调（紫色渐变）
```css
--primary: #667eea;        /* 浅紫色 */
--primary-dark: #4f46e5;   /* 深紫色 */
--secondary: #8b5cf6;      /* 蓝紫色 */
--accent: #a78bfa;         /* 浅紫 */
```

### 背景色
```css
--bg-dark: #0f172a;        /* 深色背景 - 主背景 */
--bg-card: #1e293b;        /* 卡片背景 */
--bg-card-hover: #334155;  /* 卡片悬停 */
--bg-input: #0f172a;       /* 输入框背景 */
```

### 文字色
```css
--text-primary: #f1f5f9;   /* 主文字 - 白色 */
--text-secondary: #94a3b8; /* 次要文字 - 灰白 */
--text-muted: #64748b;     /* 辅助文字 - 灰色 */
--text-dark: #1e293b;      /* 深色文字（浅色模式下用） */
```

### 功能色
```css
--success: #10b981;        /* 成功 - 绿色 */
--success-bg: rgba(16, 185, 129, 0.1);
--warning: #f59e0b;        /* 警告 - 橙色 */
--warning-bg: rgba(245, 158, 11, 0.1);
--error: #ef4444;          /* 错误 - 红色 */
--error-bg: rgba(239, 68, 68, 0.1);
--info: #3b82f6;           /* 信息 - 蓝色 */
```

### 边框色
```css
--border: #334155;         /* 默认边框 */
--border-light: #475569;   /* 浅边框 */
--border-focus: #667eea;   /* 聚焦边框 */
```

## 三、字体方案

### 字体族
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 字号
```css
--text-xs: 0.75rem;    /* 12px - 辅助说明 */
--text-sm: 0.875rem;   /* 14px - 次要文字 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 小标题 */
--text-xl: 1.25rem;    /* 20px - 标题 */
--text-2xl: 1.5rem;    /* 24px - 大标题 */
--text-3xl: 1.875rem;  /* 30px - 页面标题 */
--text-4xl: 2.25rem;   /* 36px - Hero标题 */
```

### 字重
```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

## 四、间距系统

### 基础间距
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
```

### 页面布局
```css
--container-max: 1200px;  /* 主容器最大宽度 */
--page-padding: 1.5rem;   /* 页面内边距 */
--section-gap: 3rem;      /* 区块间距 */
```

## 五、圆角系统

```css
--radius-sm: 0.375rem;    /* 6px - 小圆角 */
--radius-md: 0.5rem;      /* 8px - 中圆角 */
--radius-lg: 0.75rem;     /* 12px - 大圆角 */
--radius-xl: 1rem;        /* 16px - 超大圆角 */
--radius-2xl: 1.5rem;     /* 24px - 卡片圆角 */
--radius-full: 9999px;    /* 圆形 */
```

## 六、阴影系统

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-glow: 0 0 20px rgba(102, 126, 234, 0.3);  /* 紫色光晕 */
```

## 七、过渡动画

```css
--transition-fast: 150ms ease;
--transition-normal: 300ms ease;
--transition-slow: 500ms ease;
```

### 动画效果
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

## 八、组件样式

### 按钮 (Button)
```css
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-lg);
    font-size: var(--text-base);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-normal);
    border: none;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    box-shadow: var(--shadow-md);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border);
}

.btn-secondary:hover {
    background: var(--bg-card-hover);
    border-color: var(--primary);
}
```

### 卡片 (Card)
```css
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-2xl);
    padding: var(--space-6);
    transition: all var(--transition-normal);
}

.card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow-lg);
}
```

### 输入框 (Input)
```css
.input {
    width: 100%;
    padding: 0.75rem 1rem;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    color: var(--text-primary);
    font-size: var(--text-base);
    transition: all var(--transition-fast);
}

.input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.input::placeholder {
    color: var(--text-muted);
}
```

## 九、响应式设计

```css
/* 移动端 */
@media (max-width: 640px) {
    --page-padding: 1rem;
    --text-4xl: 1.875rem;
    --text-3xl: 1.5rem;
}

/* 平板 */
@media (min-width: 641px) and (max-width: 1024px) {
    --page-padding: 1.5rem;
}

/* 桌面端 */
@media (min-width: 1025px) {
    --page-padding: 2rem;
}
```

## 十、页面布局规范

### 顶部导航
```css
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--page-padding);
    max-width: var(--container-max);
    margin: 0 auto;
}
```

### Hero区域
```css
.hero {
    text-align: center;
    padding: var(--space-16) var(--page-padding);
}

.hero-title {
    font-size: var(--text-4xl);
    font-weight: var(--font-bold);
    margin-bottom: var(--space-4);
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: var(--text-lg);
    color: var(--text-secondary);
    margin-bottom: var(--space-8);
}
```

### 主内容区
```css
.main-content {
    max-width: var(--container-max);
    margin: 0 auto;
    padding: 0 var(--page-padding) var(--space-16);
}

.section {
    margin-bottom: var(--section-gap);
}
```

---

## 十一、设计资源

### 图标库
- 使用：Phosphor Icons 或 Heroicons
- 格式：SVG
- 大小：24x24

### 图片资源
- 插图：undraw.co 或 similar
- 头像：ui-avatars.com
- 图标：phosphoricons.com

### 设计工具
- Figma（推荐）
- Sketch
- Adobe XD

---

*文档版本：1.0*
*最后更新：2024-01-14*
