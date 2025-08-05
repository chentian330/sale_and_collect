"""
员工销售回款统计页面
查看员工销售回款详细统计
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from html import escape
from components.navigation import navigation
from components.ui_components import UIComponents
from core.state_manager import state_manager


def show():
    """显示员工销售回款统计页面"""
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    # 加载CSS样式
    UIComponents.load_css()
    
    # 检查数据
    sales_df = state_manager.get_data('sales_df')
    
    if sales_df is None:
        st.error("请先上传销售回款数据文件")
        return
    
    st.markdown('<h1 style="text-align: center; font-family: \'SF Pro Display\', sans-serif;">员工销售回款统计</h1>',
                unsafe_allow_html=True)
    
    # 显示销售回款概览
    if sales_df is not None:
        display_sales_overview(sales_df)
        display_weekly_analysis(sales_df)
    
    # 显示成就徽章
    display_achievement_badges(sales_df)
    
    # 显示员工销售回款详情
    display_sales_employee_details(sales_df)


def display_sales_overview(sales_df):
    """显示销售概览"""
    if sales_df is None or sales_df.empty:
        return

    st.markdown('<h3 class="section-title fade-in">📊 销售回款概览</h3>', unsafe_allow_html=True)

    # 排除合计行
    filtered_df = sales_df[sales_df['员工姓名'] != '合计'].copy()
    filtered_df = filtered_df[filtered_df['员工姓名'].notna()]

    # 直接使用Excel中的数据，不重新计算
    # 将金额从元转换为万元用于显示
    total_sales = filtered_df['本月销售额'].sum() / 10000
    total_payment = filtered_df['本月回款合计'].sum() / 10000
    avg_sales = filtered_df['本月销售额'].mean() / 10000
    avg_payment = filtered_df['本月回款合计'].mean() / 10000

    # 直接使用Excel中的完成进度数据
    if '销售业绩完成进度' in filtered_df.columns:
        avg_sales_progress = filtered_df['销售业绩完成进度'].mean() * 100
        progress_delta = f"{avg_sales_progress - 100:.1f}%" if avg_sales_progress >= 100 else f"{avg_sales_progress - 100:.1f}%"
        sales_delta_color = "normal" if avg_sales_progress >= 100 else "inverse"
    else:
        avg_sales_progress = None
        progress_delta = None
        sales_delta_color = "off"

    if '回款业绩完成进度' in filtered_df.columns:
        avg_payment_progress = filtered_df['回款业绩完成进度'].mean() * 100
        payment_progress_delta = f"{avg_payment_progress - 100:.1f}%" if avg_payment_progress >= 100 else f"{avg_payment_progress - 100:.1f}%"
        payment_delta_color = "normal" if avg_payment_progress >= 100 else "inverse"
    else:
        avg_payment_progress = None
        payment_progress_delta = None
        payment_delta_color = "off"

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 销售数据")
        sale_cols = st.columns(3)
        with sale_cols[0]:
            st.metric("总销售额(万元)", f"{total_sales:,.2f}", help="本月所有员工销售额总和", delta_color="off")
        with sale_cols[1]:
            st.metric("平均销售额(万元)", f"{avg_sales:,.2f}", help="本月员工平均销售额", delta_color="off")

        if avg_sales_progress is not None:
            with sale_cols[2]:
                st.metric("平均销售任务完成率", f"{avg_sales_progress:.1f}%",
                          progress_delta, delta_color=sales_delta_color,
                          help="销售额/销售任务的平均完成比例")

    with col2:
        st.markdown("#### 回款数据")
        payment_cols = st.columns(3)
        with payment_cols[0]:
            st.metric("总回款额(万元)", f"{total_payment:,.2f}", help="本月所有员工回款额总和", delta_color="off")
        with payment_cols[1]:
            st.metric("平均回款额(万元)", f"{avg_payment:,.2f}", help="本月员工平均回款额", delta_color="off")

        if avg_payment_progress is not None:
            with payment_cols[2]:
                st.metric("平均回款任务完成率", f"{avg_payment_progress:.1f}%",
                          payment_progress_delta, delta_color=payment_delta_color,
                          help="回款额/回款任务的平均完成比例")

    # 进度分布统计（以表格形式展示）
    if '销售业绩完成进度' in filtered_df.columns or '回款业绩完成进度' in filtered_df.columns:
        st.markdown("#### 业绩完成进度分布")
        
        # 销售业绩完成进度分布表格
        if '销售业绩完成进度' in filtered_df.columns:
            st.markdown("##### 销售业绩完成进度")
            
            # 按完成率分类员工
            excellent_employees = []  # >=100%
            good_employees = []       # 66%-99%
            need_effort_employees = [] # <66%
            
            for _, row in filtered_df.iterrows():
                progress = row.get('销售业绩完成进度', 0)
                name = row.get('员工姓名', '')
                
                if pd.notna(progress) and pd.notna(name):
                    if progress >= 1.0:
                        excellent_employees.append(name)
                    elif progress >= 0.66:
                        good_employees.append(name)
                    else:
                        need_effort_employees.append(name)
            
            # 创建三列表格
            progress_cols = st.columns(3)
            
            with progress_cols[0]:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #30D158, #34C759); border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">已达成</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">大于等于100%完成率</p>
                </div>
                """, unsafe_allow_html=True)
                
                if excellent_employees:
                    for emp in excellent_employees:
                        st.markdown(f"✅ {emp}")
                else:
                    st.markdown("*暂无*")
            
            with progress_cols[1]:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #FFD60A, #FF9F0A); border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">良好达成</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">66-99%完成率</p>
                </div>
                """, unsafe_allow_html=True)
                
                if good_employees:
                    for emp in good_employees:
                        st.markdown(f"🟡 {emp}")
                else:
                    st.markdown("*暂无*")
            
            with progress_cols[2]:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #FF453A, #FF6B6B); border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">须努力</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">小于66%完成率</p>
                </div>
                """, unsafe_allow_html=True)
                
                if need_effort_employees:
                    for emp in need_effort_employees:
                        st.markdown(f"🔴 {emp}")
                else:
                    st.markdown("*暂无*")

        # 回款业绩完成进度分布表格
        if '回款业绩完成进度' in filtered_df.columns:
            st.markdown("##### 回款业绩完成进度")
            
            # 按完成率分类员工
            excellent_employees = []  # >=100%
            good_employees = []       # 66%-99%
            need_effort_employees = [] # <66%
            
            for _, row in filtered_df.iterrows():
                progress = row.get('回款业绩完成进度', 0)
                name = row.get('员工姓名', '')
                
                if pd.notna(progress) and pd.notna(name):
                    if progress >= 1.0:
                        excellent_employees.append(name)
                    elif progress >= 0.66:
                        good_employees.append(name)
                    else:
                        need_effort_employees.append(name)
            
            # 创建三列表格
            progress_cols = st.columns(3)
            
            with progress_cols[0]:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #30D158, #34C759); border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">已达成</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">大于等于100%完成率</p>
                </div>
                """, unsafe_allow_html=True)
                
                if excellent_employees:
                    for emp in excellent_employees:
                        st.markdown(f"✅ {emp}")
                else:
                    st.markdown("*暂无*")
            
            with progress_cols[1]:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #FFD60A, #FF9F0A); border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">良好达成</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">66-99%完成率</p>
                </div>
                """, unsafe_allow_html=True)
                
                if good_employees:
                    for emp in good_employees:
                        st.markdown(f"🟡 {emp}")
                else:
                    st.markdown("*暂无*")
            
            with progress_cols[2]:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #FF453A, #FF6B6B); border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="color: white; margin: 0; font-weight: 600;">须努力</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">小于66%完成率</p>
                </div>
                """, unsafe_allow_html=True)
                
                if need_effort_employees:
                    for emp in need_effort_employees:
                        st.markdown(f"🔴 {emp}")
                else:
                    st.markdown("*暂无*")




def display_weekly_analysis(sales_df):
    """显示周分析"""
    if sales_df is None or sales_df.empty:
        return

    st.markdown('<h3 class="section-title fade-in">📅 周数据分析</h3>', unsafe_allow_html=True)

    # 排除合计行
    filtered_df = sales_df[sales_df['员工姓名'] != '合计'].copy()
    filtered_df = filtered_df[filtered_df['员工姓名'].notna()]

    # 动态检测所有周数据
    week_pattern = r'第(\d+)周销售额'
    available_weeks = []
    for col in filtered_df.columns:
        match = re.match(week_pattern, col)
        if match:
            week_num = int(match.group(1))
            available_weeks.append(week_num)
    
    available_weeks = sorted(set(available_weeks))

    if available_weeks:
        # 使用Excel中原始数据，只转换单位
        weekly_totals = {}
        for week_num in available_weeks:
            sales_col = f'第{week_num}周销售额'
            payment_col = f'第{week_num}周回款合计'
            if sales_col in filtered_df.columns and payment_col in filtered_df.columns:
                weekly_totals[f'第{week_num}周'] = {
                    '销售额(万元)': filtered_df[sales_col].sum() / 10000,
                    '回款额(万元)': filtered_df[payment_col].sum() / 10000
                }
        
        if weekly_totals:
            weeks = list(weekly_totals.keys())
            sales_values = [weekly_totals[week]['销售额(万元)'] for week in weeks]
            payment_values = [weekly_totals[week]['回款额(万元)'] for week in weeks]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=weeks, y=sales_values, mode='lines+markers',
                name='周销售额', line=dict(color='#0A84FF', width=3.5),
                marker=dict(size=10, color='#0A84FF')
            ))
            fig.add_trace(go.Scatter(
                x=weeks, y=payment_values, mode='lines+markers',
                name='周回款额', line=dict(color='#BF5AF2', width=3.5),
                marker=dict(size=10, color='#BF5AF2')
            ))
            fig.update_layout(
                title='各周销售与回款趋势（单位：万元）',
                xaxis_title='周次',
                yaxis_title='金额（万元）',
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1D1D1F'),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            fig.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
            fig.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**各周销售额汇总**")
                week_sales_data = []
                for week, data in weekly_totals.items():
                    formatted_sales = UIComponents.format_amount(data['销售额(万元)'])
                    week_sales_data.append({
                        '周次': week,
                        '销售额': formatted_sales
                    })
                week_sales_df = pd.DataFrame(week_sales_data)
                st.dataframe(week_sales_df, use_container_width=True, hide_index=True)
            with col2:
                st.markdown("**各周回款额汇总**")
                week_payment_data = []
                for week, data in weekly_totals.items():
                    formatted_payment = UIComponents.format_amount(data['回款额(万元)'])
                    week_payment_data.append({
                        '周次': week,
                        '回款额': formatted_payment
                    })
                week_payment_df = pd.DataFrame(week_payment_data)
                st.dataframe(week_payment_df, use_container_width=True, hide_index=True)
    else:
        st.info("当前数据中没有周数据信息")


def get_progress_color(progress):
    """根据完成进度获取颜色"""
    if progress >= 1.0:
        return "#30D158"  # 绿色
    elif progress >= 0.66:
        return "#FFD60A"  # 黄色
    else:
        return "#FF453A"  # 红色


def display_achievement_badges(sales_df):
    """显示成就徽章"""
    if sales_df is None or sales_df.empty:
        return
        
    st.markdown('<h3 class="section-title fade-in">🏆 本月成就徽章</h3>', unsafe_allow_html=True)
    
    # 排除合计行
    filtered_df = sales_df[sales_df['员工姓名'] != '合计'].copy()
    filtered_df = filtered_df[filtered_df['员工姓名'].notna()]
    
    # Apple风格成就卡片样式
    st.markdown("""
    <style>
    .achievement-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 12px;
        padding: 32px 24px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        margin: 8px 0;
        position: relative;
    }
    
    .achievement-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border-color: rgba(0,0,0,0.08);
    }
    
    .achievement-card.gold {
        border-top: 3px solid #ff9f0a;
    }
    
    .achievement-card.silver {
        border-top: 3px solid #007aff;
    }
    
    .achievement-card.bronze {
        border-top: 3px solid #ff6b35;
    }
    
    .badge-icon {
        font-size: 2.5rem;
        margin-bottom: 16px;
        display: block;
        opacity: 0.9;
    }
    
    .badge-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        letter-spacing: -0.01em;
    }
    
    .badge-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1d1d1f;
        margin-bottom: 4px;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        letter-spacing: -0.02em;
    }
    
    .badge-value {
        font-size: 0.9rem;
        font-weight: 400;
        color: #86868b;
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
        letter-spacing: -0.01em;
    }
    
    .badge-category {
        position: absolute;
        top: 12px;
        right: 16px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        opacity: 0.6;
    }
    
    .badge-category.gold {
        background: #ff9f0a;
    }
    
    .badge-category.silver {
        background: #007aff;
    }
    
    .badge-category.bronze {
        background: #ff6b35;
    }
    </style>
    """, unsafe_allow_html=True)

    # 创建成就徽章
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 销售冠军
        if '本月销售额' in filtered_df.columns:
            top_sales = filtered_df.loc[filtered_df['本月销售额'].idxmax()]
            st.markdown(f"""
            <div class="achievement-card gold">
                <div class="badge-category gold"></div>
                <div class="badge-icon">👑</div>
                <div class="badge-title">销售冠军</div>
                <div class="badge-name">{escape(str(top_sales['员工姓名']))}</div>
                <div class="badge-value">{top_sales['本月销售额']:,.0f} 元</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="achievement-card gold">
                <div class="badge-category gold"></div>
                <div class="badge-icon">👑</div>
                <div class="badge-title">销售冠军</div>
                <div class="badge-name">暂无数据</div>
                <div class="badge-value">-</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 回款达人
        if '本月回款合计' in filtered_df.columns:
            top_payment = filtered_df.loc[filtered_df['本月回款合计'].idxmax()]
            st.markdown(f"""
            <div class="achievement-card silver">
                <div class="badge-category silver"></div>
                <div class="badge-icon">💰</div>
                <div class="badge-title">回款达人</div>
                <div class="badge-name">{escape(str(top_payment['员工姓名']))}</div>
                <div class="badge-value">{top_payment['本月回款合计']:,.0f} 元</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="achievement-card silver">
                <div class="badge-category silver"></div>
                <div class="badge-icon">💰</div>
                <div class="badge-title">回款达人</div>
                <div class="badge-name">暂无数据</div>
                <div class="badge-value">-</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # 进步之星 - 使用新的计算方法
        # 进步值 = (本月销售额-上月销售额)*0.6 + (本月回款合计-上月回款额)*0.4
        progress_scores = []
        
        # 检查所需列是否存在
        required_cols = ['本月销售额', '本月回款合计']
        last_month_sales_cols = ['上月销售额', '上月销售额参考']  # 可能的列名
        last_month_payment_cols = ['上月回款额', '上月回款额参考']  # 可能的列名
        
        # 找到实际存在的上月数据列
        last_sales_col = None
        last_payment_col = None
        
        for col in last_month_sales_cols:
            if col in filtered_df.columns:
                last_sales_col = col
                break
                
        for col in last_month_payment_cols:
            if col in filtered_df.columns:
                last_payment_col = col
                break
        
        if all(col in filtered_df.columns for col in required_cols) and last_sales_col and last_payment_col:
            for idx, row in filtered_df.iterrows():
                # 获取本月和上月数据
                current_sales = row.get('本月销售额', 0)
                current_payment = row.get('本月回款合计', 0)
                last_sales = row.get(last_sales_col, 0)
                last_payment = row.get(last_payment_col, 0)
                
                # 计算进步值
                if pd.notna(current_sales) and pd.notna(current_payment) and pd.notna(last_sales) and pd.notna(last_payment):
                    sales_progress = current_sales - last_sales
                    payment_progress = current_payment - last_payment
                    total_progress = sales_progress * 0.6 + payment_progress * 0.4
                    
                    progress_scores.append({
                        'name': row['员工姓名'],
                        'progress': total_progress,
                        'sales_diff': sales_progress,
                        'payment_diff': payment_progress
                    })
            
            if progress_scores:
                # 找到进步最大的员工
                top_progress_emp = max(progress_scores, key=lambda x: x['progress'])
                progress_value = top_progress_emp['progress']
                
                st.markdown(f"""
                <div class="achievement-card bronze">
                    <div class="badge-category bronze"></div>
                    <div class="badge-icon">🚀</div>
                    <div class="badge-title">进步之星</div>
                    <div class="badge-name">{escape(str(top_progress_emp['name']))}</div>
                    <div class="badge-value">进步值: {progress_value:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="achievement-card bronze">
                    <div class="badge-category bronze"></div>
                    <div class="badge-icon">🚀</div>
                    <div class="badge-title">进步之星</div>
                    <div class="badge-name">暂无数据</div>
                    <div class="badge-value">-</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="achievement-card bronze">
                <div class="badge-category bronze"></div>
                <div class="badge-icon">🚀</div>
                <div class="badge-title">进步之星</div>
                <div class="badge-name">数据不完整</div>
                <div class="badge-value">-</div>
            </div>
            """, unsafe_allow_html=True)


def display_sales_employee_details(sales_df):
    """销售回款相关的员工详情"""
    if sales_df is None or sales_df.shape[0] == 0:
        return
    st.markdown('<h3 class="section-title fade-in">💰 员工销售回款详情</h3>', unsafe_allow_html=True)
    if '员工姓名' not in sales_df.columns or len(sales_df['员工姓名']) == 0:
        st.info("没有员工数据")
        return

    # 直接使用销售数据
    df = sales_df.copy()
    # 排除合计行
    df = df[df['员工姓名'] != '合计'].copy()
    df = df[df['员工姓名'].notna()]

    selected_employee = st.selectbox("选择员工查看销售回款数据", df['员工姓名'].unique())
    if selected_employee:
        emp_row = df[df['员工姓名'] == selected_employee]
        if len(emp_row) == 0:
            st.warning("未找到该员工数据")
            return
        emp_data = emp_row.iloc[0]

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"""
            <div class="glass-card fade-in" style="animation-delay: 0.1s;">
                <div class="employee-header">
                    <div style="font-size:1.8rem; font-weight:700; color:#1D1D1F; font-family: 'SF Pro Display';">{escape(str(selected_employee))}</div>
                    <div class="employee-group" style="color:#0A84FF; font-family: 'SF Pro Text';">队名: {emp_data.get('队名', '未知')}</div>
                </div>
                <div class="employee-stats">
                    <div class="stat-card">
                        <div class="stat-label">本月销售总额</div>
                        <div class="stat-value">{emp_data.get('本月销售额', 0):,.0f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">本月回款合计</div>
                        <div class="stat-value">{emp_data.get('本月回款合计', 0):,.0f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 添加任务完成进度显示
            has_task_data = ('本月销售任务' in emp_data and '本月回款任务' in emp_data)

            if has_task_data:
                sales_task = emp_data.get('本月销售任务', 0)
                payment_task = emp_data.get('本月回款任务', 0)
                sales_progress = emp_data.get('销售业绩完成进度', 0) * 100
                payment_progress = emp_data.get('回款业绩完成进度', 0) * 100

                st.markdown("""
                <div style="margin-top:20px; padding-top:20px; border-top:0.5px solid rgba(0, 0, 0, 0.05);">
                    <div style="font-weight:600; margin-bottom:15px; color:#86868B; font-family: 'SF Pro Text';">任务完成情况:</div>
                </div>
                """, unsafe_allow_html=True)

                # 销售任务
                st.markdown(f"""
                <div style="margin-bottom:20px;">
                    <div style="display:flex; justify-content:space-between; font-size:1.05rem; font-family: 'SF Pro Text';">
                        <div>销售任务:</div>
                        <div style="font-weight:500;">¥ {sales_task:,.0f}</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:1.05rem; font-family: 'SF Pro Text'; margin-bottom:5px;">
                        <div>完成进度:</div>
                        <div style="font-weight:500; color:{get_progress_color(sales_progress / 100)};">{sales_progress:.1f}%</div>
                    </div>
                    <div style="width:100%; height:8px; background:#E5E5EA; border-radius:4px; overflow:hidden;">
                        <div style="width:{min(sales_progress, 100)}%; height:100%; background:{get_progress_color(sales_progress / 100)};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 回款任务
                st.markdown(f"""
                <div style="margin-bottom:20px;">
                    <div style="display:flex; justify-content:space-between; font-size:1.05rem; font-family: 'SF Pro Text';">
                        <div>回款任务:</div>
                        <div style="font-weight:500;">¥ {payment_task:,.0f}</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:1.05rem; font-family: 'SF Pro Text'; margin-bottom:5px;">
                        <div>完成进度:</div>
                        <div style="font-weight:500; color:{get_progress_color(payment_progress / 100)};">{payment_progress:.1f}%</div>
                    </div>
                    <div style="width:100%; height:8px; background:#E5E5EA; border-radius:4px; overflow:hidden;">
                        <div style="width:{min(payment_progress, 100)}%; height:100%; background:{get_progress_color(payment_progress / 100)};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 显示月度销售数据
            if '本月销售额' in emp_data:
                st.markdown("""
                <div style="margin-top:20px; padding-top:20px; border-top:0.5px solid rgba(0, 0, 0, 0.05);">
                    <div style="font-weight:600; margin-bottom:15px; color:#86868B; font-family: 'SF Pro Text';">月度销售数据:</div>
                </div>
                """, unsafe_allow_html=True)

                monthly_items = [
                    ('本月销售额', emp_data.get('本月销售额', 0)),
                    ('本月回款合计', emp_data.get('本月回款合计', 0)),
                    ('本月回未超期款', emp_data.get('本月回未超期款', 0)),
                    ('本月回超期款', emp_data.get('本月回超期款', 0)),
                    ('月末逾期未收回额', emp_data.get('月末逾期未收回额', 0))
                ]
                for label, value in monthly_items:
                    if pd.notna(value):
                        st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:0.5px solid rgba(0, 0, 0, 0.03); font-size:1.05rem; font-family: 'SF Pro Text';">
                            <div>{label}:</div>
                            <div style="font-weight:500;">{value:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)



            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            # 根据有无进度数据选择不同的图表
            if '销售业绩完成进度' in emp_data and '回款业绩完成进度' in emp_data:
                # 创建仪表盘样式图表
                fig = go.Figure()

                # 销售任务仪表盘
                sales_color = get_progress_color(emp_data['销售业绩完成进度'])
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=emp_data['销售业绩完成进度'] * 100,
                    domain={'x': [0, 1], 'y': [0.6, 1]},
                    title={'text': "销售任务完成率", 'font': {'size': 20}},
                    gauge={
                        'axis': {'range': [0, 150], 'tickwidth': 1},
                        'bar': {'color': sales_color},
                        'bgcolor': "white",
                        'steps': [
                            {'range': [0, 66], 'color': "rgba(255, 69, 58, 0.15)"},
                            {'range': [66, 100], 'color': "rgba(255, 214, 10, 0.15)"},
                            {'range': [100, 150], 'color': "rgba(48, 209, 88, 0.15)"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 100
                        }
                    },
                    number={'suffix': "%"}
                ))

                # 回款任务仪表盘
                payment_color = get_progress_color(emp_data['回款业绩完成进度'])
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=emp_data['回款业绩完成进度'] * 100,
                    domain={'x': [0, 1], 'y': [0.1, 0.5]},
                    title={'text': "回款任务完成率", 'font': {'size': 20}},
                    gauge={
                        'axis': {'range': [0, 150], 'tickwidth': 1},
                        'bar': {'color': payment_color},
                        'bgcolor': "white",
                        'steps': [
                            {'range': [0, 66], 'color': "rgba(255, 69, 58, 0.15)"},
                            {'range': [66, 100], 'color': "rgba(255, 214, 10, 0.15)"},
                            {'range': [100, 150], 'color': "rgba(48, 209, 88, 0.15)"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 100
                        }
                    },
                    number={'suffix': "%"}
                ))

                fig.update_layout(
                    title=f"{selected_employee}的任务完成情况",
                    title_font=dict(size=24, color='#1D1D1F'),
                    height=600,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#1D1D1F')
                )

                st.plotly_chart(fig, use_container_width=True)

                # 添加销售和回款数据对比图表
                sales_data = {
                    'category': ['销售额', '销售任务'],
                    'value': [emp_data.get('本月销售额', 0) / 10000, emp_data.get('本月销售任务', 0) / 10000]
                }

                payment_data = {
                    'category': ['回款额', '回款任务'],
                    'value': [emp_data.get('本月回款合计', 0) / 10000, emp_data.get('本月回款任务', 0) / 10000]
                }

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=sales_data['category'],
                    y=sales_data['value'],
                    name='销售情况',
                    marker_color='#0A84FF',
                    text=[f"{val:.1f}万" for val in sales_data['value']],
                    textposition='auto',
                ))

                fig.add_trace(go.Bar(
                    x=payment_data['category'],
                    y=payment_data['value'],
                    name='回款情况',
                    marker_color='#BF5AF2',
                    text=[f"{val:.1f}万" for val in payment_data['value']],
                    textposition='auto',
                ))

                fig.update_layout(
                    title=f"{selected_employee}的销售与回款对比(万元)",
                    title_font=dict(size=20, color='#1D1D1F'),
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#1D1D1F')
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                # 如果没有任务进度数据，显示基本销售回款信息
                st.info("该员工暂无任务进度数据，仅显示基本销售回款信息")

        # 周数据详情表格 - 独立显示，占据全宽
        st.markdown("""
        <div style="margin-top:30px; padding-top:20px; border-top:1px solid rgba(0, 0, 0, 0.08);">
        </div>
        """, unsafe_allow_html=True)
        
        # 动态检测可用周数
        week_pattern = r'第(\d+)周销售额'
        available_weeks = []
        for col in df.columns:
            match = re.match(week_pattern, col)
            if match:
                week_num = int(match.group(1))
                available_weeks.append(week_num)
        
        # 去重并排序
        available_weeks = sorted(set(available_weeks))
        
        # 收集周数据并构建表格
        week_table_data = []
        for week_num in available_weeks:
            week_sales_col = f'第{week_num}周销售额'
            week_normal_payment_col = f'第{week_num}周回未超期款'
            week_overdue_payment_col = f'第{week_num}周回超期款'
            week_total_payment_col = f'第{week_num}周回款合计'
            week_overdue_uncollected_col = f'第{week_num}周逾期未收回额'

            week_sales = emp_data.get(week_sales_col, 0)
            week_normal_payment = emp_data.get(week_normal_payment_col, 0)
            week_overdue_payment = emp_data.get(week_overdue_payment_col, 0)
            week_total_payment = emp_data.get(week_total_payment_col, 0)
            week_overdue_uncollected = emp_data.get(week_overdue_uncollected_col, 0)

            # 只有当至少有一个非零值时才添加到表格
            if any([
                pd.notna(week_sales) and week_sales != 0,
                pd.notna(week_normal_payment) and week_normal_payment != 0,
                pd.notna(week_overdue_payment) and week_overdue_payment != 0,
                pd.notna(week_total_payment) and week_total_payment != 0,
                pd.notna(week_overdue_uncollected) and week_overdue_uncollected != 0
            ]):
                week_table_data.append({
                    '周数': f'第{week_num}周',
                    '销售额': week_sales if pd.notna(week_sales) else 0,
                    '回未超期款': week_normal_payment if pd.notna(week_normal_payment) else 0,
                    '回超期款': week_overdue_payment if pd.notna(week_overdue_payment) else 0,
                    '回款合计': week_total_payment if pd.notna(week_total_payment) else 0,
                    '逾期未收回额': week_overdue_uncollected if pd.notna(week_overdue_uncollected) else 0
                })

        # 显示周数据表格
        if week_table_data:
            st.markdown(f"""
            <div style="margin-bottom:20px;">
                <div style="font-size:1.5rem; font-weight:700; color:#1D1D1F; font-family: 'SF Pro Display'; margin-bottom:20px;">
                    💰 {selected_employee} - 周数据详情
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 创建DataFrame并格式化
            week_df = pd.DataFrame(week_table_data)
            
            # 格式化数值列
            for col in ['销售额', '回未超期款', '回超期款', '回款合计', '逾期未收回额']:
                week_df[col] = week_df[col].apply(lambda x: f"{x:,.0f}")
            
            # 显示表格
            st.dataframe(
                week_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "周数": st.column_config.TextColumn("周数", width="small"),
                    "销售额": st.column_config.TextColumn("销售额", width="medium"),
                    "回未超期款": st.column_config.TextColumn("回未超期款", width="medium"),
                    "回超期款": st.column_config.TextColumn("回超期款", width="medium"),
                    "回款合计": st.column_config.TextColumn("回款合计", width="medium"),
                    "逾期未收回额": st.column_config.TextColumn("逾期未收回额", width="medium")
                }
            ) 