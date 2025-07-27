# -*- coding: utf-8 -*-
"""
项目配置设置
"""

import os
from datetime import datetime

# 项目基本信息
PROJECT_NAME = "交易数据分析系统"
VERSION = "1.0.0"

# 文件路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# 默认文件名
DEFAULT_DATA_FILE = "交易数据.xlsx"
DEFAULT_OUTPUT_FILE = f"交易分析结果_{datetime.now().strftime('%Y%m%d')}.xlsx"

# Excel工作表名称
SHEET_NAMES = {
    'TRADES': '交易数据',
    'RATES': '费率配置',
    'PRICES': '收盘价格',
    'SECURITIES': '证券信息',
    'DIVIDENDS': '分红记录',
    'PNL': '盈亏分析',
    'POSITIONS': '持仓数据',
    'DETAILS': '交易明细'
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(LOGS_DIR, f'trading_{datetime.now().strftime("%Y%m%d")}.log')
}

# Streamlit配置
STREAMLIT_CONFIG = {
    'page_title': '交易数据分析仪表盘',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# 数据验证配置
VALIDATION_CONFIG = {
    'required_columns': {
        'trades': ['日期', '证券代码', '证券名称', '买卖方向', '成交价格', '成交数量'],
        'rates': ['券商', '市场', '产品类型', '手续费率', '印花税率'],
        'prices': ['日期', '证券代码', '收盘价']
    },
    'date_format': '%Y-%m-%d',
    'numeric_columns': ['成交价格', '成交数量', '收盘价', '手续费率', '印花税率']
}

# 费率默认值
DEFAULT_RATES = {
    '手续费率': 0.0003,
    '规费率': 0.00002,
    '印花税率': 0.001,
    '过户费率': 0.00002,
    '最低手续费': 5.0,
    '平台使用费': 0.0,
    '结算费': 0.0,
    '汇率费': 0.0,
    '监管费': 0.0
}

# 确保必要目录存在
for directory in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)