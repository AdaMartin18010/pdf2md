#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转Markdown工具启动脚本
用于PyInstaller打包后的可执行文件
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 设置环境变量
os.environ['PYTHONPATH'] = str(current_dir)

# 导入并启动GUI
try:
    from pdf2md_gui import PDF2MDGUI
    
    def main():
        """主函数"""
        app = PDF2MDGUI()
        app.run()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖文件都在正确位置")
    input("按回车键退出...")
except Exception as e:
    print(f"启动错误: {e}")
    input("按回车键退出...")
