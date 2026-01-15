#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户认证系统集成测试脚本
测试完整用户流程: 注册、登录、个人中心、会员中心、API调用
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

# 测试用户数据
test_user = {
    "username": "testuser_" + str(int(time.time())),
    "email": f"test{int(time.time())}@example.com",
    "password": "test123456",
    "phone": "13800138000"
}

# 存储token
token = None
user_id = None


def print_section(title):
    """打印测试分节"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(test_name, success, message=""):
    """打印测试结果"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} - {test_name}")
    if message:
        print(f"  {message}")
    return success


def test_register():
    """测试用户注册"""
    print_section("测试 1: 用户注册")

    response = requests.post(
        f"{BASE_URL}/api/user/register",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print_result("用户注册", True, f"用户: {test_user['username']}")
            return True
        else:
            print_result("用户注册", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("用户注册", False, f"HTTP {response.status_code}")
        return False


def test_login():
    """测试用户登录"""
    print_section("测试 2: 用户登录")

    global token, user_id

    response = requests.post(
        f"{BASE_URL}/api/user/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            token = result["data"]["token"]
            user_id = result["data"]["user"]["id"]
            print_result("用户登录", True, f"用户ID: {user_id}")
            print(f"  Token: {token[:50]}...")
            return True
        else:
            print_result("用户登录", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("用户登录", False, f"HTTP {response.status_code}")
        return False


def test_get_profile():
    """测试获取用户资料"""
    print_section("测试 3: 获取用户资料")

    if not token:
        return print_result("获取用户资料", False, "未登录")

    response = requests.get(
        f"{BASE_URL}/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            profile = result["data"]
            print_result("获取用户资料", True, f"用户: {profile.get('username')}")
            print(f"  邮箱: {profile.get('email')}")
            print(f"  会员等级: {profile.get('membership_level', 0)}")
            return True
        else:
            print_result("获取用户资料", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("获取用户资料", False, f"HTTP {response.status_code}")
        return False


def test_update_profile():
    """测试更新用户资料"""
    print_section("测试 4: 更新用户资料")

    if not token:
        return print_result("更新用户资料", False, "未登录")

    update_data = {
        "phone": "13900139000",
        "avatar_url": "https://example.com/avatar.jpg"
    }

    response = requests.put(
        f"{BASE_URL}/api/user/profile",
        json=update_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print_result("更新用户资料", True)
            return True
        else:
            print_result("更新用户资料", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("更新用户资料", False, f"HTTP {response.status_code}")
        return False


def test_get_membership():
    """测试获取会员信息"""
    print_section("测试 5: 获取会员信息")

    if not token:
        return print_result("获取会员信息", False, "未登录")

    response = requests.get(
        f"{BASE_URL}/api/user/membership",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            membership = result["data"]
            levels = ["免费用户", "专业版", "尊享版"]
            level_index = membership.get("level", 0)
            level_name = levels[level_index] if 0 <= level_index < len(levels) else "未知"
            print_result("获取会员信息", True, f"等级: {level_name}")
            expire_time = membership.get("expire_time")
            if expire_time:
                print(f"  到期时间: {expire_time}")
            return True
        else:
            print_result("获取会员信息", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("获取会员信息", False, f"HTTP {response.status_code}")
        return False


def test_get_usage():
    """测试获取使用统计"""
    print_section("测试 6: 获取使用统计")

    if not token:
        return print_result("获取使用统计", False, "未登录")

    response = requests.get(
        f"{BASE_URL}/api/user/usage",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            usage = result["data"]
            print_result("获取使用统计", True, f"今日: {usage.get('today_count', 0)}次")
            print(f"  剩余次数: {usage.get('remaining', 0)}")
            print(f"  每日限制: {usage.get('daily_limit', 3)}")
            return True
        else:
            print_result("获取使用统计", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("获取使用统计", False, f"HTTP {response.status_code}")
        return False


def test_create_order():
    """测试创建订单"""
    print_section("测试 7: 创建订单")

    if not token:
        return print_result("创建订单", False, "未登录")

    # 创建月卡订单 (product_type: 1)
    response = requests.post(
        f"{BASE_URL}/api/payment/create-order",
        json={
            "product_type": 1,
            "pay_type": 0  # 微信支付
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            order = result["data"]
            print_result("创建订单", True, f"订单号: {order.get('order_no')}")
            print(f"  金额: CNY{order.get('amount')}")
            return True
        else:
            print_result("创建订单", False, result.get("error", "未知错误"))
            return False
    else:
        print_result("创建订单", False, f"HTTP {response.status_code}")
        return False


def test_protected_without_auth():
    """测试未认证访问受保护接口"""
    print_section("测试 8: 未认证访问受保护接口")

    # 尝试不带token访问个人资料
    response = requests.get(f"{BASE_URL}/api/user/profile")

    if response.status_code == 200:
        result = response.json()
        if not result.get("success") and "登录" in result.get("error", ""):
            return print_result("未认证访问", True, "正确拒绝未认证请求")
        else:
            return print_result("未认证访问", False, f"应返回错误但得到: {result}")
    else:
        return print_result("未认证访问", False, f"应返回200但得到 {response.status_code}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  用户认证系统集成测试")
    print("=" * 60)

    results = []

    # 运行所有测试
    results.append(test_register())
    results.append(test_login())
    results.append(test_get_profile())
    results.append(test_update_profile())
    results.append(test_get_membership())
    results.append(test_get_usage())
    results.append(test_create_order())
    results.append(test_protected_without_auth())

    # 汇总结果
    print_section("测试结果汇总")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    run_all_tests()
