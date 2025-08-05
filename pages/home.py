"""
主页
销售积分红黑榜系统主页面
"""

import streamlit as st
from components.navigation import navigation
from components.ui_components import ui
from core.state_manager import state_manager
from core.page_manager import page_manager
from utils.data_loader import data_loader


def show():
    """显示主页面"""
    # 渲染标题区域（包含帮助按钮）
    _render_header_with_help()

    # 创建主要内容布局（参照原系统）
    col1, col2 = st.columns([1, 2])

    with col1:
        # 文件上传区域
        _render_file_upload_section()

    with col2:
        # 功能菜单区域
        _render_function_menu()


def _render_header_with_help():
    """渲染标题区域和帮助按钮"""
    help_content = """
        <h4 style="margin: 0 0 12px 0; color: #0A84FF;">🔧 快速开始</h4>
        <p style="margin: 0 0 8px 0;"><strong>1. 上传数据文件</strong><br/>请上传员工销售回款统计_XXXX年X月.xlsx文件</p>
        <p style="margin: 0 0 8px 0;"><strong>2. 选择功能模块</strong><br/>系统会根据数据自动启用相应功能</p>
        <p style="margin: 0 0 12px 0;"><strong>3. 查看分析结果</strong><br/>系统自动生成图表和统计分析</p>
        <h4 style="margin: 0 0 8px 0; color: #BF5AF2;">📋 兼容性说明</h4>
        <p style="margin: 0;"><strong>必须包含至少一个工作表：</strong><br/>
        • 员工积分数据 → 积分中心<br/>
        • 销售回款数据统计 → 员工销售统计<br/>
        • 部门销售回款统计 → 部门销售统计<br/>
        • 销售回款超期账款排名 → 销售回款排名<br/>
        💡 系统根据可用工作表智能启用对应功能</p>
    """
    
    ui.render_page_header(
        title="销售积分红黑榜系统",
        subtitle="销售团队绩效评估与数据分析平台 - 提供实时洞察与绩效分析",
        help_content=help_content,
        position="right"
    )


def _render_file_upload_section():
    """渲染文件上传区域（参照原系统样式）"""
    ui.render_function_area(
        title="文件上传区域",
        icon="📁",
        description="请上传员工销售回款统计_XXXX年X月.xlsx文件",
        delay=0.1
    )
    
    uploaded_file = st.file_uploader(
        "选择Excel文件",
        type=["xlsx"],
        help="请上传员工销售回款统计_XXXX年X月.xlsx文件。系统会自动检测可用工作表（员工积分数据、销售回款数据统计、部门销售回款统计、销售回款超期账款排名）并智能启用对应功能",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # 验证文件
        is_valid, message = data_loader.validate_uploaded_file(uploaded_file)
        
        if not is_valid:
            st.error(f"文件验证失败: {message}")
            return
        
        # 加载数据
        with st.spinner("正在加载数据..."):
            score_df, sales_df, department_sales_df, ranking_df, error = data_loader.load_excel_data(uploaded_file)
        
        if error:
            st.error(f"文件加载失败: {error}")
        else:
            # 记录数据上传操作（用于撤销）
            page_manager._record_action({
                'type': 'data_upload',
                'file_name': uploaded_file.name,
                'previous_data': {
                    'score_df': state_manager.get_data('score_df'),
                    'sales_df': state_manager.get_data('sales_df'),
                    'department_sales_df': state_manager.get_data('department_sales_df'),
                    'ranking_df': state_manager.get_data('ranking_df'),
                    'file_name': state_manager.get_file_name()
                }
            })
            
            # 存储数据到状态管理器
            state_manager.set_data('score_df', score_df)
            state_manager.set_data('sales_df', sales_df)
            state_manager.set_data('department_sales_df', department_sales_df)
            state_manager.set_data('ranking_df', ranking_df)
            state_manager.set_file_name(uploaded_file.name)
            
            # 显示成功信息
            st.success(f"文件加载成功: {uploaded_file.name}")
            
            # 显示数据基本信息
            data_info = data_loader.get_data_info(score_df, sales_df)
            _render_data_summary(data_info, department_sales_df, ranking_df)


def _render_data_summary(data_info: dict, department_sales_df=None, ranking_df=None):
    """渲染数据摘要"""
    st.markdown("##### 数据摘要")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("统计月份", data_info["month_info"])
        st.metric("员工总数", data_info["total_employees"])
    
    with col2:
        st.metric("团队数量", data_info["total_teams"])
        # 显示工作表加载状态
        st.markdown("**工作表状态：**")
        
        # 检查各工作表状态
        score_status = "✅" if state_manager.has_data('score_df') else "❌"
        sales_status = "✅" if state_manager.has_data('sales_df') else "❌"
        dept_status = "✅" if state_manager.has_data('department_sales_df') else "❌"
        ranking_status = "✅" if state_manager.has_data('ranking_df') else "❌"
        
        st.markdown(f"""
        - {score_status} 员工积分数据
        - {sales_status} 销售回款数据统计  
        - {dept_status} 部门销售回款统计
        - {ranking_status} 销售回款超期账款排名
        """, unsafe_allow_html=True)


def _render_function_menu():
    """渲染功能菜单区域（参照原系统样式）"""
    ui.render_function_area(
        title="功能菜单",
        icon="📊",
        delay=0.2
    )
    
    # 检查各功能的数据可用性
    can_score_center = state_manager.can_access_score_center()
    can_sales_center = state_manager.can_access_sales_center()
    
    # 积分中心按钮
    if st.button("🏆 积分中心", key="btn_score_center", disabled=not can_score_center, use_container_width=True):
        if can_score_center:
            page_manager.navigate_to('score_center')
        else:
            st.info("需要包含'员工积分数据'工作表的Excel文件来启用积分中心功能")
    
    # 显示积分中心状态提示
    if not can_score_center:
        st.caption("❌ 需要：员工积分数据")
    else:
        st.caption("✅ 数据已就绪")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 销售回款中心按钮
    if st.button("💰 销售回款中心", key="btn_sales_center", disabled=not can_sales_center, use_container_width=True):
        if can_sales_center:
            page_manager.navigate_to('sales_center')
        else:
            st.info("需要包含销售相关工作表的Excel文件来启用销售回款中心功能")
    
    # 显示销售回款中心状态提示
    if not can_sales_center:
        st.caption("❌ 需要：销售回款数据统计、部门销售回款统计或销售回款超期账款排名")
    else:
        available_functions = state_manager.get_available_sales_functions()
        function_names = {
            'ranking': '排名数据',
            'sales': '员工统计',
            'department_sales': '部门统计'
        }
        available_names = [function_names[f] for f in available_functions]
        st.caption(f"✅ 可用功能：{', '.join(available_names)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 月度数据对比按钮（不需要数据也可以使用）
    if st.button("📊 月度数据对比", key="btn_history_compare", use_container_width=True):
        page_manager.navigate_to('history_compare') 