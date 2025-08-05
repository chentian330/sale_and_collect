# 🏆 销售回款统计系统

> 基于 Streamlit 的企业销售业绩分析和数据可视化平台

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://github.com/chentian330/sale_and_collect)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 功能特性

### 🏠 仪表盘首页
- 数据概览和关键指标展示
- 快速导航到各功能模块
- 美观的现代化界面设计

### 🏆 积分中心
- **红黑榜排名**: 团队表现可视化展示
- **积分统计**: 员工个人积分详细分析
- 动态排名和趋势分析

### 💰 销售回款中心
- **销售排名**: 实时销售业绩排行榜
- **员工详情**: 个人销售数据深度分析
- **部门统计**: 部门级别业绩对比

### 📈 历史数据对比
- **总体趋势**: 整体销售回款走势分析
- **员工对比**: 多维度员工历史表现
- **部门对比**: 部门间历史数据比较
- 支持多月份数据上传和对比分析

## 🚀 快速开始

### 在线体验
📱 [在线演示](https://sale-and-collect.streamlit.app) - 立即体验完整功能

### 本地运行

1. **克隆项目**
```bash
git clone https://github.com/chentian330/sale_and_collect.git
cd sale_and_collect
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动应用**
```bash
streamlit run app.py
```

4. **访问应用**
打开浏览器访问 `http://localhost:8501`

## 📁 数据文件格式

系统支持标准Excel文件（.xlsx格式），需包含以下工作表：

### 必需工作表
- **`员工积分数据`**: 员工姓名、队名、积分等信息
- **`销售回款数据统计`**: 销售额、回款额、逾期金额等

### 可选工作表
- **`部门销售回款统计`**: 部门级别汇总数据
- **`销售回款超期账款排名`**: 排名和趋势数据

📋 **详细格式说明**: 查看 [数据文件格式文档](EXAMPLE_DATA.md) 了解完整的数据结构和要求

## 🎯 项目架构

```
sale_and_collect/
├── app.py                   # 应用入口文件
├── main.py                  # 核心应用逻辑
├── requirements.txt         # Python依赖包
├── components/              # UI组件库
├── pages/                   # 功能页面
├── core/                    # 核心功能模块
├── config/                  # 配置管理
├── utils/                   # 工具函数
├── DEPLOYMENT.md            # 部署文档
├── EXAMPLE_DATA.md          # 数据格式说明
└── README.md                # 项目文档
```

## 🌟 核心特性

- ✅ **零配置**: 上传Excel文件即可开始分析
- ✅ **响应式设计**: 支持各种屏幕尺寸
- ✅ **实时计算**: 动态数据处理和可视化
- ✅ **多维分析**: 支持多角度数据对比
- ✅ **现代UI**: 采用苹果风格设计语言
- ✅ **云端部署**: 一键部署到Streamlit Cloud

## 🚀 Streamlit Cloud 部署

### 部署步骤

1. **Fork 本仓库到你的 GitHub 账户**

2. **访问 [Streamlit Cloud](https://streamlit.io/cloud)**

3. **连接 GitHub 并选择仓库**
   - Repository: `chentian330/sale_and_collect`
   - Branch: `main`
   - Main file path: `app.py`

4. **点击 Deploy 开始部署**

### 环境要求
- Python 3.8+
- 所有依赖包已在 `requirements.txt` 中定义
- 使用标准 Streamlit Cloud 运行时

## 🛠️ 技术栈

- **前端框架**: [Streamlit](https://streamlit.io/)
- **数据处理**: [Pandas](https://pandas.pydata.org/)
- **数据可视化**: [Plotly](https://plotly.com/python/)
- **文件处理**: [OpenPyXL](https://openpyxl.readthedocs.io/)
- **部署平台**: [Streamlit Cloud](https://streamlit.io/cloud)

## 📸 系统截图

<!-- 添加实际截图 -->
*上传您的系统截图到 `assets/` 文件夹，并在此处引用*

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢 [Streamlit](https://streamlit.io/) 提供优秀的Web应用框架
- 感谢 [Plotly](https://plotly.com/) 提供强大的数据可视化工具

## 📞 支持

如果您遇到问题或有建议，请：
- 创建 [Issue](https://github.com/chentian330/sale_and_collect/issues)

---

⭐ 如果这个项目对您有帮助，请给个星标支持！ 