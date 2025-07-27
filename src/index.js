/**
 * Cloudflare Workers 脚本 - 简化版本
 * 处理交易数据分析的API请求
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS 处理
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // 路由处理
      if (path === '/') {
        return new Response(getIndexHTML(), {
          headers: { 'Content-Type': 'text/html', ...corsHeaders }
        });
      }

      if (path === '/api/test') {
        return new Response(JSON.stringify({ 
          message: 'API正常工作!',
          timestamp: new Date().toISOString(),
          environment: env.ENVIRONMENT 
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }

      if (path === '/api/upload' && request.method === 'POST') {
        return handleUpload(request, env);
      }

      if (path === '/api/process' && request.method === 'POST') {
        return handleProcess(request, env);
      }

      if (path === '/api/dashboard') {
        return handleDashboard(request, env);
      }

      if (path === '/api/review' && request.method === 'POST') {
        return handleReview(request, env);
      }

      return new Response('Not Found', { status: 404, headers: corsHeaders });

    } catch (error) {
      return new Response(JSON.stringify({ 
        error: error.message,
        stack: error.stack 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }
  }
};

// 处理文件上传
async function handleUpload(request, env) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    
    if (!file) {
      return new Response(JSON.stringify({ error: '没有选择文件' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 将文件存储到KV
    const fileId = generateId();
    const fileData = await file.arrayBuffer();
    
    await env.TRADING_DATA.put(`file:${fileId}`, fileData, {
      metadata: {
        filename: file.name,
        size: file.size,
        type: file.type,
        uploadTime: new Date().toISOString()
      }
    });

    return new Response(JSON.stringify({
      success: true,
      fileId: fileId,
      message: '文件上传成功'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// 处理数据分析
async function handleProcess(request, env) {
  try {
    const { fileId } = await request.json();
    
    if (!fileId) {
      return new Response(JSON.stringify({ error: '缺少文件ID' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 从KV获取文件数据
    const fileData = await env.TRADING_DATA.get(`file:${fileId}`, 'arrayBuffer');
    
    if (!fileData) {
      return new Response(JSON.stringify({ error: '文件不存在' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 模拟处理结果
    const processedData = {
      stats: {
        total_trades: 100,
        total_amount: 1000000,
        current_positions: 5,
        total_market_value: 950000
      },
      positions: [
        {
          symbol: '000001',
          name: '平安银行',
          quantity: 1000,
          cost: 10.50,
          current_price: 11.20,
          market_value: 11200,
          pnl: 700
        }
      ]
    };

    // 存储处理结果
    await env.TRADING_DATA.put(`result:${fileId}`, JSON.stringify(processedData));

    return new Response(JSON.stringify({
      success: true,
      message: '数据处理完成'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// 获取仪表盘数据
async function handleDashboard(request, env) {
  try {
    const url = new URL(request.url);
    const fileId = url.searchParams.get('fileId');
    
    if (!fileId) {
      return new Response(JSON.stringify({ error: '缺少文件ID' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const resultData = await env.TRADING_DATA.get(`result:${fileId}`);
    
    if (!resultData) {
      return new Response(JSON.stringify({ error: '数据不存在，请先处理数据' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(resultData, {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// 生成复盘报告
async function handleReview(request, env) {
  try {
    const { fileId, date } = await request.json();
    
    // 生成示例复盘报告
    const reviewContent = `# 交易复盘报告 - ${date}

## 一、市场整体环境复盘
今日市场整体呈震荡态势。

## 二、个人交易复盘
- 交易笔数：3笔
- 交易金额：¥50,000
- 实现盈亏：+¥1,200

## 三、经验总结
1. 严格执行止损策略
2. 及时获利了结
`;

    return new Response(JSON.stringify({
      success: true,
      content: reviewContent
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// 生成唯一ID
function generateId() {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// 获取首页HTML
function getIndexHTML() {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易数据分析系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .upload-area {
            border: 2px dashed #dee2e6;
            border-radius: 0.375rem;
            padding: 3rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #0d6efd;
            background-color: #f8f9fa;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-graph-up"></i>
                交易数据分析系统
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="mb-4">
                    <i class="bi bi-graph-up text-primary"></i>
                    交易数据分析系统
                </h1>
                <div class="alert alert-success">
                    <h4>🎉 系统部署成功！</h4>
                    <p>你的交易数据分析系统已经在Cloudflare Workers上运行。</p>
                    <hr>
                    <p class="mb-0">
                        <strong>测试API：</strong> 
                        <a href="/api/test" target="_blank" class="btn btn-sm btn-outline-success">测试API</a>
                    </p>
                </div>
            </div>
        </div>

        <!-- 文件上传区域 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="bi bi-cloud-upload"></i>
                            数据上传
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="upload-area" id="uploadArea">
                            <i class="bi bi-cloud-upload fs-1 text-muted mb-3"></i>
                            <h5>选择Excel文件上传</h5>
                            <p class="text-muted">支持.xlsx格式</p>
                            <input type="file" id="fileInput" accept=".xlsx" class="form-control mb-3">
                            <button class="btn btn-primary" onclick="uploadFile()">
                                上传文件
                            </button>
                        </div>
                        <div id="uploadStatus" class="mt-3"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 功能区域 -->
        <div id="mainContent" style="display: none;">
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">数据处理</h5>
                </div>
                <div class="card-body">
                    <button class="btn btn-success" onclick="processData()">
                        开始处理数据
                    </button>
                    <div id="processStatus" class="mt-3"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentFileId = null;

        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('请选择文件');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.success) {
                    currentFileId = result.fileId;
                    document.getElementById('uploadStatus').innerHTML = 
                        '<div class="alert alert-success">文件上传成功！文件ID: ' + result.fileId + '</div>';
                    document.getElementById('mainContent').style.display = 'block';
                } else {
                    document.getElementById('uploadStatus').innerHTML = 
                        '<div class="alert alert-danger">' + result.error + '</div>';
                }
            } catch (error) {
                document.getElementById('uploadStatus').innerHTML = 
                    '<div class="alert alert-danger">上传失败: ' + error.message + '</div>';
            }
        }

        async function processData() {
            if (!currentFileId) {
                alert('请先上传文件');
                return;
            }

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ fileId: currentFileId })
                });

                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('processStatus').innerHTML = 
                        '<div class="alert alert-success">数据处理完成！</div>';
                    showDashboard();
                } else {
                    document.getElementById('processStatus').innerHTML = 
                        '<div class="alert alert-danger">' + result.error + '</div>';
                }
            } catch (error) {
                document.getElementById('processStatus').innerHTML = 
                    '<div class="alert alert-danger">处理失败: ' + error.message + '</div>';
            }
        }

        async function showDashboard() {
            try {
                const response = await fetch('/api/dashboard?fileId=' + currentFileId);
                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }

                const dashboardHTML = \`
                    <div class="card mt-4">
                        <div class="card-header">
                            <h5 class="mb-0">数据仪表盘</h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-4">
                                <div class="col-md-3">
                                    <div class="card stat-card">
                                        <div class="card-body text-center">
                                            <h5>总交易笔数</h5>
                                            <h2>\${data.stats.total_trades}</h2>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card stat-card">
                                        <div class="card-body text-center">
                                            <h5>总交易金额</h5>
                                            <h2>¥\${data.stats.total_amount.toLocaleString()}</h2>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card stat-card">
                                        <div class="card-body text-center">
                                            <h5>当前持仓</h5>
                                            <h2>\${data.stats.current_positions}</h2>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card stat-card">
                                        <div class="card-body text-center">
                                            <h5>总市值</h5>
                                            <h2>¥\${data.stats.total_market_value.toLocaleString()}</h2>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                \`;

                document.getElementById('mainContent').innerHTML += dashboardHTML;
            } catch (error) {
                alert('加载仪表盘失败: ' + error.message);
            }
        }
    </script>
</body>
</html>`;
}