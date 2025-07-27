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
    const { date } = req.body || {};
    const reviewDate = date || new Date().toISOString().split('T')[0];

    // 模拟复盘报告
    const reviewContent = `# 交易复盘报告 - ${reviewDate}

## 一、市场整体环境复盘

### 指数与量能分析
今日市场整体呈震荡态势。

### 主要指数表现：
- 上证指数：需关注日均线趋势
- 深证成指：关注量能配合情况

## 二、个人交易复盘

### 今日交易概况
- 交易笔数：3笔
- 交易金额：¥50,000
- 实现盈亏：+¥1,200

### 交易明细分析
1. **买入 平安银行(000001)**
   - 买入价格：¥10.50
   - 买入数量：1000股
   - 买入理由：技术面突破，基本面良好

## 三、经验总结

### 做得好的地方
1. 严格执行止损策略
2. 及时获利了结

### 需要改进的地方
1. 仓位管理需要更加精细
2. 情绪控制有待提高

## 四、明日计划
1. 关注市场热点轮动
2. 控制仓位在合理范围内
`;

    res.status(200).json({
      success: true,
      content: reviewContent
    });
  } catch (error) {
    console.error('复盘错误:', error);
    res.status(500).json({ 
      error: '生成复盘失败: ' + error.message 
    });
  }
}