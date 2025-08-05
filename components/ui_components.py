"""
通用UI组件库
包含统一的样式和可复用的UI组件
"""

import streamlit as st
import pandas as pd
from html import escape


class UIComponents:
    """UI组件类"""
    
    @staticmethod
    def load_css():
        """加载全局CSS样式"""
        st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Text:wght@400;500&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=SF+Mono&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}

            :root {{
                --space-xxl: 4rem;
                --space-xl: 2.5rem;
                --space-lg: 1.8rem;
                --space-md: 1.2rem;
                --space-sm: 0.8rem;
                --space-xs: 0.4rem;

                --color-primary: #0A84FF;
                --color-secondary: #BF5AF2;
                --color-bg: #F5F5F7;
                --color-surface: #FFFFFF;
                --color-card: rgba(255, 255, 255, 0.92);
                --color-text-primary: #1D1D1F;
                --color-text-secondary: #86868B;
                --color-text-tertiary: #8E8E93;
                --color-accent-red: #FF453A;
                --color-accent-blue: #0A84FF;
                --color-accent-purple: #BF5AF2;
                --color-accent-green: #30D158;
                --color-accent-yellow: #FFD60A;

                --glass-bg: rgba(255, 255, 255, 0.85);
                --glass-border: rgba(0, 0, 0, 0.08);
                --glass-highlight: rgba(0, 0, 0, 0.05);
            }}

            body, .stApp {{
                background: var(--color-bg);
                color: var(--color-text-primary);
                font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
                min-height: 100vh;
                background-attachment: fixed;
                background-image: radial-gradient(circle at 15% 50%, rgba(10, 132, 255, 0.05), transparent 40%),
                                  radial-gradient(circle at 85% 30%, rgba(191, 90, 242, 0.05), transparent 40%);
            }}

            .stDeployButton {{ display: none; }}
            header[data-testid="stHeader"] {{ display: none; }}
            .stMainBlockContainer {{ padding-top: var(--space-xl); }}

            /* 玻璃卡片 */
            .glass-card {{
                background: var(--glass-bg);
                backdrop-filter: blur(20px) saturate(180%);
                -webkit-backdrop-filter: blur(20px) saturate(180%);
                border-radius: 18px;
                border: 0.5px solid var(--glass-border);
                box-shadow: 
                    0 12px 30px rgba(0, 0, 0, 0.05),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.5);
                padding: var(--space-lg);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1);
                position: relative;
                overflow: hidden;
            }}

            .glass-card:hover {{
                transform: translateY(-6px);
                box-shadow: 
                    0 20px 40px rgba(0, 0, 0, 0.08),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.7);
            }}

            /* 主标题 */
            .main-title {{
                text-align: center;
                font-family: 'SF Pro Display', sans-serif;
                font-weight: 700;
                font-size: 3.5rem;
                margin-bottom: var(--space-sm);
                background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.5px;
                line-height: 1.1;
            }}

            .main-subtitle {{
                text-align: center;
                font-family: 'SF Pro Text', sans-serif;
                font-size: 1.4rem;
                font-weight: 400;
                color: var(--color-text-secondary);
                max-width: 700px;
                margin: 0 auto var(--space-xl);
                line-height: 1.6;
            }}

            /* 节标题 */
            .section-title {{
                font-family: 'SF Pro Display', sans-serif;
                font-size: 2rem;
                font-weight: 700;
                margin: var(--space-xl) 0 var(--space-md);
                color: var(--color-text-primary);
                position: relative;
                padding-left: var(--space-md);
                letter-spacing: -0.5px;
            }}

            .section-title:before {{
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                height: 70%;
                width: 4px;
                background: linear-gradient(to bottom, var(--color-primary), var(--color-secondary));
                border-radius: 4px;
            }}

            /* 标签页样式 */
            div[data-testid="stTabs"] {{
                background: transparent;
                margin: var(--space-md) 0;
            }}

            div[data-testid="stTabs"] > div[data-testid="stMarkdown"] {{
                display: none;
            }}

            div[data-testid="stTabs"] button[role="tab"] {{
                height: 50px !important;
                padding: 0 24px !important;
                background: var(--glass-bg) !important;
                backdrop-filter: blur(10px) saturate(150%) !important;
                -webkit-backdrop-filter: blur(10px) saturate(150%) !important;
                border: 0.5px solid rgba(0, 0, 0, 0.08) !important;
                border-radius: 16px !important;
                margin-right: 12px !important;
                color: var(--color-text-primary) !important;
                font-family: 'SF Pro Text', sans-serif !important;
                font-weight: 500 !important;
                font-size: 1rem !important;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
                position: relative !important;
                overflow: hidden !important;
            }}

            div[data-testid="stTabs"] button[role="tab"]:hover {{
                transform: translateY(-2px) scale(1.02) !important;
                background: rgba(255, 255, 255, 0.95) !important;
                box-shadow: 0 8px 25px rgba(10, 132, 255, 0.15) !important;
                border-color: rgba(10, 132, 255, 0.2) !important;
                animation: tabHover 0.3s ease forwards !important;
            }}

            div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
                background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important;
                color: white !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 12px 30px rgba(10, 132, 255, 0.25) !important;
                border-color: transparent !important;
                animation: tabActive 0.4s ease forwards !important;
            }}

            div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]:hover {{
                transform: translateY(-3px) scale(1.02) !important;
                box-shadow: 0 15px 35px rgba(191, 90, 242, 0.3) !important;
            }}

            /* 标签页内容区域 */
            div[data-testid="stTabs"] div[data-baseweb="tab-panel"] {{
                background: transparent !important;
                padding: var(--space-lg) 0 !important;
                border: none !important;
            }}

            /* 标签页动画关键帧 */
            @keyframes tabHover {{
                0% {{
                    transform: translateY(0) scale(1);
                }}
                50% {{
                    transform: translateY(-1px) scale(1.01);
                }}
                100% {{
                    transform: translateY(-2px) scale(1.02);
                }}
            }}

            @keyframes tabActive {{
                0% {{
                    transform: translateY(0) scale(1);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                }}
                50% {{
                    transform: translateY(-2px) scale(1.02);
                    box-shadow: 0 8px 20px rgba(10, 132, 255, 0.2);
                }}
                100% {{
                    transform: translateY(-1px) scale(1);
                    box-shadow: 0 12px 30px rgba(10, 132, 255, 0.25);
                }}
            }}

            /* 按钮样式 */
            .stButton>button {{
                background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-family: 'SF Pro Text', sans-serif;
                font-weight: 500;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(10, 132, 255, 0.2);
            }}

            .stButton>button:hover {{
                transform: scale(1.03);
                box-shadow: 0 8px 20px rgba(191, 90, 242, 0.25);
            }}

            .stButton>button:disabled {{
                background: #E5E5EA;
                color: #8E8E93;
                transform: none;
                box-shadow: none;
            }}

            /* 文件上传器 */
            .stFileUploader > div > div {{
                background: var(--glass-bg) !important;
                border-radius: 18px !important;
                border: 0.5px solid rgba(0, 0, 0, 0.05) !important;
                padding: var(--space-md) !important;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.03) !important;
                backdrop-filter: blur(10px) !important;
            }}

            /* 数据框架 */
            .stDataFrame {{
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
                border: 0.5px solid rgba(0, 0, 0, 0.05);
                background: var(--glass-bg);
                backdrop-filter: blur(10px);
            }}

            /* 动画效果 */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @keyframes fadeInDown {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .fade-in {{
                animation: fadeIn 0.6s ease forwards;
            }}

            /* 红黑榜专用样式系统 */
            .leaderboard-container {{
                display: flex;
                gap: 25px;
                margin-top: 40px;
            }}
            
            .leaderboard-column {{
                flex: 1;
            }}
            
            .leaderboard-header {{
                text-align: center;
                padding-bottom: 20px;
                margin-bottom: 20px;
            }}
            
            .leaderboard-item {{
                display: flex;
                align-items: center;
                padding: 20px;
                margin-bottom: 20px;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 0.5px solid rgba(0, 0, 0, 0.05);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }}
            
            .leaderboard-item:hover {{
                transform: translateY(-6px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
            }}
            
            .rank {{
                font-family: 'SF Pro Display';
                font-size: 2.2rem;
                font-weight: 700;
                width: 60px;
                text-align: center;
                color: #0A84FF;
            }}
            
            .red-rank {{
                color: #FF453A;
            }}
            
            .black-rank {{
                color: #8E8E93;
            }}
            
            .medal {{
                font-size: 2rem;
                margin-left: 15px;
            }}
            
            .employee-name {{
                font-family: 'SF Pro Display';
                font-weight: 700;
                font-size: 1.5rem;
                margin-bottom: 4px;
                color: #1D1D1F;
            }}
            
            .employee-group {{
                font-family: 'SF Pro Text';
                font-size: 1rem;
                color: #86868B;
                margin-bottom: 12px;
            }}
            
            .red-title {{
                color: #FF453A !important;
            }}
            
            .black-title {{
                color: #8E8E93 !important;
            }}

            /* 头像样式系统 */
            .avatar-base {{
                width: 70px;
                height: 70px;
                border-radius: 50%;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 1.8rem;
                margin-right: 20px;
                flex-shrink: 0;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            }}
            
            .avatar {{
                background: linear-gradient(135deg, #0A84FF, #5E5CE6);
            }}
            
            .red-avatar {{
                background: linear-gradient(135deg, #FF453A, #FF375F);
            }}
            
            .black-avatar {{
                background: linear-gradient(135deg, #8E8E93, #636366);
            }}

            /* 积分统计页面专用样式系统 */
            .employee-card {{
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(20px);
                border-radius: 18px;
                padding: 25px;
                margin-bottom: 25px;
                border: 0.5px solid rgba(0, 0, 0, 0.05);
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.05);
            }}
            
            .employee-header {{
                text-align: center;
                padding-bottom: 20px;
                margin-bottom: 20px;
                border-bottom: 0.5px solid rgba(0, 0, 0, 0.05);
            }}
            
            .employee-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 25px;
            }}
            
            .stat-card {{
                background: rgba(255, 255, 255, 0.85);
                border-radius: 14px;
                padding: 20px;
                text-align: center;
                border: 0.5px solid rgba(0, 0, 0, 0.03);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
            }}
            
            .stat-value {{
                font-family: 'SF Pro Display';
                font-size: 2.2rem;
                font-weight: 700;
                margin: 15px 0;
                color: #0A84FF;
            }}
            
            .stat-label {{
                font-family: 'SF Pro Text';
                font-size: 1.05rem;
                color: #86868B;
            }}
            
            /* 小组排名样式 */
            .group-card {{
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border-radius: 18px;
                padding: 25px;
                margin-bottom: 25px;
                border: 0.5px solid rgba(0, 0, 0, 0.05);
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.05);
            }}
            
            .group-header {{
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 0.5px solid rgba(0, 0, 0, 0.05);
            }}
            
            .group-badge {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #0A84FF, #5E5CE6);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 1.5rem;
                margin-right: 20px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            }}
            
            .red-badge {{
                background: linear-gradient(135deg, #FF453A, #FF375F);
            }}
            
            .black-badge {{
                background: linear-gradient(135deg, #8E8E93, #636366);
            }}
            
            .gold {{
                color: #FFD60A;
                font-weight: 700;
            }}
            
            .silver {{
                color: #8E8E93;
                font-weight: 700;
            }}
            
            .bronze {{
                color: #FF9F0A;
                font-weight: 700;
            }}
            
            .member-card {{
                display: flex;
                align-items: center;
                padding: 15px;
                background: rgba(255, 255, 255, 0.85);
                border-radius: 14px;
                margin-bottom: 15px;
                border: 0.5px solid rgba(0, 0, 0, 0.03);
                transition: all 0.3s ease;
            }}
            
            .member-card:hover {{
                transform: translateY(-3px);
                background: rgba(255, 255, 255, 0.95);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            }}
            
            .member-avatar {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #0A84FF, #5E5CE6);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                margin-right: 15px;
                flex-shrink: 0;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }}

            /* 帮助系统组件 */
            .ui-header-container {{
                position: relative;
                text-align: center;
                margin-bottom: 2rem;
            }}
            
            .ui-help-button {{
                position: absolute;
                top: 0;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--color-primary), #5E5CE6);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                font-weight: 600;
                cursor: help;
                box-shadow: 0 4px 12px rgba(10, 132, 255, 0.3);
                transition: all 0.3s ease;
                z-index: 1000;
                font-family: 'SF Pro Text', sans-serif;
            }}
            
            .ui-help-button.position-right {{
                right: 20px;
            }}
            
            .ui-help-button.position-left {{
                left: 20px;
            }}
            
            .ui-help-button.position-center {{
                left: 50%;
                transform: translateX(-50%);
            }}
            
            .ui-help-button:hover {{
                transform: scale(1.1);
                box-shadow: 0 6px 16px rgba(10, 132, 255, 0.4);
            }}
            
            .ui-help-button.position-center:hover {{
                transform: translateX(-50%) scale(1.1);
            }}
            
            .ui-help-tooltip {{
                visibility: hidden !important;
                opacity: 0 !important;
                width: 320px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                color: var(--color-text-primary);
                text-align: left;
                border-radius: 12px;
                padding: 16px;
                position: absolute;
                z-index: 1001;
                top: 50px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                transition: opacity 0.3s ease, visibility 0.3s ease;
                font-family: 'SF Pro Text', sans-serif;
                font-size: 0.9rem;
                line-height: 1.4;
                pointer-events: none;
            }}
            
            .ui-help-tooltip.position-right {{
                right: 0;
            }}
            
            .ui-help-tooltip.position-left {{
                left: 0;
            }}
            
            .ui-help-tooltip.position-center {{
                left: 50%;
                transform: translateX(-50%);
            }}
            
            .ui-help-button:hover .ui-help-tooltip {{
                visibility: visible !important;
                opacity: 1 !important;
                pointer-events: auto;
            }}
            
            /* 功能区域组件 */
            .ui-function-area {{
                background: var(--glass-bg);
                border-radius: 18px;
                padding: var(--space-xl);
                border: 0.5px solid rgba(0, 0, 0, 0.05);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
                backdrop-filter: blur(10px);
                margin-bottom: var(--space-lg);
            }}
            
            .ui-function-title {{
                text-align: center;
                margin-bottom: 1.5rem;
                font-size: 1.8rem;
                font-weight: 600;
                font-family: 'SF Pro Display', sans-serif;
            }}
            
            .ui-function-description {{
                color: var(--color-text-secondary);
                font-size: 1.1rem;
                text-align: center;
                font-family: 'SF Pro Text', sans-serif;
            }}

            /* 页脚 */
            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.9);
                color: var(--color-text-secondary);
                padding: var(--space-sm) 0;
                text-align: center;
                font-size: 0.9rem;
                z-index: 100;
                backdrop-filter: blur(10px);
                border-top: 0.5px solid rgba(0, 0, 0, 0.05);
                font-family: 'SF Pro Text', sans-serif;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_card(title: str, content: str, icon: str = "", delay: float = 0.1):
        """渲染玻璃卡片"""
        st.markdown(f"""
        <div class="glass-card fade-in" style="animation-delay: {delay}s;">
            <h3 style="text-align: center; color: #0A84FF; margin-bottom: 1.5rem; font-size: 1.8rem;">
                {icon} {escape(title)}
            </h3>
            <div style="color: #86868B; font-size: 1.1rem; text-align: center;">
                {escape(content)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_divider():
        """渲染分割线"""
        st.markdown("""
        <div style="
            height: 0.5px;
            width: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.08), transparent);
            margin: var(--space-md) 0;
        "></div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """渲染页脚"""
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            销售积分红黑榜系统 | © 2025 销售绩效评估中心 | 版本 3.0 - 重构版
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def format_amount(value, unit="万元"):
        """智能金额格式化"""
        if pd.isna(value) or value is None:
            return "-"
        if value == int(value):
            return f"{int(value):,}{unit}"
        formatted = f"{value:,.2f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return f"{formatted}{unit}"
    
    @staticmethod
    def create_avatar(name: str, color: str = "default"):
        """创建员工头像"""
        name_str = str(name) if name else ""
        initials = ''.join([n[0] for n in name_str.split() if n])[:2]
        if not initials:
            initials = name_str[:2] if len(name_str) >= 2 else name_str
        if not initials:
            initials = "US"

        # 使用统一的CSS类，避免重复注入样式
        color_class = "avatar-base avatar"
        if color == "red":
            color_class = "avatar-base red-avatar"
        elif color == "black":
            color_class = "avatar-base black-avatar"
        
        return f'<div class="{color_class}">{escape(initials)}</div>'
    
    @staticmethod
    def get_progress_color(progress: float) -> str:
        """根据完成进度获取颜色"""
        if progress >= 1.0:
            return '#30D158'  # 绿色
        elif progress >= 0.66:
            return '#FFD60A'  # 黄色
        else:
            return '#FF453A'  # 红色
    
    @staticmethod
    def render_page_header(title: str, subtitle: str = "", help_content: str = None, position: str = "right"):
        """
        渲染页面头部组件（包含标题、副标题和可选的帮助按钮）
        
        Args:
            title: 主标题
            subtitle: 副标题（可选）
            help_content: 帮助内容（HTML格式，可选）
            position: 帮助按钮位置 ("right", "left", "center")
        """
        # 构建副标题HTML
        subtitle_html = ""
        if subtitle:
            subtitle_html = f'<div class="main-subtitle">{escape(subtitle)}</div>'
        
        # 构建帮助按钮HTML
        help_button_html = ""
        if help_content:
            # 简化content处理，只去掉前后空白
            clean_content = help_content.strip()
            help_button_html = f'<div class="ui-help-button position-{position}">?<div class="ui-help-tooltip position-{position}">{clean_content}</div></div>'
        
        # 组合完整的HTML
        full_html = f"""
        <div class="ui-header-container">
            <div class="main-title">{escape(title)}</div>
            {subtitle_html}
            {help_button_html}
        </div>
        """
        
        st.markdown(full_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_help_button(content: str, position: str = "right"):
        """
        渲染独立的帮助按钮组件
        
        Args:
            content: 帮助内容（HTML格式）
            position: 按钮位置 ("right", "left", "center")
        """
        # 清理内容，保留HTML结构
        clean_content = content.strip().replace('\n        ', '\n').replace('\n    ', '\n').strip()
        
        st.markdown(f"""
        <div style="position: relative; display: inline-block;">
            <div class="ui-help-button position-{position}">
                ?
                <div class="ui-help-tooltip position-{position}">
                    {clean_content}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_function_area(title: str, icon: str = "", description: str = "", delay: float = 0.1):
        """
        渲染功能区域组件
        
        Args:
            title: 区域标题
            icon: 图标（emoji或文本）
            description: 描述文字（可选）
            delay: 动画延迟时间
        """
        icon_text = f"{icon} " if icon else ""
        description_html = ""
        if description:
            description_html = f'<div class="ui-function-description">{escape(description)}</div>'
        
        st.markdown(f"""
        <div class="ui-function-area fade-in" style="animation-delay: {delay}s;">
            <div class="ui-function-title" style="color: var(--color-secondary);">
                {icon_text}{escape(title)}
            </div>
            {description_html}
        </div>
        """, unsafe_allow_html=True)


# 全局UI组件实例
ui = UIComponents() 