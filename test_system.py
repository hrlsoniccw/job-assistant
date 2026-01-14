#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证求职帮助系统功能
"""
import requests
import time
import sys

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://127.0.0.1:5000"

def test_api_status():
    """测试API状态"""
    print("\n[测试1] 获取API状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        provider = data['data'].get('provider', 'N/A')
        print(f"[通过] API状态正常 - 提供商: {provider}")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def test_root_page():
    """测试主页访问"""
    print("\n[测试2] 访问主页...")
    try:
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert "求职帮助系统" in response.text
        print("[通过] 主页访问正常")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def test_upload_resume():
    """测试简历上传"""
    print("\n[测试3] 测试简历上传...")
    test_resume_content = """张三
联系方式：13800138000
邮箱：test@example.com

教育背景
- 清华大学 计算机科学 本科 2015-2019

工作经历
- 腾讯 高级软件工程师 2019-2022
  负责微信支付后端开发，使用Python、Django、MySQL
  完成了日交易量1亿的系统优化

技能
- Python, Django, Flask, MySQL, Redis, Docker
- Git, Linux, RESTful API
"""
    try:
        with open('test_resume.txt', 'w', encoding='utf-8') as f:
            f.write(test_resume_content)

        with open('test_resume.txt', 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        resume_id = data['data']['resume_id']
        print(f"[通过] 简历上传成功 - ID: {resume_id}")
        return resume_id
    except Exception as e:
        print(f"[失败] {e}")
        return None

def test_analyze_resume(resume_id):
    """测试简历分析"""
    print(f"\n[测试4] 分析简历 (ID: {resume_id})...")
    try:
        response = requests.post(f"{BASE_URL}/api/analyze",
                                 json={'resume_id': resume_id})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'analysis' in data['data']
        score = data['data']['analysis'].get('score', 'N/A')
        print(f"[通过] 简历分析完成 - 评分: {score}")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def test_match_jd(resume_id):
    """测试岗位匹配"""
    print(f"\n[测试5] 岗位匹配 (ID: {resume_id})...")
    jd_text = """
岗位名称：Python后端开发工程师
岗位职责：
1. 负责后端系统设计和开发
2. 优化系统性能

任职要求：
1. 3年以上Python开发经验
2. 熟悉Django或Flask框架
3. 熟悉MySQL、Redis
"""
    try:
        response = requests.post(f"{BASE_URL}/api/match",
                                 json={'resume_id': resume_id, 'jd_text': jd_text})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        match_score = data['data'].get('match_score', 'N/A')
        print(f"[通过] 岗位匹配完成 - 匹配度: {match_score}")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def test_generate_interview(resume_id):
    """测试面试题生成"""
    print(f"\n[测试6] 生成面试题 (ID: {resume_id})...")
    try:
        response = requests.post(f"{BASE_URL}/api/interview",
                                 json={'resume_id': resume_id, 'jd_text': ''})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        questions = data['data'].get('interview_questions', [])
        print(f"[通过] 面试题生成完成 - 共 {len(questions)} 道题")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def test_self_introduction(resume_id):
    """测试自我介绍生成"""
    print(f"\n[测试7] 生成自我介绍 (ID: {resume_id})...")
    try:
        response = requests.post(f"{BASE_URL}/api/self-intro",
                                 json={'resume_id': resume_id, 'jd_text': ''})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'one_minute' in data['data']
        assert 'three_minutes' in data['data']
        print("[通过] 自我介绍生成完成")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def test_list_resumes():
    """测试简历列表"""
    print("\n[测试8] 获取简历列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/resumes")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        count = len(data['data'])
        print(f"[通过] 简历列表获取成功 - 共 {count} 份简历")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        return False

def main():
    print("="*60)
    print("求职帮助系统 - 功能测试")
    print("="*60)

    # 测试序列
    results = []
    resume_id = None

    results.append(("主页访问", test_root_page()))
    results.append(("API状态", test_api_status()))

    # 如果主页和API都正常，继续测试其他功能
    if results[0][1] and results[1][1]:
        resume_id = test_upload_resume()

        if resume_id:
            results.append(("简历分析", test_analyze_resume(resume_id)))
            results.append(("岗位匹配", test_match_jd(resume_id)))
            results.append(("面试题生成", test_generate_interview(resume_id)))
            results.append(("自我介绍", test_self_introduction(resume_id)))
            results.append(("简历列表", test_list_resumes()))

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[通过]" if result else "[失败]"
        print(f"{test_name:.<30} {status}")

    print("-"*60)
    print(f"总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n[成功] 所有测试通过！系统运行完美！")
    else:
        print(f"\n[警告] 有 {total - passed} 项测试失败，请检查")

    print("="*60)

if __name__ == "__main__":
    main()
