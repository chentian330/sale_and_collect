"""
状态管理器
集中管理应用状态和数据
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any


class StateManager:
    """应用状态管理器"""
    
    def __init__(self):
        self._initialize_state()
    
    def _initialize_state(self):
        """初始化应用状态"""
        # 页面状态
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
        
        if 'page_stack' not in st.session_state:
            st.session_state.page_stack = ['home']
        
        # 数据加载状态
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        
        if 'file_name' not in st.session_state:
            st.session_state.file_name = None
        
        # 数据存储
        self._initialize_data_state()
        
        # 历史数据状态
        if 'history_files' not in st.session_state:
            st.session_state.history_files = {}
    
    def _initialize_data_state(self):
        """初始化数据状态"""
        data_keys = [
            'score_df', 'sales_df', 'department_sales_df', 'ranking_df'
        ]
        
        for key in data_keys:
            if key not in st.session_state:
                st.session_state[key] = None
    
    # 数据管理方法
    def set_data(self, key: str, data: Any):
        """设置数据"""
        st.session_state[key] = data
        
        # 检查是否有任何数据被加载
        if key in ['score_df', 'sales_df', 'department_sales_df', 'ranking_df']:
            has_any_data = any([
                self.has_data('score_df'),
                self.has_data('sales_df'),
                self.has_data('department_sales_df'),
                self.has_data('ranking_df')
            ])
            st.session_state.data_loaded = has_any_data
    
    def get_data(self, key: str) -> Any:
        """获取数据"""
        return st.session_state.get(key)
    
    def clear_data(self):
        """清空所有数据"""
        data_keys = [
            'score_df', 'sales_df', 'department_sales_df', 'ranking_df'
        ]
        
        for key in data_keys:
            st.session_state[key] = None
        
        st.session_state.data_loaded = False
        st.session_state.file_name = None
    
    def is_data_loaded(self) -> bool:
        """检查数据是否已加载"""
        return st.session_state.get('data_loaded', False)
    
    def has_data(self, key: str) -> bool:
        """检查特定数据是否已加载"""
        data = st.session_state.get(key)
        return data is not None and not data.empty if hasattr(data, 'empty') else data is not None
    
    def can_access_score_center(self) -> bool:
        """检查是否可以访问积分中心"""
        return self.has_data('score_df')
    
    def can_access_sales_center(self) -> bool:
        """检查是否可以访问销售回款中心"""
        return (self.has_data('sales_df') or 
                self.has_data('department_sales_df') or 
                self.has_data('ranking_df'))
    
    def get_available_sales_functions(self) -> list:
        """获取可用的销售功能列表"""
        functions = []
        if self.has_data('ranking_df'):
            functions.append('ranking')
        if self.has_data('sales_df'):
            functions.append('sales')
        if self.has_data('department_sales_df'):
            functions.append('department_sales')
        return functions
    
    def get_file_name(self) -> Optional[str]:
        """获取当前加载的文件名"""
        return st.session_state.get('file_name')
    
    def set_file_name(self, file_name: str):
        """设置当前文件名"""
        st.session_state.file_name = file_name
    
    # 历史数据管理
    def add_history_file(self, month_key: str, file_info: Dict[str, Any]):
        """添加历史数据文件"""
        if 'history_files' not in st.session_state:
            st.session_state.history_files = {}
        
        st.session_state.history_files[month_key] = file_info
    
    def get_history_files(self) -> Dict[str, Any]:
        """获取历史数据文件"""
        return st.session_state.get('history_files', {})
    
    def remove_history_file(self, month_key: str):
        """删除历史数据文件"""
        if 'history_files' in st.session_state and month_key in st.session_state.history_files:
            del st.session_state.history_files[month_key]
    
    def clear_history_files(self):
        """清空所有历史数据"""
        st.session_state.history_files = {}
    
    # 页面状态管理
    def set_current_page(self, page_name: str):
        """设置当前页面"""
        st.session_state.current_page = page_name
    
    def get_current_page(self) -> str:
        """获取当前页面"""
        return st.session_state.get('current_page', 'home')
    
    def add_to_page_stack(self, page_name: str):
        """添加页面到栈"""
        if 'page_stack' not in st.session_state:
            st.session_state.page_stack = ['home']
        
        if not st.session_state.page_stack or st.session_state.page_stack[-1] != page_name:
            st.session_state.page_stack.append(page_name)
    
    def get_page_stack(self) -> list:
        """获取页面栈"""
        return st.session_state.get('page_stack', ['home'])
    
    def pop_page_stack(self) -> Optional[str]:
        """从页面栈弹出"""
        page_stack = st.session_state.get('page_stack', ['home'])
        if len(page_stack) > 1:
            page_stack.pop()
            return page_stack[-1]
        return 'home'
    
    # 数据验证方法
    def validate_score_data(self, df: pd.DataFrame) -> tuple[bool, str]:
        """验证积分数据"""
        if df is None or df.empty:
            return False, "数据为空"
        
        required_columns = ['员工姓名', '队名', '个人总积分', '加权小组总分']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"缺少必要列: {', '.join(missing_columns)}"
        
        return True, "数据验证通过"
    
    def validate_sales_data(self, df: pd.DataFrame) -> tuple[bool, str]:
        """验证销售数据"""
        if df is None or df.empty:
            return False, "数据为空"
        
        required_columns = ['员工姓名', '本月销售额', '本月回款合计']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"缺少必要列: {', '.join(missing_columns)}"
        
        return True, "数据验证通过"
    
    # 数据统计方法
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要"""
        summary = {
            "data_loaded": self.is_data_loaded(),
            "file_name": self.get_file_name(),
            "employee_count": 0,
            "team_count": 0,
            "department_count": 0,
            "history_file_count": len(self.get_history_files())
        }
        
        # 统计员工数量
        score_df = self.get_data('score_df')
        if score_df is not None and not score_df.empty:
            summary["employee_count"] = len(score_df['员工姓名'].unique())
            if '队名' in score_df.columns:
                summary["team_count"] = len(score_df['队名'].unique())
        
        # 统计部门数量
        dept_df = self.get_data('department_sales_df')
        if dept_df is not None and not dept_df.empty and '部门' in dept_df.columns:
            summary["department_count"] = len(dept_df['部门'].unique()) - 1  # 排除合计行
        
        return summary


# 全局状态管理器实例
state_manager = StateManager() 