# AGENTS.md - 求职帮助系统代码库指南

## 项目概述

**求职帮助系统** - 简历分析与面试助手
- 技术栈: Python Flask + SQLite + 原生 HTML/CSS/JavaScript
- AI集成: 硅基流动 API (OpenAI兼容接口)
- 主要功能: 简历解析、AI分析、岗位匹配、面试题生成、用户系统、会员体系

## 运行、构建和测试命令

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyjwt flask-login reportlab

# 运行应用 (http://localhost:5000)
python app.py

# 运行所有测试
python test_system.py

# 运行用户系统测试
python test_user_system.py

# 运行单个测试函数
python -c "from test_system import test_api_status; test_api_status()"

# 清理测试生成的临时文件
del test_resume.txt 2>nul
```

## 代码风格指南

### 导入顺序
标准库 → 第三方库 → 本地模块
```python
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from functools import wraps

import requests
from flask import Flask, jsonify, request

from utils.file_parser import parse_resume
from config import get_api_config
```

### 命名约定
- 变量/函数: `snake_case` (`parse_resume`, `api_stats`)
- 类名: `PascalCase` (`AIClient`, `ResumeAnalyzer`)
- 常量: `UPPER_SNAKE_CASE` (`UPLOAD_FOLDER`, `API_TIMEOUT`)
- 私有方法: 单下划线前缀 (`_parse_json_response`)
- 模块名: `snake_case` (`file_parser.py`, `ai_client.py`)

### 类型提示
```python
from typing import Optional, Dict, List, Any

def parse_resume(file_path: str, filename: str) -> str:
    """解析简历文件,返回纯文本内容"""
    pass
```

### 文档字符串
所有公共函数应包含docstring，采用简洁描述风格。
```python
def parse_resume(file_path: str, filename: str) -> str:
    """解析简历文件，返回纯文本内容"""
    pass
```

### 代码格式
- 缩进: 4空格
- 行长度: 无严格限制，但保持单行简洁
- 字符串引号: 单引号优先 `'`（JSON相关用双引号）

## 错误处理

### API路由
```python
@app.route('/api/upload', methods=['POST'])
def upload_resume():
    try:
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

### 工具函数
```python
def parse_resume(file_path: str, filename: str) -> str:
    try:
        return text
    except Exception as e:
        print(f"解析文件失败 {filename}: {e}")
        return ""
```

### 可选依赖
```python
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
```

### 错误返回格式
```python
return jsonify({'success': False, 'error': '错误描述'})
```

## 数据库操作

```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
resume = cursor.fetchone()
conn.close()
```

**注意**: 必须使用参数化查询防止SQL注入，写操作后commit。

## 配置管理

- 主配置: `config.py` - 使用 `get_api_config()` 获取
- 路径处理: 使用硬编码绝对路径避免编码问题
- API Key: 环境变量 `API_KEY` 或 `user_config.json`

## JSON响应格式

```json
{"success": true, "data": {...}}
{"success": false, "error": "错误信息"}
```

JSON序列化使用 `ensure_ascii=False` 保留中文字符。

## 文件结构

```
求职帮助系统/
├── app.py                 # Flask主应用 (路由和API)
├── config.py              # 配置文件 (API密钥管理)
├── requirements.txt       # Python依赖
├── test_system.py         # 集成测试脚本
├── static/index.html      # 单页应用界面
├── uploads/               # 上传的简历文件
├── data/                  # SQLite数据库
└── utils/                 # 工具模块
    ├── file_parser.py     # 文件解析(PDF/Word/OCR)
    ├── ai_client.py       # AI API调用
    ├── analyzer.py        # 简历分析和匹配
    └── pdf_exporter.py    # PDF导出
```

## 常用代码片段

```python
# 查询数据库
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
resume = cursor.fetchone()
conn.close()

# 调用AI分析
ai = get_ai_client()
result = ai.analyze_resume(resume_text)

# 返回API响应
return jsonify({'success': True, 'data': result})
```

## 前端代码风格

```javascript
// 常量命名: UPPER_SNAKE_CASE
const API_BASE_URL = '/api';

// 变量命名: camelCase
let resumeId = null;

// 函数命名: camelCase
function parseResume() {
    // 函数简洁，职责单一
}

// 事件处理: on + 事件名
document.getElementById('btn').onclick = handleClick;
```

```css
/* CSS类名: kebab-case */
.resume-container {
    padding: 20px;
}

/* 保持CSS简单，避免过度嵌套 */
```

## 安全注意事项

- 所有用户输入必须验证和清理
- API Key 存储在环境变量或 `user_config.json`（不提交到版本控制）
- 使用参数化查询防止SQL注入
- 文件上传检查文件类型和大小
- 返回给客户端的错误信息不泄露敏感信息

## 开发优先级

1. 功能实现 > 代码重构
2. 快速开发 > 严格类型安全
3. 简单直接 > 过度抽象

项目处于早期开发阶段，添加新功能时遵循现有模式即可。
