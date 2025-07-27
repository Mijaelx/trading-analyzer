from flask import Flask, request, jsonify
import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.trading_review import TradingReview
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

app = Flask(__name__)

@app.route('/api/review', methods=['POST', 'OPTIONS'])
def generate_trading_review():
    """生成股票交易复盘报告"""
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        data = request.get_json()
        file_id = data.get('fileId') if data else None
        review_date = data.get('date') if data else datetime.now().strftime('%Y-%m-%d')
        
        if not file_id:
            response = jsonify({'error': '缺少文件ID'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 生成详细的股票交易复盘报告
        review_content = generate_detailed_review(review_date)
        
        response = jsonify({
            'success': True,
            'content': review_content,
            'date': review_date,
            'generated_at': datetime.now().isoformat()
        })
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        response = jsonify({'error': f'生成复盘报告失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

def generate_detailed_review(review_date):
    """生成详细的股票交易复盘报告"""
    
    # 解析日期
    try:
        date_obj = datetime.strptime(review_date, '%Y-%m-%d')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
    except:
        date_obj = datetime.now()
        weekday = '周一'
    
    # 模拟市场数据
    market_trends = ['上涨', '下跌', '震荡']
    market_trend = random.choice(market_trends)
    
    # 模拟指数数据
    sh_index = round(random.uniform(3000, 3500), 2)
    sz_index = round(random.uniform(10000, 12000), 2)
    cy_index = round(random.uniform(2000, 2500), 2)
    
    # 模拟交易数据
    trades_today = [
        {
            'symbol': '000001',
            'name': '平安银行',
            'action': '买入',
            'quantity': 1000,
            'price': 10.50,
            'reason': '技术面突破，成交量放大',
            'result': '盈利',
            'pnl': 350
        },
        {
            'symbol': '300750',
            'name': '宁德时代',
            'action': '卖出',
            'quantity': 50,
            'price': 485.30,
            'reason': '获利了结，技术面见顶信号',
            'result': '盈利',
            'pnl': 1250
        }
    ]
    
    total_pnl = sum(trade['pnl'] for trade in trades_today)
    total_trades = len(trades_today)
    
    review_content = f"""# 股票交易复盘报告 - {review_date} ({weekday})

## 📊 一、市场整体环境复盘

### 指数表现
- **上证指数**: {sh_index} ({'+' if market_trend == '上涨' else '-' if market_trend == '下跌' else ''}{'1.2%' if market_trend != '震荡' else '0.3%'})
- **深证成指**: {sz_index} ({'+' if market_trend == '上涨' else '-' if market_trend == '下跌' else ''}{'0.8%' if market_trend != '震荡' else '-0.1%'})
- **创业板指**: {cy_index} ({'+' if market_trend == '上涨' else '-' if market_trend == '下跌' else ''}{'1.5%' if market_trend != '震荡' else '0.2%'})

### 市场特征
今日市场整体呈**{market_trend}**态势。

**量能分析**:
- 沪市成交额: 2,850亿元
- 深市成交额: 3,420亿元
- 两市合计: 6,270亿元

**热点板块**:
- 新能源汽车: 领涨，平均涨幅2.3%
- 人工智能: 活跃，平均涨幅1.8%
- 医药生物: 调整，平均跌幅0.5%

## 💼 二、个人交易复盘

### 今日交易概况
- **交易笔数**: {total_trades}笔
- **交易金额**: ¥{sum(trade['quantity'] * trade['price'] for trade in trades_today):,.0f}
- **实现盈亏**: {'¥+' if total_pnl >= 0 else '¥'}{total_pnl:,.0f}
- **胜率**: {len([t for t in trades_today if t['result'] == '盈利']) / len(trades_today) * 100:.1f}%

### 交易明细分析
"""

    for i, trade in enumerate(trades_today, 1):
        pnl_symbol = '+' if trade['pnl'] >= 0 else ''
        review_content += f"""
**{i}. {trade['action']} {trade['name']}({trade['symbol']})**
- 交易价格: ¥{trade['price']:.2f}
- 交易数量: {trade['quantity']:,}股
- 交易理由: {trade['reason']}
- 交易结果: {trade['result']} ({pnl_symbol}¥{trade['pnl']:,.0f})
"""

    review_content += f"""

## 📈 三、持仓分析

### 当前持仓概况
- **持仓股票数**: 5只
- **总持仓市值**: ¥194,695
- **浮动盈亏**: ¥+1,945 (+1.01%)

### 重点持仓分析
1. **贵州茅台(600519)** - 持仓占比: 44.2%
   - 成本价: ¥1,680.00，现价: ¥1,720.50
   - 浮盈: ¥2,025 (+2.41%)
   - 分析: 白酒龙头，长期价值投资标的

2. **宁德时代(300750)** - 持仓占比: 24.9%
   - 成本价: ¥520.00，现价: ¥485.30
   - 浮亏: ¥-3,470 (-6.67%)
   - 分析: 新能源电池龙头，短期调整，长期看好

## 🎯 四、交易策略回顾

### 执行良好的策略
1. **严格止损**: 今日宁德时代及时止盈，避免了后续下跌
2. **分批建仓**: 平安银行采用分批买入，降低了成本
3. **行业轮动**: 及时捕捉到金融板块的轮动机会

### 需要改进的地方
1. **仓位管理**: 单一持仓占比过高，需要分散风险
2. **情绪控制**: 盘中有追涨杀跌的冲动，需要更加理性
3. **研究深度**: 对部分标的基本面研究不够深入

## 📚 五、经验总结

### 今日收获
- 市场情绪对短期股价影响较大，需要关注市场节奏
- 技术分析结合基本面分析效果更好
- 及时止盈止损是保护利润的重要手段

### 明日计划
1. **关注重点**:
   - 新能源汽车板块的反弹机会
   - 金融板块的持续性
   - 医药板块的企稳信号

2. **操作计划**:
   - 考虑减持贵州茅台，降低单一持仓占比
   - 关注宁德时代的支撑位，寻找加仓机会
   - 继续观察平安银行的突破情况

3. **风险控制**:
   - 单日亏损不超过总资产的2%
   - 单一股票持仓不超过总资产的30%
   - 保持30%的现金仓位应对机会

## 📊 六、数据统计

### 本周交易统计
- 总交易次数: 12次
- 盈利次数: 8次，亏损次数: 4次
- 胜率: 66.7%
- 周盈亏: ¥+2,850

### 本月交易统计
- 总交易次数: 45次
- 盈利次数: 28次，亏损次数: 17次
- 胜率: 62.2%
- 月盈亏: ¥+8,650

---

**复盘时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**下次复盘**: {(date_obj + timedelta(days=1)).strftime('%Y-%m-%d')}

> 💡 **提醒**: 投资有风险，入市需谨慎。本复盘仅供参考，不构成投资建议。
"""

    return review_content

# Vercel需要这个函数作为入口点
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)