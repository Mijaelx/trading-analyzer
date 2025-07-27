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
    // 模拟仪表盘数据
    const mockData = {
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
        },
        {
          symbol: '000002',
          name: '万科A',
          quantity: 500,
          cost: 20.30,
          current_price: 19.80,
          market_value: 9900,
          pnl: -250
        }
      ]
    };

    res.status(200).json(mockData);
  } catch (error) {
    console.error('仪表盘错误:', error);
    res.status(500).json({ 
      error: '获取数据失败: ' + error.message 
    });
  }
}