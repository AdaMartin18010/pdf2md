#!/usr/bin/env python3
"""
简化GUI启动脚本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

def create_simple_gui():
    """创建简化GUI"""
    root = tk.Tk()
    root.title("PDF转Markdown工具 - 简化版")
    root.geometry("600x400")
    
    # 主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="PDF转Markdown工具", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # 状态信息
    status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding="10")
    status_frame.pack(fill=tk.X, pady=(0, 20))
    
    # 检查缓存管理器
    try:
        from enhanced_cache_manager import EnhancedCacheManager
        cache_manager = EnhancedCacheManager()
        cache_info = cache_manager.check_cache_status()
        cache_status = f"✅ 缓存管理器正常 - {cache_info['model_count']} 个模型"
    except Exception as e:
        cache_status = f"❌ 缓存管理器错误: {e}"
    
    ttk.Label(status_frame, text=cache_status).pack(anchor=tk.W)
    
    # 检查转换器
    try:
        from enhanced_batch_processor import EnhancedBatchProcessor
        processor = EnhancedBatchProcessor()
        processor_status = "✅ 批量处理器正常"
    except Exception as e:
        processor_status = f"❌ 批量处理器错误: {e}"
    
    ttk.Label(status_frame, text=processor_status).pack(anchor=tk.W)
    
    # 按钮框架
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    def start_full_gui():
        """启动完整GUI"""
        try:
            root.destroy()
            from pdf2md_gui import PDF2MDGUI
            app = PDF2MDGUI()
            app.run()
        except Exception as e:
            messagebox.showerror("错误", f"启动完整GUI失败: {e}")
    
    def test_conversion():
        """测试转换功能"""
        try:
            from enhanced_batch_processor import EnhancedBatchProcessor
            processor = EnhancedBatchProcessor()
            messagebox.showinfo("测试", "转换功能测试通过！")
        except Exception as e:
            messagebox.showerror("错误", f"转换功能测试失败: {e}")
    
    def check_cache():
        """检查缓存"""
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            cache_manager = EnhancedCacheManager()
            cache_info = cache_manager.check_cache_status()
            
            info_text = f"""缓存信息:
目录: {cache_info['cache_dir']}
总大小: {cache_info['total_size'] / (1024**3):.2f} GB
模型文件数: {cache_info['model_count']}
缓存效率: {cache_info['cache_efficiency']*100:.1f}%"""
            
            messagebox.showinfo("缓存信息", info_text)
        except Exception as e:
            messagebox.showerror("错误", f"检查缓存失败: {e}")
    
    # 按钮
    ttk.Button(button_frame, text="启动完整GUI", command=start_full_gui).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="测试转换", command=test_conversion).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="检查缓存", command=check_cache).pack(side=tk.LEFT)
    
    # 退出按钮
    ttk.Button(main_frame, text="退出", command=root.quit).pack(pady=(20, 0))
    
    return root

def main():
    """主函数"""
    print("🚀 启动简化GUI...")
    
    try:
        root = create_simple_gui()
        root.mainloop()
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 