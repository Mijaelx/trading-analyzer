from flask import Flask, request, jsonify
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """处理文件上传"""
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and file.filename.endswith('.xlsx'):
            # 生成文件ID
            file_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 在实际项目中，这里会保存文件并处理
            # 现在返回成功响应
            response = jsonify({
                'success': True,
                'fileId': file_id,
                'message': '文件上传成功',
                'filename': file.filename,
                'size': len(file.read())
            })
            
            # 添加CORS头
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            response = jsonify({'error': '请上传Excel文件(.xlsx)'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
            
    except Exception as e:
        response = jsonify({'error': f'文件处理失败: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# Vercel需要这个函数作为入口点
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)