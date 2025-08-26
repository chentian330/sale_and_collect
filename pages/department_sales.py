"""
部门销售回款统计页面
查看部门级销售回款统计和详细分析
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from html import escape
from components.navigation import navigation
from components.ui_components import ui
from core.state_manager import state_manager


def get_text_positions(df_length):
    """
    根据部门数量动态生成文本位置数组
    
    Args:
        df_length: 部门数量
        
    Returns:
        文本位置列表
    """
    if df_length <= 2:
        # 1-2个部门：全部内显
        return ['inside'] * df_length
    elif df_length == 3:
        # 3个部门：前2内显，最后外显
        return ['inside', 'inside', 'outside']
    elif df_length == 4:
        # 4个部门：前2内显，第3自动，最后外显
        return ['inside', 'inside', 'auto', 'outside']
    else:
        # 5个及以上：前2内显，后2外显，中间auto
        positions = []
        for i in range(df_length):
            if i == 0 or i == 1:  # 第1名、第2名
                positions.append('inside')
            elif i == df_length - 2 or i == df_length - 1:  # 倒数第2名、倒数第1名
                positions.append('outside')
            else:  # 其他排名
                positions.append('auto')
        return positions


def show():
    """显示部门销售回款统计页面"""
    # 渲染导航
    navigation.render_navigation_bar()
    navigation.render_breadcrumb()
    
    # 加载CSS样式
    ui.load_css()
    
    # 获取部门销售数据
    department_sales_df = state_manager.get_data('department_sales_df')
    if department_sales_df is None:
        st.error("部门销售回款数据未加载。请上传有效文件。")
        return

    st.markdown('<h1 style="text-align: center; font-family: \'SF Pro Display\', sans-serif;">🏢 部门销售回款分析</h1>',
                unsafe_allow_html=True)

    # --- 数据准备 ---
    df = department_sales_df.copy()

    # 移除"合计"行用于排名和图表
    df = df[df['部门'] != '合计'].copy()
    if df.empty:
        st.warning("数据文件中没有有效的部门数据。")
        return

    # --- 动态识别周次数据 ---
    # 识别销售额周次
    sales_week_pattern = r'第(\d+)周销售额'
    available_sales_weeks = []
    for col in df.columns:
        match = re.match(sales_week_pattern, col)
        if match:
            week_num = int(match.group(1))
            available_sales_weeks.append(week_num)
    
    # 识别回款周次
    payment_week_pattern = r'第(\d+)周回.*款'
    available_payment_weeks = []
    for col in df.columns:
        match = re.match(payment_week_pattern, col)
        if match:
            week_num = int(match.group(1))
            available_payment_weeks.append(week_num)
    
    # 获取所有可用周次并排序
    available_sales_weeks = sorted(set(available_sales_weeks))
    available_payment_weeks = sorted(set(available_payment_weeks))
    all_weeks = sorted(set(available_sales_weeks + available_payment_weeks))

    # --- 列名修正 ---
    # 使用全角中文括号
    payment_col_normal = '本月回未超期款'
    payment_col_overdue = '本月回超期款'

    if payment_col_normal in df.columns and payment_col_overdue in df.columns:
        df['月总回款额'] = df[payment_col_normal].fillna(0) + df[payment_col_overdue].fillna(0)
    else:
        st.error(f"月度回款列缺失，请检查文件中的列名是否为 '{payment_col_normal}' 和 '{payment_col_overdue}'。")
        return
    
    # 动态计算各周总回款额
    for week_num in available_payment_weeks:
        week_payment_normal = f'第{week_num}周回未超期款'
        week_payment_overdue = f'第{week_num}周回超期款'
        if week_payment_normal in df.columns and week_payment_overdue in df.columns:
            df[f'第{week_num}周总回款额'] = df[week_payment_normal].fillna(0) + df[week_payment_overdue].fillna(0)

    # --- 1 & 2. 月度排名 ---
    st.markdown('<h3 class="section-title fade-in">📊 月度排名</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 销售额排名 (部门)")
        sales_ranking_df = df.sort_values('本月销售额', ascending=False).copy()
        
        # 转换为万元
        sales_ranking_df['本月销售额(万元)'] = sales_ranking_df['本月销售额'] / 10000
        
        # 动态生成文本位置
        sales_text_positions = get_text_positions(len(sales_ranking_df))
        
        fig_sales = px.bar(sales_ranking_df, x='本月销售额(万元)', y='部门', orientation='h', title='月销售额排名',
                          labels={'本月销售额(万元)': '销售额 (万元)', '部门': '部门'}, text='本月销售额(万元)',
                          color_discrete_sequence=['#0A84FF'])
        fig_sales.update_traces(texttemplate='%{text:,.1f}万', textposition=sales_text_positions)
        fig_sales.update_layout(yaxis={'categoryorder': 'total ascending'}, plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#1D1D1F'))
        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        st.markdown("#### 回款额排名 (部门)")
        payment_ranking_df = df.sort_values('月总回款额', ascending=False).copy()
        
        # 转换为万元
        payment_ranking_df['月总回款额(万元)'] = payment_ranking_df['月总回款额'] / 10000
        
        # 动态生成文本位置
        payment_text_positions = get_text_positions(len(payment_ranking_df))
        
        fig_payment = px.bar(payment_ranking_df, x='月总回款额(万元)', y='部门', orientation='h', title='月回款额排名',
                             labels={'月总回款额(万元)': '回款额 (万元)', '部门': '部门'}, text='月总回款额(万元)',
                             color_discrete_sequence=['#BF5AF2'])
        fig_payment.update_traces(texttemplate='%{text:,.1f}万', textposition=payment_text_positions)
        fig_payment.update_layout(yaxis={'categoryorder': 'total ascending'}, plot_bgcolor='rgba(0,0,0,0)',
                                  paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#1D1D1F'))
        st.plotly_chart(fig_payment, use_container_width=True)

    # --- 3 & 4. 各周走势 ---
    st.markdown('<h3 class="section-title fade-in">📈 各周走势</h3>', unsafe_allow_html=True)

    # 动态构建线图数据
    sales_cols = ['部门'] + [f'第{week_num}周销售额' for week_num in available_sales_weeks if f'第{week_num}周销售额' in df.columns]
    payment_cols = ['部门'] + [f'第{week_num}周总回款额' for week_num in available_payment_weeks if f'第{week_num}周总回款额' in df.columns]

    sales_melted = pd.DataFrame()
    payment_melted = pd.DataFrame()
    
    if len(sales_cols) > 1:
        sales_melted = df[sales_cols].melt(id_vars='部门', var_name='周次', value_name='销售额').dropna()
        # 转换为万元
        sales_melted['销售额(万元)'] = sales_melted['销售额'] / 10000
        
    if len(payment_cols) > 1:
        payment_melted = df[payment_cols].melt(id_vars='部门', var_name='周次', value_name='回款额').dropna()
        # 转换为万元
        payment_melted['回款额(万元)'] = payment_melted['回款额'] / 10000

    # 正确提取周序号用于排序
    if not sales_melted.empty:
        sales_melted['周序号'] = sales_melted['周次'].str.extract(r'第(\d+)周').astype(int)
    if not payment_melted.empty:
        payment_melted['周序号'] = payment_melted['周次'].str.extract(r'第(\d+)周').astype(int)

    col3, col4 = st.columns(2)
    
    # 添加图例操作提示
    st.info("💡 提示：点击图例可以隐藏或显示对应的数据线")
    
    with col3:
        st.markdown("#### 各周销售额走势")
        if not sales_melted.empty:
            fig_sales_trend = px.line(sales_melted.sort_values('周序号'), x='周次', y='销售额(万元)', color='部门',
                                      title='各部门周销售额趋势', markers=True,
                                      labels={'销售额(万元)': '销售额 (万元)', '周次': '周次'})
            fig_sales_trend.update_layout(
                height=550, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1D1D1F'), xaxis_title=None,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_sales_trend, use_container_width=True)
        else:
            st.info(f"无周销售额数据可供展示。检测到的销售额周次: {available_sales_weeks}")

    with col4:
        st.markdown("#### 各周回款额走势")
        if not payment_melted.empty:
            # 使用自定义排序的x轴标签
            custom_x_labels = sorted(payment_melted['周次'].unique(),
                                     key=lambda x: int(re.search(r'第(\d+)周', x).group(1)))
            fig_payment_trend = px.line(payment_melted.sort_values('周序号'), x='周次', y='回款额(万元)', color='部门', 
                                      title='各部门周回款额趋势', markers=True, 
                                      category_orders={"周次": custom_x_labels},
                                      labels={'回款额(万元)': '回款额 (万元)', '周次': '周次'})
            fig_payment_trend.update_layout(
                height=550, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1D1D1F'), xaxis_title=None,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_payment_trend, use_container_width=True)
        else:
            st.info(f"无周回款额数据可供展示。检测到的回款周次: {available_payment_weeks}")

    # --- 5. 各周详细数据表格 ---
    st.markdown('<h3 class="section-title fade-in">📊 各周详细数据</h3>', unsafe_allow_html=True)
    
    # 创建两列布局
    col5, col6 = st.columns(2)
    
    # 销售额详细表格
    with col5:
        if not sales_melted.empty:
            st.markdown("#### 📈 各周销售额详细数据")
            sales_detail_df = create_sales_detail_table(sales_melted)
            display_styled_dataframe(sales_detail_df)
        else:
            st.markdown("#### 📈 各周销售额详细数据")
            st.info("无销售额数据可供展示")
    
    # 回款额详细表格
    with col6:
        if not payment_melted.empty:
            st.markdown("#### 💰 各周回款额详细数据")
            payment_detail_df = create_payment_detail_table(payment_melted)
            display_styled_dataframe(payment_detail_df)
        else:
            st.markdown("#### 💰 各周回款额详细数据")
            st.info("无回款额数据可供展示")

    # --- 6. 部门详情 ---
    st.markdown('<h3 class="section-title fade-in">🏢 部门销售回款详情</h3>', unsafe_allow_html=True)

    departments = df['部门'].unique()
    selected_dept = st.selectbox("选择要查看的部门", departments, label_visibility="collapsed")

    if selected_dept:
        dept_data = df[df['部门'] == selected_dept].iloc[0]

        st.markdown(f"""
        <div class="glass-card fade-in">
            <h2 style="text-align:center; color: #BF5AF2; font-family: 'SF Pro Display';">{escape(selected_dept)} - 月度总览</h2>
            <div class="divider"></div> """, unsafe_allow_html=True)

        kpi_cols = st.columns(3)
        with kpi_cols[0]:
            st.metric("本月销售额", f"¥ {dept_data.get('本月销售额', 0):,.2f}")
        with kpi_cols[1]:
            st.metric("本月总回款额", f"¥ {dept_data.get('月总回款额', 0):,.2f}")
        with kpi_cols[2]:
            overdue_val = dept_data.get(payment_col_overdue, 0)
            total_payment = dept_data.get('月总回款额', 0)
            overdue_payment_pct = (overdue_val / total_payment * 100) if total_payment > 0 else 0
            st.metric("超期回款占比", f"{overdue_payment_pct:.2f}%", help=f"超期回款额: ¥ {overdue_val:,.2f}")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<h4 style="margin-top:20px; font-family: \'SF Pro Display\', sans-serif;">周度数据详情</h4>',
                    unsafe_allow_html=True)

        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.markdown("##### 周销售额")
            weekly_sales_data = []
            for week_num in available_sales_weeks:
                col_name = f'第{week_num}周销售额'
                if col_name in dept_data and pd.notna(dept_data[col_name]):
                    weekly_sales_data.append({'周次': f'第 {week_num} 周', '销售额': dept_data[col_name]})
            if weekly_sales_data:
                st.dataframe(pd.DataFrame(weekly_sales_data).style.format({'销售额': '¥ {:,.2f}'}),
                             use_container_width=True, hide_index=True)
            else:
                st.info(f"无周销售数据。可用周次: {available_sales_weeks}")

        with detail_cols[1]:
            st.markdown("##### 周回款额")
            weekly_payment_data = []
            for week_num in available_payment_weeks:
                col_name = f'第{week_num}周总回款额'
                if col_name in dept_data and pd.notna(dept_data[col_name]):
                    weekly_payment_data.append({'周次': f'第 {week_num} 周', '回款额': dept_data[col_name]})
            if weekly_payment_data:
                st.dataframe(pd.DataFrame(weekly_payment_data).style.format({'回款额': '¥ {:,.2f}'}),
                             use_container_width=True, hide_index=True)
            else:
                st.info(f"无周回款数据。可用周次: {available_payment_weeks}")

        st.markdown("</div>", unsafe_allow_html=True)


def create_sales_detail_table(sales_melted):
    """创建销售额详细数据表格"""
    # 按部门和周次排序
    detail_df = sales_melted.sort_values(['部门', '周序号']).copy()
    
    # 重新整理数据结构
    detail_df['周数'] = detail_df['周序号']
    detail_df['销售额（万元）'] = detail_df['销售额'] / 10000
    
    # 计算环比增长率
    detail_df['环比增长率'] = ""
    for dept in detail_df['部门'].unique():
        dept_data = detail_df[detail_df['部门'] == dept].sort_values('周序号')
        for i in range(1, len(dept_data)):
            current_idx = dept_data.index[i]
            prev_idx = dept_data.index[i-1]
            current_val = dept_data.loc[current_idx, '销售额']
            prev_val = dept_data.loc[prev_idx, '销售额']
            
            if prev_val != 0 and pd.notna(prev_val) and pd.notna(current_val):
                growth_rate = ((current_val - prev_val) / prev_val) * 100
                detail_df.loc[current_idx, '环比增长率'] = f"{growth_rate:+.1f}%"
    
    # 选择要显示的列
    result_df = detail_df[['周数', '部门', '销售额', '销售额（万元）', '环比增长率']].copy()
    
    # 格式化销售额列
    result_df['销售额'] = result_df['销售额'].apply(lambda x: f"¥ {x:,.2f}")
    result_df['销售额（万元）'] = result_df['销售额（万元）'].apply(lambda x: f"¥ {x:,.2f}")
    
    return result_df


def create_payment_detail_table(payment_melted):
    """创建回款额详细数据表格"""
    # 按部门和周次排序
    detail_df = payment_melted.sort_values(['部门', '周序号']).copy()
    
    # 重新整理数据结构
    detail_df['周数'] = detail_df['周序号']
    detail_df['回款额（万元）'] = detail_df['回款额'] / 10000
    
    # 计算环比增长率
    detail_df['环比增长率'] = ""
    for dept in detail_df['部门'].unique():
        dept_data = detail_df[detail_df['部门'] == dept].sort_values('周序号')
        for i in range(1, len(dept_data)):
            current_idx = dept_data.index[i]
            prev_idx = dept_data.index[i-1]
            current_val = dept_data.loc[current_idx, '回款额']
            prev_val = dept_data.loc[prev_idx, '回款额']
            
            if prev_val != 0 and pd.notna(prev_val) and pd.notna(current_val):
                growth_rate = ((current_val - prev_val) / prev_val) * 100
                detail_df.loc[current_idx, '环比增长率'] = f"{growth_rate:+.1f}%"
    
    # 选择要显示的列
    result_df = detail_df[['周数', '部门', '回款额', '回款额（万元）', '环比增长率']].copy()
    
    # 格式化回款额列
    result_df['回款额'] = result_df['回款额'].apply(lambda x: f"¥ {x:,.2f}")
    result_df['回款额（万元）'] = result_df['回款额（万元）'].apply(lambda x: f"¥ {x:,.2f}")
    
    return result_df


def display_styled_dataframe(df):
    """显示带条件格式的数据表（参照总体趋势的颜色样式）"""
    def apply_growth_color(val):
        """为增长率列应用颜色格式"""
        if val == "" or pd.isna(val):
            return ""
        try:
            # 提取数值部分
            num_val = float(val.replace('%', '').replace('+', ''))
            if num_val > 0:
                return "color: green; font-weight: bold"
            else:
                return "color: red; font-weight: bold"
        except:
            return ""
    
    # 获取环比增长率列
    growth_columns = [col for col in df.columns if '环比增长率' in col]
    
    # 应用样式
    styled_df = df.style
    for col in growth_columns:
        styled_df = styled_df.applymap(apply_growth_color, subset=[col])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True) 