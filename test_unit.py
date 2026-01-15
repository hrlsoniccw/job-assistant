#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单元测试 - 支付系统
"""
import unittest
import requests
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:5000"


class TestPaymentSystem(unittest.TestCase):
    """支付系统测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user_token = None
        self.user_id = None
        self._register_user()
    
    def _register_user(self):
        """注册测试用户"""
        try:
            response = requests.post(f"{BASE_URL}/api/user/register", json={
                'username': 'test_payment_user',
                'email': 'test_payment@example.com',
                'password': 'test123456',
                'phone': '13800138000'
            })
            data = response.json()
            if data.get('success'):
                self.user_token = data['data']['token']
                self.user_id = data['data']['user']['id']
        except Exception as e:
            print(f"注册失败: {e}")
    
    def test_get_products(self):
        """测试获取会员套餐"""
        print("\n[测试] 获取会员套餐...")
        response = requests.get(f"{BASE_URL}/api/products")
        data = response.json()
        
        self.assertTrue(data['success'], msg=f"获取套餐失败: {data.get('error')}")
        self.assertIsInstance(data['data'], list)
        self.assertEqual(len(data['data']), 3)
        
        # 检查套餐数据
        for product in data['data']:
            self.assertIn('id', product)
            self.assertIn('name', product)
            self.assertIn('price', product)
            self.assertIn('features', product)
        
        print(f"[Pass] 套餐列表: {[p['name'] for p in data['data']]}")
    
    def test_create_order(self):
        """测试创建支付订单"""
        if not self.user_token:
            self.skip("未获取到用户token")
        
        print("\n[测试] 创建支付订单...")
        headers = {'Authorization': f'Bearer {self.user_token}'}
        
        response = requests.post(
            f"{BASE_URL}/api/payment/create-order",
            json={'product_type': 1, 'pay_type': 0},
            headers=headers
        )
        data = response.json()
        
        self.assertTrue(data['success'], msg=f"创建订单失败: {data.get('error')}")
        self.assertIn('data', data)
        self.assertIn('order_no', data['data'])
        self.assertIn('pay_params', data['data'])
        
        print(f"[Pass] 订单创建成功: {data['data']['order_no']}")
        return data['data']['order_no']
    
    def test_query_order(self):
        """测试查询订单"""
        if not self.user_token:
            self.skip("未获取到用户token")
        
        print("\n[测试] 查询订单...")
        
        # 先创建一个订单
        headers = {'Authorization': f'Bearer {self.user_token}'}
        create_resp = requests.post(
            f"{BASE_URL}/api/payment/create-order",
            json={'product_type': 1, 'pay_type': 0},
            headers=headers
        )
        create_data = create_resp.json()
        
        if create_data['success']:
            order_no = create_data['data']['order_no']
            
            # 查询订单
            query_resp = requests.get(f"{BASE_URL}/api/payment/query-order/{order_no}")
            query_data = query_resp.json()
            
            self.assertTrue(query_data['success'], msg=f"查询订单失败: {query_data.get('error')}")
            self.assertIn('data', query_data)
            self.assertIn('order_no', query_data['data'])
            self.assertIn('pay_status', query_data['data'])
            
            print(f"[Pass] 订单查询成功: {query_data['data']['order_no']}")
        else:
            self.fail(f"创建订单失败: {create_data.get('error')}")


class TestUserService(unittest.TestCase):
    """用户系统测试"""
    
    def test_user_register(self):
        """测试用户注册"""
        print("\n[测试] 用户注册...")
        
        import time
        timestamp = int(time.time())
        
        response = requests.post(f"{BASE_URL}/api/user/register", json={
            'username': f'testuser_{timestamp}',
            'email': f'test_{timestamp}@example.com',
            'password': 'test123456',
            'phone': '13800138000'
        })
        data = response.json()
        
        self.assertTrue(data['success'], msg=f"注册失败: {data.get('error')}")
        self.assertIn('data', data)
        self.assertIn('token', data['data'])
        self.assertIn('user', data['data'])
        
        print(f"[Pass] 注册成功: {data['data']['user']['username']}")
        return data['data']['token'], data['data']['user']['id']
    
    def test_user_login(self):
        """测试用户登录"""
        print("\n[测试] 用户登录...")
        
        # 先注册一个用户
        register_resp = requests.post(f"{BASE_URL}/api/user/register", json={
            'username': 'test_login_user',
            'email': 'test_login@example.com',
            'password': 'test123456'
        })
        register_data = register_resp.json()
        
        if register_data['success']:
            # 登录
            login_resp = requests.post(f"{BASE_URL}/api/user/login", json={
                'email': 'test_login@example.com',
                'password': 'test123456'
            })
            login_data = login_resp.json()
            
            self.assertTrue(login_data['success'], msg=f"登录失败: {login_data.get('error')}")
            self.assertIn('token', login_data['data'])
            self.assertIn('user', login_data['data'])
            
            print(f"[Pass] 登录成功: {login_data['data']['user']['username']}")
        else:
            self.fail(f"注册失败: {register_data.get('error')}")


class TestJobAPI(unittest.TestCase):
    """招聘API测试"""
    
    def test_get_hot_jobs(self):
        """测试获取热门职位"""
        print("\n[测试] 获取热门职位...")
        
        response = requests.get(f"{BASE_URL}/api/jobs/hot")
        data = response.json()
        
        self.assertTrue(data['success'], msg=f"获取失败: {data.get('error')}")
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        
        # 检查职位数据结构
        for job in data['data'][:3]:
            self.assertIn('id', job)
            self.assertIn('title', job)
            self.assertIn('company', job)
            self.assertIn('salary', job)
        
        print(f"[Pass] 获取到 {len(data['data'])} 个热门职位")
    
    def test_search_jobs(self):
        """测试搜索职位"""
        print("\n[测试] 搜索职位...")
        
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={'keywords': 'Python', 'page': 1, 'limit': 5}
        )
        data = response.json()
        
        self.assertTrue(data['success'], msg=f"搜索失败: {data.get('error')}")
        self.assertIn('data', data)
        self.assertIn('jobs', data['data'])
        
        print(f"[Pass] 搜索到 {len(data['data']['jobs'])} 个职位")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("求职帮助系统 - 单元测试")
    print("=" * 60)
    print(f"API地址: {BASE_URL}\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestPaymentSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestUserService))
    suite.addTests(loader.loadTestsFromTestCase(TestJobAPI))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("\n[成功] 所有测试通过！")
    else:
        print(f"\n[警告] 有 {len(result.failures) + len(result.errors)} 项测试失败")


if __name__ == "__main__":
    run_tests()
