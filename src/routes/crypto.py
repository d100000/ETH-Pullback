from flask import Blueprint, jsonify, request
from src.services.bitget_service import BitgetService
from src.services.simple_technical_analysis import SimpleTechnicalAnalysis
import asyncio
import threading
import time

crypto_bp = Blueprint('crypto', __name__)

# 初始化服务
bitget_service = BitgetService()
technical_analysis = SimpleTechnicalAnalysis()

# 全局变量存储最新数据
latest_data = {
    'klines': [],
    'analysis': {},
    'last_update': 0
}

@crypto_bp.route('/klines', methods=['GET'])
def get_klines():
    """获取K线数据"""
    try:
        symbol = request.args.get('symbol', 'ETHUSDT')
        granularity = request.args.get('granularity', '1m')
        limit = request.args.get('limit', '1000')
        
        # 获取K线数据
        klines = bitget_service.get_klines(symbol, granularity, limit)
        
        if klines:
            # 更新全局数据
            latest_data['klines'] = klines
            latest_data['last_update'] = int(time.time() * 1000)
            
            return jsonify({
                'success': True,
                'data': klines,
                'timestamp': latest_data['last_update']
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取K线数据'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/analysis', methods=['GET'])
def get_technical_analysis():
    """获取技术分析数据"""
    try:
        symbol = request.args.get('symbol', 'ETHUSDT')
        
        # 如果没有K线数据，先获取
        if not latest_data['klines']:
            klines = bitget_service.get_klines(symbol, '1m', '1000')
            latest_data['klines'] = klines
        
        if latest_data['klines']:
            # 进行技术分析
            analysis = technical_analysis.analyze(latest_data['klines'])
            latest_data['analysis'] = analysis
            latest_data['last_update'] = int(time.time() * 1000)
            
            return jsonify({
                'success': True,
                'data': analysis,
                'timestamp': latest_data['last_update']
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取分析数据'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/latest', methods=['GET'])
def get_latest_data():
    """获取最新的综合数据"""
    try:
        symbol = request.args.get('symbol', 'ETHUSDT')
        
        # 获取最新K线数据
        klines = bitget_service.get_klines(symbol, '1m', '100')
        
        if klines:
            # 进行技术分析
            analysis = technical_analysis.analyze(klines)
            
            # 更新全局数据
            latest_data['klines'] = klines
            latest_data['analysis'] = analysis
            latest_data['last_update'] = int(time.time() * 1000)
            
            return jsonify({
                'success': True,
                'data': {
                    'klines': klines[-50:],  # 只返回最近50条K线
                    'analysis': analysis,
                    'current_price': float(klines[-1][4]) if klines else 0,  # 最新收盘价
                    'timestamp': latest_data['last_update']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取最新数据'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    return jsonify({
        'success': True,
        'status': 'running',
        'last_update': latest_data['last_update'],
        'has_data': len(latest_data['klines']) > 0
    })

