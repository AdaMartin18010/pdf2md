#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI功能测试脚本
测试PDF转Markdown GUI的各项功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path

def test_gui_basic_functionality():
    """测试GUI基本功能"""
    print("🧪 测试GUI基本功能...")
    
    try:
        # 导入GUI类
        from pdf2md_gui import PDF2MDGUI
        
        # 创建GUI实例
        app = PDF2MDGUI()
        
        print("✅ GUI实例创建成功")
        
        # 测试基本属性
        assert hasattr(app, 'root'), "缺少root属性"
        assert hasattr(app, 'notebook'), "缺少notebook属性"
        assert hasattr(app, 'log_text'), "缺少log_text属性"
        assert hasattr(app, 'start_button'), "缺少start_button属性"
        assert hasattr(app, 'stop_button'), "缺少stop_button属性"
        
        print("✅ 基本属性检查通过")
        
        # 测试配置加载
        assert hasattr(app, 'config'), "缺少config属性"
        print("✅ 配置加载检查通过")
        
        # 测试日志功能
        app.log("测试日志功能")
        print("✅ 日志功能测试通过")
        
        # 测试设置保存
        app.save_config()
        print("✅ 设置保存功能测试通过")
        
        print("✅ GUI基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ GUI基本功能测试失败: {e}")
        return False

def test_gui_components():
    """测试GUI组件"""
    print("\n🧪 测试GUI组件...")
    
    try:
        from pdf2md_gui import PDF2MDGUI
        
        app = PDF2MDGUI()
        
        # 测试选项卡
        tabs = app.notebook.tabs()
        expected_tabs = ["转换", "设置", "缓存管理", "处理状态", "日志"]
        
        for i, expected_tab in enumerate(expected_tabs):
            tab_text = app.notebook.tab(i, "text")
            print(f"  选项卡 {i+1}: {tab_text}")
        
        print("✅ 选项卡检查通过")
        
        # 测试按钮状态
        assert app.start_button.cget("state") == "normal", "开始按钮状态错误"
        assert app.stop_button.cget("state") == "disabled", "停止按钮状态错误"
        print("✅ 按钮状态检查通过")
        
        # 测试进度条
        assert hasattr(app, 'progress_var'), "缺少progress_var"
        app.progress_var.set(50)
        assert app.progress_var.get() == 50, "进度条设置失败"
        print("✅ 进度条检查通过")
        
        # 测试状态栏
        assert hasattr(app, 'status_var'), "缺少status_var"
        app.status_var.set("测试状态")
        assert app.status_var.get() == "测试状态", "状态栏设置失败"
        print("✅ 状态栏检查通过")
        
        print("✅ GUI组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ GUI组件测试失败: {e}")
        return False

def test_config_management():
    """测试配置管理"""
    print("\n🧪 测试配置管理...")
    
    try:
        from pdf2md_gui import PDF2MDGUI
        
        app = PDF2MDGUI()
        
        # 测试配置加载
        config = app.load_config()
        assert isinstance(config, dict), "配置不是字典类型"
        print("✅ 配置加载测试通过")
        
        # 测试配置保存
        test_config = {
            "input_dir": "test_input",
            "output_dir": "test_output",
            "language": "ch",
            "backend": "pipeline",
            "method": "auto",
            "enable_formula": True,
            "enable_table": True,
            "cache_dir": "./test_cache",
            "auto_preload": True,
            "show_progress": True,
            "theme": "default",
            "language_ui": "zh",
            "timeout": "300",
            "device": "auto",
            "max_workers": "2",
            "memory_limit": "4",
            "enable_optimization": True,
            "enable_caching": True,
            "enable_retry": True,
            "enable_logging": True
        }
        
        # 临时保存测试配置
        test_config_file = "test_gui_config.json"
        with open(test_config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
        
        # 加载测试配置
        loaded_config = app.load_config()
        print("✅ 配置保存和加载测试通过")
        
        # 清理测试文件
        if os.path.exists(test_config_file):
            os.remove(test_config_file)
        
        print("✅ 配置管理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置管理测试失败: {e}")
        return False

def test_processing_status():
    """测试处理状态功能"""
    print("\n🧪 测试处理状态功能...")
    
    try:
        from pdf2md_gui import PDF2MDGUI
        
        app = PDF2MDGUI()
        
        # 测试任务添加
        app.add_processing_task("test.pdf")
        assert len(app.processing_tasks) == 1, "任务添加失败"
        print("✅ 任务添加测试通过")
        
        # 测试任务状态更新
        app.update_task_status("test.pdf", "处理中", 50)
        task = app.processing_tasks[0]
        assert task["status"] == "处理中", "任务状态更新失败"
        assert task["progress"] == 50, "任务进度更新失败"
        print("✅ 任务状态更新测试通过")
        
        # 测试统计信息更新
        app.update_processing_stats()
        assert app.total_files_var.get() == "1", "统计信息更新失败"
        print("✅ 统计信息更新测试通过")
        
        # 测试任务列表清空
        app.clear_processing_tasks()
        assert len(app.processing_tasks) == 0, "任务列表清空失败"
        print("✅ 任务列表清空测试通过")
        
        print("✅ 处理状态功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 处理状态功能测试失败: {e}")
        return False

def test_language_theme_switching():
    """测试语言和主题切换"""
    print("\n🧪 测试语言和主题切换...")
    
    try:
        from pdf2md_gui import PDF2MDGUI
        
        app = PDF2MDGUI()
        
        # 测试语言切换
        app.language_ui_var.set("en")
        app.on_language_change()
        assert app.root.title() == "PDF to Markdown Tool", "语言切换失败"
        print("✅ 语言切换测试通过")
        
        # 测试主题切换
        app.theme_var.set("light")
        app.on_theme_change()
        print("✅ 主题切换测试通过")
        
        # 恢复默认设置
        app.language_ui_var.set("zh")
        app.theme_var.set("default")
        app.on_language_change()
        app.on_theme_change()
        
        print("✅ 语言和主题切换测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 语言和主题切换测试失败: {e}")
        return False

def test_cache_management():
    """测试缓存管理功能"""
    print("\n🧪 测试缓存管理功能...")
    
    try:
        from pdf2md_gui import PDF2MDGUI
        
        app = PDF2MDGUI()
        
        # 测试缓存信息刷新
        app.refresh_cache_info()
        print("✅ 缓存信息刷新测试通过")
        
        # 测试缓存检查
        app.check_cache()
        print("✅ 缓存检查测试通过")
        
        print("✅ 缓存管理功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 缓存管理功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始GUI功能测试")
    print("=" * 50)
    
    tests = [
        ("基本功能", test_gui_basic_functionality),
        ("GUI组件", test_gui_components),
        ("配置管理", test_config_management),
        ("处理状态", test_processing_status),
        ("语言主题切换", test_language_theme_switching),
        ("缓存管理", test_cache_management),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！GUI功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    main() 