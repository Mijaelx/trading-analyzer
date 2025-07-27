#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易数据可视化界面
基于Streamlit构建的交易数据和分红记录可视化界面
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trading_processor import TradingProcessor, DividendRecord
from core.trading_review import TradingReview

# 设置页面配置
st.set_page_config(
    page_title="交易数据分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e78;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1f4e78;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-text {
        color: #555;
        font-size: 1rem;
    }
    .highlight {
        background-color: #e6f2ff;
        padding: 0.5rem;
        border-radius: 0.3rem;
    }
    .profit {
        color: #006600;
        font-weight: bold;
    }
    .loss {
        color: #cc0000;
        font-weight: bold;
    }
    .centered {
        text-align: center;
    }
    .dashboard-container {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "概览"

# 主标题
st.markdown('<h1 class="main-header">交易数据分析仪表盘</h1>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("数据加载")
    
    # 文件上传
    uploaded_file = st.file_uploader("上传交易数据Excel文件", type=["xlsx"])
    
    if uploaded_file is not None:
        # 使用临时文件名，避免覆盖原始文件
        temp_file_path = os.path.join("data", f"temp_upload_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        
        # 确保data目录存在
        os.makedirs("data", exist_ok=True)
        
        # 保存上传的文件到临时位置
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 加载数据
        if st.button("加载数据"):
            with st.spinner("正在加载数据..."):
                # 创建交易数据处理器
                processor = TradingProcessor()
                
                # 加载数据
                if processor.load_data(temp_file_path):
                    # 处理数据
                    if processor.process_data():
                        st.session_state.processor = processor
                        st.session_state.data_loaded = True
                        st.success("数据加载成功！")
                    else:
                        st.error("数据处理失败！")
                else:
                    st.error("数据加载失败！")
                
                # 加载完成后删除临时文件
                try:
                    os.remove(temp_file_path)
                    st.info(f"临时文件已删除，原始文件未被修改")
                except:
                    pass
    
    # 导航菜单
    st.header("导航")
    tabs = ["概览", "持仓分析", "交易明细", "盈亏分析", "分红记录", "数据可视化", "交易复盘"]
    selected_tab = st.radio("选择页面", tabs)
    st.session_state.current_tab = selected_tab
    
    # 添加分红记录
    if st.session_state.data_loaded:
        st.header("添加分红记录")
        with st.form("add_dividend_form"):
            col1, col2 = st.columns(2)
            with col1:
                dividend_date = st.date_input("分红日期", datetime.now())
                symbol = st.text_input("证券代码")
                name = st.text_input("证券名称")
            with col2:
                shares = st.number_input("持有数量", min_value=0, value=100)
                dividend_per_share = st.number_input("每股分红", min_value=0.0, value=0.1, format="%.4f")
                tax = st.number_input("税费", min_value=0.0, value=0.0, format="%.2f")
            
            remark = st.text_input("备注")
            submitted = st.form_submit_button("添加分红记录")
            
            if submitted and st.session_state.processor:
                if st.session_state.processor.add_dividend_record(
                    dividend_date, symbol, name, shares, dividend_per_share, tax, remark
                ):
                    st.success(f"成功添加 {name}({symbol}) 的分红记录")
                else:
                    st.error("添加分红记录失败")

# 主内容区域
if not st.session_state.data_loaded:
    st.info("请先上传交易数据Excel文件并点击'加载数据'按钮")
else:
    processor = st.session_state.processor
    
    # 概览页面
    if st.session_state.current_tab == "概览":
        st.markdown('<h2 class="sub-header">交易数据概览</h2>', unsafe_allow_html=True)
        
        # 获取数据
        positions_df = processor.get_current_positions()
        stock_pnl_df = processor.get_stock_historical_pnl()
        dividend_summary = processor.get_dividend_summary()
        
        # 创建概览指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="持仓股票数量", 
                value=len(positions_df) if not positions_df.empty else 0
            )
        
        with col2:
            total_market_value = positions_df['持仓市值'].sum() if not positions_df.empty else 0
            st.metric(
                label="总持仓市值", 
                value=f"{total_market_value:,.2f}"
            )
        
        with col3:
            total_pnl = stock_pnl_df['总盈亏'].sum() if not stock_pnl_df.empty else 0
            delta = f"{total_pnl/total_market_value*100:.2f}%" if total_market_value > 0 else "0.00%"
            st.metric(
                label="总盈亏", 
                value=f"{total_pnl:,.2f}",
                delta=delta,
                delta_color="normal" if total_pnl >= 0 else "inverse"
            )
        
        with col4:
            total_dividend = dividend_summary.get('净分红金额', 0)
            st.metric(
                label="总分红金额", 
                value=f"{total_dividend:,.2f}"
            )
        
        # 持仓分布饼图
        if not positions_df.empty:
            st.markdown('<h3 class="sub-header">持仓分布</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 按市值分布
                fig = px.pie(
                    positions_df, 
                    values='持仓市值', 
                    names='证券名称',
                    title='持仓市值分布',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 按盈亏分布
                if '总盈亏' in stock_pnl_df.columns:
                    profit_stocks = stock_pnl_df[stock_pnl_df['总盈亏'] > 0]
                    loss_stocks = stock_pnl_df[stock_pnl_df['总盈亏'] < 0]
                    
                    profit_loss_df = pd.DataFrame([
                        {'类型': '盈利股票', '数量': len(profit_stocks), '金额': profit_stocks['总盈亏'].sum()},
                        {'类型': '亏损股票', '数量': len(loss_stocks), '金额': abs(loss_stocks['总盈亏'].sum())}
                    ])
                    
                    fig = px.pie(
                        profit_loss_df, 
                        values='金额', 
                        names='类型',
                        title='盈亏分布',
                        hole=0.4,
                        color_discrete_sequence=['#4CAF50', '#F44336']
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        
        # 最近交易
        if processor.trades_df is not None and not processor.trades_df.empty:
            st.markdown('<h3 class="sub-header">最近交易</h3>', unsafe_allow_html=True)
            
            recent_trades = processor.trades_df.sort_values('日期', ascending=False).head(5)
            
            # 格式化显示
            recent_trades_display = recent_trades.copy()
            recent_trades_display['日期'] = recent_trades_display['日期'].dt.strftime('%Y-%m-%d')
            recent_trades_display['成交价格'] = recent_trades_display['成交价格'].map('{:.4f}'.format)
            recent_trades_display['交易金额'] = recent_trades_display['交易金额'].map('{:,.2f}'.format)
            recent_trades_display['总费用'] = recent_trades_display['总费用'].map('{:.2f}'.format)
            
            # 只显示部分列
            columns_to_show = ['日期', '证券代码', '证券名称', '买卖方向', '成交价格', '成交数量', '交易金额', '总费用']
            st.dataframe(recent_trades_display[columns_to_show], use_container_width=True)
    
    # 持仓分析页面
    elif st.session_state.current_tab == "持仓分析":
        st.markdown('<h2 class="sub-header">持仓分析</h2>', unsafe_allow_html=True)
        
        # 获取持仓数据
        positions_df = processor.get_current_positions()
        
        if positions_df.empty:
            st.info("当前没有持仓数据")
        else:
            # 持仓概览
            total_market_value = positions_df['持仓市值'].sum()
            total_cost = positions_df['持仓成本总额'].sum()
            unrealized_pnl = total_market_value - total_cost
            pnl_ratio = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="持仓股票数量", 
                    value=len(positions_df)
                )
            
            with col2:
                st.metric(
                    label="总持仓市值", 
                    value=f"{total_market_value:,.2f}"
                )
            
            with col3:
                st.metric(
                    label="总持仓成本", 
                    value=f"{total_cost:,.2f}"
                )
            
            with col4:
                st.metric(
                    label="未实现盈亏", 
                    value=f"{unrealized_pnl:,.2f}",
                    delta=f"{pnl_ratio:.2f}%",
                    delta_color="normal" if unrealized_pnl >= 0 else "inverse"
                )
            
            # 持仓明细表格
            st.markdown('<h3 class="sub-header">持仓明细</h3>', unsafe_allow_html=True)
            
            # 格式化显示
            positions_display = positions_df.copy()
            
            # 添加盈亏列（如果没有）
            if '未实现盈亏' not in positions_display.columns:
                positions_display['未实现盈亏'] = positions_display['持仓市值'] - positions_display['持仓成本总额']
            
            if '盈亏比例(%)' not in positions_display.columns:
                positions_display['盈亏比例(%)'] = positions_display.apply(
                    lambda x: (x['未实现盈亏'] / x['持仓成本总额'] * 100) if x['持仓成本总额'] > 0 else 0, 
                    axis=1
                )
            
            # 格式化数字列
            numeric_cols = ['持仓成本价', '当前价格', '平均买入价', '平均卖出价']
            for col in numeric_cols:
                if col in positions_display.columns:
                    positions_display[col] = positions_display[col].map('{:.4f}'.format)
            
            money_cols = ['持仓市值', '持仓成本总额', '未实现盈亏', '买入手续费', '卖出手续费', '总手续费']
            for col in money_cols:
                if col in positions_display.columns:
                    positions_display[col] = positions_display[col].map('{:,.2f}'.format)
            
            if '盈亏比例(%)' in positions_display.columns:
                positions_display['盈亏比例(%)'] = positions_display['盈亏比例(%)'].map('{:.2f}%'.format)
            
            # 选择要显示的列
            columns_to_show = [
                '证券代码', '证券名称', '持仓数量', '持仓成本价', '当前价格', 
                '持仓市值', '持仓成本总额', '未实现盈亏', '盈亏比例(%)', 
                '交易次数', '持有天数'
            ]
            
            # 确保所有列都存在
            columns_to_show = [col for col in columns_to_show if col in positions_display.columns]
            
            # 显示表格
            st.dataframe(positions_display[columns_to_show], use_container_width=True)
            
            # 持仓市值分布图
            st.markdown('<h3 class="sub-header">持仓市值分布</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 按市值排序的条形图
                positions_sorted = positions_df.sort_values('持仓市值', ascending=False)
                
                fig = px.bar(
                    positions_sorted,
                    x='证券名称',
                    y='持仓市值',
                    title='持仓市值分布',
                    color='证券名称',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(xaxis_title="", yaxis_title="市值", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 盈亏分布图
                if '未实现盈亏' not in positions_df.columns:
                    positions_df['未实现盈亏'] = positions_df['持仓市值'] - positions_df['持仓成本总额']
                
                positions_sorted = positions_df.sort_values('未实现盈亏')
                
                colors = ['#4CAF50' if x >= 0 else '#F44336' for x in positions_sorted['未实现盈亏']]
                
                fig = px.bar(
                    positions_sorted,
                    x='证券名称',
                    y='未实现盈亏',
                    title='持仓盈亏分布',
                    color='证券名称',
                    color_discrete_sequence=colors
                )
                fig.update_layout(xaxis_title="", yaxis_title="未实现盈亏", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # 交易明细页面
    elif st.session_state.current_tab == "交易明细":
        st.markdown('<h2 class="sub-header">交易明细</h2>', unsafe_allow_html=True)
        
        if processor.trades_df is None or processor.trades_df.empty:
            st.info("没有交易数据")
        else:
            # 交易统计
            trades_df = processor.trades_df
            
            # 买入和卖出交易
            buy_trades = trades_df[~trades_df['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
            sell_trades = trades_df[trades_df['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
            
            # 交易统计
            total_buy_amount = (buy_trades['成交价格'] * buy_trades['成交数量']).sum()
            total_sell_amount = (sell_trades['成交价格'] * sell_trades['成交数量']).sum()
            total_buy_fee = buy_trades['总费用'].sum()
            total_sell_fee = sell_trades['总费用'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="总交易次数", 
                    value=len(trades_df)
                )
            
            with col2:
                st.metric(
                    label="总买入金额", 
                    value=f"{total_buy_amount:,.2f}"
                )
            
            with col3:
                st.metric(
                    label="总卖出金额", 
                    value=f"{total_sell_amount:,.2f}"
                )
            
            with col4:
                st.metric(
                    label="总手续费", 
                    value=f"{total_buy_fee + total_sell_fee:,.2f}"
                )
            
            # 交易过滤器
            st.markdown('<h3 class="sub-header">交易过滤</h3>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # 按证券代码或名称过滤
                search_term = st.text_input("搜索证券代码或名称", "")
            
            with col2:
                # 按交易方向过滤
                direction_options = ["全部", "买入", "卖出"]
                selected_direction = st.selectbox("交易方向", direction_options)
            
            with col3:
                # 按日期范围过滤
                date_range = st.date_input(
                    "日期范围",
                    [
                        trades_df['日期'].min().date(),
                        trades_df['日期'].max().date()
                    ]
                )
            
            # 应用过滤器
            filtered_trades = trades_df.copy()
            
            # 按证券代码或名称过滤
            if search_term:
                filtered_trades = filtered_trades[
                    filtered_trades['证券代码'].str.contains(search_term) | 
                    filtered_trades['证券名称'].str.contains(search_term)
                ]
            
            # 按交易方向过滤
            if selected_direction == "买入":
                filtered_trades = filtered_trades[~filtered_trades['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
            elif selected_direction == "卖出":
                filtered_trades = filtered_trades[filtered_trades['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
            
            # 按日期范围过滤
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_trades = filtered_trades[
                    (filtered_trades['日期'].dt.date >= start_date) & 
                    (filtered_trades['日期'].dt.date <= end_date)
                ]
            
            # 显示过滤后的交易明细
            st.markdown('<h3 class="sub-header">交易明细表格</h3>', unsafe_allow_html=True)
            
            # 格式化显示
            trades_display = filtered_trades.copy()
            trades_display['日期'] = trades_display['日期'].dt.strftime('%Y-%m-%d')
            trades_display['成交价格'] = trades_display['成交价格'].map('{:.4f}'.format)
            trades_display['交易金额'] = trades_display['交易金额'].map('{:,.2f}'.format)
            
            fee_cols = ['手续费', '规费', '印花税', '过户费', '总费用']
            for col in fee_cols:
                if col in trades_display.columns:
                    trades_display[col] = trades_display[col].map('{:.2f}'.format)
            
            # 选择要显示的列
            columns_to_show = [
                '日期', '证券代码', '证券名称', '买卖方向', '成交价格', 
                '成交数量', '交易金额', '手续费', '印花税', '总费用'
            ]
            
            # 确保所有列都存在
            columns_to_show = [col for col in columns_to_show if col in trades_display.columns]
            
            # 显示表格
            st.dataframe(trades_display[columns_to_show], use_container_width=True)
            
            # 交易趋势图
            st.markdown('<h3 class="sub-header">交易趋势</h3>', unsafe_allow_html=True)
            
            # 按日期汇总交易
            daily_trades = trades_df.copy()
            daily_trades['日期'] = daily_trades['日期'].dt.date
            daily_trades['买入金额'] = daily_trades.apply(
                lambda x: x['成交价格'] * x['成交数量'] if x['买卖方向'] not in ['卖出', '卖', 'SELL', 'S'] else 0, 
                axis=1
            )
            daily_trades['卖出金额'] = daily_trades.apply(
                lambda x: x['成交价格'] * x['成交数量'] if x['买卖方向'] in ['卖出', '卖', 'SELL', 'S'] else 0, 
                axis=1
            )
            
            daily_summary = daily_trades.groupby('日期').agg({
                '买入金额': 'sum',
                '卖出金额': 'sum',
                '总费用': 'sum'
            }).reset_index()
            
            # 创建趋势图
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=daily_summary['日期'],
                y=daily_summary['买入金额'],
                name='买入金额',
                marker_color='#FF9999'
            ))
            
            fig.add_trace(go.Bar(
                x=daily_summary['日期'],
                y=daily_summary['卖出金额'],
                name='卖出金额',
                marker_color='#99CC99'
            ))
            
            fig.add_trace(go.Scatter(
                x=daily_summary['日期'],
                y=daily_summary['总费用'],
                name='总费用',
                marker_color='#666666',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='每日交易金额和费用',
                xaxis_title='日期',
                yaxis_title='交易金额',
                yaxis2=dict(
                    title='费用',
                    overlaying='y',
                    side='right'
                ),
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 盈亏分析页面
    elif st.session_state.current_tab == "盈亏分析":
        st.markdown('<h2 class="sub-header">盈亏分析</h2>', unsafe_allow_html=True)
        
        # 获取股票历史盈亏数据
        stock_pnl_df = processor.get_stock_historical_pnl()
        
        if stock_pnl_df.empty:
            st.info("没有盈亏数据")
        else:
            # 盈亏概览
            total_realized_pnl = stock_pnl_df['已实现盈亏'].sum()
            total_unrealized_pnl = stock_pnl_df['未实现盈亏'].sum()
            total_pnl = stock_pnl_df['总盈亏'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="交易股票数量", 
                    value=len(stock_pnl_df)
                )
            
            with col2:
                st.metric(
                    label="已实现盈亏", 
                    value=f"{total_realized_pnl:,.2f}",
                    delta=f"{total_realized_pnl/abs(total_realized_pnl)*100:.2f}%" if total_realized_pnl != 0 else "0.00%",
                    delta_color="normal" if total_realized_pnl >= 0 else "inverse"
                )
            
            with col3:
                st.metric(
                    label="未实现盈亏", 
                    value=f"{total_unrealized_pnl:,.2f}",
                    delta=f"{total_unrealized_pnl/abs(total_unrealized_pnl)*100:.2f}%" if total_unrealized_pnl != 0 else "0.00%",
                    delta_color="normal" if total_unrealized_pnl >= 0 else "inverse"
                )
            
            with col4:
                st.metric(
                    label="总盈亏", 
                    value=f"{total_pnl:,.2f}",
                    delta=f"{total_pnl/abs(total_pnl)*100:.2f}%" if total_pnl != 0 else "0.00%",
                    delta_color="normal" if total_pnl >= 0 else "inverse"
                )
            
            # 盈亏明细表格
            st.markdown('<h3 class="sub-header">股票盈亏明细</h3>', unsafe_allow_html=True)
            
            # 格式化显示
            pnl_display = stock_pnl_df.copy()
            
            # 格式化数字列
            price_cols = ['当前成本价', '当前价格', '平均买入价', '平均卖出价']
            for col in price_cols:
                if col in pnl_display.columns:
                    pnl_display[col] = pnl_display[col].map('{:.4f}'.format)
            
            money_cols = ['当前市值', '已实现盈亏', '未实现盈亏', '总盈亏', '买入手续费', '卖出手续费', '总手续费']
            for col in money_cols:
                if col in pnl_display.columns:
                    pnl_display[col] = pnl_display[col].map('{:,.2f}'.format)
            
            if '盈亏比例(%)' in pnl_display.columns:
                pnl_display['盈亏比例(%)'] = pnl_display['盈亏比例(%)'].map('{:.2f}%'.format)
            
            # 选择要显示的列
            columns_to_show = [
                '证券代码', '证券名称', '当前持仓数量', '当前成本价', '当前价格', 
                '当前市值', '已实现盈亏', '未实现盈亏', '总盈亏', '盈亏比例(%)', 
                '交易次数', '总手续费'
            ]
            
            # 确保所有列都存在
            columns_to_show = [col for col in columns_to_show if col in pnl_display.columns]
            
            # 显示表格
            st.dataframe(pnl_display[columns_to_show], use_container_width=True)
            
            # 盈亏分布图
            st.markdown('<h3 class="sub-header">盈亏分布</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 总盈亏排名
                pnl_sorted = stock_pnl_df.sort_values('总盈亏')
                
                colors = ['#4CAF50' if x >= 0 else '#F44336' for x in pnl_sorted['总盈亏']]
                
                fig = px.bar(
                    pnl_sorted,
                    x='证券名称',
                    y='总盈亏',
                    title='股票总盈亏排名',
                    color='证券名称',
                    color_discrete_sequence=colors
                )
                fig.update_layout(xaxis_title="", yaxis_title="总盈亏", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 盈亏比例分布
                if '盈亏比例(%)' in stock_pnl_df.columns:
                    pnl_ratio_sorted = stock_pnl_df.sort_values('盈亏比例(%)')
                    
                    colors = ['#4CAF50' if x >= 0 else '#F44336' for x in pnl_ratio_sorted['盈亏比例(%)']]
                    
                    fig = px.bar(
                        pnl_ratio_sorted,
                        x='证券名称',
                        y='盈亏比例(%)',
                        title='股票盈亏比例排名',
                        color='证券名称',
                        color_discrete_sequence=colors
                    )
                    fig.update_layout(xaxis_title="", yaxis_title="盈亏比例(%)", height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    # 分红记录页面
    elif st.session_state.current_tab == "分红记录":
        st.markdown('<h2 class="sub-header">分红记录</h2>', unsafe_allow_html=True)
        
        # 获取分红记录
        dividend_records = processor.get_dividend_records()
        dividend_summary = processor.get_dividend_summary()
        
        # 分红概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="分红记录数量", 
                value=dividend_summary.get('总记录数', 0)
            )
        
        with col2:
            st.metric(
                label="总分红金额", 
                value=f"{dividend_summary.get('总分红金额', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                label="总税费", 
                value=f"{dividend_summary.get('总税费', 0):,.2f}"
            )
        
        with col4:
            st.metric(
                label="净分红金额", 
                value=f"{dividend_summary.get('净分红金额', 0):,.2f}"
            )
        
        # 分红记录表格
        st.markdown('<h3 class="sub-header">分红记录明细</h3>', unsafe_allow_html=True)
        
        if dividend_records.empty:
            st.info("没有分红记录")
        else:
            # 格式化显示
            dividend_display = dividend_records.copy()
            
            # 格式化日期列
            if '日期' in dividend_display.columns:
                dividend_display['日期'] = pd.to_datetime(dividend_display['日期']).dt.strftime('%Y-%m-%d')
            
            # 格式化金额列
            money_cols = ['每股分红', '总分红金额', '税费', '净分红金额']
            for col in money_cols:
                if col in dividend_display.columns:
                    dividend_display[col] = dividend_display[col].map('{:,.4f}'.format)
            
            # 显示表格
            st.dataframe(dividend_display, use_container_width=True)
            
            # 分红趋势图
            if len(dividend_records) > 1:
                st.markdown('<h3 class="sub-header">分红趋势</h3>', unsafe_allow_html=True)
                
                # 按日期汇总分红
                dividend_records['日期'] = pd.to_datetime(dividend_records['日期'])
                dividend_records['年月'] = dividend_records['日期'].dt.strftime('%Y-%m')
                
                monthly_dividends = dividend_records.groupby('年月').agg({
                    '总分红金额': 'sum',
                    '税费': 'sum',
                    '净分红金额': 'sum'
                }).reset_index()
                
                # 创建趋势图
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=monthly_dividends['年月'],
                    y=monthly_dividends['净分红金额'],
                    name='净分红金额',
                    marker_color='#4CAF50'
                ))
                
                fig.add_trace(go.Bar(
                    x=monthly_dividends['年月'],
                    y=monthly_dividends['税费'],
                    name='税费',
                    marker_color='#F44336'
                ))
                
                fig.update_layout(
                    title='月度分红趋势',
                    xaxis_title='年月',
                    yaxis_title='金额',
                    barmode='stack',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 按证券汇总分红
                stock_dividends = dividend_records.groupby(['证券代码', '证券名称']).agg({
                    '总分红金额': 'sum',
                    '税费': 'sum',
                    '净分红金额': 'sum'
                }).reset_index()
                
                # 创建饼图
                fig = px.pie(
                    stock_dividends,
                    values='净分红金额',
                    names='证券名称',
                    title='各股票分红占比',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
    
    # 数据可视化页面
    elif st.session_state.current_tab == "数据可视化":
        st.markdown('<h2 class="sub-header">数据可视化</h2>', unsafe_allow_html=True)
        
        # 获取数据
        positions_df = processor.get_current_positions()
        stock_pnl_df = processor.get_stock_historical_pnl()
        trades_df = processor.trades_df
        dividend_records = processor.get_dividend_records()
        
        # 选择可视化类型
        viz_type = st.selectbox(
            "选择可视化类型",
            ["持仓分析", "盈亏分析", "交易分析", "分红分析"]
        )
        
        if viz_type == "持仓分析" and not positions_df.empty:
            # 持仓分析可视化
            st.markdown('<h3 class="sub-header">持仓分析可视化</h3>', unsafe_allow_html=True)
            
            # 持仓市值树状图
            fig = px.treemap(
                positions_df,
                path=['证券名称'],
                values='持仓市值',
                color='持仓市值',
                color_continuous_scale='Blues',
                title='持仓市值树状图'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # 持仓成本与市值对比
            positions_compare = positions_df.copy()
            positions_compare = positions_compare.sort_values('持仓市值', ascending=False)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=positions_compare['证券名称'],
                y=positions_compare['持仓市值'],
                name='当前市值',
                marker_color='#4CAF50'
            ))
            
            fig.add_trace(go.Bar(
                x=positions_compare['证券名称'],
                y=positions_compare['持仓成本总额'],
                name='持仓成本',
                marker_color='#2196F3'
            ))
            
            fig.update_layout(
                title='持仓成本与市值对比',
                xaxis_title='',
                yaxis_title='金额',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "盈亏分析" and not stock_pnl_df.empty:
            # 盈亏分析可视化
            st.markdown('<h3 class="sub-header">盈亏分析可视化</h3>', unsafe_allow_html=True)
            
            # 盈亏瀑布图
            pnl_waterfall = stock_pnl_df.sort_values('总盈亏', ascending=False).head(10)
            
            fig = go.Figure(go.Waterfall(
                name="盈亏瀑布图",
                orientation="v",
                measure=["relative"] * len(pnl_waterfall),
                x=pnl_waterfall['证券名称'],
                y=pnl_waterfall['总盈亏'],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": "#4CAF50"}},
                decreasing={"marker": {"color": "#F44336"}}
            ))
            
            fig.update_layout(
                title="前10只股票盈亏瀑布图",
                xaxis_title="",
                yaxis_title="总盈亏",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 已实现与未实现盈亏对比
            pnl_compare = stock_pnl_df.copy()
            pnl_compare = pnl_compare.sort_values('总盈亏', ascending=False)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=pnl_compare['证券名称'],
                y=pnl_compare['已实现盈亏'],
                name='已实现盈亏',
                marker_color='#4CAF50'
            ))
            
            fig.add_trace(go.Bar(
                x=pnl_compare['证券名称'],
                y=pnl_compare['未实现盈亏'],
                name='未实现盈亏',
                marker_color='#2196F3'
            ))
            
            fig.update_layout(
                title='已实现与未实现盈亏对比',
                xaxis_title='',
                yaxis_title='盈亏金额',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 盈亏比例散点图
            if '盈亏比例(%)' in stock_pnl_df.columns:
                fig = px.scatter(
                    stock_pnl_df,
                    x='总盈亏',
                    y='盈亏比例(%)',
                    size='当前市值',
                    color='证券名称',
                    hover_name='证券名称',
                    title='盈亏金额与比例散点图'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "交易分析" and trades_df is not None and not trades_df.empty:
            # 交易分析可视化
            st.markdown('<h3 class="sub-header">交易分析可视化</h3>', unsafe_allow_html=True)
            
            # 交易频率热力图
            trades_df['日期'] = pd.to_datetime(trades_df['日期'])
            trades_df['星期'] = trades_df['日期'].dt.day_name()
            trades_df['小时'] = trades_df['日期'].dt.hour
            
            # 创建交易频率数据
            trade_counts = trades_df.groupby(['星期', '小时']).size().reset_index(name='交易次数')
            
            # 确保所有星期和小时都有数据
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hours = list(range(24))
            
            # 创建完整的索引
            idx = pd.MultiIndex.from_product([weekdays, hours], names=['星期', '小时'])
            trade_counts = trade_counts.set_index(['星期', '小时']).reindex(idx, fill_value=0).reset_index()
            
            # 创建热力图
            fig = px.density_heatmap(
                trade_counts,
                x='小时',
                y='星期',
                z='交易次数',
                title='交易频率热力图',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # 交易金额趋势图
            trades_df['月份'] = trades_df['日期'].dt.strftime('%Y-%m')
            
            monthly_trades = trades_df.groupby('月份').agg({
                '交易金额': 'sum',
                '总费用': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_trades['月份'],
                y=monthly_trades['交易金额'],
                mode='lines+markers',
                name='交易金额',
                line=dict(color='#2196F3', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_trades['月份'],
                y=monthly_trades['总费用'],
                mode='lines+markers',
                name='总费用',
                line=dict(color='#F44336', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='月度交易金额与费用趋势',
                xaxis_title='月份',
                yaxis_title='交易金额',
                yaxis2=dict(
                    title='费用',
                    overlaying='y',
                    side='right'
                ),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "分红分析" and not dividend_records.empty:
            # 分红分析可视化
            st.markdown('<h3 class="sub-header">分红分析可视化</h3>', unsafe_allow_html=True)
            
            # 分红金额趋势图
            dividend_records['日期'] = pd.to_datetime(dividend_records['日期'])
            dividend_records['月份'] = dividend_records['日期'].dt.strftime('%Y-%m')
            
            monthly_dividends = dividend_records.groupby('月份').agg({
                '总分红金额': 'sum',
                '税费': 'sum',
                '净分红金额': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_dividends['月份'],
                y=monthly_dividends['净分红金额'],
                mode='lines+markers',
                name='净分红金额',
                line=dict(color='#4CAF50', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_dividends['月份'],
                y=monthly_dividends['税费'],
                mode='lines+markers',
                name='税费',
                line=dict(color='#F44336', width=2)
            ))
            
            fig.update_layout(
                title='月度分红金额趋势',
                xaxis_title='月份',
                yaxis_title='金额',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 分红股票占比
            stock_dividends = dividend_records.groupby('证券名称').agg({
                '净分红金额': 'sum'
            }).reset_index()
            
            fig = px.pie(
                stock_dividends,
                values='净分红金额',
                names='证券名称',
                title='各股票分红占比',
                color_discrete_sequence=px.colors.sequential.Greens
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("没有足够的数据进行可视化")
            
    # 交易复盘页面
    elif st.session_state.current_tab == "交易复盘":
        st.markdown('<h2 class="sub-header">交易复盘</h2>', unsafe_allow_html=True)
        
        # 创建复盘记录生成器
        review = TradingReview(processor=processor)
        
        # 日期选择
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_date = st.date_input(
                "选择复盘日期",
                value=datetime.now().date(),
                min_value=(datetime.now() - timedelta(days=365)).date(),
                max_value=datetime.now().date()
            )
        
        # 设置复盘日期
        review.set_review_date(selected_date)
        
        with col2:
            # 生成复盘报告按钮
            if st.button("生成复盘报告", type="primary"):
                with st.spinner("正在生成复盘报告..."):
                    # 确保reports目录存在
                    os.makedirs("reports", exist_ok=True)
                    
                    # 生成复盘报告
                    report_path = review.save_review_report()
                    
                    if report_path:
                        st.success(f"复盘报告已生成: {report_path}")
                        
                        # 读取报告内容
                        with open(report_path, "r", encoding="utf-8") as f:
                            report_content = f.read()
                        
                        # 显示下载按钮
                        st.download_button(
                            label="下载复盘报告",
                            data=report_content,
                            file_name=f"trading_review_{selected_date.strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error("复盘报告生成失败")
        
        # 复盘数据预览
        st.markdown('<h3 class="sub-header">复盘数据预览</h3>', unsafe_allow_html=True)
        
        # 获取当天交易记录
        daily_trades = review.get_daily_trades()
        daily_pnl = review.get_daily_pnl()
        daily_dividends = review.get_daily_dividends()
        
        # 创建三个标签页
        tab1, tab2, tab3 = st.tabs(["当日交易", "当日盈亏", "当日分红"])
        
        with tab1:
            if daily_trades.empty:
                st.info(f"{selected_date.strftime('%Y-%m-%d')} 没有交易记录")
            else:
                # 格式化显示
                trades_display = daily_trades.copy()
                trades_display['日期'] = trades_display['日期'].dt.strftime('%Y-%m-%d')
                trades_display['成交价格'] = trades_display['成交价格'].map('{:.4f}'.format)
                trades_display['交易金额'] = trades_display['交易金额'].map('{:,.2f}'.format)
                
                fee_cols = ['手续费', '规费', '印花税', '过户费', '总费用']
                for col in fee_cols:
                    if col in trades_display.columns:
                        trades_display[col] = trades_display[col].map('{:.2f}'.format)
                
                # 选择要显示的列
                columns_to_show = [
                    '证券代码', '证券名称', '买卖方向', '成交价格', 
                    '成交数量', '交易金额', '总费用'
                ]
                
                # 确保所有列都存在
                columns_to_show = [col for col in columns_to_show if col in trades_display.columns]
                
                # 显示表格
                st.dataframe(trades_display[columns_to_show], use_container_width=True)
                
                # 交易统计
                buy_trades = daily_trades[~daily_trades['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
                sell_trades = daily_trades[daily_trades['买卖方向'].isin(['卖出', '卖', 'SELL', 'S'])]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="买入笔数", 
                        value=len(buy_trades)
                    )
                
                with col2:
                    st.metric(
                        label="卖出笔数", 
                        value=len(sell_trades)
                    )
                
                with col3:
                    st.metric(
                        label="总交易金额", 
                        value=f"{daily_trades['交易金额'].sum():,.2f}"
                    )
        
        with tab2:
            if daily_pnl.empty:
                st.info(f"{selected_date.strftime('%Y-%m-%d')} 没有盈亏记录")
            else:
                # 盈亏统计
                realized_pnl = daily_pnl['当日已实现盈亏'].sum()
                unrealized_pnl = daily_pnl['当日未实现盈亏'].sum()
                total_pnl = realized_pnl + unrealized_pnl
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="已实现盈亏", 
                        value=f"{realized_pnl:,.2f}",
                        delta_color="normal" if realized_pnl >= 0 else "inverse"
                    )
                
                with col2:
                    st.metric(
                        label="未实现盈亏", 
                        value=f"{unrealized_pnl:,.2f}",
                        delta_color="normal" if unrealized_pnl >= 0 else "inverse"
                    )
                
                with col3:
                    st.metric(
                        label="总盈亏", 
                        value=f"{total_pnl:,.2f}",
                        delta_color="normal" if total_pnl >= 0 else "inverse"
                    )
                
                # 格式化显示
                pnl_display = daily_pnl.copy()
                
                # 格式化数字列
                price_cols = ['持仓成本价', '收盘价']
                for col in price_cols:
                    if col in pnl_display.columns:
                        pnl_display[col] = pnl_display[col].map('{:.4f}'.format)
                
                money_cols = ['持仓市值', '持仓成本总额', '当日已实现盈亏', '当日未实现盈亏']
                for col in money_cols:
                    if col in pnl_display.columns:
                        pnl_display[col] = pnl_display[col].map('{:,.2f}'.format)
                
                # 选择要显示的列
                columns_to_show = [
                    '证券代码', '证券名称', '持仓数量', '持仓成本价', '收盘价', 
                    '当日已实现盈亏', '当日未实现盈亏'
                ]
                
                # 确保所有列都存在
                columns_to_show = [col for col in columns_to_show if col in pnl_display.columns]
                
                # 显示表格
                st.dataframe(pnl_display[columns_to_show], use_container_width=True)
                
                # 盈亏分布图
                st.markdown('<h4 class="sub-header">当日盈亏分布</h4>', unsafe_allow_html=True)
                
                # 计算每只股票的总盈亏
                pnl_data = []
                for _, row in daily_pnl.iterrows():
                    pnl_data.append({
                        '证券名称': row['证券名称'],
                        '总盈亏': row['当日已实现盈亏'] + row['当日未实现盈亏']
                    })
                
                pnl_df = pd.DataFrame(pnl_data)
                pnl_sorted = pnl_df.sort_values('总盈亏')
                
                colors = ['#4CAF50' if x >= 0 else '#F44336' for x in pnl_sorted['总盈亏']]
                
                fig = px.bar(
                    pnl_sorted,
                    x='证券名称',
                    y='总盈亏',
                    title='当日股票盈亏分布',
                    color='证券名称',
                    color_discrete_sequence=colors
                )
                fig.update_layout(xaxis_title="", yaxis_title="总盈亏", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if daily_dividends.empty:
                st.info(f"{selected_date.strftime('%Y-%m-%d')} 没有分红记录")
            else:
                # 分红统计
                total_dividend = daily_dividends['总分红金额'].sum()
                total_tax = daily_dividends['税费'].sum()
                net_dividend = daily_dividends['净分红金额'].sum()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="分红记录数", 
                        value=len(daily_dividends)
                    )
                
                with col2:
                    st.metric(
                        label="总分红金额", 
                        value=f"{total_dividend:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="净分红金额", 
                        value=f"{net_dividend:,.2f}"
                    )
                
                # 格式化显示
                dividend_display = daily_dividends.copy()
                
                # 格式化日期列
                if '日期' in dividend_display.columns:
                    dividend_display['日期'] = pd.to_datetime(dividend_display['日期']).dt.strftime('%Y-%m-%d')
                
                # 格式化金额列
                money_cols = ['每股分红', '总分红金额', '税费', '净分红金额']
                for col in money_cols:
                    if col in dividend_display.columns:
                        dividend_display[col] = dividend_display[col].map('{:,.4f}'.format)
                
                # 显示表格
                st.dataframe(dividend_display, use_container_width=True)
                
                # 分红分布图
                st.markdown('<h4 class="sub-header">分红分布</h4>', unsafe_allow_html=True)
                
                fig = px.pie(
                    daily_dividends,
                    values='净分红金额',
                    names='证券名称',
                    title='当日分红分布',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
        
        # 复盘报告预览
        st.markdown('<h3 class="sub-header">复盘报告预览</h3>', unsafe_allow_html=True)
        
        # 生成复盘报告（不保存）
        report_content = review.generate_review_report()
        
        # 显示报告预览
        st.markdown(report_content)

        # 页脚
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding-t
            <p>交易数据分析仪表盘 © 2025</p>
        </div>
        """, unsml=True)

# 运行说明
if __name__ == "__main":
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    main()