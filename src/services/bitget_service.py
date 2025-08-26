import requests
import time
import os
from typing import List, Dict, Optional
import json

class BitgetService:
    """Bitget API服务类"""
    
    def __init__(self, proxy_config: Optional[Dict] = None):
        self.base_url = "https://api.bitget.com"
        self.session = requests.Session()
        self.proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }


        self.session.proxies.update(self.proxies)
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ETH-Trading-Dashboard/1.0'
        })
        
        # 请求限制
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms最小间隔
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发起API请求"""
        try:
            # 请求频率限制
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10,proxies=self.proxies)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None
    
    def get_klines(self, symbol: str = "ETHUSDT", granularity: str = "1m", 
                   limit: str = "1000", product_type: str = "usdt-futures") -> List[List]:
        """
        获取K线数据
        
        Args:
            symbol: 交易币对，如 ETHUSDT
            granularity: K线粒度，如 1m, 5m, 1H, 1D
            limit: 返回数据条数，最大1000
            product_type: 产品类型，默认 usdt-futures
        
        Returns:
            K线数据列表，每个元素包含 [时间戳, 开盘价, 最高价, 最低价, 收盘价, 成交量, 成交额]
        """
        endpoint = "/api/v2/mix/market/candles"
        
        # 构建请求参数
        params = {
            'symbol': symbol,
            'granularity': granularity,
            'limit': limit,
            'productType': product_type
        }
        
        # 添加结束时间（当前时间）
        params['endTime'] = str(int(time.time() * 1000))
        
        response = self._make_request(endpoint, params)
        
        if response and response.get('code') == '00000':
            data = response.get('data', [])
            # 转换数据格式，确保数值类型正确
            processed_data = []
            for item in data:
                try:
                    processed_item = [
                        int(item[0]),      # 时间戳
                        float(item[1]),    # 开盘价
                        float(item[2]),    # 最高价
                        float(item[3]),    # 最低价
                        float(item[4]),    # 收盘价
                        float(item[5]),    # 成交量
                        float(item[6])     # 成交额
                    ]
                    processed_data.append(processed_item)
                except (ValueError, IndexError) as e:
                    print(f"数据格式错误: {e}, 原始数据: {item}")
                    continue
            
            # 按时间戳排序（升序）
            processed_data.sort(key=lambda x: x[0])
            return processed_data
        else:
            error_msg = response.get('msg', '未知错误') if response else '请求失败'
            print(f"获取K线数据失败: {error_msg}")
            return []
    
    def get_latest_price(self, symbol: str = "ETHUSDT") -> Optional[float]:
        """获取最新价格"""
        klines = self.get_klines(symbol, "1m", "1")
        if klines:
            return klines[-1][4]  # 返回最新收盘价
        return None
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = self._make_request("/api/v2/public/time")
            return response is not None and response.get('code') == '00000'
        except Exception:
            return False
    
    def set_proxy(self, proxy_config: Dict):
        """设置代理配置"""
        self.session.proxies.update(proxy_config)
    
    def get_server_time(self) -> Optional[int]:
        """获取服务器时间"""
        response = self._make_request("/api/v2/public/time")
        if response and response.get('code') == '00000':
            return int(response.get('data', 0))
        return None

