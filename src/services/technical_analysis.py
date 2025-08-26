import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import math

class TechnicalAnalysis:
    """技术分析服务类"""
    
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
        
        # 转换为DataFrame便于计算
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'amount'])
        df = df.astype({
            'timestamp': 'int64',
            'open': 'float64',
            'high': 'float64', 
            'low': 'float64',
            'close': 'float64',
            'volume': 'float64',
            'amount': 'float64'
        })
        
        current_price = float(df['close'].iloc[-1])
        
        analysis = {
            'current_price': current_price,
            'timestamp': int(df['timestamp'].iloc[-1]),
            'moving_averages': self._calculate_moving_averages(df),
            'fibonacci_retracements': self._calculate_fibonacci_retracements(df),
            'pivot_points': self._calculate_pivot_points(df),
            'trend_lines': self._calculate_trend_lines(df),
            'support_resistance': self._calculate_support_resistance(df),
            'optimized_levels': {}
        }
        
        # 应用整数价位和价格修正理论优化
        analysis['optimized_levels'] = self._optimize_price_levels(analysis, current_price)
        
        return analysis
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """计算移动平均线"""
        ma_data = {}
        current_price = float(df['close'].iloc[-1])
        
        for period in self.ma_periods:
            if len(df) >= period:
                ma_value = float(df['close'].rolling(window=period).mean().iloc[-1])
                ma_data[f'MA{period}'] = {
                    'value': ma_value,
                    'support_resistance': self._classify_support_resistance(current_price, ma_value),
                    'distance_percent': ((current_price - ma_value) / ma_value) * 100
                }
        
        return ma_data
    
    def _calculate_fibonacci_retracements(self, df: pd.DataFrame) -> Dict:
        """计算斐波那契回撤与扩展"""
        # 寻找最近的高点和低点
        recent_data = df.tail(100)  # 使用最近100个数据点
        
        high_idx = recent_data['high'].idxmax()
        low_idx = recent_data['low'].idxmin()
        
        high_price = float(recent_data.loc[high_idx, 'high'])
        low_price = float(recent_data.loc[low_idx, 'low'])
        
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
    
    def _calculate_pivot_points(self, df: pd.DataFrame) -> Dict:
        """计算枢轴点"""
        # 使用前一日的数据计算枢轴点
        if len(df) < 2:
            return {}
        
        # 取最近一个完整周期的高低收盘价
        recent_high = float(df['high'].tail(24).max())  # 假设1分钟K线，24小时
        recent_low = float(df['low'].tail(24).min())
        recent_close = float(df['close'].iloc[-2])  # 前一个收盘价
        
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
    
    def _calculate_trend_lines(self, df: pd.DataFrame) -> Dict:
        """计算趋势线"""
        if len(df) < 50:
            return {}
        
        # 使用最近50个数据点
        recent_data = df.tail(50).copy()
        recent_data.reset_index(drop=True, inplace=True)
        
        # 寻找支撑趋势线（连接低点）
        support_line = self._find_trend_line(recent_data, 'low', 'support')
        
        # 寻找阻力趋势线（连接高点）
        resistance_line = self._find_trend_line(recent_data, 'high', 'resistance')
        
        return {
            'support_trend': support_line,
            'resistance_trend': resistance_line
        }
    
    def _find_trend_line(self, df: pd.DataFrame, price_col: str, line_type: str) -> Dict:
        """寻找趋势线"""
        try:
            prices = df[price_col].values
            x = np.arange(len(prices))
            
            # 使用线性回归找趋势线
            coeffs = np.polyfit(x, prices, 1)
            slope = coeffs[0]
            intercept = coeffs[1]
            
            # 计算当前趋势线价格
            current_trend_price = slope * (len(prices) - 1) + intercept
            
            # 计算未来几个点的趋势线价格
            future_points = []
            for i in range(1, 11):  # 未来10个点
                future_price = slope * (len(prices) - 1 + i) + intercept
                future_points.append(future_price)
            
            return {
                'slope': slope,
                'intercept': intercept,
                'current_price': current_trend_price,
                'future_prices': future_points,
                'trend_direction': 'up' if slope > 0 else 'down',
                'strength': abs(slope)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """计算支撑阻力位"""
        if len(df) < 20:
            return {}
        
        # 使用最近的价格数据寻找关键价位
        recent_data = df.tail(100)
        
        # 寻找局部高点和低点
        highs = []
        lows = []
        
        for i in range(2, len(recent_data) - 2):
            # 局部高点
            if (recent_data.iloc[i]['high'] > recent_data.iloc[i-1]['high'] and 
                recent_data.iloc[i]['high'] > recent_data.iloc[i-2]['high'] and
                recent_data.iloc[i]['high'] > recent_data.iloc[i+1]['high'] and
                recent_data.iloc[i]['high'] > recent_data.iloc[i+2]['high']):
                highs.append(recent_data.iloc[i]['high'])
            
            # 局部低点
            if (recent_data.iloc[i]['low'] < recent_data.iloc[i-1]['low'] and 
                recent_data.iloc[i]['low'] < recent_data.iloc[i-2]['low'] and
                recent_data.iloc[i]['low'] < recent_data.iloc[i+1]['low'] and
                recent_data.iloc[i]['low'] < recent_data.iloc[i+2]['low']):
                lows.append(recent_data.iloc[i]['low'])
        
        # 聚类相近的价位
        resistance_levels = self._cluster_price_levels(highs) if highs else []
        support_levels = self._cluster_price_levels(lows) if lows else []
        
        return {
            'resistance_levels': resistance_levels,
            'support_levels': support_levels
        }
    
    def _cluster_price_levels(self, prices: List[float], tolerance: float = 0.005) -> List[Dict]:
        """聚类相近的价位"""
        if not prices:
            return []
        
        prices = sorted(prices)
        clusters = []
        current_cluster = [prices[0]]
        
        for price in prices[1:]:
            if abs(price - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                current_cluster.append(price)
            else:
                # 完成当前聚类
                avg_price = sum(current_cluster) / len(current_cluster)
                clusters.append({
                    'price': avg_price,
                    'count': len(current_cluster),
                    'strength': len(current_cluster)
                })
                current_cluster = [price]
        
        # 添加最后一个聚类
        if current_cluster:
            avg_price = sum(current_cluster) / len(current_cluster)
            clusters.append({
                'price': avg_price,
                'count': len(current_cluster),
                'strength': len(current_cluster)
            })
        
        # 按强度排序
        clusters.sort(key=lambda x: x['strength'], reverse=True)
        return clusters[:5]  # 返回前5个最强的价位
    
    def _classify_support_resistance(self, current_price: float, level_price: float) -> str:
        """分类支撑阻力"""
        if current_price > level_price:
            return 'support'
        else:
            return 'resistance'
    
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
        
        # 优化斐波那契价位
        if 'fibonacci_retracements' in analysis:
            fib_data = analysis['fibonacci_retracements']
            for level_name, level_data in fib_data.get('levels', {}).items():
                original_price = level_data['price']
                optimized_price = self._round_to_significant_level(original_price)
                optimized['optimized_fibonacci'][level_name] = {
                    'original': original_price,
                    'optimized': optimized_price,
                    'adjustment': abs(optimized_price - original_price) / original_price * 100
                }
        
        # 优化枢轴点
        if 'pivot_points' in analysis:
            pivot_data = analysis['pivot_points']
            for level_type in ['pivot', 'resistance_levels', 'support_levels']:
                if level_type in pivot_data:
                    if isinstance(pivot_data[level_type], dict):
                        optimized['optimized_pivots'][level_type] = {}
                        for sub_level, price in pivot_data[level_type].items():
                            optimized_price = self._round_to_significant_level(price)
                            optimized['optimized_pivots'][level_type][sub_level] = {
                                'original': price,
                                'optimized': optimized_price,
                                'adjustment': abs(optimized_price - price) / price * 100
                            }
                    else:
                        optimized_price = self._round_to_significant_level(pivot_data[level_type])
                        optimized['optimized_pivots'][level_type] = {
                            'original': pivot_data[level_type],
                            'optimized': optimized_price,
                            'adjustment': abs(optimized_price - pivot_data[level_type]) / pivot_data[level_type] * 100
                        }
        
        return optimized
    
    def _round_to_significant_level(self, price: float) -> float:
        """将价格调整到重要的心理价位"""
        if price <= 0:
            return price
        
        # 确定价格的数量级
        magnitude = 10 ** math.floor(math.log10(price))
        
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

