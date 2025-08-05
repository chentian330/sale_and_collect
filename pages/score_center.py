"""
积分中心页面
员工积分统计与团队排名分析
"""

import streamlit as st
from components.navigation import navigation
from components.ui_components import ui


def show():
    """显示积分中心页面"""
    # 渲染页面头部
    help_content = """
        <h4 style="margin: 0 0 12px 0; color: #0A84FF;">🏆 积分中心功能</h4>
        <p style="margin: 0 0 8px 0;"><strong>红黑榜</strong><br/>查看月度团队红黑榜排名和绩效对比</p>
        <p style="margin: 0 0 8px 0;"><strong>积分统计</strong><br/>查看员工积分详细统计和分析</p>
        <h4 style="margin: 12px 0 8px 0; color: #BF5AF2;">📋 数据依赖</h4>
        <p style="margin: 0;">依赖工作表：员工积分数据<br/>
        💡 当该工作表可用时，积分中心所有功能自动启用</p>
    """
    
    # 渲染导航栏（最顶部）
    navigation.render_navigation_bar()
    
    # 渲染页面头部
    ui.render_page_header(
        title="积分中心",
        subtitle="员工积分统计与团队排名分析",
        help_content=help_content,
        position="right"
    )
    
    # 渲染面包屑
    navigation.render_breadcrumb()
    
    # 渲染页面标题和菜单按钮
    navigation.render_menu_buttons('score_center') 