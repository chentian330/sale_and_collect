"""
导航组件
处理多级菜单导航和面包屑显示
"""

import streamlit as st
from core.page_manager import page_manager
from config.menu_config import MENU_CONFIG


class Navigation:
    """导航组件类"""
    
    def __init__(self):
        self.page_manager = page_manager
    
    def render_breadcrumb(self):
        """渲染面包屑导航"""
        breadcrumb = self.page_manager.get_breadcrumb()
        
        if len(breadcrumb) > 1:  # 只有在非主页时显示面包屑
            breadcrumb_html = '<div style="margin: 15px 0; padding: 10px 20px; background: rgba(255,255,255,0.7); border-radius: 10px; display: flex; align-items: center; font-family: \'SF Pro Text\', sans-serif;">'
            
            for i, item in enumerate(breadcrumb):
                if i > 0:
                    breadcrumb_html += '<span style="margin: 0 10px; color: #86868B;">></span>'
                
                if i == len(breadcrumb) - 1:  # 当前页面
                    breadcrumb_html += f'<span style="color: #0A84FF; font-weight: 500;">{item["icon"]} {item["label"]}</span>'
                else:  # 可点击的父页面
                    breadcrumb_html += f'<span style="color: #86868B; cursor: pointer;" onclick="window.location.reload()">{item["icon"]} {item["label"]}</span>'
            
            breadcrumb_html += '</div>'
            st.markdown(breadcrumb_html, unsafe_allow_html=True)
    
    def render_navigation_bar(self):
        """渲染导航栏"""
        current_page = self.page_manager.get_current_page()
        
        if current_page == 'home':
            return  # 主页不显示导航栏
        
        # 创建居中的导航按钮布局
        col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1.5, 3])
        
        with col2:
            if st.button("🏠 主页", key="nav_home", use_container_width=True):
                self.page_manager.go_home()
        
        with col3:
            if st.button("⬅️ 返回", key="nav_back", use_container_width=True):
                self.page_manager.go_back()
        
        with col4:
            if st.button("↩️ 撤销", key="nav_undo", use_container_width=True):
                self.page_manager.undo_last_action()
        
        # 添加导航栏样式
        st.markdown("""
        <style>
        /* 简化导航栏布局 */
        .main .block-container {
            padding-top: 1rem;
        }
        
        /* 导航按钮统一样式 */
        .stButton>button,
        .stButton>button[disabled] {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(15px) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            color: #1D1D1F !important;
            font-family: 'SF Pro Text', -apple-system, sans-serif !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            height: 48px !important;
            min-height: 48px !important;
            line-height: 1.2 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            white-space: nowrap !important;
            padding: 0 16px !important;
            margin: 0 !important;
        }
        
        /* 确保所有导航按钮图标和文字居中对齐 */
        .stButton>button span {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
        }
        
        /* 按钮悬浮效果 */
        .stButton>button:hover:not(:disabled) {
            background: rgba(255, 255, 255, 1) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12) !important;
            border-color: rgba(0, 0, 0, 0.12) !important;
        }
        
        /* 禁用状态样式 */
        .stButton>button:disabled,
        .stButton>button[disabled] {
            background: rgba(248, 248, 248, 0.8) !important;
            color: #8E8E93 !important;
            border: 1px solid rgba(0, 0, 0, 0.04) !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
            cursor: not-allowed !important;
            transform: none !important;
            backdrop-filter: blur(10px) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            height: 48px !important;
            min-height: 48px !important;
            line-height: 1.2 !important;
            padding: 0 16px !important;
            margin: 0 !important;
        }
        
        /* 禁用状态下的文字对齐 */
        .stButton>button:disabled span,
        .stButton>button[disabled] span {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
        }
        
        /* 点击效果 */
        .stButton>button:active:not(:disabled) {
            transform: translateY(0px) !important;
            box-shadow: 0 1px 8px rgba(0, 0, 0, 0.15) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 添加分割线
        st.markdown("""
        <div style="
            height: 1px;
            width: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.08), transparent);
            margin: 20px 0 24px;
        "></div>
        """, unsafe_allow_html=True)
    
    def render_menu_buttons(self, page_name: str):
        """渲染菜单按钮"""
        config = MENU_CONFIG.get(page_name)
        if not config or 'menu_items' not in config:
            return
        
        menu_items = config['menu_items']
        
        # 根据菜单项数量调整布局
        if len(menu_items) <= 3:
            cols = st.columns(len(menu_items))
        else:
            # 如果超过3个，使用2行布局
            cols = st.columns(3)
        
        for i, item in enumerate(menu_items):
            col_index = i % len(cols)
            
            with cols[col_index]:
                # 检查数据要求
                disabled = self._check_button_disabled(item['key'])
                
                if st.button(
                    f"{item['icon']} {item['title']}", 
                    key=f"menu_{item['key']}", 
                    disabled=disabled,
                    use_container_width=True,
                    help=item['description']
                ):
                    if not disabled:
                        self.page_manager.navigate_to(item['key'])
                
                # 显示描述文本和数据状态
                description_color = "#86868B" if not disabled else "#D1D1D6"
                status_text = self._get_button_status_text(item['key'], disabled)
                
                st.markdown(f"""
                <div style="text-align: center; color: {description_color}; font-size: 0.9rem; margin-top: 8px;">
                    {item['description']}
                </div>
                <div style="text-align: center; font-size: 0.8rem; margin-top: 4px; margin-bottom: 20px;">
                    {status_text}
                </div>
                """, unsafe_allow_html=True)
    
    def _check_button_disabled(self, page_key: str) -> bool:
        """检查按钮是否应该禁用"""
        from config.menu_config import DATA_REQUIREMENTS
        from core.state_manager import state_manager
        
        requirements = DATA_REQUIREMENTS.get(page_key, [])
        
        # 如果没有数据要求，则不禁用
        if not requirements:
            return False
        
        # 检查所有要求的数据是否可用
        for requirement in requirements:
            if not state_manager.has_data(requirement):
                return True
        
        return False
    
    def _get_button_status_text(self, page_key: str, disabled: bool) -> str:
        """获取按钮状态提示文本"""
        if not disabled:
            return '<span style="color: #30D158;">✅ 数据已就绪</span>'
        
        from config.menu_config import DATA_REQUIREMENTS
        
        requirements = DATA_REQUIREMENTS.get(page_key, [])
        if not requirements:
            return ""
        
        # 根据页面类型生成具体的提示信息
        data_names = {
            'score_df': '员工积分数据',
            'sales_df': '销售回款数据统计',
            'department_sales_df': '部门销售回款统计',
            'ranking_df': '销售回款超期账款排名'
        }
        
        missing_data = []
        for req in requirements:
            missing_data.append(data_names.get(req, req))
        
        return f'<span style="color: #FF453A;">❌ 需要：{", ".join(missing_data)}</span>'
    
    def render_data_status(self):
        """渲染数据状态信息"""
        from core.state_manager import state_manager
        
        summary = state_manager.get_data_summary()
        
        if summary['data_loaded']:
            st.success(f"✅ 已加载数据文件: {summary['file_name']}")
            
            # 显示数据统计
            cols = st.columns(4)
            with cols[0]:
                st.metric("员工数量", summary['employee_count'])
            with cols[1]:
                st.metric("团队数量", summary['team_count'])
            with cols[2]:
                st.metric("部门数量", summary['department_count']) 
            with cols[3]:
                st.metric("历史数据", summary['history_file_count'])
        else:
            st.warning("⚠️ 请上传数据文件以使用完整功能")


# 全局导航实例
navigation = Navigation() 