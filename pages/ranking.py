"""
销售回款排名页面
基于销售回款超期账款排名数据的可视化分析
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from components.navigation import navigation
from components.ui_components import ui
from core.state_manager import state_manager


def show():
    """显示销售回款排名页面"""
    # 渲染导航栏
    navigation.render_navigation_bar()
    
    # 渲染面包屑
    navigation.render_breadcrumb()
    
    # 渲染标题区域（包含帮助按钮）
    _render_header_with_help()
    
    # 检查数据
    ranking_df = state_manager.get_data('ranking_df')
    
    if ranking_df is None:
        st.error("请先上传包含'销售回款超期账款排名'工作表的数据文件")
        return
    
    # 显示各种柱状图分析
    _display_weekly_sales_chart(ranking_df)
    _display_weekly_payment_chart(ranking_df)
    _display_monthly_data_chart(ranking_df)
    _display_overdue_warning_chart(ranking_df)





def _render_header_with_help():
    """渲染标题区域和帮助按钮"""
    help_content = """
        <h4 style="margin: 0 0 12px 0; color: #0A84FF;">🏆 排名图标说明</h4>
        <p style="margin: 0 0 8px 0;"><strong>🥇 金牌</strong> - 第一名，表现优秀</p>
        <p style="margin: 0 0 8px 0;"><strong>🥈 银牌</strong> - 第二名，表现良好</p>
        <p style="margin: 0 0 12px 0;"><strong>🥉 铜牌</strong> - 第三名，表现不错</p>
        <h4 style="margin: 0 0 8px 0; color: #FF9500;">⚠️ 警示说明</h4>
        <p style="margin: 0 0 8px 0;"><strong>⚠️ 橙色警示</strong> - 排名后三位需要改进</p>
        <p style="margin: 0 0 8px 0;"><strong>条件</strong> - 仅在总人数≥6人时显示警示图标</p>
        <p style="margin: 0 0 12px 0;"><strong>目的</strong> - 激励团队提升整体表现</p>
        <h4 style="margin: 0 0 8px 0; color: #FF3B30;">🚨 逾期警示颜色</h4>
        <p style="margin: 0;"><strong style="color: #FF3B30;">深红色</strong> - 逾期金额较大，重点关注<br/>
        <strong style="color: #FF9500;">橙色</strong> - 逾期金额中等，及时跟进<br/>
        <strong style="color: #FFCC00;">黄色</strong> - 逾期金额较小，仍需关注</p>
    """
    
    ui.render_page_header(
        title="📈 销售回款排名分析",
        subtitle="基于Excel数据的多维度排名分析与绩效评估",
        help_content=help_content,
        position="right"
    )


def _display_weekly_sales_chart(df):
    """显示周销售额柱状图"""
    st.markdown('<h3 class="section-title fade-in">📊 周销售额排名</h3>', unsafe_allow_html=True)
    
    # 检查是否有排名类型列
    if '排名类型' not in df.columns:
        st.info("数据格式不正确，缺少'排名类型'列")
        return
    
    # 查找周销售额相关的排名类型
    week_sales_types = []
    for ranking_type in df['排名类型'].dropna().unique():
        if '周销售额' in str(ranking_type):
            week_sales_types.append(ranking_type)
    
    if not week_sales_types:
        st.info("暂无周销售额数据")
        return
    
    # 创建标签页
    tab_names = [str(ranking_type).replace('销售额', '') for ranking_type in week_sales_types]
    tabs = st.tabs(tab_names)
    
    for i, (tab, ranking_type) in enumerate(zip(tabs, week_sales_types)):
        with tab:
            # 过滤该排名类型的数据
            type_data = df[df['排名类型'] == ranking_type].copy()
            
            if type_data.empty:
                st.info(f"{ranking_type}暂无有效数据")
                continue
            
            # 检查必要的列
            name_col = '姓名' if '姓名' in type_data.columns else ('员工姓名' if '员工姓名' in type_data.columns else None)
            amount_col = '金额' if '金额' in type_data.columns else None
            
            if not name_col or not amount_col:
                st.info(f"{ranking_type}数据格式不正确，缺少姓名或金额列")
                continue
            
            # 过滤有效数据并排序（包含0值）
            valid_data = type_data[type_data[amount_col].notna() & (type_data[amount_col] >= 0)].copy()
            if valid_data.empty:
                st.info(f"{ranking_type}暂无有效数据")
                continue
                
            valid_data = valid_data.sort_values(amount_col, ascending=False)  # 展示所有有效数据
            
            # 准备显示文本和颜色
            display_texts = []
            colors = []
            total_count = len(valid_data)
            
            for idx, val in enumerate(valid_data[amount_col]):
                text = f"{val/10000:.1f}万"
                
                # 为0值添加警示图标
                if val == 0:
                    if idx == 0:  # 第一名且为0
                        text = f"🥇⚠️ {text}"
                        colors.append('#FFD700')  # 金色
                    elif idx == 1:  # 第二名且为0
                        text = f"🥈⚠️ {text}"
                        colors.append('#C0C0C0')  # 银色
                    elif idx == 2:  # 第三名且为0
                        text = f"🥉⚠️ {text}"
                        colors.append('#CD7F32')  # 铜色
                    else:  # 其他名次且为0
                        text = f"⚠️ {text}"
                        colors.append('#FF9500')  # 橙色警示
                else:
                    # 非0值的正常逻辑
                    if idx == 0:  # 第一名
                        text = f"🥇 {text}"
                        colors.append('#FFD700')  # 金色
                    elif idx == 1:  # 第二名
                        text = f"🥈 {text}"
                        colors.append('#C0C0C0')  # 银色
                    elif idx == 2:  # 第三名
                        text = f"🥉 {text}"
                        colors.append('#CD7F32')  # 铜色
                    elif total_count >= 6 and idx >= total_count - 3:  # 后三名（总人数>=6时）
                        text = f"⚠️ {text}"
                        colors.append('#FF9500')  # 橙色警示
                    else:
                        colors.append('#0A84FF')  # 默认蓝色
                
                display_texts.append(text)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=valid_data[name_col],
                y=valid_data[amount_col],
                name=str(ranking_type),
                marker_color=colors,
                text=display_texts,
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f"{ranking_type}排名榜 (共{total_count}人)",
                title_font=dict(size=20, color='#1D1D1F'),
                xaxis_title='员工姓名',
                yaxis_title='销售额(元)',
                height=max(500, total_count * 25),  # 根据人数调整高度
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1D1D1F'),
                xaxis=dict(tickangle=45)
            )
            
            st.plotly_chart(fig, use_container_width=True)


def _display_weekly_payment_chart(df):
    """显示周回款合计柱状图"""
    st.markdown('<h3 class="section-title fade-in">💰 周回款合计排名</h3>', unsafe_allow_html=True)
    
    # 检查是否有排名类型列
    if '排名类型' not in df.columns:
        st.info("数据格式不正确，缺少'排名类型'列")
        return
    
    # 查找周回款合计相关的排名类型
    week_payment_types = []
    for ranking_type in df['排名类型'].dropna().unique():
        if '周回款合计' in str(ranking_type):
            week_payment_types.append(ranking_type)
    
    if not week_payment_types:
        st.info("暂无周回款合计数据")
        return
    
    # 创建标签页
    tab_names = [str(ranking_type).replace('回款合计', '') for ranking_type in week_payment_types]
    tabs = st.tabs(tab_names)
    
    for i, (tab, ranking_type) in enumerate(zip(tabs, week_payment_types)):
        with tab:
            # 过滤该排名类型的数据
            type_data = df[df['排名类型'] == ranking_type].copy()
            
            if type_data.empty:
                st.info(f"{ranking_type}暂无有效数据")
                continue
            
            # 检查必要的列
            name_col = '姓名' if '姓名' in type_data.columns else ('员工姓名' if '员工姓名' in type_data.columns else None)
            amount_col = '金额' if '金额' in type_data.columns else None
            
            if not name_col or not amount_col:
                st.info(f"{ranking_type}数据格式不正确，缺少姓名或金额列")
                continue
            
            # 过滤有效数据并排序（包含0值）
            valid_data = type_data[type_data[amount_col].notna() & (type_data[amount_col] >= 0)].copy()
            if valid_data.empty:
                st.info(f"{ranking_type}暂无有效数据")
                continue
                
            valid_data = valid_data.sort_values(amount_col, ascending=False)  # 展示所有有效数据
            
            # 准备显示文本和颜色
            display_texts = []
            colors = []
            total_count = len(valid_data)
            
            for idx, val in enumerate(valid_data[amount_col]):
                text = f"{val/10000:.1f}万"
                
                # 为0值添加警示图标
                if val == 0:
                    if idx == 0:  # 第一名且为0
                        text = f"🥇⚠️ {text}"
                        colors.append('#FFD700')  # 金色
                    elif idx == 1:  # 第二名且为0
                        text = f"🥈⚠️ {text}"
                        colors.append('#C0C0C0')  # 银色
                    elif idx == 2:  # 第三名且为0
                        text = f"🥉⚠️ {text}"
                        colors.append('#CD7F32')  # 铜色
                    else:  # 其他名次且为0
                        text = f"⚠️ {text}"
                        colors.append('#FF9500')  # 橙色警示
                else:
                    # 非0值的正常逻辑
                    if idx == 0:  # 第一名
                        text = f"🥇 {text}"
                        colors.append('#FFD700')  # 金色
                    elif idx == 1:  # 第二名
                        text = f"🥈 {text}"
                        colors.append('#C0C0C0')  # 银色
                    elif idx == 2:  # 第三名
                        text = f"🥉 {text}"
                        colors.append('#CD7F32')  # 铜色
                    elif total_count >= 6 and idx >= total_count - 3:  # 后三名（总人数>=6时）
                        text = f"⚠️ {text}"
                        colors.append('#FF9500')  # 橙色警示
                    else:
                        colors.append('#30D158')  # 默认绿色
                
                display_texts.append(text)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=valid_data[name_col],
                y=valid_data[amount_col],
                name=str(ranking_type),
                marker_color=colors,
                text=display_texts,
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f"{ranking_type}排名榜 (共{total_count}人)",
                title_font=dict(size=20, color='#1D1D1F'),
                xaxis_title='员工姓名',
                yaxis_title='回款额(元)',
                height=max(500, total_count * 25),  # 根据人数调整高度
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1D1D1F'),
                xaxis=dict(tickangle=45)
            )
            
            st.plotly_chart(fig, use_container_width=True)


def _display_monthly_data_chart(df):
    """显示月度数据对比柱状图"""
    st.markdown('<h3 class="section-title fade-in">📈 月度销售回款对比</h3>', unsafe_allow_html=True)
    
    # 检查是否有排名类型列
    if '排名类型' not in df.columns:
        st.info("数据格式不正确，缺少'排名类型'列")
        return
    
    # 查找月度销售额和回款相关的排名类型
    monthly_sales_type = None
    monthly_payment_type = None
    
    for ranking_type in df['排名类型'].dropna().unique():
        if '本月销售额' in str(ranking_type):
            monthly_sales_type = ranking_type
        elif '本月回款合计' in str(ranking_type):
            monthly_payment_type = ranking_type
    
    if not monthly_sales_type and not monthly_payment_type:
        st.info("暂无月度销售回款数据")
        return
    
    # 获取销售额数据
    sales_data = None
    if monthly_sales_type:
        sales_data = df[df['排名类型'] == monthly_sales_type].copy()
    
    # 获取回款数据  
    payment_data = None
    if monthly_payment_type:
        payment_data = df[df['排名类型'] == monthly_payment_type].copy()
    
    # 如果只有一种数据，直接显示
    if sales_data is not None and payment_data is None:
        _display_single_ranking_chart(sales_data, monthly_sales_type, '销售额(元)', '#0A84FF')
        return
    elif payment_data is not None and sales_data is None:  
        _display_single_ranking_chart(payment_data, monthly_payment_type, '回款额(元)', '#30D158')
        return
    
    # 如果两种数据都有，分别显示
    if sales_data is not None and payment_data is not None:
        _display_single_ranking_chart(sales_data, monthly_sales_type, '销售额(元)', '#0A84FF')
        _display_single_ranking_chart(payment_data, monthly_payment_type, '回款额(元)', '#30D158')


def _display_single_ranking_chart(data, ranking_type, y_label, color):
    """显示单一排名图表"""
    # 检查必要的列
    name_col = '姓名' if '姓名' in data.columns else ('员工姓名' if '员工姓名' in data.columns else None)
    amount_col = '金额' if '金额' in data.columns else None
    
    if not name_col or not amount_col:
        st.info(f"{ranking_type}数据格式不正确，缺少姓名或金额列")
        return
    
    # 过滤有效数据并排序（包含0值）
    valid_data = data[data[amount_col].notna() & (data[amount_col] >= 0)].copy()
    if valid_data.empty:
        st.info(f"{ranking_type}暂无有效数据")
        return
        
    valid_data = valid_data.sort_values(amount_col, ascending=False)
    total_count = len(valid_data)
    
    # 准备显示文本和颜色
    display_texts = []
    colors = []
    
    for idx, val in enumerate(valid_data[amount_col]):
        text = f"{val/10000:.1f}万"
        
        # 为0值添加警示图标
        if val == 0:
            if idx == 0:  # 第一名且为0
                text = f"🥇⚠️ {text}"
                colors.append('#FFD700')  # 金色
            elif idx == 1:  # 第二名且为0
                text = f"🥈⚠️ {text}"
                colors.append('#C0C0C0')  # 银色
            elif idx == 2:  # 第三名且为0
                text = f"🥉⚠️ {text}"
                colors.append('#CD7F32')  # 铜色
            else:  # 其他名次且为0
                text = f"⚠️ {text}"
                colors.append('#FF9500')  # 橙色警示
        else:
            # 非0值的正常逻辑
            if idx == 0:  # 第一名
                text = f"🥇 {text}"
                colors.append('#FFD700')  # 金色
            elif idx == 1:  # 第二名
                text = f"🥈 {text}"
                colors.append('#C0C0C0')  # 银色
            elif idx == 2:  # 第三名
                text = f"🥉 {text}"
                colors.append('#CD7F32')  # 铜色
            elif total_count >= 6 and idx >= total_count - 3:  # 后三名（总人数>=6时）
                text = f"⚠️ {text}"
                colors.append('#FF9500')  # 橙色警示
            else:
                colors.append(color)  # 默认颜色
        
        display_texts.append(text)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=valid_data[name_col],
        y=valid_data[amount_col],
        name=str(ranking_type),
        marker_color=colors,
        text=display_texts,
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"{ranking_type}排名榜 (共{total_count}人)",
        title_font=dict(size=20, color='#1D1D1F'),
        xaxis_title='员工姓名',
        yaxis_title=y_label,
        height=max(500, total_count * 25),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1D1D1F'),
        xaxis=dict(tickangle=45)
    )
    
    st.plotly_chart(fig, use_container_width=True)



def _display_overdue_warning_chart(df):
    """显示逾期清收失职警示榜"""
    st.markdown('<h3 class="section-title fade-in">⚠️ 逾期清收失职警示榜</h3>', unsafe_allow_html=True)
    
    # 检查是否有排名类型列
    if '排名类型' not in df.columns:
        st.info("数据格式不正确，缺少'排名类型'列")
        return
    
    # 查找逾期相关的排名类型
    overdue_type = None
    for ranking_type in df['排名类型'].dropna().unique():
        type_str = str(ranking_type)
        if any(keyword in type_str for keyword in ['逾期', '超期', '未收回']):
            overdue_type = ranking_type
            break
    
    if overdue_type is None:
        st.info("暂无逾期未收回数据")
        return
    
    # 过滤该排名类型的数据
    type_data = df[df['排名类型'] == overdue_type].copy()
    
    if type_data.empty:
        st.success("🎉 恭喜！本月暂无逾期未收回情况")
        return
    
    # 检查必要的列
    name_col = '姓名' if '姓名' in type_data.columns else ('员工姓名' if '员工姓名' in type_data.columns else None)
    amount_col = '金额' if '金额' in type_data.columns else None
    
    if not name_col or not amount_col:
        st.info(f"{overdue_type}数据格式不正确，缺少姓名或金额列")
        return
    
    # 过滤有逾期未收回额的员工
    warning_data = type_data[type_data[amount_col].notna() & (type_data[amount_col] > 0)].copy()
    
    if warning_data.empty:
        st.success("🎉 恭喜！本月暂无逾期未收回情况")
        return
    
    # 按逾期金额倒序排列
    warning_data = warning_data.sort_values(amount_col, ascending=False)
    
    # 创建警示色彩 - 金额越高颜色越红
    max_overdue = warning_data[amount_col].max()
    colors = []
    for val in warning_data[amount_col]:
        intensity = val / max_overdue
        if intensity > 0.7:
            colors.append('#FF3B30')  # 深红色 - 严重
        elif intensity > 0.4:
            colors.append('#FF9500')  # 橙色 - 警告
        else:
            colors.append('#FFCC00')  # 黄色 - 注意
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=warning_data[name_col],
        y=warning_data[amount_col],
        name='逾期未收回额',
        marker_color=colors,
        text=[f"{val/10000:.1f}万" for val in warning_data[amount_col]],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>逾期未收回额: %{y:,.0f}元<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'逾期清收失职警示榜 - {overdue_type}',
        title_font=dict(size=22, color='#FF3B30'),
        xaxis_title='员工姓名',
        yaxis_title='逾期金额(元)',
        height=max(500, len(warning_data) * 25),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1D1D1F'),
        xaxis=dict(tickangle=45)
    )
    
    st.plotly_chart(fig, use_container_width=True) 