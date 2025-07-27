#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例数据文件
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_data():
    """创建示例数据文件"""
    print("正在创建示例数据文件...")
    
    # 设置根目录
    root_dir = r"D:\Ni_Trading"
    
    # 确保目录存在
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
        print(f"已创建目录: {root_dir}")
    
    # 创建交易数据
    trades_df = create_trades_data()
    
    # 创建费率配置
    rates_df = create_rates_data()
    
    # 创建收盘价格
    prices_df = create_prices_data()
    
    # 创建证券信息
    securities_df = create_securities_data()
    
    # 将所有数据保存到一个Excel文件中
    output_file = os.path.join(root_dir, '交易数据.xlsx')
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        trades_df.to_excel(writer, sheet_name='交易数据', index=False)
        rates_df.to_excel(writer, sheet_name='费率配置', index=False)
        prices_df.to_excel(writer, sheet_name='收盘价格', index=False)
        securities_df.to_excel(writer, sheet_name='证券信息', index=False)
    
    print(f"所有数据已保存到: {output_file}")
    print("示例数据文件创建完成！")

def create_trades_data():
    """创建交易数据示例"""
    # 生成日期序列
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(10)]
    
    # 证券信息
    securities = [
        ('000001', '平安银行', '深交所', '股票'),
        ('600036', '招商银行', '上交所', '股票'),
        ('159919', '300ETF', '深交所', 'ETF'),
        ('510300', '沪深300ETF', '上交所', 'ETF'),
        ('00700', '腾讯控股', '港交所', '港股'),
        ('AAPL', '苹果公司', '美股', '美股')
    ]
    
    # 生成交易数据
    trades_data = []
    
    for date in dates:
        # 每天随机选择1-3只证券进行交易
        num_trades = min(np.random.randint(1, 4), len(securities))
        # 使用随机索引而不是直接选择元组
        selected_indices = np.random.choice(len(securities), num_trades, replace=False)
        
        for idx in selected_indices:
            security = securities[idx]
            code, name, market, product_type = security
            
            # 随机决定买入或卖出
            direction = np.random.choice(['买入', '卖出'], p=[0.6, 0.4])
            
            # 随机生成价格和数量
            if market == '港交所':
                price = np.random.uniform(50, 500)
                quantity = np.random.randint(100, 1000)
            elif market == '美股':
                price = np.random.uniform(100, 500)
                quantity = np.random.randint(10, 100)
            else:
                price = np.random.uniform(5, 50)
                quantity = np.random.randint(100, 2000)
            
            # 随机选择券商
            broker = np.random.choice(['国泰君安', '华泰证券', '中信证券', '富途证券'])
            
            trades_data.append({
                '日期': date,
                '证券代码': code,
                '买卖方向': direction,
                '成交价格': round(price, 2),
                '成交数量': quantity,
                '券商': broker
            })
    
    # 创建DataFrame
    trades_df = pd.DataFrame(trades_data)
    print(f"已生成 {len(trades_df)} 条交易数据")
    return trades_df

