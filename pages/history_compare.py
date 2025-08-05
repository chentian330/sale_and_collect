"""
月度数据对比页面
多月份历史数据趋势对比分析
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
import re
import time
from components.navigation import navigation
from components.ui_components import ui
from core.state_manager import state_manager
from core.page_manager import page_manager
from utils.data_loader import data_loader


def show():
    """显示月度数据对比页面"""
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    # 显示主页面 - 上传区域和功能菜单
    # 只显示标题，不使用帮助内容
    ui.render_page_header(
        title="📊 历史数据对比"
    )

    # 创建左右分栏布局
    col_upload, col_menu = st.columns([1, 2])
    
    # 左侧上传区域
    with col_upload:
        show_upload_section()
    
    # 右侧功能菜单
    with col_menu:
        show_function_menu()

    # 底部数据展示区域
    show_data_management_section()


def show_upload_section():
    """显示上传区域"""
    st.markdown("""
    <div class="glass-card fade-in" style="animation-delay: 0.2s;">
        <h3 style="color: #0A84FF; margin-bottom: 1.5rem; font-size: 1.4rem; text-align: center;">
            📁 历史数据上传
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # 初始化文件上传器key
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 'history_file_uploader_0'
    
    # 获取文件上传器的key，确保删除后能重置
    uploader_key = st.session_state.uploader_key
    
    # 文件上传器
    uploaded_files = st.file_uploader(
        "选择历史Excel文件（可多选）",
        type=["xlsx"],
        accept_multiple_files=True,
        help="请上传包含'销售回款数据统计'工作表的Excel文件",
        key=uploader_key
    )

    # 处理上传的文件
    if uploaded_files:
        # 初始化已处理文件列表
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = set()
        
        process_uploaded_files(uploaded_files)


def show_function_menu():
    """显示功能菜单"""
    st.markdown("""
    <div class="glass-card fade-in" style="animation-delay: 0.3s;">
        <h3 style="color: #0A84FF; margin-bottom: 1.5rem; font-size: 1.4rem; text-align: center;">
            🎛️ 分析功能
        </h3>
    </div>
    """, unsafe_allow_html=True)

    history_files = state_manager.get_history_files()
    can_analyze = len(history_files) >= 2
    
    st.markdown("### 选择分析类型")
    
    # 提示信息
    if not can_analyze:
        if len(history_files) == 1:
            st.info("📊 请再上传至少1个月份的数据文件，即可开始对比分析")
        else:
            st.info("📋 请先上传历史数据文件，然后选择分析功能")
    
    # 总体趋势按钮
    if st.button(
        "📈 总体趋势", 
        key="btn_overall_trends", 
        use_container_width=True,
        disabled=not can_analyze,
        help="查看整体销售回款趋势分析" if can_analyze else "需要至少2个月份的数据才能进行分析"
    ):
        page_manager.navigate_to('overall_trends')
    
    st.markdown("""
    <p style="color: #86868B; font-size: 0.9rem; margin-bottom: 1rem; text-align: center;">
        查看月度数据汇总表、销售额与回款额对比
    </p>
    """, unsafe_allow_html=True)
    
    # 员工详情按钮
    if st.button(
        "👥 员工详情", 
        key="btn_employee_details", 
        use_container_width=True,
        disabled=not can_analyze,
        help="查看员工历史表现对比分析" if can_analyze else "需要至少2个月份的数据才能进行分析"
    ):
        page_manager.navigate_to('employee_details')
    
    st.markdown("""
    <p style="color: #86868B; font-size: 0.9rem; margin-bottom: 1rem; text-align: center;">
        员工历史对比、月度汇总表、雷达图对比
    </p>
    """, unsafe_allow_html=True)
    
    # 部门详情按钮
    if st.button(
        "🏢 部门详情", 
        key="btn_department_details", 
        use_container_width=True,
        disabled=not can_analyze,
        help="查看部门级别历史数据对比" if can_analyze else "需要至少2个月份的数据才能进行分析"
    ):
        page_manager.navigate_to('department_details')
    
    st.markdown("""
    <p style="color: #86868B; font-size: 0.9rem; text-align: center;">
        部门历史对比、月度汇总表、热力图展示
    </p>
    """, unsafe_allow_html=True)


