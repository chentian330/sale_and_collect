"""
员工详情分析页面
员工销售回款历史对比分析
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
    """显示员工详情分析页面"""
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    # 页面标题
    st.markdown('<h1 class="section-title fade-in">👥 员工详情分析</h1>', unsafe_allow_html=True)

    history_files = state_manager.get_history_files()
    if len(history_files) < 2:
        st.error("需要至少2个月份的数据才能进行员工对比分析")
        return

    # 显示员工详情分析
    display_employee_details(history_files)


def display_employee_details(history_files):
    """显示员工详情分析"""
    st.markdown("### 👥 员工销售回款历史对比")

    # 获取所有员工列表
    all_employees = set()
    for month_key, file_info in history_files.items():
        if file_info['sales_df'] is not None and '员工姓名' in file_info['sales_df'].columns:
            employees = [str(emp) for emp in file_info['sales_df']['员工姓名'].unique() if pd.notna(emp)]
            all_employees.update(employees)

    if not all_employees:
        st.error("没有找到员工数据，请确保上传的Excel文件包含销售回款数据")
        return

    # 员工选择
    employee_list = sorted(list(all_employees), key=lambda x: str(x).lower())
    selected_employees = st.multiselect(
        "选择要对比的员工",
        options=employee_list,
        default=[employee_list[0]] if employee_list else []
    )

    if not selected_employees:
        st.info("请选择至少一个员工进行对比")
        return

    # 准备员工数据
    employee_data = prepare_employee_data(history_files, selected_employees)
    
    if not employee_data:
        st.info("没有找到所选员工的历史数据")
        return

    # 创建员工趋势DataFrame
    employee_trend_df = pd.DataFrame(employee_data)
    
    # 按员工和月份排序
    employee_trend_df = sort_employee_data(employee_trend_df)
    
    # 计算环比增长率
    employee_trend_df = calculate_employee_growth_rate(employee_trend_df)

    # 显示员工历史对比图表（包含对应的数据汇总表）
    display_employee_charts(employee_trend_df)

    # 显示员工销售能力雷达图对比
    if len(selected_employees) <= 5:
        display_employee_radar_chart(employee_trend_df)

    # 数据下载功能
    csv = employee_trend_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 下载员工数据(CSV)",
        data=csv,
        file_name=f"员工销售回款历史数据_{time.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="download_emp_data"
    )


def prepare_employee_data(history_files, selected_employees):
    """准备员工数据"""
    employee_data = []
    
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
        if file_info['sales_df'] is not None:
            sales_df = file_info['sales_df']
            for employee in selected_employees:
                emp_row = sales_df[sales_df['员工姓名'] == employee]
                if not emp_row.empty:
                    sales_amount = emp_row['本月销售额'].iloc[0] / 10000 if '本月销售额' in emp_row.columns else 0
                    payment_amount = emp_row['本月回款合计'].iloc[0] / 10000 if '本月回款合计' in emp_row.columns else 0
                    overdue_amount = emp_row['月末逾期未收回额'].iloc[0] / 10000 if '月末逾期未收回额' in emp_row.columns else 0

                    employee_data.append({
                        '月份': month_key,
                        '员工': employee,
                        '销售额(万元)': sales_amount,
                        '回款额(万元)': payment_amount,
                        '逾期未收回额(万元)': overdue_amount
                    })
    
    return employee_data


def display_employee_charts(employee_trend_df):
    """显示员工对比图表"""
    st.markdown("### 📈 员工销售回款历史对比")
    
    # 添加图例操作提示
    st.info("💡 提示：点击图例可以隐藏或显示对应的数据线")
    
    # 1. 员工销售额趋势图
    fig_emp_sales = px.line(
        employee_trend_df, x='月份', y='销售额(万元)', color='员工',
        markers=True, title='员工销售额月度变化趋势',
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_emp_sales.update_layout(
        height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    fig_emp_sales.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig_emp_sales.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    st.plotly_chart(fig_emp_sales, use_container_width=True)
    
    # 销售额数据汇总表
    st.markdown("### 📋 员工月度数据汇总表（销售额）")
    display_specific_employee_metric_table(employee_trend_df, '销售额(万元)')

    # 2. 员工回款额趋势图
    fig_emp_payment = px.line(
        employee_trend_df, x='月份', y='回款额(万元)', color='员工',
        markers=True, title='员工回款额月度变化趋势',
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_emp_payment.update_layout(
        height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    fig_emp_payment.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig_emp_payment.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    st.plotly_chart(fig_emp_payment, use_container_width=True)
    
    # 回款额数据汇总表
    st.markdown("### 📋 员工月度数据汇总表（回款额）")
    display_specific_employee_metric_table(employee_trend_df, '回款额(万元)')

    # 3. 员工逾期未收回额趋势图
    fig_emp_overdue = px.line(
        employee_trend_df, x='月份', y='逾期未收回额(万元)', color='员工',
        markers=True, title='员工逾期未收回额月度变化趋势',
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_emp_overdue.update_layout(
        height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    fig_emp_overdue.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig_emp_overdue.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    st.plotly_chart(fig_emp_overdue, use_container_width=True)
    
    # 逾期未收回额数据汇总表
    st.markdown("### 📋 员工月度数据汇总表（逾期未收回额）")
    display_specific_employee_metric_table(employee_trend_df, '逾期未收回额(万元)')


def display_employee_radar_chart(employee_trend_df):
    """显示员工销售能力雷达图对比"""
    st.markdown("### 🎯 员工销售能力雷达图对比")

    # 计算每个员工的平均值
    radar_data = employee_trend_df.groupby('员工').agg({
        '销售额(万元)': 'mean',
        '回款额(万元)': 'mean',
        '逾期未收回额(万元)': 'mean'
    }).reset_index()

    # 创建雷达图
    fig_radar = go.Figure()

    for employee in radar_data['员工']:
        fig_radar.add_trace(go.Scatterpolar(
            r=[
                radar_data.loc[radar_data['员工'] == employee, '销售额(万元)'].iloc[0],
                radar_data.loc[radar_data['员工'] == employee, '回款额(万元)'].iloc[0],
                -radar_data.loc[radar_data['员工'] == employee, '逾期未收回额(万元)'].iloc[0]  # 负值表示逾期越少越好
            ],
            theta=['销售额', '回款额', '逾期控制'],
            fill='toself',
            name=employee
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=False)),
        showlegend=True, height=450,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_radar, use_container_width=True)
    st.caption("注：逾期控制维度中，值越高表示逾期未收回额越低，表现越好")


def sort_employee_data(df):
    """按员工分组，组内按年月排序"""
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
    
    # 按员工和年月排序
    df = df.sort_values(['员工', '年月排序']).reset_index(drop=True)
    
    # 删除临时排序列
    df = df.drop('年月排序', axis=1)
    
    return df


def calculate_employee_growth_rate(df):
    """为每个员工计算环比增长率"""
    if df.empty:
        return df
    
    df = df.copy()
    growth_columns = ['销售额(万元)', '回款额(万元)', '逾期未收回额(万元)']
    
    # 为每个员工分别计算增长率
    for employee in df['员工'].unique():
        emp_mask = df['员工'] == employee
        emp_indices = df[emp_mask].index
        
        for col in growth_columns:
            growth_col = f"{col}环比增长率"
            if growth_col not in df.columns:
                df[growth_col] = ""
            
            emp_data = df.loc[emp_indices, col]
            growth_rates = emp_data.pct_change() * 100
            
            # 第一行设为空值
            growth_rates.iloc[0] = None
            
            # 格式化为百分比字符串
            growth_rates = growth_rates.apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
            
            df.loc[emp_indices, growth_col] = growth_rates
    
    return df


def display_styled_employee_dataframe(df):
    """显示带条件格式的员工数据表"""
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


def display_specific_employee_metric_table(df, metric_column):
    """显示特定指标的员工数据汇总表"""
    # 提取相关列
    growth_column = f"{metric_column}环比增长率"
    columns_to_show = ['月份', '员工', metric_column]
    
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