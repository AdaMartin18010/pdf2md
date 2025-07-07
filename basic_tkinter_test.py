#!/usr/bin/env python3
"""
基础tkinter测试
"""

import tkinter as tk
from tkinter import ttk, messagebox

def test_basic_tkinter():
    """测试基础tkinter功能"""
    print("🔍 测试基础tkinter...")
    
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("基础tkinter测试")
        root.geometry("400x300")
        
        # 添加一些基本控件
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="tkinter测试", font=("Arial", 16)).pack(pady=20)
        
        def test_message():
            messagebox.showinfo("测试", "tkinter消息框正常工作！")
        
        ttk.Button(frame, text="测试消息框", command=test_message).pack(pady=10)
        ttk.Button(frame, text="退出", command=root.quit).pack(pady=10)
        
        print("✅ tkinter基础功能正常")
        print("📱 显示GUI窗口...")
        
        # 运行GUI
        root.mainloop()
        
        print("✅ GUI测试完成")
        return True
        
    except Exception as e:
        print(f"❌ tkinter测试失败: {e}")
        return False

def test_imports():
    """测试导入功能"""
    print("🔍 测试导入功能...")
    
    try:
        # 测试基本导入
        import tkinter
        import tkinter.ttk
        import tkinter.messagebox
        import tkinter.filedialog
        print("✅ 基本tkinter导入正常")
        
        # 测试项目模块导入
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            print("✅ 缓存管理器导入正常")
        except Exception as e:
            print(f"⚠️ 缓存管理器导入失败: {e}")
        
        try:
            from enhanced_batch_processor import EnhancedBatchProcessor
            print("✅ 批量处理器导入正常")
        except Exception as e:
            print(f"⚠️ 批量处理器导入失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始基础tkinter测试...")
    
    # 测试导入
    import_ok = test_imports()
    
    if import_ok:
        # 测试GUI
        gui_ok = test_basic_tkinter()
        
        if gui_ok:
            print("\n✅ 所有基础测试通过！")
        else:
            print("\n❌ GUI测试失败")
    else:
        print("\n❌ 导入测试失败")

if __name__ == "__main__":
    main() 