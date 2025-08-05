#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售回款统计系统 - 应用入口文件
Sales and Collection Statistics System - Application Entry Point

适用于 Streamlit Cloud 部署
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行主应用
if __name__ == "__main__":
    from main import main
    main()
else:
    # Streamlit Cloud 部署时的入口点
    from main import main
    main() 