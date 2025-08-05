"""
部门销售回款统计页面
查看部门级销售回款统计
"""

import streamlit as st
from components.navigation import navigation
from core.state_manager import state_manager


def show():
    """显示部门销售回款统计页面"""
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    department_sales_df = state_manager.get_data('department_sales_df')
    if department_sales_df is None:
        st.error("请先上传部门销售回款数据文件")
        return
    
    st.markdown('<h1 class="section-title fade-in">🏢 部门销售回款统计</h1>', unsafe_allow_html=True)
    st.info("部门销售回款统计功能正在开发中，请从原系统迁移相关代码")
    
    with st.expander("查看原始部门数据"):
        st.dataframe(department_sales_df, use_container_width=True) 