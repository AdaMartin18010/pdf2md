#!/usr/bin/env python3
"""
简单GUI测试 - 避免内存占用过高
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from pathlib import Path

class SimplePDFConverter:
    """简单的PDF转换器GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具 - 简单版")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="PDF转Markdown工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="简单版本 - 避免内存占用过高", font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 输入文件
        ttk.Label(file_frame, text="输入PDF文件:").pack(anchor=tk.W)
        
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_file_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_file_var, width=50)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(input_frame, text="浏览", command=self.browse_input_file).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 输出目录
        ttk.Label(file_frame, text="输出目录:").pack(anchor=tk.W, pady=(10, 0))
        
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_dir_var = tk.StringVar(value="./output")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(output_frame, text="浏览", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 转换选项框架
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 设备选择
        device_frame = ttk.Frame(options_frame)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(device_frame, text="处理设备:").pack(side=tk.LEFT)
        
        self.device_var = tk.StringVar(value="cpu")
        device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, 
                                   values=["cpu", "gpu"], width=10, state="readonly")
        device_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 并发设置
        concurrent_frame = ttk.Frame(options_frame)
        concurrent_frame.pack(fill=tk.X)
        
        ttk.Label(concurrent_frame, text="并发数:").pack(side=tk.LEFT)
        
        self.concurrent_var = tk.StringVar(value="1")
        concurrent_combo = ttk.Combobox(concurrent_frame, textvariable=self.concurrent_var,
                                       values=["1", "2", "4"], width=10, state="readonly")
        concurrent_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=20)
        
        self.convert_button = ttk.Button(control_frame, text="开始转换", 
                                        command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def test_connection(self):
        """测试组件连接"""
        self.status_var.set("正在测试组件...")
        
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
        
        self.status_var.set("组件测试完成")
    
    def start_conversion(self):
        """开始转换"""
        input_file = self.input_file_var.get()
        output_dir = self.output_dir_var.get()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入PDF文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 显示转换信息
        device = self.device_var.get()
        concurrent = self.concurrent_var.get()
        
        info_text = f"""转换信息:
输入文件: {input_file}
输出目录: {output_dir}
处理设备: {device}
并发数: {concurrent}

注意: 这是简单版本，实际转换功能需要完整版本支持。
"""
        
        messagebox.showinfo("转换信息", info_text)
        self.status_var.set("转换信息已显示")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动简单GUI测试...")
    
    try:
        app = SimplePDFConverter()
        app.run()
    except Exception as e:
        print(f"❌ 简单GUI测试失败: {e}")
        import traceback
        traceback.print_exc()

 