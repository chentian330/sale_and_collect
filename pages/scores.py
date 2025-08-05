"""
积分统计页面
查看员工积分详细统计 - 从旧系统完整迁移
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from html import escape
from components.navigation import navigation
from components.ui_components import ui
from core.state_manager import state_manager
from utils.data_loader import data_loader


def show():
    """显示积分统计页面"""
    # 渲染导航栏
    navigation.render_navigation_bar()
    
    # 渲染面包屑
    navigation.render_breadcrumb()
    
    # 检查数据
    score_df = state_manager.get_data('score_df')
    
    if score_df is None:
        st.error("请先上传积分数据文件")
        return
    
    # 获取小组数据并显示小组排名
    group_data = data_loader.get_group_data(score_df)
    if group_data is not None:
        _display_group_ranking(group_data, score_df)
    
    # 显示员工详情
    _display_employee_details(score_df)


def _display_group_ranking(group_data, df):
    """显示小组排名"""
    if group_data is None or df is None:
        return

    st.markdown('<h3 class="section-title fade-in">🏅 小组加权积分排名</h3>', unsafe_allow_html=True)

    # 创建水平柱状图
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=group_data['加权小组总分'],
        y=group_data['队名'],
        orientation='h',
        marker=dict(
            color=['#FFD60A' if rank == 1 else '#8E8E93' if rank == 2 else '#FF9F0A' if rank == 3 else '#0A84FF' for
                   rank in group_data['排名']],
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        ),
        text=group_data['加权小组总分'],
        textposition='auto',
        hoverinfo='text',
        hovertext=[f"{row['队名']}<br>加权总分: {row['加权小组总分']}<br>排名: {row['排名']}" for _, row in
                   group_data.iterrows()]
    ))

    fig.update_layout(
        height=500,
        margin=dict(l=150, r=50, t=80, b=50),
        title='小组加权总分排行榜',
        title_font=dict(size=26, color='#1D1D1F'),
        xaxis_title='加权小组总分',
        yaxis_title='队名',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1D1D1F'),
        yaxis=dict(
            tickfont=dict(size=14),
            autorange="reversed"
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.05)'
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="SF Pro Text"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # 显示小组详情
    st.markdown('<h3 class="section-title fade-in">👥 小组详情</h3>', unsafe_allow_html=True)
    cols = st.columns(3)
    group_cols = [group_data.iloc[i:i + 2] for i in range(0, len(group_data), 2)]
    
    for idx, groups in enumerate(group_cols):
        with cols[idx % 3]:
            for _, group_row in groups.iterrows():
                team_name = group_row['队名']
                weighted_team_score = group_row['加权小组总分']
                team_rank = group_row['排名']
                team_members = df[df['队名'] == team_name].sort_values(by='个人总积分', ascending=False)

                # 确定徽章样式
                badge_class = "group-badge"
                if team_rank <= 2:
                    badge_class += " red-badge"
                elif team_rank >= len(group_data) - 1:
                    badge_class += " black-badge"

                # 确定排名样式
                rank_class = ""
                if team_rank == 1:
                    rank_class = "gold"
                elif team_rank == 2:
                    rank_class = "silver"
                elif team_rank == 3:
                    rank_class = "bronze"

                # 渲染小组卡片
                st.markdown(f"""
                <div class="group-card fade-in" style="animation-delay: {0.1 + idx * 0.05}s;">
                    <div class="group-header">
                        <div class="{badge_class}">#{team_rank}</div>
                        <div>
                            <div style="font-size:1.5rem; font-weight:700; color:#1D1D1F;" class="{rank_class}">{escape(str(team_name))}</div>
                            <div style="color:#86868B;">加权总分: <strong>{weighted_team_score}</strong></div>
                        </div>
                    </div>
                    <div style="font-weight:600; margin-bottom:15px; color:#86868B;">团队成员:</div>
                """, unsafe_allow_html=True)

                # 显示团队成员
                for _, member in team_members.iterrows():
                    member_name = str(member['员工姓名'])
                    member_initials = ''.join([n[0] for n in member_name.split() if n])[:2] or member_name[:2] or "US"
                    
                    st.markdown(f"""
                    <div class="member-card">
                        <div class="member-avatar">{escape(member_initials)}</div>
                        <div style="flex-grow:1;">
                            <div style="font-weight:600; color:#1D1D1F;">{escape(member_name)}</div>
                            <div style="color:#86868B; font-size:0.9rem;">个人积分: {member['个人总积分']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)