def create_rates_data():
    """创建费率配置示例"""
    # 费率数据
    rates_data = [
        # 国泰君安
        {'券商': '国泰君安', '市场': '上交所', '产品类型': '股票', '手续费率': 0.0003, '印花税率': 0.001, '过户费率': 0.00002, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '国泰君安', '市场': '上交所', '产品类型': 'ETF', '手续费率': 0.0003, '印花税率': 0, '过户费率': 0.00002, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '国泰君安', '市场': '深交所', '产品类型': '股票', '手续费率': 0.0003, '印花税率': 0.001, '过户费率': 0, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '国泰君安', '市场': '深交所', '产品类型': 'ETF', '手续费率': 0.0003, '印花税率': 0, '过户费率': 0, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        
        # 华泰证券
        {'券商': '华泰证券', '市场': '上交所', '产品类型': '股票', '手续费率': 0.00025, '印花税率': 0.001, '过户费率': 0.00002, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '华泰证券', '市场': '上交所', '产品类型': 'ETF', '手续费率': 0.00025, '印花税率': 0, '过户费率': 0.00002, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '华泰证券', '市场': '深交所', '产品类型': '股票', '手续费率': 0.00025, '印花税率': 0.001, '过户费率': 0, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '华泰证券', '市场': '深交所', '产品类型': 'ETF', '手续费率': 0.00025, '印花税率': 0, '过户费率': 0, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        
        # 中信证券
        {'券商': '中信证券', '市场': '上交所', '产品类型': '股票', '手续费率': 0.0003, '印花税率': 0.001, '过户费率': 0.00002, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '中信证券', '市场': '上交所', '产品类型': 'ETF', '手续费率': 0.0003, '印花税率': 0, '过户费率': 0.00002, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '中信证券', '市场': '深交所', '产品类型': '股票', '手续费率': 0.0003, '印花税率': 0.001, '过户费率': 0, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        {'券商': '中信证券', '市场': '深交所', '产品类型': 'ETF', '手续费率': 0.0003, '印花税率': 0, '过户费率': 0, '最低手续费': 5, '平台使用费': 0, '结算费': 0, '汇率费': 0, '监管费': 0},
        
        # 富途证券
        {'券商': '富途证券', '市场': '港交所', '产品类型': '港股', '手续费率': 0.0008, '印花税率': 0.0013, '过户费率': 0, '最低手续费': 15, '平台使用费': 15, '结算费': 0.00005, '汇率费': 0.0001, '监管费': 0},
        {'券商': '富途证券', '市场': '美股', '产品类型': '美股', '手续费率': 0.0015, '印花税率': 0, '过户费率': 0, '最低手续费': 1, '平台使用费': 1, '结算费': 0.0001, '汇率费': 0.0001, '监管费': 0.00002}
    ]
    
    # 创建DataFrame
    rates_df = pd.DataFrame(rates_data)
    print(f"已生成 {len(rates_df)} 条费率配置")
    return rates_df

def create_prices_data():
    """创建收盘价格示例"""
    # 生成日期序列
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(15)]  # 多几天的价格数据
    
    # 证券信息
    securities = [
        ('000001', '平安银行'),
        ('600036', '招商银行'),
        ('159919', '300ETF'),
        ('510300', '沪深300ETF'),
        ('00700', '腾讯控股'),
        ('AAPL', '苹果公司')
    ]
    
    # 生成收盘价格数据
    prices_data = []
    
    for security in securities:
        code, name = security
        
        # 初始价格
        if code == '00700':
            base_price = 350.0
        elif code == 'AAPL':
            base_price = 180.0
        else:
            base_price = 10.0 + np.random.uniform(0, 20)
        
        for date in dates:
            # 随机波动价格
            price_change = np.random.uniform(-0.03, 0.03)
            price = base_price * (1 + price_change)
            base_price = price  # 更新基准价格
            
            # 随机有些日期没有收盘价（设为0或留空）
            if np.random.random() < 0.1:
                price = 0
            
            prices_data.append({
                '日期': date,
                '证券代码': code,
                '证券名称': name,
                '收盘价': round(price, 2)
            })
    
    # 创建DataFrame
    prices_df = pd.DataFrame(prices_data)
    print(f"已生成 {len(prices_df)} 条收盘价格数据")
    return prices_df

def create_securities_data():
    """创建证券信息示例"""
    # 证券信息数据
    securities_data = [
        {'证券代码': '000001', '证券名称': '平安银行', '交易所': '深交所'},
        {'证券代码': '600036', '证券名称': '招商银行', '交易所': '上交所'},
        {'证券代码': '159919', '证券名称': '300ETF', '交易所': '深交所'},
        {'证券代码': '510300', '证券名称': '沪深300ETF', '交易所': '上交所'},
        {'证券代码': '00700', '证券名称': '腾讯控股', '交易所': '港交所'},
        {'证券代码': 'AAPL', '证券名称': '苹果公司', '交易所': '美股'}
    ]
    
    # 创建DataFrame
    securities_df = pd.DataFrame(securities_data)
    print(f"已生成 {len(securities_df)} 条证券信息")
    return securities_df

if __name__ == "__main__":
    create_sample_data()