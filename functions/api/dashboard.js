// Cloudflare Pages Function - 获取仪表盘数据
export async function onRequestGet(context) {
  const { request, env } = context;
  
  try {
    // 获取查询参数
    const url = new URL(request.url);
    const queryString = url.search;
    
    // 转发请求到Workers
    const workerUrl = 'https://trading-analyzer.qfz4kq6xmr.workers.dev/api/dashboard' + queryString;
    
    const response = await fetch(workerUrl, {
      method: 'GET'
    });
    
    const responseData = await response.text();
    
    return new Response(responseData, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ 
      error: '代理请求失败: ' + error.message 
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}