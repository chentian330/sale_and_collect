"""
数据加载器
处理Excel文件的加载和解析
"""

import pandas as pd
import streamlit as st
import os
import glob
import warnings
from typing import Tuple, Optional

# 忽略警告
warnings.filterwarnings('ignore')

# 列名常量定义
LAST_MONTH_SALES_COL = "上月销售额"
LAST_MONTH_PAYMENT_COL = "上月回款额"


class DataLoader:
    """数据加载器类"""
    
    @staticmethod
    def auto_detect_excel_file() -> Optional[str]:
        """
        自动检测Excel文件
        
        Returns:
            文件路径或None
        """
        try:
            pattern = "员工销售回款统计_*.xlsx"
            files = glob.glob(pattern)
            if files:
                latest_file = max(files, key=os.path.getctime)
                return latest_file
            return None
        except Exception as e:
            st.error(f"文件检测出错: {e}")
            return None
    
    @staticmethod
    def load_excel_data(file_path) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], 
                                           Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[str]]:
        """
        加载Excel数据 - 智能兼容模式，基本验证+工作表可选
        
        Args:
            file_path: 文件路径或上传的文件对象
            
        Returns:
            (score_df, sales_df, department_sales_df, ranking_df, error_message)
            
        Basic Requirement:
            - 文件必须包含至少一个预期的工作表，否则认为是错误文件
            
        Sheet Requirements (Optional but at least one required):
            - 员工积分数据 (可选) - 启用积分中心功能
            - 销售回款数据统计 (可选) - 启用员工销售统计功能
            - 部门销售回款统计 (可选) - 启用部门销售统计功能
            - 销售回款超期账款排名 (可选) - 启用销售回款排名功能
            
        Note: 
            - 如果没有任何预期工作表，返回错误提示上传正确文件
            - 如果有至少一个预期工作表，系统智能启用对应功能
            - 各工作表独立加载，支持部分工作表缺失的情况
        """
        try:
            # 检查文件中包含的工作表
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
            available_sheets = excel_file.sheet_names
            
            # 检查是否包含任何预期的工作表
            expected_sheets = ['员工积分数据', '销售回款数据统计', '部门销售回款统计', '销售回款超期账款排名']
            has_any_expected_sheet = any(sheet in available_sheets for sheet in expected_sheets)
            
            if not has_any_expected_sheet:
                return None, None, None, None, "请上传员工销售回款统计_XXXX年X月.xlsx文件，文件中应包含以下工作表之一：员工积分数据、销售回款数据统计、部门销售回款统计、销售回款超期账款排名"
            
            # Load score_df (可选)
            score_df = None
            if '员工积分数据' in available_sheets:
                try:
                    score_df = pd.read_excel(file_path, sheet_name='员工积分数据', engine='openpyxl')
                    # 验证必要列是否存在
                    if '队名' not in score_df.columns:
                        score_df = None  # 如果缺少必要列，将数据设为None
                except Exception as e:
                    score_df = None

            # Load sales_df (可选)
            sales_df = None
            if '销售回款数据统计' in available_sheets:
                try:
                    sales_df = pd.read_excel(file_path, sheet_name='销售回款数据统计', engine='openpyxl')
                except Exception as e:
                    sales_df = None

            # Load department_sales_df (可选)
            department_sales_df = None
            if '部门销售回款统计' in available_sheets:
                try:
                    department_sales_df = pd.read_excel(file_path, sheet_name='部门销售回款统计', engine='openpyxl')
                except Exception as e:
                    department_sales_df = None

            # Load ranking_df (可选)
            ranking_df = None
            if '销售回款超期账款排名' in available_sheets:
                try:
                    ranking_df = pd.read_excel(file_path, sheet_name='销售回款超期账款排名', engine='openpyxl')
                except Exception as e:
                    ranking_df = None

            return score_df, sales_df, department_sales_df, ranking_df, None
        except Exception as e:
            return None, None, None, None, f"读取文件时出错: {str(e)}"
    
    @staticmethod
    def get_group_data(score_df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        获取小组数据
        
        Args:
            score_df: 积分数据DataFrame
            
        Returns:
            小组数据DataFrame或None
        """
        if score_df is None or score_df.empty:
            return None

        if '队名' not in score_df.columns:
            st.error("数据中缺少'队名'列")
            return None

        valid_data = score_df.dropna(subset=['队名'])
        if valid_data.empty:
            st.error("所有记录的队名都为空")
            return None

        group_data = valid_data[['队名', '加权小组总分']].drop_duplicates().sort_values(by='加权小组总分', ascending=False)
        group_data['排名'] = range(1, len(group_data) + 1)

        return group_data
    
    @staticmethod
    def get_leaderboard_data(score_df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        获取红黑榜数据
        
        Args:
            score_df: 积分数据DataFrame
            
        Returns:
            (red_df, black_df, group_data)
        """
        if score_df is None or score_df.empty:
            return None, None, None
        
        group_data = DataLoader.get_group_data(score_df)
        if group_data is None:
            return None, None, None
        
        red_groups = group_data.head(2)['队名'].tolist()
        red_df = score_df[score_df['队名'].isin(red_groups)].sort_values(by='个人总积分', ascending=False)
        
        black_groups = group_data.tail(2)['队名'].tolist()
        black_df = score_df[score_df['队名'].isin(black_groups)].sort_values(by='个人总积分', ascending=True)
        
        return red_df, black_df, group_data
    
    @staticmethod
    def validate_uploaded_file(file_obj) -> Tuple[bool, str]:
        """
        验证上传的文件
        
        Args:
            file_obj: 上传的文件对象
            
        Returns:
            (is_valid, message)
        """
        if file_obj is None:
            return False, "未选择文件"
        
        if not file_obj.name.endswith('.xlsx'):
            return False, "文件格式必须为Excel(.xlsx)"
        
        if file_obj.size > 50 * 1024 * 1024:  # 50MB限制
            return False, "文件大小不能超过50MB"
        
        return True, "文件验证通过"
    
    @staticmethod
    def get_sheet_names(file_path) -> list:
        """
        获取Excel文件的工作表名称
        
        Args:
            file_path: 文件路径
            
        Returns:
            工作表名称列表
        """
        try:
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
            return excel_file.sheet_names
        except Exception as e:
            st.error(f"读取工作表名称失败: {e}")
            return []
    
    @staticmethod
    def get_data_info(score_df: pd.DataFrame, sales_df: pd.DataFrame = None) -> dict:
        """
        获取数据信息摘要
        
        Args:
            score_df: 积分数据
            sales_df: 销售数据
            
        Returns:
            数据信息字典
        """
        info = {
            "total_employees": 0,
            "total_teams": 0,
            "month_info": "未知",
            "has_sales_data": False,
            "sales_employees": 0
        }
        
        if score_df is not None and not score_df.empty:
            info["total_employees"] = len(score_df['员工姓名'].unique())
            if '队名' in score_df.columns:
                info["total_teams"] = len(score_df['队名'].unique())
            if '统计月份' in score_df.columns:
                month_values = score_df['统计月份'].unique()
                if len(month_values) > 0 and pd.notna(month_values[0]):
                    info["month_info"] = str(month_values[0])
        
        if sales_df is not None and not sales_df.empty:
            info["has_sales_data"] = True
            info["sales_employees"] = len(sales_df['员工姓名'].unique())
            if '统计月份' in sales_df.columns and info["month_info"] == "未知":
                month_values = sales_df['统计月份'].unique()
                if len(month_values) > 0 and pd.notna(month_values[0]):
                    info["month_info"] = str(month_values[0])
        
        return info


# 全局数据加载器实例
data_loader = DataLoader() 