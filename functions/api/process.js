// Cloudflare Pages Function - 处理数据处理
export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    // 转发请求到Workers
    const workerUrl = 'https://trading-analyzer.qfz4kq6xmr.workers.dev/api/process';
    
    const requestBody = await request.text();
    
    const newRequest = new Request(workerUrl, {
      method: 'POST',
      body: requestBody,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const response = await fetch(newRequest);
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

export async function onRequestOptions(context) {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }
  });
}