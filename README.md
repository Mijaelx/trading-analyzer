# 交易数据分析系统

一个用于处理股票交易数据、分析盈亏情况和生成交易复盘报告的综合性工具。支持本地运行和云端部署。

## ✨ 功能特点

- **📊 交易数据处理**：自动处理交易记录，计算手续费、印花税等各项费用
- **💰 盈亏分析**：实时计算已实现和未实现盈亏，生成详细的盈亏报告
- **📈 持仓管理**：跟踪当前持仓情况，计算持仓成本和市值
- **📝 交易复盘**：生成专业的交易复盘报告，帮助总结交易经验和教训
- **🎨 可视化界面**：基于Streamlit和Web的交互式数据可视化界面
- **💵 分红记录**：管理股票分红记录，计算分红收益
- **☁️ 云端部署**：支持Cloudflare Workers部署，随时随地访问

## 🚀 快速开始

### 本地运行

```bash
# 克隆项目
git clone https://github.com/yourusername/trading-analyzer.git
cd trading-analyzer

# 安装依赖
pip install -r requirements.txt

# 启动Streamlit界面
python run_dashboard.py

# 或使用命令行
python main.py --help
```

### 云端部署

支持一键部署到Cloudflare Workers：

```bash
# 安装Wrangler CLI
npm install -g wrangler

# 登录Cloudflare
wrangler login

# 部署到云端
wrangler deploy --env production
```

详细部署指南请参考：[部署指南](docs/部署指南.md)

## 📁 项目结构

```
交易分析系统/
├── core/                    # 核心功能模块
│   ├── trading_processor.py # 交易数据处理器
│   └── trading_review.py    # 交易复盘生成器
├── ui/                      # 用户界面模块
│   └── trading_dashboard.py # Streamlit仪表盘
├── web/                     # Web应用模块
│   ├── app.py              # Flask Web应用
│   └── templates/          # HTML模板
├── config/                  # 配置模块
│   └── settings.py         # 项目配置
├── utils/                   # 工具模块
│   └── create_sample.py    # 示例数据生成
├── docs/                    # 文档目录
├── data/                    # 数据文件目录
├── reports/                 # 报告输出目录
├── src/                     # Cloudflare Workers代码
│   └── index.js            # Workers入口文件
├── main.py                  # 主入口文件
├── run_dashboard.py         # 仪表盘启动脚本
└── wrangler.toml           # Cloudflare配置
```

## 💻 使用方法

### 命令行使用

```bash
# 处理交易数据
python main.py process data/交易数据.xlsx

# 生成复盘报告
python main.py review --date 2025-07-25

# 启动可视化界面
python main.py dashboard
```

### Web界面使用

1. 访问部署的域名或本地地址
2. 上传Excel交易数据文件
3. 点击"处理数据"进行分析
4. 查看仪表盘和生成复盘报告

### 程序化使用

```python
from core.trading_processor import TradingProcessor
from core.trading_review import TradingReview

# 创建处理器
processor = TradingProcessor()
processor.load_data("data/交易数据.xlsx")
processor.calculate_fees()
processor.calculate_pnl()

# 生成复盘
review = TradingReview(processor)
review.generate_review_report("reports/review.md")
```

## 📋 数据格式

程序支持Excel文件输入，需要包含以下工作表：

### 交易数据
| 列名 | 说明 | 示例 |
|------|------|------|
| 日期 | 交易日期 | 2025-07-25 |
| 证券代码 | 股票代码 | 000001 |
| 证券名称 | 股票名称 | 平安银行 |
| 买卖方向 | 买入/卖出 | 买入 |
| 成交价格 | 交易价格 | 10.50 |
| 成交数量 | 交易数量 | 1000 |

### 费率配置
| 列名 | 说明 | 示例 |
|------|------|------|
| 券商 | 券商名称 | 华泰证券 |
| 市场 | 交易市场 | 上交所 |
| 产品类型 | 产品类型 | 股票 |
| 手续费率 | 手续费率 | 0.0003 |
| 印花税率 | 印花税率 | 0.001 |

详细格式说明：[示例数据说明](docs/示例数据说明.md)

## 📊 输出结果

- **盈亏分析报告**：每日盈亏统计和趋势分析
- **交易明细表**：详细的交易记录和费用计算
- **持仓数据表**：当前持仓情况和盈亏状态
- **交易复盘文档**：专业的交易复盘和经验总结

## 🌐 在线演示

- **演示地址**：https://your-domain.workers.dev
- **测试数据**：可使用 `python utils/create_sample.py` 生成

## 🔧 配置说明

### 环境变量
```bash
# 数据目录
DATA_DIR=./data

# 报告目录  
REPORTS_DIR=./reports

# 日志级别
LOG_LEVEL=INFO
```

### 费率配置
支持多券商、多市场的费率配置，可在Excel文件中自定义。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 技术支持

- **文档**：查看 [docs/](docs/) 目录下的详细文档
- **问题反馈**：提交 [GitHub Issues](https://github.com/yourusername/trading-analyzer/issues)
- **功能建议**：欢迎提交 Pull Request

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！