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
    
    if request.method != 'POST':
        return jsonify({'error': '只支持POST请求'}), 405, {
            'Access-Control-Allow-Origin': '*'
        }
    
    try:
        # 获取请求数据
        data = request.get_json() or {}
        review_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 生成模拟复盘报告
        review_content = f"""# 股票交易复盘报告 - {review_date}

## 📊 市场环境分析
今日市场整体呈震荡上涨态势，成交量较昨日放大。

## 💼 个人交易回顾
- 交易笔数：3笔
- 交易金额：¥85,000
- 实现盈亏：+¥1,250
- 胜率：66.7%

## 📈 持仓分析
当前持仓5只股票，总市值¥485,000，浮盈¥15,000。

## 🎯 经验总结
1. 严格执行止损策略
2. 及时获利了结
3. 控制仓位风险

## 📅 明日计划
1. 关注新能源板块机会
2. 控制单日风险敞口
3. 保持理性交易心态

---
报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        response_data = {
            'success': True,
            'content': review_content,
            'date': review_date,
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200, {
            'Access-Control-Allow-Origin': '*'
        }
        
    except Exception as e:
        return jsonify({'error': f'生成复盘失败: {str(e)}'}), 500, {
            'Access-Control-Allow-Origin': '*'
        }