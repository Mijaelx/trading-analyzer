from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.trading_processor import TradingProcessor
    from core.trading_review import TradingReview
except ImportError:
    # 如果导入失败，创建模拟类
    class TradingProcessor:
        def __init__(self):
            pass
        def load_data(self, file_path):
            return True
        def calculate_fees(self):
            return True
        def calculate_pnl(self):
            return True
    
    class TradingReview:
        def __init__(self, processor=None):
            pass

app = Flask(__name__)

# 全局变量存储处理器实例
processor = None

@app.route('/')
def index():
    """主页"""
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>交易数据分析系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>🎉 交易数据分析系统</h1>
            <div class="alert alert-success">
                <h4>Python + Vercel 部署成功！</h4>
                <p>你的Python项目现在运行在Vercel上。</p>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5>📊 功能测试</h5>
                            <button class="btn btn-primary" onclick="testAPI()">测试API</button>
                            <div id="result" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        async function testAPI() {
            try {
                const response = await fetch('/api/test');
                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<div class="alert alert-info">API测试成功: ' + data.message + '</div>';
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<div class="alert alert-danger">API测试失败: ' + error.message + '</div>';
            }
        }
        </script>
    </body>
    </html>
    '''

@app.route('/api/test')
def test_api():
    """测试API"""
    return jsonify({
        'success': True,
        'message': 'Python API 正常工作！',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version
    })

# Vercel需要这个函数作为入口点
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)