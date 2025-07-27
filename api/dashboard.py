from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

def handler(request):
    """Vercel函数入口点"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS'
        }
    
    if request.method != 'GET':
        return jsonify({'error': '只支持GET请求'}), 405, {
            'Access-Control-Allow-Origin': '*'
        }
    
    try:
        # 模拟股票交易分析数据
        dashboard_data = {
            'stats': {
                'total_trades': 25,
                'total_amount': 500000,
                'current_positions': 5,
                'total_market_value': 485000,
                'total_pnl': 15000,
                'win_rate': 68.5
            },
            'positions': [
                {
                    'symbol': '000001',
                    'name': '平安银行',
                    'quantity': 1000,
                    'cost': 10.50,
                    'current_price': 11.20,
                    'market_value': 11200,
                    'pnl': 700
                },
                {
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'quantity': 50,
                    'cost': 1680.00,
                    'current_price': 1720.50,
                    'market_value': 86025,
                    'pnl': 2025
                },
                {
                    'symbol': '300750',
                    'name': '宁德时代',
                    'quantity': 100,
                    'cost': 520.00,
                    'current_price': 485.30,
                    'market_value': 48530,
                    'pnl': -3470
                }
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(dashboard_data), 200, {
            'Access-Control-Allow-Origin': '*'
        }
        
    except Exception as e:
        return jsonify({'error': f'获取数据失败: {str(e)}'}), 500, {
            'Access-Control-Allow-Origin': '*'
        }