"""
页面管理器
统一管理页面注册、跳转和导航逻辑
"""

import streamlit as st
import importlib
from typing import Optional, Dict, Any
from config.menu_config import MENU_CONFIG, ROUTES, DATA_REQUIREMENTS


class PageManager:
    """页面管理器类"""
    
    def __init__(self):
        self.current_page = "home"
        self.page_stack = ["home"]  # 页面栈，用于实现返回功能
        self.pages = {}  # 已加载的页面缓存
        self.action_history = []  # 操作历史记录，用于撤销功能
    
    def navigate_to(self, page_name: str, add_to_stack: bool = True):
        """
        导航到指定页面
        
        Args:
            page_name: 页面名称
            add_to_stack: 是否添加到页面栈
        """
        if page_name in ROUTES:
            # 检查数据要求
            if self._check_data_requirements(page_name):
                # 记录操作到历史记录（用于撤销）
                previous_page = self.current_page
                self._record_action({
                    'type': 'navigate',
                    'from_page': previous_page,
                    'to_page': page_name,
                    'previous_stack': self.page_stack.copy()
                })
                
                self.current_page = page_name
                st.session_state.current_page = page_name
                
                if add_to_stack and (not self.page_stack or self.page_stack[-1] != page_name):
                    self.page_stack.append(page_name)
                    st.session_state.page_stack = self.page_stack
                
                st.rerun()
            else:
                st.error("请先上传所需的数据文件")
        else:
            st.error(f"页面 {page_name} 不存在")
    
    def go_back(self):
        """返回上一个页面"""
        if len(self.page_stack) > 1:
            self.page_stack.pop()  # 移除当前页面
            previous_page = self.page_stack[-1]
            self.navigate_to(previous_page, add_to_stack=False)
        else:
            self.navigate_to("home", add_to_stack=False)
    
    def go_home(self):
        """返回主页"""
        self.page_stack = ["home"]
        st.session_state.page_stack = self.page_stack
        self.navigate_to("home", add_to_stack=False)
    
    def get_current_page(self) -> str:
        """获取当前页面"""
        return st.session_state.get('current_page', 'home')
    
    def get_page_config(self, page_name: str) -> Optional[Dict[str, Any]]:
        """获取页面配置"""
        return MENU_CONFIG.get(page_name)
    
    def get_breadcrumb(self) -> list:
        """获取面包屑导航"""
        current = self.get_current_page()
        breadcrumb = []
        
        # 添加主页
        breadcrumb.append({"name": "home", "label": "主页", "icon": "🏠"})
        
        if current != "home":
            # 查找父页面
            config = self.get_page_config(current)
            if config and "parent" in config:
                parent_config = self.get_page_config(config["parent"])
                if parent_config:
                    breadcrumb.append({
                        "name": config["parent"], 
                        "label": parent_config["title"],
                        "icon": parent_config.get("icon", "📂")
                    })
            
            # 添加当前页面
            if config:
                breadcrumb.append({
                    "name": current,
                    "label": config.get("title", current),
                    "icon": config.get("icon", "📄")
                })
            else:
                # 如果没有配置，从菜单项中查找
                for page_key, page_config in MENU_CONFIG.items():
                    if "menu_items" in page_config:
                        for item in page_config["menu_items"]:
                            if item["key"] == current:
                                breadcrumb.append({
                                    "name": current,
                                    "label": item["label"], 
                                    "icon": item["icon"]
                                })
                                break
        
        return breadcrumb
    
    def load_page(self, page_name: str):
        """动态加载页面模块"""
        if page_name in self.pages:
            return self.pages[page_name]
        
        try:
            module_path = ROUTES.get(page_name)
            if module_path:
                module = importlib.import_module(module_path)
                self.pages[page_name] = module
                return module
        except ImportError as e:
            st.error(f"无法加载页面 {page_name}: {e}")
            return None
    
    def render_current_page(self):
        """渲染当前页面"""
        current_page = self.get_current_page()
        page_module = self.load_page(current_page)
        
        if page_module and hasattr(page_module, 'show'):
            page_module.show()
        else:
            st.error(f"页面 {current_page} 缺少 show() 函数")
    
    def _check_data_requirements(self, page_name: str) -> bool:
        """检查页面的数据要求是否满足"""
        requirements = DATA_REQUIREMENTS.get(page_name, [])
        
        for requirement in requirements:
            if requirement not in st.session_state or st.session_state[requirement] is None:
                return False
        
        return True
    
    def initialize_from_session(self):
        """从session state初始化页面状态"""
        if 'current_page' in st.session_state:
            self.current_page = st.session_state.current_page
        
        if 'page_stack' in st.session_state:
            self.page_stack = st.session_state.page_stack
        else:
            st.session_state.page_stack = self.page_stack
            
        if 'action_history' in st.session_state:
            self.action_history = st.session_state.action_history
        else:
            st.session_state.action_history = self.action_history
    
    def _record_action(self, action: Dict[str, Any]):
        """记录操作到历史记录"""
        # 限制历史记录数量，避免内存过多占用
        max_history = 10
        
        if len(self.action_history) >= max_history:
            self.action_history.pop(0)  # 移除最旧的记录
        
        self.action_history.append(action)
        st.session_state.action_history = self.action_history
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return len(self.action_history) > 0
    
    def undo_last_action(self):
        """撤销上一个操作"""
        if not self.can_undo():
            st.warning("没有可撤销的操作")
            return
        
        last_action = self.action_history.pop()
        st.session_state.action_history = self.action_history
        
        if last_action['type'] == 'navigate':
            # 撤销页面导航
            self.current_page = last_action['from_page']
            st.session_state.current_page = self.current_page
            
            # 恢复之前的页面栈
            self.page_stack = last_action['previous_stack']
            st.session_state.page_stack = self.page_stack
            
            st.success(f"已撤销导航操作：{last_action['to_page']} → {last_action['from_page']}")
            st.rerun()
        elif last_action['type'] == 'data_upload':
            # 撤销数据上传
            from core.state_manager import state_manager
            
            previous_data = last_action['previous_data']
            
            # 恢复之前的数据状态
            state_manager.set_data('score_df', previous_data['score_df'])
            state_manager.set_data('sales_df', previous_data['sales_df'])
            state_manager.set_data('department_sales_df', previous_data['department_sales_df'])
            state_manager.set_data('ranking_df', previous_data['ranking_df'])
            
            if previous_data['file_name']:
                state_manager.set_file_name(previous_data['file_name'])
            else:
                # 如果之前没有文件，清空文件名
                st.session_state.file_name = None
            
            st.success(f"已撤销数据上传操作：{last_action['file_name']}")
            st.rerun()
        else:
            st.warning(f"不支持撤销操作类型: {last_action['type']}")


# 全局页面管理器实例
page_manager = PageManager() 