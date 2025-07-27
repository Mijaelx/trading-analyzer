from flask import Flask, request, jsonify
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/api/process', methods=['POST', 'OPTIONS'])
def process_data():
    """处理交易数据"""
    
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
        
        if not file_id:
            response = jsonify({'error': '缺少文件ID'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 在实际项目中，这里会：
        # 1. 从存储中获取上传的文件
        # 2. 使用 TradingProcessor 处理数据
        # 3. 计算费用和盈亏
        # 4. 保存处理结果
        
        # 现在返回模拟的成功响应
        response = jsonify({
            'success': True,
            'message': '数据处理完成',
            'fileId': file_id,
            'processTime': datetime.now().isoformat()
        })
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        response = jsonify({'error': f'数据处理失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# Vercel需要这个函数作为入口点
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)