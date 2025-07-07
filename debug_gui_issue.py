#!/usr/bin/env python3
"""
调试GUI启动问题
"""

import sys
import os

def step1_check_python():
    """步骤1：检查Python环境"""
    print("🔍 步骤1：检查Python环境")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"当前目录: {os.getcwd()}")
    print("✅ Python环境检查完成\n")

def step2_check_imports():
    """步骤2：检查导入"""
    print("🔍 步骤2：检查导入")
    
    try:
        import tkinter
        print("✅ tkinter导入成功")
    except Exception as e:
        print(f"❌ tkinter导入失败: {e}")
        return False
    
    try:
        from tkinter import ttk, messagebox
        print("✅ tkinter子模块导入成功")
    except Exception as e:
        print(f"❌ tkinter子模块导入失败: {e}")
        return False
    
    try:
        from enhanced_cache_manager import EnhancedCacheManager
        print("✅ 缓存管理器导入成功")
    except Exception as e:
        print(f"❌ 缓存管理器导入失败: {e}")
        return False
    
    try:
        from enhanced_batch_processor import EnhancedBatchProcessor
        print("✅ 批量处理器导入成功")
    except Exception as e:
        print(f"❌ 批量处理器导入失败: {e}")
        return False
    
    print("✅ 所有导入检查完成\n")
    return True

def step3_check_tkinter():
    """步骤3：检查tkinter功能"""
    print("🔍 步骤3：检查tkinter功能")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 测试基本功能
        root.title("测试")
        root.geometry("100x100")
        
        # 测试消息框
        from tkinter import messagebox
        # messagebox.showinfo("测试", "tkinter工作正常")  # 注释掉避免弹窗
        
        root.destroy()
        print("✅ tkinter基本功能正常")
        return True
        
    except Exception as e:
        print(f"❌ tkinter功能测试失败: {e}")
        return False

def step4_check_memory():
    """步骤4：检查内存使用"""
    print("🔍 步骤4：检查内存使用")
    
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        print(f"当前进程内存使用: {memory_mb:.1f} MB")
        
        # 检查系统内存
        memory = psutil.virtual_memory()
        print(f"系统内存使用: {memory.percent:.1f}%")
        
        if memory.percent > 90:
            print("⚠️ 系统内存使用率过高")
        else:
            print("✅ 系统内存使用正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 内存检查失败: {e}")
        return False

def step5_test_simple_gui():
    """步骤5：测试简单GUI"""
    print("🔍 步骤5：测试简单GUI")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        root.title("简单测试")
        root.geometry("300x200")
        
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="GUI测试", font=("Arial", 14)).pack(pady=20)
        
        def close_window():
            root.quit()
        
        ttk.Button(frame, text="关闭", command=close_window).pack(pady=10)
        
        print("📱 显示测试窗口...")
        print("请关闭窗口继续测试...")
        
        root.mainloop()
        
        print("✅ 简单GUI测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 简单GUI测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始调试GUI启动问题...")
    print("=" * 50)
    
    # 逐步检查
    step1_check_python()
    
    if not step2_check_imports():
        print("❌ 导入检查失败，停止测试")
        return
    
    if not step3_check_tkinter():
        print("❌ tkinter检查失败，停止测试")
        return
    
    if not step4_check_memory():
        print("❌ 内存检查失败，停止测试")
        return
    
    print("🔍 所有基础检查通过，开始GUI测试...")
    print("=" * 50)
    
    if step5_test_simple_gui():
        print("\n✅ 所有测试通过！")
        print("建议：如果简单GUI测试通过，可以尝试使用安全启动器")
    else:
        print("\n❌ GUI测试失败")
        print("建议：检查系统环境或重启系统后重试")

if __name__ == "__main__":
    main() 