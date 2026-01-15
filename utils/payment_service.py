"""
支付系统模块
支持微信支付和支付宝
"""
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class Order:
    """订单数据模型"""
    id: int = 0
    order_no: str = ''
    user_id: int = 0
    product_type: int = 0  # 1:月卡, 2:年卡, 3:终身
    amount: float = 0.0
    pay_status: int = 0  # 0:待支付, 1:已支付, 2:已取消
    pay_type: int = 0  # 0:微信, 1:支付宝
    transaction_id: str = ''
    created_at: str = ''
    paid_at: str = ''


class PaymentService:
    """支付服务"""
    
    # 会员套餐配置
    PRODUCTS = {
        1: {
            'name': '专业版会员(月卡)',
            'price': 19.9,
            'duration_days': 30,
            'membership_level': 1
        },
        2: {
            'name': '专业版会员(年卡)',
            'price': 199.0,
            'duration_days': 365,
            'membership_level': 1
        },
        3: {
            'name': '尊享版会员(终身)',
            'price': 499.0,
            'duration_days': 36500,
            'membership_level': 2
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化支付服务"""
        self.config = config or {}
        self.wechatpay_config = self.config.get('wechatpay', {})
        self.alipay_config = self.config.get('alipay', {})
    
    def create_order(self, user_id: int, product_type: int, pay_type: int = 0) -> Dict:
        """
        创建支付订单
        
        Args:
            user_id: 用户ID
            product_type: 产品类型 (1:月卡, 2:年卡, 3:终身)
            pay_type: 支付类型 (0:微信, 1:支付宝)
        
        Returns:
            订单信息，包含支付参数
        """
        if product_type not in self.PRODUCTS:
            return {
                'success': False,
                'error': '无效的产品类型'
            }
        
        product = self.PRODUCTS[product_type]
        order_no = self._generate_order_no()
        
        # 创建订单（需要保存到数据库）
        order_data = {
            'order_no': order_no,
            'user_id': user_id,
            'product_type': product_type,
            'amount': product['price'],
            'pay_type': pay_type,
            'pay_status': 0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 生成支付参数
        if pay_type == 0:  # 微信支付
            pay_params = self._generate_wechat_pay_params(order_no, product)
        else:  # 支付宝
            pay_params = self._generate_alipay_params(order_no, product)
        
        return {
            'success': True,
            'data': {
                'order_no': order_no,
                'product_name': product['name'],
                'amount': product['price'],
                'pay_type': pay_type,
                'pay_params': pay_params
            }
        }
    
    def _generate_order_no(self) -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f'JA{timestamp}{random_num}'
    
    def _generate_wechat_pay_params(self, order_no: str, product: Dict) -> Dict:
        """
        生成微信支付参数
        (实际项目中需要调用微信支付API)
        """
        # 模拟返回微信支付参数
        # 实际项目中需要：
        # 1. 调用微信统一下单API
        # 2. 获取prepay_id
        # 3. 生成小程序支付参数
        
        timestamp = str(int(time.time()))
        nonce_str = self._generate_nonce_str()
        
        # 签名（实际项目中需要使用微信支付私钥签名）
        pay_sign = self._mock_wechat_sign(timestamp, nonce_str, order_no)
        
        return {
            'timeStamp': timestamp,
            'nonceStr': nonce_str,
            'package': f'prepay_id={self._mock_prepay_id(order_no)}',
            'signType': 'RSA',
            'paySign': pay_sign,
            # 小程序支付所需参数
            'appId': self.wechatpay_config.get('app_id', ''),
            'prepayId': self._mock_prepay_id(order_no)
        }
    
    def _generate_alipay_params(self, order_no: str, product: Dict) -> Dict:
        """
        生成支付宝支付参数
        (实际项目中需要调用支付宝API)
        """
        # 模拟返回支付宝支付参数
        return {
            'orderStr': self._mock_alipay_order_str(order_no, product['price']),
            'appId': self.alipay_config.get('app_id', ''),
            'timestamp': str(int(time.time()))
        }
    
    def _mock_prepay_id(self, order_no: str) -> str:
        """模拟微信prepay_id"""
        return f'wx{order_no}'
    
    def _mock_wechat_sign(self, timestamp: str, nonce_str: str, order_no: str) -> str:
        """模拟微信签名"""
        app_id = self.wechatpay_config.get('app_id', '')
        sign_str = f'appId={app_id}&nonceStr={nonce_str}&package=prepay_id={self._mock_prepay_id(order_no)}&timeStamp={timestamp}'
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def _mock_alipay_order_str(self, order_no: str, amount: float) -> str:
        """模拟支付宝订单字符串"""
        app_id = self.alipay_config.get('app_id', '')
        total_amount = int(amount * 100)
        return f'app_id={app_id}&method=alipay.trade.create&out_trade_no={order_no}&total_amount={total_amount}'
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(32))
    
    def handle_notify(self, notify_data: Dict) -> Dict:
        """
        处理支付回调
        
        Args:
            notify_data: 回调数据
        
        Returns:
            处理结果
        """
        order_no = notify_data.get('out_trade_no', '')
        transaction_id = notify_data.get('transaction_id', '')
        
        # 验证签名（实际项目中需要验证）
        # if not self._verify_notify(notify_data):
        #     return {'code': 'FAIL', 'message': '签名验证失败'}
        
        # 更新订单状态（需要在数据库中执行）
        # 这里返回模拟的成功响应
        return {
            'code': 'SUCCESS',
            'message': 'OK',
            'order_no': order_no,
            'transaction_id': transaction_id
        }
    
    def handle_payment_success(self, order_no: str, transaction_id: str) -> Dict:
        """
        处理支付成功
        
        Args:
            order_no: 订单号
            transaction_id: 交易流水号
        
        Returns:
            会员开通信息
        """
        # 从数据库查询订单
        order = self._get_order_by_no(order_no)
        if not order:
            return {'success': False, 'error': '订单不存在'}
        
        if order['pay_status'] == 1:
            return {'success': False, 'error': '订单已支付'}
        
        product = self.PRODUCTS.get(order['product_type'], {})
        expire_time = self._calculate_expire_time(order['product_type'])
        
        # 更新订单状态和会员信息（需要在数据库中执行）
        success = self._update_order_and_membership(
            order_no=order_no,
            transaction_id=transaction_id,
            user_id=order['user_id'],
            membership_level=product['membership_level'],
            membership_expire=expire_time
        )
        
        if success:
            return {
                'success': True,
                'message': '会员开通成功',
                'data': {
                    'order_no': order_no,
                    'membership_level': product['membership_level'],
                    'expire_time': expire_time,
                    'product_name': product['name']
                }
            }
        else:
            return {'success': False, 'error': '开通会员失败'}
    
    def _calculate_expire_time(self, product_type: int) -> str:
        """计算会员到期时间"""
        duration_days = self.PRODUCTS.get(product_type, {}).get('duration_days', 0)
        expire_date = datetime.now() + timedelta(days=duration_days)
        return expire_date.strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_order_by_no(self, order_no: str) -> Optional[Dict]:
        """根据订单号查询订单（需要在数据库中查询）"""
        # 模拟从数据库查询
        return {
            'id': 1,
            'order_no': order_no,
            'user_id': 1,
            'product_type': 1,
            'amount': 19.9,
            'pay_status': 0,
            'pay_type': 0
        }
    
    def _update_order_and_membership(self, order_no: str, transaction_id: str,
                                  user_id: int, membership_level: int,
                                  membership_expire: str) -> bool:
        """
        更新订单和会员信息
        
        Returns:
            是否成功
        """
        # 模拟数据库更新
        return True
    
    def query_order(self, order_no: str) -> Dict:
        """
        查询订单状态
        
        Args:
            order_no: 订单号
        
        Returns:
            订单信息
        """
        order = self._get_order_by_no(order_no)
        if order:
            return {
                'success': True,
                'data': order
            }
        else:
            return {
                'success': False,
                'error': '订单不存在'
            }


# 单例实例
_payment_service = None


def get_payment_service(config: Optional[Dict] = None) -> PaymentService:
    """获取支付服务单例"""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService(config)
    return _payment_service
