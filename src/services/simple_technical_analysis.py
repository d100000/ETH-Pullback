import math
from typing import List, Dict, Tuple, Optional

class SimpleTechnicalAnalysis:
    """简化版技术分析服务类（不依赖numpy）"""
    
    def __init__(self):
        self.fibonacci_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        self.ma_periods = [5, 10, 20, 50, 100, 200]
    
    def analyze(self, klines: List[List]) -> Dict:
        """
        综合技术分析
        
        Args:
            klines: K线数据 [[timestamp, open, high, low, close, volume, amount], ...]
        
        Returns:
            技术分析结果字典
        """
        if not klines or len(klines) < 20:
            return {'error': 'K线数据不足，至少需要20条数据'}
        
        current_price = float(klines[-1][4])
        
        analysis = {
            'current_price': current_price,
            'timestamp': int(klines[-1][0]),
            'moving_averages': self._calculate_moving_averages(klines),
            'fibonacci_retracements': self._calculate_fibonacci_retracements(klines),
            'pivot_points': self._calculate_pivot_points(klines),
            'trend_lines': self._calculate_trend_lines(klines),
            'support_resistance': self._calculate_support_resistance(klines),
            'optimized_levels': {}
        }
        
        # 应用整数价位和价格修正理论优化
        analysis['optimized_levels'] = self._optimize_price_levels(analysis, current_price)
        
        return analysis
    
    def _calculate_moving_averages(self, klines: List[List]) -> Dict:
        """计算移动平均线"""
        ma_data = {}
        current_price = float(klines[-1][4])
        closes = [float(k[4]) for k in klines]
        
        for period in self.ma_periods:
            if len(closes) >= period:
                ma_value = sum(closes[-period:]) / period
                ma_data[f'MA{period}'] = {
                    'value': ma_value,
                    'support_resistance': 'support' if current_price > ma_value else 'resistance',
                    'distance_percent': ((current_price - ma_value) / ma_value) * 100
                }
        
        return ma_data
    
    def _calculate_fibonacci_retracements(self, klines: List[List]) -> Dict:
        """计算斐波那契回撤与扩展"""
        # 使用最近100个数据点
        recent_data = klines[-100:] if len(klines) > 100 else klines
        
        highs = [float(k[2]) for k in recent_data]
        lows = [float(k[3]) for k in recent_data]
        
        high_price = max(highs)
        low_price = min(lows)
        
        # 找到高点和低点的位置
        high_idx = highs.index(high_price)
        low_idx = lows.index(low_price)
        
        # 确定趋势方向
        if high_idx > low_idx:
            # 上升趋势中的回撤
            trend = 'uptrend'
            price_range = high_price - low_price
            base_price = high_price
            multiplier = -1
        else:
            # 下降趋势中的回撤
            trend = 'downtrend'
            price_range = high_price - low_price
            base_price = low_price
            multiplier = 1
        
        fib_levels = {}
        for level in self.fibonacci_levels:
            price = base_price + (multiplier * price_range * level)
            fib_levels[f'Fib_{level:.1%}'] = {
                'price': price,
                'level': level,
                'trend': trend
            }
        
        # 添加扩展位
        extension_levels = [1.272, 1.414, 1.618, 2.0]
        for level in extension_levels:
            price = base_price + (multiplier * price_range * level)
            fib_levels[f'Ext_{level:.3f}'] = {
                'price': price,
                'level': level,
                'trend': trend
            }
        
        return {
            'levels': fib_levels,
            'high_price': high_price,
            'low_price': low_price,
            'trend': trend,
            'range': price_range
        }
    
    def _calculate_pivot_points(self, klines: List[List]) -> Dict:
        """计算枢轴点"""
        if len(klines) < 2:
            return {}
        
        # 取最近24个数据点（假设1分钟K线）
        recent_data = klines[-24:] if len(klines) > 24 else klines
        
        recent_high = max(float(k[2]) for k in recent_data)
        recent_low = min(float(k[3]) for k in recent_data)
        recent_close = float(klines[-2][4])  # 前一个收盘价
        
        # 标准枢轴点计算
        pivot = (recent_high + recent_low + recent_close) / 3
        
        # 支撑位和阻力位
        r1 = 2 * pivot - recent_low
        r2 = pivot + (recent_high - recent_low)
        r3 = recent_high + 2 * (pivot - recent_low)
        
        s1 = 2 * pivot - recent_high
        s2 = pivot - (recent_high - recent_low)
        s3 = recent_low - 2 * (recent_high - pivot)
        
        return {
            'pivot': pivot,
            'resistance_levels': {
                'R1': r1,
                'R2': r2,
                'R3': r3
            },
            'support_levels': {
                'S1': s1,
                'S2': s2,
                'S3': s3
            },
            'high': recent_high,
            'low': recent_low,
            'close': recent_close
        }
    
    def _calculate_trend_lines(self, klines: List[List]) -> Dict:
        """计算趋势线（简化版）"""
        if len(klines) < 50:
            return {}
        
        # 使用最近50个数据点
        recent_data = klines[-50:]
        
        # 简化的趋势线计算
        closes = [float(k[4]) for k in recent_data]
        
        # 计算简单的线性趋势
        n = len(closes)
        sum_x = sum(range(n))
        sum_y = sum(closes)
        sum_xy = sum(i * closes[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        current_trend_price = slope * (n - 1) + intercept
        
        return {
            'support_trend': {
                'slope': slope,
                'intercept': intercept,
                'current_price': current_trend_price,
                'trend_direction': 'up' if slope > 0 else 'down',
                'strength': abs(slope)
            },
            'resistance_trend': {
                'slope': slope * 1.1,  # 简化的阻力线
                'intercept': intercept + (max(closes) - min(closes)) * 0.1,
                'current_price': current_trend_price * 1.01,
                'trend_direction': 'up' if slope > 0 else 'down',
                'strength': abs(slope)
            }
        }
    
    def _calculate_support_resistance(self, klines: List[List]) -> Dict:
        """计算支撑阻力位（简化版）"""
        if len(klines) < 20:
            return {}
        
        # 使用最近100个数据点
        recent_data = klines[-100:] if len(klines) > 100 else klines
        
        highs = [float(k[2]) for k in recent_data]
        lows = [float(k[3]) for k in recent_data]
        
        # 简化的支撑阻力位计算
        resistance_levels = []
        support_levels = []
        
        # 找到局部高点和低点
        for i in range(2, len(recent_data) - 2):
            high = highs[i]
            low = lows[i]
            
            # 局部高点
            if (high > highs[i-1] and high > highs[i-2] and 
                high > highs[i+1] and high > highs[i+2]):
                resistance_levels.append({'price': high, 'strength': 1})
            
            # 局部低点
            if (low < lows[i-1] and low < lows[i-2] and 
                low < lows[i+1] and low < lows[i+2]):
                support_levels.append({'price': low, 'strength': 1})
        
        # 按强度排序并取前5个
        resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
        support_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'resistance_levels': resistance_levels[:5],
            'support_levels': support_levels[:5]
        }
    
    def _optimize_price_levels(self, analysis: Dict, current_price: float) -> Dict:
        """应用整数价位和价格修正理论优化价位"""
        optimized = {
            'psychological_levels': [],
            'round_numbers': [],
            'optimized_fibonacci': {},
            'optimized_pivots': {}
        }
        
        # 心理价位（整数价位）
        price_magnitude = 10 ** (len(str(int(current_price))) - 2)
        for i in range(-5, 6):
            level = round(current_price / price_magnitude + i) * price_magnitude
            if level > 0:
                distance = abs(level - current_price) / current_price
                if distance <= 0.1:  # 10%范围内
                    optimized['psychological_levels'].append({
                        'price': level,
                        'distance_percent': distance * 100,
                        'type': 'psychological'
                    })
        
        # 整数价位
        for multiplier in [1, 5, 10, 50, 100]:
            base = price_magnitude * multiplier
            for i in range(-3, 4):
                level = round(current_price / base + i) * base
                if level > 0:
                    distance = abs(level - current_price) / current_price
                    if distance <= 0.05:  # 5%范围内
                        optimized['round_numbers'].append({
                            'price': level,
                            'distance_percent': distance * 100,
                            'type': f'round_{multiplier}'
                        })
        
        return optimized
    
    def _round_to_significant_level(self, price: float) -> float:
        """将价格调整到重要的心理价位"""
        if price <= 0:
            return price
        
        # 根据价格范围选择合适的舍入精度
        if price >= 1000:
            precision = 10
        elif price >= 100:
            precision = 5
        elif price >= 10:
            precision = 1
        elif price >= 1:
            precision = 0.1
        else:
            precision = 0.01
        
        return round(price / precision) * precision

