"""
菜单配置文件
定义系统的页面配置、路由映射和数据依赖关系
"""

# 菜单配置 - 定义页面层次结构和菜单项
MENU_CONFIG = {
    "home": {
        "title": "主页",
        "icon": "🏠",
        "description": "销售积分红黑榜系统主页",
        "show_in_nav": True,
        "order": 0
    },
    "score_center": {
        "title": "积分中心",
        "icon": "🏆",
        "description": "员工积分统计与团队排名分析",
        "show_in_nav": True,
        "order": 1,
        "menu_items": [
            {
                "key": "leaderboard",
                "title": "红黑榜",
                "icon": "🏆",
                "description": "查看月度团队红黑榜排名和绩效对比"
            },
            {
                "key": "scores",
                "title": "积分统计",
                "icon": "📊",
                "description": "查看员工积分详细统计和分析"
            }
        ]
    },
    "sales_center": {
        "title": "销售中心",
        "icon": "💰",
        "description": "销售数据统计与回款分析",
        "show_in_nav": True,
        "order": 2,
        "menu_items": [
            {
                "key": "ranking",
                "title": "销售回款排名",
                "icon": "📈",
                "description": "查看销售回款超期账款排名分析"
            },
            {
                "key": "sales",
                "title": "员工销售统计",
                "icon": "👥",
                "description": "查看员工销售业绩和回款统计"
            },
            {
                "key": "department_sales",
                "title": "部门销售统计", 
                "icon": "🏢",
                "description": "查看部门销售业绩和回款统计"
            }
        ]
    },
    "history_compare": {
        "title": "历史对比",
        "icon": "📅",
        "description": "历史数据对比分析",
        "show_in_nav": True,
        "order": 3
    },
    # 子页面配置
    "leaderboard": {
        "title": "红黑榜",
        "icon": "🏆",
        "description": "月度团队红黑榜排名",
        "parent": "score_center",
        "show_in_nav": False
    },
    "scores": {
        "title": "积分统计",
        "icon": "📊", 
        "description": "员工积分详细统计",
        "parent": "score_center",
        "show_in_nav": False
    },
    "sales": {
        "title": "员工销售统计",
        "icon": "👥",
        "description": "员工销售业绩统计",
        "parent": "sales_center", 
        "show_in_nav": False
    },
    "ranking": {
        "title": "销售回款排名",
        "icon": "📈",
        "description": "销售回款超期账款排名分析",
        "parent": "sales_center",
        "show_in_nav": False
    },
    "department_sales": {
        "title": "部门销售统计",
        "icon": "🏢",
        "description": "部门销售业绩统计",
        "parent": "sales_center",
        "show_in_nav": False
    },
    "overall_trends": {
        "title": "总体趋势",
        "icon": "📈",
        "description": "总体趋势分析",
        "parent": "history_compare",
        "show_in_nav": False
    },
    "employee_details": {
        "title": "员工详情",
        "icon": "👥",
        "description": "员工详情分析",
        "parent": "history_compare",
        "show_in_nav": False
    },
    "department_details": {
        "title": "部门详情",
        "icon": "🏢",
        "description": "部门详情分析",
        "parent": "history_compare",
        "show_in_nav": False
    }
}

# 路由配置 - 页面名称到模块路径的映射
ROUTES = {
    "home": "pages.home",
    "score_center": "pages.score_center",
    "sales_center": "pages.sales_center", 
    "leaderboard": "pages.leaderboard",
    "scores": "pages.scores",
    "sales": "pages.sales",
    "department_sales": "pages.department_sales",
    "ranking": "pages.ranking",
    "history_compare": "pages.history_compare",
    "overall_trends": "pages.overall_trends",
    "employee_details": "pages.employee_details",
    "department_details": "pages.department_details"
}

# 数据依赖配置 - 每个页面需要的数据类型
DATA_REQUIREMENTS = {
    "home": [],  # 主页不需要特定数据
    "score_center": [],  # 中心页面不需要特定数据，由子页面决定
    "sales_center": [],  # 中心页面不需要特定数据，由子页面决定
    "leaderboard": ["score_df"],  # 红黑榜需要积分数据
    "scores": ["score_df"],  # 积分统计需要积分数据
    "sales": ["sales_df"],  # 员工销售统计需要销售数据
    "department_sales": ["department_sales_df"],  # 部门销售统计需要部门销售数据
    "ranking": ["ranking_df"],  # 排名需要排名数据
    "history_compare": [],  # 历史对比主页面不需要特定数据
    "overall_trends": [],  # 总体趋势需要历史数据（通过state_manager获取）
    "employee_details": [],  # 员工详情需要历史数据（通过state_manager获取）
    "department_details": []  # 部门详情需要历史数据（通过state_manager获取）
} 