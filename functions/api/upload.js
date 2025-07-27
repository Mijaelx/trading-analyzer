// Cloudflare Pages Function - 处理文件上传
export async function onRequestPost(context) {
  const { request, env } = context;
  
  // 添加CORS预检请求处理
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      }
    });
  }
  
  try {
    console.log('Pages Function: 收到上传请求');
    
    // 转发请求到Workers
    const workerUrl = 'https://trading-analyzer.qfz4kq6xmr.workers.dev/api/upload';
    
    // 获取请求体
    const formData = await request.formData();
    
    // 创建新的请求
    const newRequest = new Request(workerUrl, {
      method: 'POST',
      body: formData,
      headers: {
        // 不要复制所有headers，可能会有问题
      }
    });
    
    console.log('Pages Function: 转发请求到Workers');
    
    // 调用Workers API
    const response = await fetch(newRequest);
    
    console.log('Pages Function: Workers响应状态', response.status);
    
    // 获取响应数据
    const responseData = await response.text();
    
    // 返回响应，添加CORS头
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
    console.error('Pages Function错误:', error);
    
    return new Response(JSON.stringify({ 
      error: '代理请求失败: ' + error.message,
      details: error.stack
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

// 处理OPTIONS请求
export async function onRequestOptions(context) {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }
  });
}