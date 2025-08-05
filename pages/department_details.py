"""
部门详情分析页面
部门销售回款历史对比分析
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
    """显示部门详情分析页面"""
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    # 页面标题
    st.markdown('<h1 class="section-title fade-in">🏢 部门详情分析</h1>', unsafe_allow_html=True)

    history_files = state_manager.get_history_files()
    if len(history_files) < 2:
        st.error("需要至少2个月份的数据才能进行部门对比分析")
        return

    # 显示部门详情分析
    display_department_details(history_files)


def display_department_details(history_files):
    """显示部门详情分析"""
    st.markdown("### 🏢 部门销售回款历史对比")

    # 获取所有部门列表
    all_departments = set()
    for month_key, file_info in history_files.items():
        if file_info['department_sales_df'] is not None and '部门' in file_info['department_sales_df'].columns:
            departments = [str(d) for d in file_info['department_sales_df']['部门'].unique()
                           if pd.notna(d) and str(d) != '合计']
            all_departments.update(departments)

    if not all_departments:
        st.error("没有找到部门数据，请确保上传的Excel文件包含'部门销售回款统计'工作表")
        return

    # 部门选择
    department_list = sorted(list(all_departments), key=lambda x: str(x).lower())
    default_depts = department_list[:min(3, len(department_list))]
    selected_departments = st.multiselect(
        "选择要对比的部门",
        options=department_list,
        default=default_depts
    )

    if not selected_departments:
        st.info("请选择至少一个部门进行对比")
        return

    # 准备部门数据
    dept_data = prepare_department_data(history_files, selected_departments)
    
    if not dept_data:
        st.info("没有找到所选部门的历史数据")
        return

    # 创建部门趋势DataFrame
    dept_trend_df = pd.DataFrame(dept_data)
    
    # 按部门和月份排序
    dept_trend_df = sort_department_data(dept_trend_df)
    
    # 计算环比增长率
    dept_trend_df = calculate_department_growth_rate(dept_trend_df)

    # 显示部门历史对比图表（包含对应的数据汇总表）
    display_department_charts(dept_trend_df)

    # 显示热力图
    display_department_heatmap(dept_trend_df)

    # 数据下载功能
    csv = dept_trend_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 下载部门数据(CSV)",
        data=csv,
        file_name=f"部门销售回款历史数据_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_dept_data"
    )


def prepare_department_data(history_files, selected_departments):
    """准备部门数据"""
    dept_data = []
    
    # 按月份排序
    def extract_year_month(key):
        year_match = re.search(r'(\d{4})年', key)
        month_match = re.search(r'年(\d{1,2})月', key)
        year = year_match.group(1) if year_match else '0000'
        month = month_match.group(1) if month_match else '00'
        if len(month) == 1:
            month = '0' + month
        return year + month

    try:
        sorted_months = sorted(history_files.keys(), key=extract_year_month)
    except Exception:
        sorted_months = list(history_files.keys())

    for month_key in sorted_months:
        file_info = history_files[month_key]
        if file_info['department_sales_df'] is not None:
            dept_df = file_info['department_sales_df']
            for dept in selected_departments:
                dept_row = dept_df[dept_df['部门'] == dept]
                if not dept_row.empty:
                    sales_amount = dept_row['本月销售额'].iloc[0] / 10000 if '本月销售额' in dept_row.columns else 0
                    
                    payment_amount = 0
                    if '本月回未超期款' in dept_row.columns and '本月回超期款' in dept_row.columns:
                        payment_amount = (dept_row['本月回未超期款'].iloc[0] + dept_row['本月回超期款'].iloc[0]) / 10000
                    
                    overdue_amount = dept_row['月末逾期未收回额'].iloc[0] / 10000 if '月末逾期未收回额' in dept_row.columns else 0

                    dept_data.append({
                        '月份': month_key,
                        '部门': dept,
                        '销售额(万元)': sales_amount,
                        '回款额(万元)': payment_amount,
                        '逾期未收回额(万元)': overdue_amount
                    })
    
    return dept_data


def display_department_charts(dept_trend_df):
    """显示部门对比图表"""
    st.markdown("### 📈 部门销售回款历史对比")
    
    # 1. 部门销售额趋势图
    fig_dept_sales = px.line(
        dept_trend_df, x='月份', y='销售额(万元)', color='部门',
        markers=True, title='部门销售额月度变化趋势',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_dept_sales.update_layout(
        height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig_dept_sales.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig_dept_sales.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    st.plotly_chart(fig_dept_sales, use_container_width=True)
    
    # 销售额数据汇总表
    st.markdown("### 📋 部门月度数据汇总表（销售额）")
    display_specific_metric_table(dept_trend_df, '销售额(万元)')

    # 2. 部门回款额趋势图
    fig_dept_payment = px.line(
        dept_trend_df, x='月份', y='回款额(万元)', color='部门',
        markers=True, title='部门回款额月度变化趋势',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_dept_payment.update_layout(
        height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig_dept_payment.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig_dept_payment.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    st.plotly_chart(fig_dept_payment, use_container_width=True)
    
    # 回款额数据汇总表
    st.markdown("### 📋 部门月度数据汇总表（回款额）")
    display_specific_metric_table(dept_trend_df, '回款额(万元)')

    # 3. 部门逾期未收回额趋势图
    fig_dept_overdue = px.line(
        dept_trend_df, x='月份', y='逾期未收回额(万元)', color='部门',
        markers=True, title='部门逾期未收回额月度变化趋势',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_dept_overdue.update_layout(
        height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig_dept_overdue.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig_dept_overdue.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    st.plotly_chart(fig_dept_overdue, use_container_width=True)
    
    # 逾期未收回额数据汇总表
    st.markdown("### 📋 部门月度数据汇总表（逾期未收回额）")
    display_specific_metric_table(dept_trend_df, '逾期未收回额(万元)')


def display_department_heatmap(dept_trend_df):
    """显示部门销售额热力图"""
    st.markdown("### 🌡️ 部门销售额热力图")
    
    # 将数据透视为宽格式
    pivot_sales = dept_trend_df.pivot_table(
        values='销售额(万元)',
        index='部门',
        columns='月份'
    ).fillna(0)

    fig_heatmap = px.imshow(
        pivot_sales,
        text_auto=True,
        color_continuous_scale='Blues',
        labels=dict(x="月份", y="部门", color="销售额(万元)")
    )

    fig_heatmap.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)


def display_specific_metric_table(df, metric_column):
    """显示特定指标的数据汇总表"""
    # 提取相关列
    growth_column = f"{metric_column}环比增长率"
    columns_to_show = ['月份', '部门', metric_column]
    
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


def sort_department_data(df):
    """按部门分组，组内按年月排序"""
    if df.empty:
        return df
    
    def extract_year_month_for_sort(month_str):
        """提取年月用于排序"""
        year_match = re.search(r'(\d{4})年', str(month_str))
        month_match = re.search(r'年(\d{1,2})月', str(month_str))
        year = year_match.group(1) if year_match else '0000'
        month = month_match.group(1) if month_match else '00'
        if len(month) == 1:
            month = '0' + month
        return year + month
    
    # 添加排序用的年月列
    df['年月排序'] = df['月份'].apply(extract_year_month_for_sort)
    
    # 按部门和年月排序
    df = df.sort_values(['部门', '年月排序']).reset_index(drop=True)
    
    # 删除临时排序列
    df = df.drop('年月排序', axis=1)
    
    return df


def calculate_department_growth_rate(df):
    """为每个部门计算环比增长率"""
    if df.empty:
        return df
    
    df = df.copy()
    growth_columns = ['销售额(万元)', '回款额(万元)', '逾期未收回额(万元)']
    
    # 为每个部门分别计算增长率
    for department in df['部门'].unique():
        dept_mask = df['部门'] == department
        dept_indices = df[dept_mask].index
        
        for col in growth_columns:
            growth_col = f"{col}环比增长率"
            if growth_col not in df.columns:
                df[growth_col] = ""
            
            dept_data = df.loc[dept_indices, col]
            growth_rates = dept_data.pct_change() * 100
            
            # 第一行设为空值
            growth_rates.iloc[0] = None
            
            # 格式化为百分比字符串
            growth_rates = growth_rates.apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
            
            df.loc[dept_indices, growth_col] = growth_rates
    
    return df


def display_styled_department_dataframe(df):
    """显示带条件格式的部门数据表"""
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