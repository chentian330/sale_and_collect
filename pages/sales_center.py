"""
销售回款中心页面
销售业绩与回款数据全面分析
"""

import streamlit as st
from components.navigation import navigation
from components.ui_components import ui


def show():
    """显示销售回款中心页面"""
    # 渲染页面头部
    help_content = """
        <h4 style="margin: 0 0 12px 0; color: #0A84FF;">💰 销售回款功能</h4>
        <p style="margin: 0 0 8px 0;"><strong>销售回款排名</strong><br/>查看员工销售回款排名和绩效对比</p>
        <p style="margin: 0 0 8px 0;"><strong>员工销售统计</strong><br/>查看员工销售回款详细统计分析</p>
        <p style="margin: 0 0 8px 0;"><strong>部门销售统计</strong><br/>查看部门级销售回款统计分析</p>
        <h4 style="margin: 12px 0 8px 0; color: #BF5AF2;">📋 数据依赖</h4>
        <p style="margin: 0;"><strong>排名功能：</strong>销售回款超期账款排名<br/>
        <strong>员工统计：</strong>销售回款数据统计<br/>
        <strong>部门统计：</strong>部门销售回款统计<br/>
        💡 每个功能独立，按可用数据启用</p>
    """
    
    # 渲染导航栏（最顶部）
    navigation.render_navigation_bar()
    
    # 渲染页面头部
    ui.render_page_header(
        title="销售回款中心",
        subtitle="销售业绩与回款数据全面分析",
        help_content=help_content,
        position="right"
    )
    
    # 渲染面包屑
    navigation.render_breadcrumb()
    
    # 渲染页面标题和菜单按钮
    navigation.render_menu_buttons('sales_center') 