def process_uploaded_files(uploaded_files):
    """处理上传的文件"""
    # 防止在删除操作后意外处理文件
    if st.session_state.get('skip_file_processing', False):
        st.session_state.skip_file_processing = False
        return
    
    history_files = state_manager.get_history_files()
    
    for uploaded_file in uploaded_files:
        # 创建文件唯一标识符（文件名+大小）
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # 检查是否在当前会话中已处理过此文件
        if file_id in st.session_state.processed_files:
            continue
            
        # 检查文件是否已经在历史数据中存在
        file_already_exists = False
        for key, info in history_files.items():
            if info['file_name'] == uploaded_file.name:
                file_already_exists = True
                break

        if file_already_exists:
            # 标记为已处理，避免重复检查
            st.session_state.processed_files.add(file_id)
            continue

        # 加载Excel数据
        with st.spinner(f"正在加载 {uploaded_file.name}..."):
            score_df, sales_df, department_sales_df, ranking_df, error = data_loader.load_excel_data(uploaded_file)

        if error:
            st.error(f"文件 {uploaded_file.name} 加载失败: {error}")
        else:
            # 提取年月信息
            month_info = extract_month_info(uploaded_file, sales_df, score_df)

            # 存储数据
            state_manager.add_history_file(month_info, {
                'file_name': uploaded_file.name,
                'sales_df': sales_df,
                'department_sales_df': department_sales_df
            })

            st.success(f"✅ 成功加载 {month_info} 的数据")
        
        # 标记文件为已处理
        st.session_state.processed_files.add(file_id)


def extract_month_info(uploaded_file, sales_df, score_df):
    """提取月份信息"""
    month_info = None

    # 方法1：从文件名提取
    match = re.search(r'(\d{4})年(\d{1,2})月', uploaded_file.name)
    if match:
        year = match.group(1)
        month = match.group(2)
        month_info = f"{year}年{month}月"

    # 方法2：从数据中提取
    if month_info is None and sales_df is not None and '统计月份' in sales_df.columns:
        month_values = sales_df['统计月份'].unique()
        if len(month_values) > 0 and pd.notna(month_values[0]):
            month_info = str(month_values[0])

    if month_info is None and score_df is not None and '统计月份' in score_df.columns:
        month_values = score_df['统计月份'].unique()
        if len(month_values) > 0 and pd.notna(month_values[0]):
            month_info = str(month_values[0])

    # 如果无法提取，使用文件名作为标识
    if month_info is None:
        month_info = uploaded_file.name

    return month_info


def reset_file_uploader():
    """重置文件上传器，清空显示"""
    # 设置标志，防止文件重新处理
    st.session_state.skip_file_processing = True
    
    # 生成新的uploader key，强制重新创建文件上传器组件
    current_key = st.session_state.get('uploader_key', 'history_file_uploader_0')
    if current_key.endswith('_0'):
        new_key = 'history_file_uploader_1'
    else:
        new_key = 'history_file_uploader_0'
    st.session_state.uploader_key = new_key
    
    # 清空旧的uploader状态
    if current_key in st.session_state:
        del st.session_state[current_key]


def show_data_management_section():
    """显示数据管理区域"""
    history_files = state_manager.get_history_files()
    
    # 创建左右分栏，各占一半
    col_loaded, col_management = st.columns(2)
    
    # 左侧：已加载数据
    with col_loaded:
        st.markdown("### 📋 已加载数据")
        
        if history_files:
            # 创建文件表格
            file_data = []
            for month_key, file_info in history_files.items():
                file_data.append({
                    "月份": month_key,
                    "文件名": file_info['file_name']
                })

            file_df = pd.DataFrame(file_data)
            st.dataframe(file_df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无已加载的数据文件")
    
    # 右侧：数据管理
    with col_management:
        st.markdown("### 🗑️ 数据管理")
        
        if history_files:
            file_data = []
            for month_key, file_info in history_files.items():
                file_data.append({
                    "月份": month_key,
                    "文件名": file_info['file_name']
                })
            file_df = pd.DataFrame(file_data)
            
            selected_file = st.selectbox(
                "选择要删除的文件",
                options=[f"{row['月份']}" for _, row in file_df.iterrows()],
                key="file_to_delete_select"
            )
            
            col_del, col_clear = st.columns(2)
            
            with col_del:
                if st.button("删除所选", key="delete_selected", use_container_width=True):
                    state_manager.remove_history_file(selected_file)
                    # 重置文件上传器
                    reset_file_uploader()
                    st.success(f"已删除 {selected_file} 的数据")
                    st.rerun()
            
            with col_clear:
                if st.button("清空全部", key="clear_all", use_container_width=True):
                    state_manager.clear_history_files()
                    # 重置文件上传器
                    reset_file_uploader()
                    # 清空已处理文件记录
                    if 'processed_files' in st.session_state:
                        st.session_state.processed_files.clear()
                    st.success("已清空所有历史数据")
                    st.rerun()
        else:
            st.info("暂无数据文件可管理")











 