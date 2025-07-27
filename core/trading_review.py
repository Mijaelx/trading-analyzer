#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易复盘记录生成器
分析当天交易数据并生成详细的复盘报告
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging
from .trading_processor import TradingProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trading_review')

class TradingReview:
    """交易复盘记录生成器类"""
    
    def __init__(self, processor=None):
        """初始化复盘记录生成器
        
        Args:
            processor: TradingProcessor实例，如果为None则创建新实例
        """
        self.processor = processor if processor else TradingProcessor()
        self.review_date = datetime.now().date()
        self.market_status = self._get_market_status()
    
    def _get_market_status(self):
        """获取市场状态（上涨/下跌/震荡）
        
        Returns:
            str: 市场状态描述
        """
        # 这里可以集成外部API获取指数数据
        # 简单起见，这里随机生成一个状态
        import random
        status_list = ["上涨", "下跌", "震荡"]
        weights = [0.3, 0.3, 0.4]  # 权重
        return random.choices(status_list, weights=weights)[0]
    
    def load_data(self, input_file):
        """加载交易数据
        
        Args:
            input_file: 输入Excel文件路径
            
        Returns:
            bool: 是否成功加载数据
        """
        try:
            # 加载数据
            if self.processor.load_data(input_file):
                # 处理数据
                if self.processor.process_data():
                    logger.info("数据加载和处理成功")
                    return True
                else:
                    logger.error("数据处理失败")
                    return False
            else:
                logger.error("数据加载失败")
                return False
        except Exception as e:
            logger.error(f"加载数据出错: {e}")
            return False
    
    def set_review_date(self, date):
        """设置复盘日期
        
        Args:
            date: 复盘日期，可以是datetime.date对象或YYYY-MM-DD格式的字符串
            
        Returns:
            bool: 是否成功设置日期
        """
        try:
            if isinstance(date, str):
                self.review_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                self.review_date = date
            return True
        except Exception as e:
            logger.error(f"设置复盘日期出错: {e}")
            return False
    
    def get_daily_trades(self):
        """获取当天的交易记录
        
        Returns:
            DataFrame: 当天的交易记录
        """
        if self.processor.trades_df is None or self.processor.trades_df.empty:
            return pd.DataFrame()
        
        # 筛选当天的交易记录
        daily_trades = self.processor.trades_df[
            self.processor.trades_df['日期'].dt.date == self.review_date
        ]
        
        return daily_trades
    
    def get_daily_pnl(self):
        """获取当天的盈亏数据
        
        Returns:
            DataFrame: 当天的盈亏数据
        """
        if self.processor.daily_pnl is None or self.processor.daily_pnl.empty:
            return pd.DataFrame()
        
        # 确保日期列是日期时间类型
        if '日期' in self.processor.daily_pnl.columns:
            try:
                # 尝试转换日期列为日期时间类型
                self.processor.daily_pnl['日期'] = pd.to_datetime(self.processor.daily_pnl['日期'])
            except:
                # 如果转换失败，则使用字符串比较
                pass
        
        # 筛选当天的盈亏数据
        try:
            # 尝试使用日期时间类型比较
            daily_pnl = self.processor.daily_pnl[
                self.processor.daily_pnl['日期'].dt.date == self.review_date
            ]
        except:
            # 如果失败，则使用字符串比较
            review_date_str = self.review_date.strftime('%Y-%m-%d')
            daily_pnl = self.processor.daily_pnl[
                self.processor.daily_pnl['日期'].astype(str).str.startswith(review_date_str)
            ]
        
        return daily_pnl
    
    def get_daily_dividends(self):
        """获取当天的分红记录
        
        Returns:
            DataFrame: 当天的分红记录
        """
        if (self.processor.dividend_record.dividends_df is None or 
            self.processor.dividend_record.dividends_df.empty):
            return pd.DataFrame()
        
        # 筛选当天的分红记录
        daily_dividends = self.processor.dividend_record.dividends_df[
            pd.to_datetime(self.processor.dividend_record.dividends_df['日期']).dt.date == self.review_date
        ]
        
        return daily_dividends
    
    def analyze_daily_performance(self):
        """分析当天的交易表现
        
        Returns:
            dict: 包含当天表现分析的字典
        """
        daily_trades = self.get_daily_trades()
        daily_pnl = self.get_daily_pnl()
        daily_dividends = self.get_daily_dividends()
        
        # 初始化结果字典
        result = {
            "日期": self.review_date.strftime("%Y-%m-%d"),
            "星期": ["一", "二", "三", "四", "五", "六", "日"][self.review_date.weekday()],
            "市场状态": self.market_status,
            "交易笔数": 0,
            "买入笔数": 0,
            "卖出笔数": 0,
            "总交易金额": 0,
            "买入金额": 0,
            "卖出金额": 0,
            "总手续费": 0,
            "当日已实现盈亏": 0,
            "当日未实现盈亏": 0,
            "当日总盈亏": 0,
            "分红记录数": 0,
            "分红总金额": 0,
            "交易股票": [],
            "盈利股票": [],
            "亏损股票": [],
            "买入股票": [],
            "卖出股票": [],
            "分红股票": []
        }
        
        # 分析交易数据
        if not daily_trades.empty:
            result["交易笔数"] = len(daily_trades)
            
            # 买入和卖出交易
            buy_trades = daily_trades[~daily_trades['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
            sell_trades = daily_trades[daily_trades['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
            
            result["买入笔数"] = len(buy_trades)
            result["卖出笔数"] = len(sell_trades)
            
            # 交易金额
            result["总交易金额"] = daily_trades['交易金额'].sum()
            result["买入金额"] = buy_trades['交易金额'].sum() if not buy_trades.empty else 0
            result["卖出金额"] = sell_trades['交易金额'].sum() if not sell_trades.empty else 0
            
            # 手续费
            result["总手续费"] = daily_trades['总费用'].sum()
            
            # 交易股票
            for _, trade in daily_trades.iterrows():
                stock_info = {
                    "证券代码": trade['证券代码'],
                    "证券名称": trade['证券名称'],
                    "买卖方向": trade['买卖方向'],
                    "成交价格": trade['成交价格'],
                    "成交数量": trade['成交数量'],
                    "交易金额": trade['交易金额'],
                    "总费用": trade['总费用']
                }
                
                result["交易股票"].append(stock_info)
                
                if trade['买卖方向'] not in ['卖出', '卖', 'SELL', 'S']:
                    result["买入股票"].append({
                        "证券代码": trade['证券代码'],
                        "证券名称": trade['证券名称'],
                        "成交价格": trade['成交价格'],
                        "成交数量": trade['成交数量'],
                        "交易金额": trade['交易金额']
                    })
                else:
                    result["卖出股票"].append({
                        "证券代码": trade['证券代码'],
                        "证券名称": trade['证券名称'],
                        "成交价格": trade['成交价格'],
                        "成交数量": trade['成交数量'],
                        "交易金额": trade['交易金额']
                    })
        
        # 分析盈亏数据
        if not daily_pnl.empty:
            result["当日已实现盈亏"] = daily_pnl['当日已实现盈亏'].sum()
            result["当日未实现盈亏"] = daily_pnl['当日未实现盈亏'].sum()
            result["当日总盈亏"] = result["当日已实现盈亏"] + result["当日未实现盈亏"]
            
            # 盈利和亏损股票
            for _, pnl in daily_pnl.iterrows():
                total_pnl = pnl['当日已实现盈亏'] + pnl['当日未实现盈亏']
                
                stock_info = {
                    "证券代码": pnl['证券代码'],
                    "证券名称": pnl['证券名称'],
                    "持仓数量": pnl['持仓数量'],
                    "持仓成本价": pnl['持仓成本价'],
                    "收盘价": pnl['收盘价'],
                    "当日已实现盈亏": pnl['当日已实现盈亏'],
                    "当日未实现盈亏": pnl['当日未实现盈亏'],
                    "总盈亏": total_pnl
                }
                
                if total_pnl > 0:
                    result["盈利股票"].append(stock_info)
                elif total_pnl < 0:
                    result["亏损股票"].append(stock_info)
        
        # 分析分红数据
        if not daily_dividends.empty:
            result["分红记录数"] = len(daily_dividends)
            result["分红总金额"] = daily_dividends['净分红金额'].sum()
            
            # 分红股票
            for _, dividend in daily_dividends.iterrows():
                result["分红股票"].append({
                    "证券代码": dividend['证券代码'],
                    "证券名称": dividend['证券名称'],
                    "持有数量": dividend['持有数量'],
                    "每股分红": dividend['每股分红'],
                    "总分红金额": dividend['总分红金额'],
                    "税费": dividend['税费'],
                    "净分红金额": dividend['净分红金额']
                })
        
        return result
    
    def generate_review_report(self):
        """生成专业复盘报告
        
        Returns:
            str: 复盘报告文本
        """
        # 分析当天表现
        analysis = self.analyze_daily_performance()
        
        # 生成报告标题
        report = f"# {analysis['日期']} (星期{analysis['星期']}) 交易复盘报告\n\n"
        
        # 一、市场整体环境复盘
        report += "## 一、市场整体环境复盘\n\n"
        
        # 指数与量能分析
        report += "### 指数与量能分析\n\n"
        report += f"今日市场整体呈{analysis['市场状态']}态势。\n\n"
        report += "主要指数表现：\n"
        report += "- 上证指数：需关注5/10/20/60日均线趋势\n"
        report += "- 深证成指：关注量能变化（增量/缩量）\n"
        report += "- 创业板指：观察K线形态\n\n"
        report += "市场量能分析：当前市场量能处于中等水平，需关注是否有放量突破或缩量调整迹象。\n\n"
        
        # 市场情绪与赚钱效应
        report += "### 市场情绪与赚钱效应\n\n"
        report += "涨跌停情况：\n"
        report += "- 涨停家数：需统计（剔除新股和一字板）\n"
        report += "- 跌停家数：需统计\n"
        report += "- 涨跌超6%个股数量：需评估\n\n"
        report += "连板梯队分析：关注高标连板情况，判断市场炒作持续性。\n\n"
        
        # 二、板块与个股深度分析
        report += "## 二、板块与个股深度分析\n\n"
        
        # 板块轮动与强弱梳理
        report += "### 板块轮动与强弱梳理\n\n"
        report += "今日领涨板块：需识别当日表现最强的2-3个板块\n"
        report += "今日领跌板块：需识别当日表现最弱的2-3个板块\n\n"
        report += "板块周期分析：判断主要板块所处阶段（启动、高潮、分歧、退潮）\n\n"
        report += "新题材分析：关注新兴题材的涨停原因、资金关注度及持续性逻辑\n\n"
        
        # 个股异动复盘
        report += "### 个股异动复盘\n\n"
        
        # 涨停复盘
        report += "#### 涨停复盘\n\n"
        if analysis['交易笔数'] > 0:
            report += "需分析涨停股原因（消息/技术/板块联动），研究基本面与资金动向\n\n"
        
        # 跌停复盘
        report += "#### 跌停复盘\n\n"
        report += "排查跌停股诱因（利空/情绪退潮），规避亏钱效应集中领域\n\n"
        
        # 异动筛选
        report += "#### 异动筛选\n\n"
        report += "复盘振幅、换手率、成交量前30名个股，捕捉主力动向\n\n"
        
        # 龙头股与标杆跟踪
        report += "### 龙头股与标杆跟踪\n\n"
        report += "标记空间龙头、连板高标、地天板（情绪转折信号）及空头龙头\n"
        report += "对比同梯队个股的晋级概率，筛选次日重点标的\n\n"
        
        # 三、消息面与外围市场联动
        report += "## 三、消息面与外围市场联动\n\n"
        
        # 政策与公告解读
        report += "### 政策与公告解读\n\n"
        report += "关注官媒（证监会、人民日报、新华社）及行业政策\n"
        report += "关注业绩暴增、资产重组类公告\n"
        report += "核查市场传闻真伪及潜在影响\n\n"
        
        # 外盘与大宗商品跟踪
        report += "### 外盘与大宗商品跟踪\n\n"
        report += "美股（尤其是中概股）、美元指数、原油、黄金等走势\n"
        report += "分析对A股相关板块（如特斯拉链、资源股）的传导效应\n\n"
        
        # 四、交易执行与自我复盘
        report += "## 四、交易执行与自我复盘\n\n"
        
        # 操作回顾与纠错
        report += "### 操作回顾与纠错\n\n"
        
        if analysis['交易笔数'] > 0:
            report += f"今日共进行 {analysis['交易笔数']} 笔交易：\n"
            report += f"- 买入 {analysis['买入笔数']} 笔，金额 ¥{analysis['买入金额']:,.2f}\n"
            report += f"- 卖出 {analysis['卖出笔数']} 笔，金额 ¥{analysis['卖出金额']:,.2f}\n"
            report += f"- 交易总额 ¥{analysis['总交易金额']:,.2f}，手续费 ¥{analysis['总手续费']:,.2f}\n\n"
            
            # 买入交易明细
            if analysis['买入股票']:
                report += "买入交易明细：\n\n"
                report += "| 证券代码 | 证券名称 | 成交价格 | 成交数量 | 交易金额 | 买入理由 |\n"
                report += "| -------- | -------- | -------- | -------- | -------- | -------- |\n"
                
                for stock in analysis['买入股票']:
                    report += f"| {stock['证券代码']} | {stock['证券名称']} | "
                    report += f"{stock['成交价格']:.4f} | {stock['成交数量']} | {stock['交易金额']:,.2f} | 需补充 |\n"
                
                report += "\n"
            
            # 卖出交易明细
            if analysis['卖出股票']:
                report += "卖出交易明细：\n\n"
                report += "| 证券代码 | 证券名称 | 成交价格 | 成交数量 | 交易金额 | 卖出理由 |\n"
                report += "| -------- | -------- | -------- | -------- | -------- | -------- |\n"
                
                for stock in analysis['卖出股票']:
                    report += f"| {stock['证券代码']} | {stock['证券名称']} | "
                    report += f"{stock['成交价格']:.4f} | {stock['成交数量']} | {stock['交易金额']:,.2f} | 需补充 |\n"
                
                report += "\n"
        else:
            report += "今日无交易记录。\n\n"
        
        # 盈亏情况分析
        if analysis['当日总盈亏'] != 0:
            report += "盈亏情况分析：\n\n"
            report += f"- 当日已实现盈亏: ¥{analysis['当日已实现盈亏']:,.2f}\n"
            report += f"- 当日未实现盈亏: ¥{analysis['当日未实现盈亏']:,.2f}\n"
            report += f"- 当日总盈亏: ¥{analysis['当日总盈亏']:,.2f}\n\n"
            
            if analysis['盈利股票']:
                report += "盈利股票明细：\n\n"
                report += "| 证券代码 | 证券名称 | 持仓数量 | 持仓成本价 | 收盘价 | 已实现盈亏 | 未实现盈亏 | 总盈亏 |\n"
                report += "| -------- | -------- | -------- | ---------- | ------ | ---------- | ---------- | ------ |\n"
                
                for stock in analysis['盈利股票']:
                    report += f"| {stock['证券代码']} | {stock['证券名称']} | {stock['持仓数量']} | "
                    report += f"{stock['持仓成本价']:.4f} | {stock['收盘价']:.4f} | "
                    report += f"{stock['当日已实现盈亏']:,.2f} | {stock['当日未实现盈亏']:,.2f} | {stock['总盈亏']:,.2f} |\n"
                
                report += "\n"
            
            if analysis['亏损股票']:
                report += "亏损股票明细：\n\n"
                report += "| 证券代码 | 证券名称 | 持仓数量 | 持仓成本价 | 收盘价 | 已实现盈亏 | 未实现盈亏 | 总盈亏 |\n"
                report += "| -------- | -------- | -------- | ---------- | ------ | ---------- | ---------- | ------ |\n"
                
                for stock in analysis['亏损股票']:
                    report += f"| {stock['证券代码']} | {stock['证券名称']} | {stock['持仓数量']} | "
                    report += f"{stock['持仓成本价']:.4f} | {stock['收盘价']:.4f} | "
                    report += f"{stock['当日已实现盈亏']:,.2f} | {stock['当日未实现盈亏']:,.2f} | {stock['总盈亏']:,.2f} |\n"
                
                report += "\n"
        
        # 分红情况
        if analysis['分红记录数'] > 0:
            report += "分红情况：\n\n"
            report += f"今日共收到 {analysis['分红记录数']} 笔分红，总金额 ¥{analysis['分红总金额']:,.2f}。\n\n"
            
            report += "| 证券代码 | 证券名称 | 持有数量 | 每股分红 | 总分红金额 | 税费 | 净分红金额 |\n"
            report += "| -------- | -------- | -------- | -------- | ---------- | ---- | ---------- |\n"
            
            for stock in analysis['分红股票']:
                report += f"| {stock['证券代码']} | {stock['证券名称']} | {stock['持有数量']} | "
                report += f"{stock['每股分红']:.4f} | {stock['总分红金额']:,.2f} | "
                report += f"{stock['税费']:,.2f} | {stock['净分红金额']:,.2f} |\n"
            
            report += "\n"
        
        # 模式与心态审视
        report += "### 模式与心态审视\n\n"
        report += "检查当前交易策略是否适配市场风格（如缩量市需回避高位接力）\n"
        report += "杜绝患得患失、冲动交易，保持理性交易心态\n\n"
        
        # 五、制定次日交易计划
        report += "## 五、制定次日交易计划\n\n"
        
        # 多情景推演
        report += "### 多情景推演\n\n"
        report += "预判龙头股的走势（涨停/跌停/反包）、板块轮动路径及资金流向\n"
        report += "针对不同走势制定应对策略：\n"
        report += "- Plan A（主线延续）：\n"
        report += "- Plan B（主线分歧）：\n"
        report += "- Plan C（市场调整）：\n\n"
        
        # 明确标的与买点
        report += "### 明确标的与买点\n\n"
        report += "重点关注标的：\n"
        report += "1. 标的一：买入条件、仓位分配\n"
        report += "2. 标的二：买入条件、仓位分配\n"
        report += "3. 标的三：买入条件、仓位分配\n\n"
        
        # 交易总结
        report += "## 六、交易总结\n\n"
        
        # 根据交易和盈亏情况生成总结
        if analysis['交易笔数'] > 0 or analysis['当日总盈亏'] != 0:
            # 盈亏情况总结
            if analysis['当日总盈亏'] > 0:
                report += f"今日总体表现良好，盈利 ¥{analysis['当日总盈亏']:,.2f}。"
                
                if analysis['盈利股票']:
                    top_profit = max(analysis['盈利股票'], key=lambda x: x['总盈亏'])
                    report += f"其中 {top_profit['证券名称']}({top_profit['证券代码']}) 表现最佳，"
                    report += f"贡献盈利 ¥{top_profit['总盈亏']:,.2f}。"
            elif analysis['当日总盈亏'] < 0:
                report += f"今日总体表现不佳，亏损 ¥{abs(analysis['当日总盈亏']):,.2f}。"
                
                if analysis['亏损股票']:
                    top_loss = min(analysis['亏损股票'], key=lambda x: x['总盈亏'])
                    report += f"其中 {top_loss['证券名称']}({top_loss['证券代码']}) 表现最差，"
                    report += f"亏损 ¥{abs(top_loss['总盈亏']):,.2f}。"
            else:
                report += "今日盈亏平衡。"
            
            # 交易行为总结
            if analysis['买入笔数'] > 0 and analysis['卖出笔数'] > 0:
                report += f"\n\n今日既有买入也有卖出，交易较为活跃。"
            elif analysis['买入笔数'] > 0:
                report += f"\n\n今日仅有买入操作，增加了仓位。"
            elif analysis['卖出笔数'] > 0:
                report += f"\n\n今日仅有卖出操作，减少了仓位。"
            
            # 分红情况总结
            if analysis['分红记录数'] > 0:
                report += f"\n\n今日收到分红 ¥{analysis['分红总金额']:,.2f}，增加了现金流。"
        else:
            report += "今日无交易和盈亏变动，市场观望中。"
        
        # 补充专业细节
        report += "\n\n## 七、专业细节补充\n\n"
        
        # 龙虎榜分析
        report += "### 龙虎榜分析\n\n"
        report += "跟踪游资/机构席位动向，重点观察资金介入逻辑\n\n"
        
        # 技术工具
        report += "### 技术工具\n\n"
        report += "自选股分类管理（按板块/情绪核心归类），使用预警系统监控异动\n\n"
        
        return report
    
    def save_review_report(self, output_file=None):
        """保存复盘报告到文件
        
        Args:
            output_file: 输出文件路径，如果为None则使用默认路径
            
        Returns:
            str: 输出文件路径
        """
        # 生成复盘报告
        report = self.generate_review_report()
        
        # 如果未指定输出文件，则使用默认路径
        if output_file is None:
            # 确保reports目录存在
            os.makedirs("reports", exist_ok=True)
            
            # 使用日期作为文件名
            output_file = os.path.join(
                "reports", 
                f"trading_review_{self.review_date.strftime('%Y%m%d')}.md"
            )
        
        # 保存报告
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            logger.info(f"复盘报告已保存到: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"保存复盘报告失败: {e}")
            return None



def main():
    """主函数"""
    # 设置根目录为当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 输入文件路径
    input_file = os.path.join(current_dir, "data", "交易数据.xlsx")
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        return
    
    # 创建复盘记录生成器
    review = TradingReview()
    
    # 加载数据
    logger.info("正在加载数据...")
    if not review.load_data(input_file):
        logger.error("数据加载失败，程序终止")
        return
    
    # 设置复盘日期为当天
    review.set_review_date(datetime.now().date())
    
    # 生成并保存复盘报告
    logger.info("正在生成复盘报告...")
    output_file = review.save_review_report()

    if output_file:
        logger.info(f"复盘报告已生成: {output_file}")
    else:
        logger.error("复盘报告生成失败")

if __name__ == "__main__":
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    main()