def _display_employee_details(score_df):
    """显示员工积分详情"""
    if score_df is None or score_df.shape[0] == 0:
        return
        
    st.markdown('<h3 class="section-title fade-in">📋 员工积分详情</h3>', unsafe_allow_html=True)
    
    if '员工姓名' not in score_df.columns or len(score_df['员工姓名']) == 0:
        st.info("没有员工数据")
        return

    df = score_df.copy()

    # 员工选择器
    selected_employee = st.selectbox("选择员工查看积分详情", df['员工姓名'].unique())
    
    if selected_employee:
        emp_row = df[df['员工姓名'] == selected_employee]
        if len(emp_row) == 0:
            st.warning("未找到该员工数据")
            return
        emp_data = emp_row.iloc[0]

        # 积分类别和值
        categories = ['销售额目标分', '回款额目标分', '超期账款追回分',
                      '销售排名分', '回款排名分',
                      '销售进步分', '回款进步分', '基础分', '小组加分']
        values = [emp_data.get(cat, 0) for cat in categories]

        col1, col2 = st.columns([1, 2])

        with col1:
            # 员工基本信息卡片
            st.markdown(f"""
            <div class="glass-card fade-in" style="animation-delay: 0.1s;">
                <div class="employee-header">
                    <div style="font-size:1.8rem; font-weight:700; color:#1D1D1F; font-family: 'SF Pro Display';">{escape(str(selected_employee))}</div>
                    <div class="employee-group" style="color:#0A84FF; font-family: 'SF Pro Text';">队名: {emp_data['队名']}</div>
                </div>
                <div class="employee-stats">
                    <div class="stat-card">
                        <div class="stat-label">个人总积分</div>
                        <div class="stat-value">{emp_data['个人总积分']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">加权小组总分</div>
                        <div class="stat-value">{emp_data['加权小组总分']}</div>
                    </div>
                </div>
                <div style="font-weight:600; margin-bottom:15px; color:#86868B; font-family: 'SF Pro Text';">积分构成:</div>
            """, unsafe_allow_html=True)

            # 积分构成明细
            for i, category in enumerate(categories):
                st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:0.5px solid rgba(0, 0, 0, 0.05); font-size:1.05rem; font-family: 'SF Pro Text';">
                            <div>{category}:</div>
                            <div style="font-weight:500;">{values[i]}</div>
                        </div>
                        """, unsafe_allow_html=True)



            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            # 图表展示
            _render_employee_charts(emp_data, selected_employee, values, categories)


def _render_employee_charts(emp_data, selected_employee, values, categories):
    """渲染员工积分图表"""
    # 只显示积分构成雷达图
    if values and categories:
        fig = go.Figure()

        # 添加雷达图
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='积分构成',
            line=dict(color='#BF5AF2', width=3),
            fillcolor='rgba(191, 90, 242, 0.1)'
        ))

        # 设置图表布局
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-10, max(values) * 1.2 if values else 1],
                    gridcolor='rgba(0,0,0,0.05)',
                    linecolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    linecolor='rgba(0,0,0,0.1)',
                    gridcolor='rgba(0,0,0,0.05)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            height=500,
            margin=dict(l=100, r=100, t=80, b=80),
            title=f"{selected_employee}的积分构成雷达图",
            title_font=dict(size=24, color='#1D1D1F'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1D1D1F')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无积分构成数据可显示图表") 