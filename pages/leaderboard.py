"""
红黑榜页面
查看月度团队红黑榜排名
"""

import streamlit as st
from components.navigation import navigation
from components.ui_components import ui
from core.state_manager import state_manager
from utils.data_loader import data_loader
from html import escape


def show():
    """显示红黑榜页面"""
    # 渲染导航栏
    navigation.render_navigation_bar()
    
    # 渲染面包屑
    navigation.render_breadcrumb()
    
    # 检查数据
    score_df = state_manager.get_data('score_df')
    sales_df = state_manager.get_data('sales_df')
    
    if score_df is None:
        st.error("请先上传积分数据文件")
        return
    
    # 获取红黑榜数据
    red_df, black_df, group_data = data_loader.get_leaderboard_data(score_df)
    
    if red_df is None or black_df is None:
        st.warning("无法生成红黑榜数据，请检查数据文件")
        return
    
    # 显示红黑榜
    _display_leaderboard(red_df, black_df, sales_df)


def _display_leaderboard(red_df, black_df, sales_df=None):
    """显示红黑榜"""
    # 页面标题
    if red_df is not None and not red_df.empty and '统计月份' in red_df.columns:
        month_info = red_df['统计月份'].iloc[0]
        st.markdown(f"""
        <div class="header fade-in">
            <h1 style="margin:0; text-align:center; font-size:3rem; font-family: 'SF Pro Display'; color: #1D1D1F;">销售积分红黑榜</h1>
            <p style="margin:10px 0 0; text-align:center; color:#86868B; font-size:1.3rem;">{month_info} 销售团队绩效评估系统</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header fade-in">
            <h1 style="margin:0; text-align:center; font-size:3rem; font-family: 'SF Pro Display'; color: #1D1D1F;">销售积分红黑榜</h1>
            <p style="margin:10px 0 0; text-align:center; color:#86868B; font-size:1.3rem;">月度销售团队绩效评估系统</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 样式已通过ui_components.load_css()统一加载，无需重复定义
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-title red-title fade-in">🏆 红榜 - 卓越团队</h3>', unsafe_allow_html=True)
        if not red_df.empty:
            for i, (_, row) in enumerate(red_df.iterrows()):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
                st.markdown(
                    f'<div class="leaderboard-item fade-in" style="animation-delay: {0.1 + i * 0.05}s;">'
                    f'<div class="rank red-rank">#{i + 1}</div>'
                    f'{ui.create_avatar(row["员工姓名"], "red")}'
                    f'<div style="flex-grow:1;">'
                    f'<div class="employee-name">{escape(str(row["员工姓名"]))}</div>'
                    f'<div class="employee-group">队名: <strong>{row["队名"]}</strong> · 积分: <strong>{row["个人总积分"]}</strong></div>'
                    f'</div>'
                    f'<div class="medal">{medal}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("暂无红榜数据", icon="ℹ️")
    
    with col2:
        st.markdown('<h3 class="section-title black-title fade-in">⚫ 黑榜 - 待提升团队</h3>', unsafe_allow_html=True)
        if not black_df.empty:
            for i, (_, row) in enumerate(black_df.iterrows()):
                st.markdown(
                    f'<div class="leaderboard-item fade-in" style="animation-delay: {0.1 + i * 0.05}s;">'
                    f'<div class="rank black-rank">#{i + 1}</div>'
                    f'{ui.create_avatar(row["员工姓名"], "black")}'
                    f'<div style="flex-grow:1;">'
                    f'<div class="employee-name">{escape(str(row["员工姓名"]))}</div>'
                    f'<div class="employee-group">队名: <strong>{row["队名"]}</strong> · 积分: <strong>{row["个人总积分"]}</strong></div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("暂无黑榜数据", icon="ℹ️") 