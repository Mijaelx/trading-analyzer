#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易数据分析系统主入口
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.trading_processor import TradingProcessor
from core.trading_review import TradingReview


def process_trading_data(input_file, output_file=None):
    """处理交易数据"""
    processor = TradingProcessor()
    
    if not processor.load_data(input_file):
        print("❌ 数据加载失败")
        return False
    
    if not processor.calculate_fees():
        print("❌ 费用计算失败")
        return False
    
    if not processor.calculate_pnl():
        print("❌ 盈亏计算失败")
        return False
    
    # 生成输出文件名
    if not output_file:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"reports/{base_name}_分析结果_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if processor.save_results(output_file):
        print(f"✅ 分析结果已保存到: {output_file}")
        return True
    else:
        print("❌ 结果保存失败")
        return False


def generate_review(date_str=None):
    """生成交易复盘报告"""
    review = TradingReview()
    
    # 加载数据
    data_file = "data/交易数据.xlsx"
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return False
    
    if not review.load_data(data_file):
        print("❌ 数据加载失败")
        return False
    
    # 设置复盘日期
    if date_str:
        try:
            review_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            review.set_review_date(review_date)
        except ValueError:
            print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
            return False
    
    # 生成复盘报告
    report_file = f"reports/trading_review_{review.review_date.strftime('%Y%m%d')}.md"
    os.makedirs("reports", exist_ok=True)
    
    if review.generate_review_report(report_file):
        print(f"✅ 复盘报告已生成: {report_file}")
        return True
    else:
        print("❌ 复盘报告生成失败")
        return False


def start_dashboard():
    """启动可视化仪表盘"""
    import subprocess
    import sys
    
    try:
        subprocess.run([sys.executable, "run_dashboard.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动仪表盘失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 仪表盘已关闭")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="交易数据分析系统")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 处理交易数据命令
    process_parser = subparsers.add_parser('process', help='处理交易数据')
    process_parser.add_argument('input', help='输入Excel文件路径')
    process_parser.add_argument('-o', '--output', help='输出文件路径')
    
    # 生成复盘报告命令
    review_parser = subparsers.add_parser('review', help='生成交易复盘报告')
    review_parser.add_argument('-d', '--date', help='复盘日期 (YYYY-MM-DD)')
    
    # 启动仪表盘命令
    subparsers.add_parser('dashboard', help='启动可视化仪表盘')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        return process_trading_data(args.input, args.output)
    elif args.command == 'review':
        return generate_review(args.date)
    elif args.command == 'dashboard':
        return start_dashboard()
    else:
        parser.print_help()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)