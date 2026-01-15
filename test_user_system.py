#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户系统测试脚本
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000"


def test_user_register():
    """测试用户注册"""
    print("\n[Test] 用户注册...")
    try:
        response = requests.post(f"{BASE_URL}/api/user/register", json={
            'username': f'testuser_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'test123456',
            'phone': '13800138000'
        })
        data = response.json()
        if data['success']:
            print(f"[Pass] 注册成功 - Token: {data['data']['token'][:20]}...")
            return data['data']['token'], data['data']['user']['id']
        else:
            print(f"[Fail] 注册失败: {data['error']}")
            return None, None
    except Exception as e:
        print(f"[Error] {e}")
        return None, None


def test_user_login(token):
    """测试用户登录"""
    print("\n[Test] 用户登录...")
    try:
        response = requests.post(f"{BASE_URL}/api/user/login", json={
            'email': 'test@example.com',  # 需要先用有效邮箱注册
            'password': 'test123456'
        })
        data = response.json()
        if data['success']:
            print(f"[Pass] 登录成功 - Token: {data['data']['token'][:20]}...")
            return data['data']['token']
        else:
            print(f"[Fail] 登录失败: {data['error']}")
            return None
    except Exception as e:
        print(f"[Error] {e}")
        return None


def test_profile(token, user_id):
    """测试获取用户信息"""
    print("\n[Test] 获取用户信息...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        data = response.json()
        if data['success']:
            print(f"[Pass] 用户信息: {data['data']}")
            return True
        else:
            print(f"[Fail] 获取失败: {data['error']}")
            return False
    except Exception as e:
        print(f"[Error] {e}")
        return False


def test_membership(token):
    """测试会员信息"""
    print("\n[Test] 获取会员信息...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}/api/user/membership", headers=headers)
        data = response.json()
        if data['success']:
            print(f"[Pass] 会员信息: {data['data']}")
            return True
        else:
            print(f"[Fail] 获取失败: {data['error']}")
            return False
    except Exception as e:
        print(f"[Error] {e}")
        return False


def test_usage(token):
    """测试使用统计"""
    print("\n[Test] 获取使用统计...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}/api/user/usage", headers=headers)
        data = response.json()
        if data['success']:
            print(f"[Pass] 使用统计: {data['data']}")
            return True
        else:
            print(f"[Fail] 获取失败: {data['error']}")
            return False
    except Exception as e:
        print(f"[Error] {e}")
        return False


def test_products():
    """测试获取会员套餐"""
    print("\n[Test] 获取会员套餐...")
    try:
        response = requests.get(f"{BASE_URL}/api/products")
        data = response.json()
        if data['success']:
            print(f"[Pass] 套餐列表:")
            for p in data['data']:
                print(f"  - {p['name']}: ¥{p['price']}")
            return True
        else:
            print(f"[Fail] 获取失败: {data['error']}")
            return False
    except Exception as e:
        print(f"[Error] {e}")
        return False


def main():
    print("=" * 60)
    print("用户系统 - 功能测试")
    print("=" * 60)
    
    # 确保服务已启动
    print("\n确保Flask服务已启动: python app.py")
    print(f"API地址: {BASE_URL}")
    print()
    
    results = []
    
    # 1. 测试注册
    token, user_id = test_user_register()
    results.append(('用户注册', token is not None))
    
    if token:
        # 2. 测试获取用户信息
        results.append(('获取用户信息', test_profile(token, user_id)))
        
        # 3. 测试会员信息
        results.append(('会员信息', test_membership(token)))
        
        # 4. 测试使用统计
        results.append(('使用统计', test_usage(token)))
        
        # 5. 测试记录使用次数
        print("\n[Test] 记录使用次数...")
        try:
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.post(f"{BASE_URL}/api/user/usage", json={'usage_type': 'analyze', 'count': 1}, headers=headers)
            data = resp.json()
            if data['success']:
                print("[Pass] 使用记录成功")
                results.append(('记录使用次数', True))
            else:
                print(f"[Fail] 记录失败: {data['error']}")
                results.append(('记录使用次数', False))
        except Exception as e:
            print(f"[Error] {e}")
            results.append(('记录使用次数', False))
    
    # 6. 测试获取会员套餐
    results.append(('会员套餐', test_products()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[Pass]" if result else "[Fail]"
        print(f"{test_name:<30} {status}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n[成功] 所有测试通过！")
    else:
        print(f"\n[警告] 有 {total - passed} 项测试失败")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
