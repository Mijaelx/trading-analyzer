from flask import Flask, request, jsonify
import sys
import os
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.trading_processor import TradingProcessor
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

app = Flask(__name__)

@app.route('/api/dashboard', methods=['GET', 'OPTIONS'])
def get_dashboard_data():
    """获取股票交易分析仪表盘数据"""
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        file_id = request.args.get('fileId')
        
        if not file_id:
            response = jsonify({'error': '缺少文件ID'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 如果核心模块可用，尝试加载真实数据
        if CORE_AVAILABLE:
            # 这里应该从存储中获取处理后的数据
            # 现在返回增强的模拟数据，更接近真实的股票交易分析
            pass
        
        # 生成更真实的股票交易分析数据
        dashboard_data = generate_realistic_trading_data()
        
        response = jsonify(dashboard_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        response = jsonify({'error': f'获取仪表盘数据失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

def generate_realistic_trading_data():
    """生成更真实的股票交易分析数据"""
    
    # 模拟真实的股票持仓数据
    positions = [
        {
            'symbol': '000001',
            'name': '平安银行',
            'quantity': 1000,
            'cost': 10.50,
            'current_price': 11.20,
            'market_value': 11200,
            'pnl': 700,
            'sector': '金融'
        },
        {
            'symbol': '000002',
            'name': '万科A',
            'quantity': 500,
            'cost': 20.30,
            'current_price': 19.80,
            'market_value': 9900,
            'pnl': -250,
            'sector': '房地产'
        },
        {
            'symbol': '000858',
            'name': '五粮液',
            'quantity': 200,
            'cost': 180.50,
            'current_price': 195.20,
            'market_value': 39040,
            'pnl': 2940,
            'sector': '食品饮料'
        },
        {
            'symbol': '300750',
            'name': '宁德时代',
            'quantity': 100,
            'cost': 520.00,
            'current_price': 485.30,
            'market_value': 48530,
            'pnl': -3470,
            'sector': '新能源'
        },
        {
            'symbol': '600519',
            'name': '贵州茅台',
            'quantity': 50,
            'cost': 1680.00,
            'current_price': 1720.50,
            'market_value': 86025,
            'pnl': 2025,
            'sector': '食品饮料'
        }
    ]
    
    # 计算统计数据
    total_market_value = sum(pos['market_value'] for pos in positions)
    total_cost = sum(pos['cost'] * pos['quantity'] for pos in positions)
    total_pnl = sum(pos['pnl'] for pos in positions)
    total_trades = 25  # 模拟总交易笔数
    
    # 模拟交易历史数据
    trading_history = [
        {
            'date': '2025-01-20',
            'symbol': '000001',
            'name': '平安银行',
            'action': '买入',
            'quantity': 1000,
            'price': 10.50,
            'amount': 10500,
            'fee': 31.50
        },
        {
            'date': '2025-01-18',
            'symbol': '600519',
            'name': '贵州茅台',
            'action': '买入',
            'quantity': 50,
            'price': 1680.00,
            'amount': 84000,
            'fee': 252.00
        },
        {
            'date': '2025-01-15',
            'symbol': '300750',
            'name': '宁德时代',
            'action': '买入',
            'quantity': 100,
            'price': 520.00,
            'amount': 52000,
            'fee': 156.00
        }
    ]
    
    # 按行业分组统计
    sector_stats = {}
    for pos in positions:
        sector = pos['sector']
        if sector not in sector_stats:
            sector_stats[sector] = {
                'market_value': 0,
                'pnl': 0,
                'count': 0
            }
        sector_stats[sector]['market_value'] += pos['market_value']
        sector_stats[sector]['pnl'] += pos['pnl']
        sector_stats[sector]['count'] += 1
    
    # 计算盈亏统计
    profit_positions = [pos for pos in positions if pos['pnl'] > 0]
    loss_positions = [pos for pos in positions if pos['pnl'] < 0]
    
    total_profit = sum(pos['pnl'] for pos in profit_positions)
    total_loss = abs(sum(pos['pnl'] for pos in loss_positions))
    
    return {
        'stats': {
            'total_trades': total_trades,
            'total_amount': total_cost,
            'current_positions': len(positions),
            'total_market_value': total_market_value,
            'total_cost': total_cost,
            'total_pnl': total_pnl,
            'total_pnl_percent': (total_pnl / total_cost * 100) if total_cost > 0 else 0,
            'profit_positions': len(profit_positions),
            'loss_positions': len(loss_positions),
            'win_rate': (len(profit_positions) / len(positions) * 100) if positions else 0
        },
        'positions': positions,
        'trading_history': trading_history,
        'sector_analysis': sector_stats,
        'pnl_distribution': {
            'profit': total_profit,
            'loss': total_loss
        },
        'top_performers': sorted(positions, key=lambda x: x['pnl'], reverse=True)[:3],
        'worst_performers': sorted(positions, key=lambda x: x['pnl'])[:3],
        'last_updated': datetime.now().isoformat()
    }

# Vercel需要这个函数作为入口点
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)