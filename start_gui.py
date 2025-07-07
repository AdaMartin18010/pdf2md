#!/usr/bin/env python3
"""
PDF转Markdown GUI启动脚本
"""

import sys
import os
from pathlib import Path

def main():
    """启动GUI"""
    print("🚀 启动PDF转Markdown GUI...")
    
    # 检查依赖
    try:
        import tkinter
        print("✅ tkinter 可用")
    except ImportError:
        print("❌ tkinter 不可用，请安装Python GUI支持")
        return
    
    # 检查核心文件
    required_files = [
        "pdf2md_gui.py",
        "stable_mineru_converter.py",
        "enhanced_cache_manager.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少核心文件: {file}")
            return
        else:
            print(f"✅ 找到文件: {file}")
    
    # 启动GUI
    try:
        from pdf2md_gui import PDF2MDGUI
        app = PDF2MDGUI()
        app.run()
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 