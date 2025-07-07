#!/usr/bin/env python3
"""
快速修复版GUI - 禁用自动预加载
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path

class QuickFixedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具 - 快速修复版")
        self.root.geometry("600x400")
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="PDF转Markdown工具", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        ttk.Label(main_frame, text="快速修复版 - 禁用自动预加载", font=("Arial", 10)).pack(pady=(0, 30))
        
        # 文件选择
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 输入目录
        ttk.Label(file_frame, text="输入目录:").pack(anchor=tk.W)
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_dir_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_dir_var, width=50)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="浏览", command=self.browse_input_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 输出目录
        ttk.Label(file_frame, text="输出目录:").pack(anchor=tk.W, pady=(10, 0))
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_dir_var = tk.StringVar(value="./output")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 转换选项
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 设备选择
        device_frame = ttk.Frame(options_frame)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(device_frame, text="处理设备:").pack(side=tk.LEFT)
        self.device_var = tk.StringVar(value="cpu")
        device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, 
                                   values=["cpu", "gpu", "auto"], width=10)
        device_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 并发设置
        ttk.Label(device_frame, text="并发数:").pack(side=tk.LEFT, padx=(20, 0))
        self.max_workers_var = tk.StringVar(value="1")
        workers_combo = ttk.Combobox(device_frame, textvariable=self.max_workers_var,
                                    values=["1", "2", "4"], width=10)
        workers_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 初始日志
        print("✅ 快速修复版GUI已启动")
        print("📝 已禁用自动预加载，避免启动卡顿")
    
    def browse_input_dir(self):
        directory = filedialog.askdirectory(title="选择输入目录")
        if directory:
            self.input_dir_var.set(directory)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def test_connection(self):
        """测试组件连接"""
        print("🔍 测试组件连接...")
        
        results = []
        
        # 测试缓存管理器
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            cache_manager = EnhancedCacheManager()
            cache_info = cache_manager.check_cache_status()
            results.append(f"✅ 缓存管理器: {cache_info['model_count']} 个模型")
        except Exception as e:
            results.append(f"❌ 缓存管理器: {str(e)[:50]}")
        
        # 测试批量处理器
        try:
            from enhanced_batch_processor import EnhancedBatchProcessor
            processor = EnhancedBatchProcessor()
            results.append("✅ 批量处理器: 正常")
        except Exception as e:
            results.append(f"❌ 批量处理器: {str(e)[:50]}")
        
        # 显示结果
        result_text = "\n".join(results)
        messagebox.showinfo("组件测试", f"测试结果:\n\n{result_text}")
        
        print("组件测试完成")
    
    def start_conversion(self):
        """开始转换"""
        input_dir = self.input_dir_var.get()
        output_dir = self.output_dir_var.get()
        
        if not input_dir:
            messagebox.showerror("错误", "请选择输入目录")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("错误", "输入目录不存在")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        self.start_button.config(state=tk.DISABLED)
        self.status_var.set("正在转换...")
        
        # 显示转换信息
        device = self.device_var.get()
        workers = self.max_workers_var.get()
        
        info_text = f"""转换信息:
输入目录: {input_dir}
输出目录: {output_dir}
处理设备: {device}
并发数: {workers}

注意: 这是快速修复版，实际转换功能需要完整版本支持。
"""
        
        messagebox.showinfo("转换信息", info_text)
        self.status_var.set("转换信息已显示")
        self.start_button.config(state=tk.NORMAL)
    
    def run(self):
        self.root.mainloop()

def main():
    print("🚀 启动快速修复版GUI...")
    
    try:
        app = QuickFixedGUI()
        app.run()
    except Exception as e:
        print(f"❌ 快速修复版GUI启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 