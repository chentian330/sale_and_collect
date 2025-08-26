"""
总体趋势分析页面
月度销售回款总体趋势对比分析
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import time
from components.navigation import navigation
from core.state_manager import state_manager


def show():
    """显示总体趋势分析页面"""
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    # 页面标题
    st.markdown('<h1 class="section-title fade-in">📈 总体趋势分析</h1>', unsafe_allow_html=True)

    history_files = state_manager.get_history_files()
    if len(history_files) < 2:
        st.error("需要至少2个月份的数据才能进行趋势分析")
        return

    # 显示总体趋势分析
    display_overall_trends(history_files)


def display_overall_trends(history_files):
    """显示总体趋势分析"""
    st.markdown("### 📊 月度销售回款趋势分析")

    # 准备数据
    trend_data = []

    # 自定义排序函数，按年月排序
    def extract_year_month(key):
        year_match = re.search(r'(\d{4})年', key)
        month_match = re.search(r'年(\d{1,2})月', key)
        year = year_match.group(1) if year_match else '0000'
        month = month_match.group(1) if month_match else '00'
        if len(month) == 1:
            month = '0' + month
        return year + month

    # 按月份排序
    try:
        sorted_months = sorted(history_files.keys(), key=extract_year_month)
    except Exception:
        sorted_months = list(history_files.keys())

    for month_key in sorted_months:
        file_info = history_files[month_key]

        # 计算各项指标 - 使用合计行数据
        total_sales = 0
        total_payment = 0
        total_overdue = 0
        
        if file_info['sales_df'] is not None:
            sales_df = file_info['sales_df']
            
            # 查找合计行（员工姓名列为"合计"的行）
            if '员工姓名' in sales_df.columns:
                total_row = sales_df[sales_df['员工姓名'] == '合计']
                
                if not total_row.empty:
                    # 获取合计行的各项数据
                    if '本月销售额' in sales_df.columns:
                        total_sales_value = total_row['本月销售额'].iloc[0]
                        if pd.notna(total_sales_value):
                            total_sales = float(total_sales_value) / 10000
                    
                    if '本月回款合计' in sales_df.columns:
                        total_payment_value = total_row['本月回款合计'].iloc[0]
                        if pd.notna(total_payment_value):
                            total_payment = float(total_payment_value) / 10000
                    
                    if '月末逾期未收回额' in sales_df.columns:
                        total_overdue_value = total_row['月末逾期未收回额'].iloc[0]
                        if pd.notna(total_overdue_value):
                            total_overdue = float(total_overdue_value) / 10000

        trend_data.append({
            '月份': month_key,
            '总销售额(万元)': total_sales,
            '总回款额(万元)': total_payment,
            '总逾期未收回额(万元)': total_overdue
        })

    # 创建趋势DataFrame
    trend_df = pd.DataFrame(trend_data)
    
    # 计算环比增长率
    trend_df = calculate_growth_rate(trend_df)

    # 显示趋势图表
    if len(trend_df) >= 2:
        st.markdown("### 📈 总体趋势分析")
        
        # 添加图例操作提示
        st.info("💡 提示：点击图例可以隐藏或显示对应的数据线")
        
        # 1. 总销售额月度变化趋势
        fig_sales = px.line(
            trend_df, x='月份', y='总销售额(万元)',
            markers=True, title='总销售额月度变化趋势',
            color_discrete_sequence=['#0A84FF']
        )
        fig_sales.update_layout(
            height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        fig_sales.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
        fig_sales.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig_sales, use_container_width=True)
        
        # 销售额数据汇总表
        st.markdown("### 📋 月度数据汇总表（总销售额）")
        display_specific_metric_table(trend_df, '总销售额(万元)')

        # 2. 总回款额月度变化趋势
        fig_payment = px.line(
            trend_df, x='月份', y='总回款额(万元)',
            markers=True, title='总回款额月度变化趋势',
            color_discrete_sequence=['#BF5AF2']
        )
        fig_payment.update_layout(
            height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        fig_payment.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
        fig_payment.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig_payment, use_container_width=True)
        
        # 回款额数据汇总表
        st.markdown("### 📋 月度数据汇总表（总回款额）")
        display_specific_metric_table(trend_df, '总回款额(万元)')

        # 3. 总逾期未收回额月度变化趋势
        fig_overdue = px.line(
            trend_df, x='月份', y='总逾期未收回额(万元)',
            markers=True, title='总逾期未收回额月度变化趋势',
            color_discrete_sequence=['#FF453A']
        )
        fig_overdue.update_layout(
            height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        fig_overdue.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
        fig_overdue.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig_overdue, use_container_width=True)
        
        # 逾期未收回额数据汇总表
        st.markdown("### 📋 月度数据汇总表（总逾期未收回额）")
        display_specific_metric_table(trend_df, '总逾期未收回额(万元)')

        # 数据下载功能
        csv = trend_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下载总体趋势数据(CSV)",
            data=csv,
            file_name=f"销售回款总体趋势数据_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_trend_data"
        )
    else:
        st.info("需要至少2个月份的数据才能显示趋势图")


def calculate_growth_rate(df):
    """计算环比增长率"""
    df = df.copy()
    
    # 为需要计算增长率的列添加环比增长率列
    growth_columns = ['总销售额(万元)', '总回款额(万元)', '总逾期未收回额(万元)']
    
    for col in growth_columns:
        growth_col = f"{col}环比增长率"
        df[growth_col] = df[col].pct_change() * 100
        # 第一行设为空值
        df.loc[0, growth_col] = None
        # 格式化为百分比字符串
        df[growth_col] = df[growth_col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    
    return df


def display_styled_dataframe(df):
    """显示带条件格式的数据表"""
    def apply_growth_color(val):
        """为增长率列应用颜色格式"""
        if val == "" or pd.isna(val):
            return ""
        try:
            # 提取数值部分
            num_val = float(val.replace('%', ''))
            if num_val > 0:
                return "color: green; font-weight: bold"
            else:
                return "color: red; font-weight: bold"
        except:
            return ""
    
    # 获取环比增长率列
    growth_columns = [col for col in df.columns if '环比增长率' in col]
    
    # 应用样式
    styled_df = df.style
    for col in growth_columns:
        styled_df = styled_df.applymap(apply_growth_color, subset=[col])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def display_specific_metric_table(df, metric_column):
    """显示特定指标的数据汇总表"""
    # 提取相关列
    growth_column = f"{metric_column}环比增长率"
    columns_to_show = ['月份', metric_column]
    
    if growth_column in df.columns:
        columns_to_show.append(growth_column)
    
    # 创建显示用的数据框
    display_df = df[columns_to_show].copy()
    
    def apply_growth_color(val):
        """为增长率列应用颜色格式"""
        if val == "" or pd.isna(val):
            return ""
        try:
            # 提取数值部分
            num_val = float(val.replace('%', ''))
            if num_val > 0:
                return "color: green; font-weight: bold"
            else:
                return "color: red; font-weight: bold"
        except:
            return ""
    
    # 应用样式
    styled_df = display_df.style
    if growth_column in display_df.columns:
        styled_df = styled_df.applymap(apply_growth_color, subset=[growth_column])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True) 