// 交易数据分析系统 - 前端JavaScript
// 配置API基础URL - 使用相对路径，通过Vercel API代理
const API_BASE_URL = '';

// 全局变量
let uploadedFile = null;
let processedData = null;

// 显示消息
function showMessage(message, type = 'info') {
    const toast = document.getElementById('messageToast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : 'bg-success text-white'}`;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// 文件上传处理
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadLoading = document.getElementById('uploadLoading');
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
    
    // 文件选择上传
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // 处理数据按钮
    document.getElementById('processBtn').addEventListener('click', processData);
    
    // 生成复盘按钮
    document.getElementById('generateReviewBtn').addEventListener('click', generateReview);
    
    // 设置默认日期为今天
    document.getElementById('reviewDate').valueAsDate = new Date();
});

// 处理文件上传
async function handleFileUpload(file) {
    if (!file.name.endsWith('.xlsx')) {
        showMessage('请选择Excel文件(.xlsx)', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const uploadLoading = document.getElementById('uploadLoading');
    uploadLoading.style.display = 'block';
    
    console.log('开始上传文件:', file.name, '大小:', file.size);
    console.log('API URL:', `${API_BASE_URL}/api/upload`);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        console.log('响应状态:', response.status, response.statusText);
        console.log('响应头:', Object.fromEntries(response.headers));
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('响应数据:', data);
        
        uploadLoading.style.display = 'none';
        
        if (data.success) {
            showMessage('文件上传成功！');
            uploadedFile = data.fileId;
            document.getElementById('processSection').style.display = 'block';
            document.getElementById('uploadStatus').innerHTML = 
                `<div class="alert alert-success">文件上传成功！文件ID: ${data.fileId}</div>`;
        } else {
            showMessage(data.error || '上传失败', 'error');
            document.getElementById('uploadStatus').innerHTML = 
                `<div class="alert alert-danger">${data.error || '上传失败'}</div>`;
        }
    } catch (error) {
        console.error('上传错误:', error);
        uploadLoading.style.display = 'none';
        showMessage('上传失败: ' + error.message, 'error');
        document.getElementById('uploadStatus').innerHTML = 
            `<div class="alert alert-danger">上传失败: ${error.message}<br>
            <small>请打开浏览器开发者工具查看详细错误信息</small></div>`;
    }
}

// 处理数据
async function processData() {
    if (!uploadedFile) {
        showMessage('请先上传文件', 'error');
        return;
    }
    
    const processLoading = document.getElementById('processLoading');
    processLoading.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fileId: uploadedFile })
        });
        
        const data = await response.json();
        processLoading.style.display = 'none';
        
        if (data.success) {
            showMessage('数据处理完成！');
            document.getElementById('dashboardSection').style.display = 'block';
            document.getElementById('reviewSection').style.display = 'block';
            loadDashboardData();
        } else {
            showMessage(data.error || '处理失败', 'error');
        }
    } catch (error) {
        processLoading.style.display = 'none';
        showMessage('处理失败: ' + error.message, 'error');
    }
}

// 加载仪表盘数据
async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard?fileId=${uploadedFile}`);
        const data = await response.json();
        
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }
        
        // 更新统计卡片
        updateStatsCards(data.stats);
        
        // 更新持仓表格
        updatePositionsTable(data.positions);
    } catch (error) {
        showMessage('加载数据失败: ' + error.message, 'error');
    }
}

// 更新统计卡片
function updateStatsCards(stats) {
    const statsCards = document.getElementById('statsCards');
    statsCards.innerHTML = `
        <div class="col-md-3">
            <div class="card stat-card">
                <div class="card-body text-center">
                    <h5 class="card-title">总交易笔数</h5>
                    <h2>${stats.total_trades || 0}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stat-card">
                <div class="card-body text-center">
                    <h5 class="card-title">总交易金额</h5>
                    <h2>¥${(stats.total_amount || 0).toLocaleString()}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stat-card">
                <div class="card-body text-center">
                    <h5 class="card-title">当前持仓</h5>
                    <h2>${stats.current_positions || 0}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stat-card">
                <div class="card-body text-center">
                    <h5 class="card-title">总市值</h5>
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
        
        row.innerHTML = `
            <td>${position.symbol}</td>
            <td>${position.name}</td>
            <td>${position.quantity}</td>
            <td>¥${position.cost.toFixed(2)}</td>
            <td>¥${position.current_price.toFixed(2)}</td>
            <td>¥${position.market_value.toLocaleString()}</td>
            <td class="${pnlClass}">¥${position.pnl.toFixed(2)}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// 生成复盘报告
async function generateReview() {
    const reviewDate = document.getElementById('reviewDate').value;
    if (!reviewDate) {
        showMessage('请选择复盘日期', 'error');
        return;
    }
    
    const reviewLoading = document.getElementById('reviewLoading');
    reviewLoading.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                fileId: uploadedFile,
                date: reviewDate 
            })
        });
        
        const data = await response.json();
        reviewLoading.style.display = 'none';
        
        if (data.success) {
            showMessage('复盘报告生成成功！');
            const reviewContent = document.getElementById('reviewContent');
            reviewContent.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <pre style="white-space: pre-wrap; font-family: inherit;">${data.content}</pre>
                    </div>
                </div>
            `;
        } else {
            showMessage(data.error || '生成失败', 'error');
        }
    } catch (error) {
        reviewLoading.style.display = 'none';
        showMessage('生成失败: ' + error.message, 'error');
    }
}