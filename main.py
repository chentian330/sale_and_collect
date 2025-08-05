"""
销售积分红黑榜系统 - 主应用程序
重构版本 3.0
"""

import streamlit as st
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入核心组件
from components.ui_components import ui
from components.navigation import navigation
from core.page_manager import page_manager
from core.state_manager import state_manager
from utils.data_loader import data_loader


def initialize_app():
    """初始化应用程序"""
    # 设置页面配置
    st.set_page_config(
        page_title="销售积分红黑榜系统",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 加载CSS样式
    ui.load_css()
    
    # 初始化状态管理器
    state_manager._initialize_state()
    
    # 初始化页面管理器
    page_manager.initialize_from_session()


def auto_load_data():
    """自动加载数据"""
    if not state_manager.is_data_loaded() and state_manager.get_file_name() is None:
        detected_file = data_loader.auto_detect_excel_file()
        if detected_file:
            score_df, sales_df, department_sales_df, ranking_df, error = data_loader.load_excel_data(detected_file)
            if not error:
                state_manager.set_data('score_df', score_df)
                state_manager.set_data('sales_df', sales_df)
                state_manager.set_data('department_sales_df', department_sales_df)
                state_manager.set_data('ranking_df', ranking_df)
                state_manager.set_file_name(detected_file)
                st.success(f"自动加载文件成功: {detected_file}")
            else:
                st.error(f"自动加载文件失败: {error}")


def main():
    """主应用程序函数"""
    # 初始化应用
    initialize_app()
    
    # 自动加载数据
    auto_load_data()
    
    # 获取当前页面
    current_page = page_manager.get_current_page()
    
    # 渲染页面
    try:
        page_manager.render_current_page()
    except Exception as e:
        st.error(f"页面加载错误: {e}")
        st.info("正在返回主页...")
        page_manager.go_home()
    
    # 渲染页脚
    ui.render_footer()


if __name__ == "__main__":
    main() 