// Vercel API函数 - 获取仪表盘数据
export default async function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: '只支持GET请求' });
    return;
  }

  try {
    // 获取查询参数
    const queryString = new URLSearchParams(req.query).toString();
    
    // 转发到Cloudflare Workers
    const workerUrl = `https://trading-analyzer.qfz4kq6xmr.workers.dev/api/dashboard?${queryString}`;
    
    const response = await fetch(workerUrl, {
      method: 'GET'
    });

    const data = await response.json();
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('仪表盘代理错误:', error);
    res.status(500).json({ 
      error: '代理请求失败: ' + error.message 
    });
  }
}