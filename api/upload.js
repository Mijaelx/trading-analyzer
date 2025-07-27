// Vercel API函数 - 处理文件上传
import formidable from 'formidable';

export default async function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: '只支持POST请求' });
    return;
  }

  try {
    // 转发到Cloudflare Workers
    const workerUrl = 'https://trading-analyzer.qfz4kq6xmr.workers.dev/api/upload';
    
    // 获取原始请求体
    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const body = Buffer.concat(chunks);

    const response = await fetch(workerUrl, {
      method: 'POST',
      body: body,
      headers: {
        'Content-Type': req.headers['content-type'],
      }
    });

    const data = await response.json();
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('上传代理错误:', error);
    res.status(500).json({ 
      error: '代理请求失败: ' + error.message 
    });
  }
}