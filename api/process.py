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
        # 模拟数据处理成功
        response_data = {
            'success': True,
            'message': '数据处理完成（演示模式）',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200, {
            'Access-Control-Allow-Origin': '*'
        }
        
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500, {
            'Access-Control-Allow-Origin': '*'
        }