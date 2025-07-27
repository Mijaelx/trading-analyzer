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
    // 模拟数据处理成功
    res.status(200).json({
      success: true,
      message: '数据处理完成（测试模式）'
    });
  } catch (error) {
    console.error('处理错误:', error);
    res.status(500).json({ 
      error: '处理失败: ' + error.message 
    });
  }
}