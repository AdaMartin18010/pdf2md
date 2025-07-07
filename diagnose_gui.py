#!/usr/bin/env python3
"""
GUI诊断脚本
检查主GUI的问题并修复
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
import traceback

def diagnose_gui_issues():
    """诊断GUI问题"""
    print("开始诊断GUI问题...")
    
    issues = []
    
    # 检查导入
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        print("✅ tkinter导入正常")
    except Exception as e:
        issues.append(f"tkinter导入失败: {e}")
        print(f"❌ tkinter导入失败: {e}")
    
    # 检查主GUI文件
    try:
        from pdf2md_gui import PDF2MDGUI
        print("✅ 主GUI类导入正常")
    except Exception as e:
        issues.append(f"主GUI类导入失败: {e}")
        print(f"❌ 主GUI类导入失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
    
    # 检查依赖文件
    dependencies = [
        "stable_mineru_converter.py",
        "enhanced_cache_manager.py",
        "gui_config.json"
    ]
    
    for dep in dependencies:
        if Path(dep).exists():
            print(f"✅ 依赖文件存在: {dep}")
        else:
            issues.append(f"依赖文件缺失: {dep}")
            print(f"❌ 依赖文件缺失: {dep}")
    
    # 测试基本GUI功能
    try:
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 测试文件对话框
        directory = filedialog.askdirectory(title="测试目录选择")
        print("✅ 文件对话框功能正常")
        
        # 测试消息框
        messagebox.showinfo("测试", "消息框测试")
        print("✅ 消息框功能正常")
        
        root.destroy()
        
    except Exception as e:
        issues.append(f"基本GUI功能测试失败: {e}")
        print(f"❌ 基本GUI功能测试失败: {e}")
    
    # 检查配置
    try:
        config_file = Path("gui_config.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ 配置文件加载正常")
        else:
            print("⚠️ 配置文件不存在，将使用默认配置")
    except Exception as e:
        issues.append(f"配置文件加载失败: {e}")
        print(f"❌ 配置文件加载失败: {e}")
    
    # 检查缓存管理器
    try:
        from enhanced_cache_manager import EnhancedCacheManager
        cache_manager = EnhancedCacheManager()
        cache_info = cache_manager.check_cache_status()
        print("✅ 缓存管理器功能正常")
    except Exception as e:
        issues.append(f"缓存管理器测试失败: {e}")
        print(f"❌ 缓存管理器测试失败: {e}")
    
    # 检查转换器
    try:
        from stable_mineru_converter import MineruConverter
        converter = MineruConverter()
        print("✅ 转换器导入正常")
    except Exception as e:
        issues.append(f"转换器导入失败: {e}")
        print(f"❌ 转换器导入失败: {e}")
    
    # 显示诊断结果
    print(f"\n诊断完成!")
    print(f"发现 {len(issues)} 个问题:")
    
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    if not issues:
        print("✅ 所有检查都通过，GUI应该可以正常工作")
    else:
        print("\n建议修复步骤:")
        print("1. 确保所有依赖文件存在")
        print("2. 检查Python环境和tkinter安装")
        print("3. 验证配置文件格式")
        print("4. 测试转换器和缓存管理器功能")
    
    return issues

def create_fixed_gui():
    """创建修复版的GUI"""
    print("\n创建修复版GUI...")
    
    # 复制简化版GUI作为修复版
    with open("test_main_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 修改为修复版
    content = content.replace("SimplePDF2MDGUI", "FixedPDF2MDGUI")
    content = content.replace("PDF转Markdown工具 - 测试版", "PDF转Markdown工具 - 修复版")
    
    with open("fixed_gui.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ 修复版GUI已创建: fixed_gui.py")

def main():
    """主函数"""
    print("=== GUI诊断工具 ===")
    
    # 运行诊断
    issues = diagnose_gui_issues()
    
    # 创建修复版GUI
    create_fixed_gui()
    
    print("\n=== 使用建议 ===")
    if issues:
        print("由于发现问题，建议使用修复版GUI:")
        print("python fixed_gui.py")
    else:
        print("GUI诊断正常，可以尝试运行主GUI:")
        print("python pdf2md_gui.py")

if __name__ == "__main__":
    main() 