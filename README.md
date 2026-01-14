# 求职帮助系统 - 使用说明

## 快速开始

### 方法1：双击启动（推荐）
直接双击 `启动服务器.bat` 文件启动系统

### 方法2：命令行启动
```bash
python app.py
```

服务器启动后，在浏览器中访问：
```
http://localhost:5000
```

## 功能测试

启动服务器后，在新终端运行测试脚本：
```bash
python test_system.py
```

## 系统功能

### 1. 简历上传
支持格式：PDF、Word (docx)、TXT、图片 (jpg/png)
操作：点击上传区域或拖拽文件

### 2. 简历分析
- 自动提取技能关键词
- 评估简历质量（0-100分）
- 提供改进建议
- 推荐适合的岗位方向

### 3. 岗位匹配
- 输入岗位JD
- 计算匹配度评分
- 显示匹配/缺失技能
- 提供提升建议

### 4. 面试题生成
- 自动生成12-15道面试题
- 包含参考回答和要点
- 涵盖自我介绍、技术能力、行为面试等

### 5. 自我介绍生成
- 1分钟精简版（200-300字）
- 3分钟详细版（500-800字）
- 根据简历和JD定制

## API配置

系统默认使用硅基流动API。如需自定义：

1. 访问 http://localhost:5000
2. 点击右上角"配置"按钮
3. 输入自定义API Key
4. 测试连接并保存

## 文件说明

- `app.py` - Flask主应用
- `run.html` - 独立HTML文件（包含所有CSS和JS）
- `test_system.py` - 系统测试脚本
- `启动服务器.bat` - Windows启动脚本
- `requirements.txt` - Python依赖

## 依赖安装

```bash
pip install -r requirements.txt
```

## 注意事项

1. **API Key**：系统需要AI服务API Key，首次使用请配置
2. **网络**：需要访问AI API服务，确保网络连接正常
3. **OCR**：图片识别需要安装Tesseract OCR
4. **文件大小**：上传文件限制16MB

## 故障排除

### 端口被占用
如果5000端口被占用，修改 `app.py` 最后一行：
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为其他端口
```

### 模块未找到
```bash
pip install -r requirements.txt
```

### OCR识别失败
确保已安装Tesseract OCR：
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

## 技术栈

- **后端**: Python Flask
- **数据库**: SQLite
- **前端**: 原生 HTML/CSS/JavaScript
- **AI服务**: 硅基流动 API (兼容OpenAI接口)
- **文件处理**: pdfplumber, python-docx, Pillow, pytesseract

## 开发说明

详见 `AGENTS.md` 文件，包含：
- 代码风格指南
- API设计说明
- 数据库结构
- 错误处理规范

---

**祝您求职顺利！**
