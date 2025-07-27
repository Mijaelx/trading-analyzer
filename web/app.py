#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web应用
用于Cloudflare部署的Web版本
"""

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import os
import sys
from datetime import datetime
import io
import base64

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trading_processor import TradingProcessor
from core.trading_review import TradingReview
from config.settings import DATA_DIR, REPORTS_DIR

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 全局变量存储处理器实例
processor = None

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传Excel文件"""
    global processor
    
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and file.filename.endswith('.xlsx'):
        try:
            # 保存上传的文件
            filename = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(DATA_DIR, filename)
            file.save(filepath)
            
            # 创建处理器并加载数据
            processor = TradingProcessor()
            if processor.load_data(filepath):
                return jsonify({
                    'success': True,
                    'message': '文件上传成功',
                    'filename': filename
                })
            else:
                return jsonify({'error': '数据加载失败'}), 400
                
        except Exception as e:
            return jsonify({'error': f'文件处理失败: {str(e)}'}), 500
    
    return jsonify({'error': '请上传Excel文件(.xlsx)'}), 400

@app.route('/process', methods=['POST'])
def process_data():
    """处理交易数据"""
    global processor
    
    if processor is None:
        return jsonify({'error': '请先上传数据文件'}), 400
    
    try:
        # 计算费用和盈亏
        if not processor.calculate_fees():
            return jsonify({'error': '费用计算失败'}), 500
        
        if not processor.calculate_pnl():
            return jsonify({'error': '盈亏计算失败'}), 500
        
        # 生成结果文件
        output_filename = f"analysis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(REPORTS_DIR, output_filename)
        
        if processor.save_results(output_path):
            return jsonify({
                'success': True,
                'message': '数据处理完成',
                'download_url': f'/download/{output_filename}'
            })
        else:
            return jsonify({'error': '结果保存失败'}), 500
            
    except Exception as e:
        return jsonify({'error': f'数据处理失败: {str(e)}'}), 500

@app.route('/dashboard_data')
def get_dashboard_data():
    """获取仪表盘数据"""
    global processor
    
    if processor is None:
        return jsonify({'error': '请先上传并处理数据'}), 400
    
    try:
        # 获取基本统计信息
        stats = {}
        
        if processor.trades_df is not None:
            stats['total_trades'] = len(processor.trades_df)
            stats['total_amount'] = float(processor.trades_df['交易金额'].sum()) if '交易金额' in processor.trades_df.columns else 0
        
        if processor.positions:
            stats['current_positions'] = len(processor.positions)
            stats['total_market_value'] = sum([pos.get('市值', 0) for pos in processor.positions.values()])
        
        # 获取持仓数据
        positions_data = []
        for symbol, position in processor.positions.items():
            positions_data.append({
                'symbol': symbol,
                'name': position.get('证券名称', ''),
                'quantity': position.get('数量', 0),
                'cost': position.get('成本价', 0),
                'current_price': position.get('当前价格', 0),
                'market_value': position.get('市值', 0),
                'pnl': position.get('盈亏', 0)
            })
        
        return jsonify({
            'stats': stats,
            'positions': positions_data
        })
        
    except Exception as e:
        return jsonify({'error': f'获取数据失败: {str(e)}'}), 500

@app.route('/generate_review', methods=['POST'])
def generate_review():
    """生成交易复盘"""
    global processor
    
    if processor is None:
        return jsonify({'error': '请先上传并处理数据'}), 400
    
    try:
        review = TradingReview(processor)
        
        # 获取请求中的日期参数
        data = request.get_json()
        if data and 'date' in data:
            review_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            review.set_review_date(review_date)
        
        # 生成复盘报告
        report_filename = f"review_{review.review_date.strftime('%Y%m%d')}.md"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        
        if review.generate_review_report(report_path):
            # 读取报告内容
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            return jsonify({
                'success': True,
                'content': report_content,
                'download_url': f'/download/{report_filename}'
            })
        else:
            return jsonify({'error': '复盘报告生成失败'}), 500
            
    except Exception as e:
        return jsonify({'error': f'复盘生成失败: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下载文件"""
    try:
        file_path = os.path.join(REPORTS_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件太大，请上传小于16MB的文件'}), 413

if __name__ == '__main__':
    # 确保必要目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)