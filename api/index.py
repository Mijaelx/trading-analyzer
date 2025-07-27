from flask import Flask, request, jsonify
import sys
import os
from datetime import datetime

app = Flask(__name__)

# 全局变量存储处理器实例
processor = None

@app.route('/')
def index():
    """股票交易分析系统主页"""
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>股票交易数据分析系统</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .upload-area {
                border: 2px dashed #dee2e6;
                border-radius: 0.375rem;
                padding: 3rem;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .upload-area:hover {
                border-color: #0d6efd;
                background-color: #f8f9fa;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .profit { color: #198754; font-weight: bold; }
            .loss { color: #dc3545; font-weight: bold; }
            .loading { display: none; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="bi bi-graph-up"></i>
                    股票交易数据分析系统
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="#upload">数据上传</a>
                    <a class="nav-link" href="#analysis">分析结果</a>
                    <a class="nav-link" href="#review">交易复盘</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- 系统介绍 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="jumbotron bg-light p-4 rounded">
                        <h1 class="display-4">📈 股票交易数据分析系统</h1>
                        <p class="lead">专业的股票交易数据处理和分析工具，帮助你深入了解交易表现，优化投资策略。</p>
                        <hr class="my-4">
                        <p>支持交易费用计算、盈亏分析、持仓管理、分红记录和交易复盘等功能。</p>
                        <div class="alert alert-info">
                            <small><i class="bi bi-info-circle"></i> 系统已更新 - 版本 v1.1.0</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 文件上传区域 -->
            <div class="row mb-4" id="upload">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-cloud-upload"></i>
                                交易数据上传
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                                <i class="bi bi-file-earmark-excel fs-1 text-muted mb-3"></i>
                                <h5>点击选择Excel文件或拖拽到此处</h5>
                                <p class="text-muted">支持.xlsx格式，包含交易数据、费率配置和收盘价格</p>
                                <input type="file" id="fileInput" accept=".xlsx" style="display: none;" onchange="uploadFile()">
                                <button class="btn btn-primary">
                                    <i class="bi bi-upload"></i>
                                    选择文件
                                </button>
                            </div>
                            <div class="loading mt-3" id="uploadLoading">
                                <div class="d-flex align-items-center">
                                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                                    <span>正在上传和处理文件...</span>
                                </div>
                            </div>
                            <div id="uploadStatus" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 分析结果展示区域 -->
            <div class="row mb-4" id="analysis" style="display: none;">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-bar-chart"></i>
                                交易分析结果
                            </h5>
                        </div>
                        <div class="card-body">
                            <!-- 统计卡片 -->
                            <div class="row mb-4" id="statsCards">
                                <!-- 动态生成 -->
                            </div>
                            
                            <!-- 图表区域 -->
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <canvas id="pnlChart"></canvas>
                                </div>
                                <div class="col-md-6">
                                    <canvas id="positionChart"></canvas>
                                </div>
                            </div>
                            
                            <!-- 持仓详情表格 -->
                            <h6>当前持仓详情</h6>
                            <div class="table-responsive">
                                <table class="table table-striped" id="positionsTable">
                                    <thead>
                                        <tr>
                                            <th>证券代码</th>
                                            <th>证券名称</th>
                                            <th>持仓数量</th>
                                            <th>成本价</th>
                                            <th>当前价格</th>
                                            <th>持仓市值</th>
                                            <th>盈亏金额</th>
                                            <th>盈亏比例</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <!-- 动态生成 -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 交易复盘区域 -->
            <div class="row mb-4" id="review" style="display: none;">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-journal-text"></i>
                                交易复盘报告
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="reviewDate" class="form-label">复盘日期</label>
                                    <input type="date" class="form-control" id="reviewDate">
                                </div>
                                <div class="col-md-6 d-flex align-items-end">
                                    <button class="btn btn-info" onclick="generateReview()">
                                        <i class="bi bi-file-text"></i>
                                        生成复盘报告
                                    </button>
                                </div>
                            </div>
                            <div class="loading" id="reviewLoading">
                                <div class="d-flex align-items-center">
                                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                                    <span>正在生成复盘报告...</span>
                                </div>
                            </div>
                            <div id="reviewContent" class="mt-3">
                                <!-- 复盘内容 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-light mt-5 py-4">
            <div class="container text-center">
                <p class="mb-0 text-muted">© 2025 股票交易数据分析系统 - 专业的投资分析工具</p>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let currentFileId = null;
            let pnlChart = null;
            let positionChart = null;

            // 设置默认复盘日期
            document.getElementById('reviewDate').valueAsDate = new Date();

            // 文件上传处理
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('请选择文件');
                    return;
                }

                if (!file.name.endsWith('.xlsx')) {
                    alert('请选择Excel文件(.xlsx)');
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);

                const uploadLoading = document.getElementById('uploadLoading');
                uploadLoading.style.display = 'block';

                try {
                    // 上传文件
                    const uploadResponse = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const uploadResult = await uploadResponse.json();
                    
                    if (uploadResult.success) {
                        currentFileId = uploadResult.fileId;
                        
                        // 自动处理数据
                        const processResponse = await fetch('/api/process', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ fileId: currentFileId })
                        });

                        const processResult = await processResponse.json();
                        
                        if (processResult.success) {
                            document.getElementById('uploadStatus').innerHTML = 
                                '<div class="alert alert-success">文件上传和处理成功！</div>';
                            
                            // 加载分析结果
                            await loadAnalysisResults();
                            
                            // 显示分析和复盘区域
                            document.getElementById('analysis').style.display = 'block';
                            document.getElementById('review').style.display = 'block';
                        } else {
                            throw new Error(processResult.error || '数据处理失败');
                        }
                    } else {
                        throw new Error(uploadResult.error || '文件上传失败');
                    }
                } catch (error) {
                    document.getElementById('uploadStatus').innerHTML = 
                        '<div class="alert alert-danger">错误: ' + error.message + '</div>';
                } finally {
                    uploadLoading.style.display = 'none';
                }
            }

            // 加载分析结果
            async function loadAnalysisResults() {
                try {
                    const response = await fetch('/api/dashboard?fileId=' + currentFileId);
                    const data = await response.json();
                    
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    // 更新统计卡片
                    updateStatsCards(data.stats);
                    
                    // 更新持仓表格
                    updatePositionsTable(data.positions);
                    
                    // 创建图表
                    createCharts(data);
                    
                } catch (error) {
                    console.error('加载分析结果失败:', error);
                }
            }

            // 更新统计卡片
            function updateStatsCards(stats) {
                const statsCards = document.getElementById('statsCards');
                statsCards.innerHTML = `
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body text-center">
                                <h5>总交易笔数</h5>
                                <h2>${stats.total_trades || 0}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body text-center">
                                <h5>总交易金额</h5>
                                <h2>¥${(stats.total_amount || 0).toLocaleString()}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body text-center">
                                <h5>当前持仓</h5>
                                <h2>${stats.current_positions || 0}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body text-center">
                                <h5>总市值</h5>
                                <h2>¥${(stats.total_market_value || 0).toLocaleString()}</h2>
                            </div>
                        </div>
                    </div>
                `;
            }

            // 更新持仓表格
            function updatePositionsTable(positions) {
                const tbody = document.querySelector('#positionsTable tbody');
                tbody.innerHTML = '';
                
                positions.forEach(position => {
                    const row = document.createElement('tr');
                    const pnlClass = position.pnl >= 0 ? 'profit' : 'loss';
                    const pnlPercent = ((position.pnl / (position.cost * position.quantity)) * 100).toFixed(2);
                    
                    row.innerHTML = `
                        <td><strong>${position.symbol}</strong></td>
                        <td>${position.name}</td>
                        <td>${position.quantity.toLocaleString()}</td>
                        <td>¥${position.cost.toFixed(2)}</td>
                        <td>¥${position.current_price.toFixed(2)}</td>
                        <td>¥${position.market_value.toLocaleString()}</td>
                        <td class="${pnlClass}">¥${position.pnl.toFixed(2)}</td>
                        <td class="${pnlClass}">${pnlPercent}%</td>
                    `;
                    
                    tbody.appendChild(row);
                });
            }

            // 创建图表
            function createCharts(data) {
                // 盈亏图表
                const pnlCtx = document.getElementById('pnlChart').getContext('2d');
                if (pnlChart) pnlChart.destroy();
                
                pnlChart = new Chart(pnlCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['盈利', '亏损'],
                        datasets: [{
                            data: [
                                data.positions.filter(p => p.pnl > 0).reduce((sum, p) => sum + p.pnl, 0),
                                Math.abs(data.positions.filter(p => p.pnl < 0).reduce((sum, p) => sum + p.pnl, 0))
                            ],
                            backgroundColor: ['#198754', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: '盈亏分布'
                            }
                        }
                    }
                });

                // 持仓分布图表
                const positionCtx = document.getElementById('positionChart').getContext('2d');
                if (positionChart) positionChart.destroy();
                
                positionChart = new Chart(positionCtx, {
                    type: 'bar',
                    data: {
                        labels: data.positions.map(p => p.symbol),
                        datasets: [{
                            label: '持仓市值',
                            data: data.positions.map(p => p.market_value),
                            backgroundColor: 'rgba(54, 162, 235, 0.8)'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: '持仓市值分布'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }

            // 生成复盘报告
            async function generateReview() {
                const reviewDate = document.getElementById('reviewDate').value;
                if (!reviewDate) {
                    alert('请选择复盘日期');
                    return;
                }

                const reviewLoading = document.getElementById('reviewLoading');
                reviewLoading.style.display = 'block';

                try {
                    const response = await fetch('/api/review', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            fileId: currentFileId,
                            date: reviewDate 
                        })
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('reviewContent').innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <pre style="white-space: pre-wrap; font-family: inherit;">${result.content}</pre>
                                </div>
                            </div>
                        `;
                    } else {
                        throw new Error(result.error || '生成复盘报告失败');
                    }
                } catch (error) {
                    document.getElementById('reviewContent').innerHTML = 
                        '<div class="alert alert-danger">生成复盘报告失败: ' + error.message + '</div>';
                } finally {
                    reviewLoading.style.display = 'none';
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