#!/usr/bin/env python3
"""
主GUI功能测试脚本
测试PDF2MDGUI的核心功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

class SimplePDF2MDGUI:
    """简化的PDF转Markdown GUI测试类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具 - 测试版")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 配置
        self.config_file = Path("test_gui_config.json")
        self.config = self.load_config()
        
        # 转换器
        self.converter = None
        self.conversion_thread = None
        self.is_converting = False
        
        self.setup_ui()
        self.load_config_to_ui()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "input_dir": "",
            "output_dir": "./output",
            "language": "ch",
            "backend": "pipeline",
            "method": "auto",
            "enable_formula": True,
            "enable_table": True,
            "cache_dir": "./models_cache",
            "auto_preload": True,
            "show_progress": True,
            "theme": "default"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"加载配置失败: {e}")
                return default_config
        else:
            return default_config
    
    def setup_ui(self):
        """设置主界面UI"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入设置
        input_frame = ttk.LabelFrame(main_frame, text="输入设置", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输入目录
        ttk.Label(input_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W)
        self.input_dir_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_dir_var, width=50)
        input_entry.grid(row=0, column=1, padx=(10, 5), sticky="ew")
        ttk.Button(input_frame, text="浏览", command=self.browse_input_dir).grid(row=0, column=2)
        
        # 输出目录
        ttk.Label(input_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(input_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=1, column=1, padx=(10, 5), pady=(10, 0), sticky="ew")
        ttk.Button(input_frame, text="浏览", command=self.browse_output_dir).grid(row=1, column=2, pady=(10, 0))
        
        input_frame.columnconfigure(1, weight=1)
        
        # 转换选项
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 语言设置
        ttk.Label(options_frame, text="语言:").grid(row=0, column=0, sticky=tk.W)
        self.language_var = tk.StringVar(value="ch")
        language_combo = ttk.Combobox(options_frame, textvariable=self.language_var, 
                                     values=["ch", "en"], width=10)
        language_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # 后端设置
        ttk.Label(options_frame, text="后端:").grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        self.backend_var = tk.StringVar(value="pipeline")
        backend_combo = ttk.Combobox(options_frame, textvariable=self.backend_var,
                                    values=["pipeline"], width=15)
        backend_combo.grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        # 解析方法
        ttk.Label(options_frame, text="解析方法:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.method_var = tk.StringVar(value="auto")
        method_combo = ttk.Combobox(options_frame, textvariable=self.method_var,
                                   values=["auto", "ocr", "layout"], width=10)
        method_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # 功能开关
        self.enable_formula_var = tk.BooleanVar(value=True)
        formula_check = ttk.Checkbutton(options_frame, text="启用公式解析", 
                                       variable=self.enable_formula_var)
        formula_check.grid(row=1, column=2, padx=(20, 0), pady=(10, 0), sticky=tk.W)
        
        self.enable_table_var = tk.BooleanVar(value=True)
        table_check = ttk.Checkbutton(options_frame, text="启用表格解析", 
                                     variable=self.enable_table_var)
        table_check.grid(row=1, column=3, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始转换", 
                                      command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止转换", 
                                     command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="检查缓存", command=self.check_cache).pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=(10, 0))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_config_to_ui(self):
        """加载配置到UI"""
        self.input_dir_var.set(self.config.get("input_dir", ""))
        self.output_dir_var.set(self.config.get("output_dir", "./output"))
        self.language_var.set(self.config.get("language", "ch"))
        self.backend_var.set(self.config.get("backend", "pipeline"))
        self.method_var.set(self.config.get("method", "auto"))
        self.enable_formula_var.set(self.config.get("enable_formula", True))
        self.enable_table_var.set(self.config.get("enable_table", True))
    
    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择输入目录")
        if directory:
            self.input_dir_var.set(directory)
            self.log(f"选择输入目录: {directory}")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
            self.log(f"选择输出目录: {directory}")
    
    def log(self, message: str):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_cache(self):
        """检查缓存"""
        self.log("检查缓存状态...")
        try:
            # 模拟缓存检查
            cache_info = {
                "cache_dir": "./models_cache",
                "total_size": 1024 * 1024 * 100,  # 100MB
                "model_count": 5,
                "cache_efficiency": 0.85
            }
            
            self.log(f"缓存目录: {cache_info['cache_dir']}")
            self.log(f"总大小: {cache_info['total_size'] / (1024**3):.2f} GB")
            self.log(f"模型文件数: {cache_info['model_count']}")
            self.log(f"缓存效率: {cache_info['cache_efficiency']*100:.1f}%")
            
            self.status_var.set("缓存检查完成")
        except Exception as e:
            self.log(f"检查缓存失败: {e}")
            self.status_var.set("缓存检查失败")
    
    def start_conversion(self):
        """开始转换"""
        if self.is_converting:
            return
        
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
        
        self.is_converting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("正在转换...")
        
        self.log("开始转换...")
        
        # 在新线程中运行转换
        self.conversion_thread = threading.Thread(
            target=self._run_conversion,
            args=(input_dir, output_dir)
        )
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
    
    def _run_conversion(self, input_dir: str, output_dir: str):
        """运行转换"""
        try:
            # 模拟转换过程
            for i in range(101):
                if not self.is_converting:
                    break
                
                # 更新进度
                self.root.after(0, lambda p=i: self._update_progress(p, f"处理中... {p}%"))
                
                import time
                time.sleep(0.05)  # 模拟处理时间
            
            if self.is_converting:
                self.root.after(0, lambda: self._conversion_complete({"success": True}, "test.pdf"))
            
        except Exception as e:
            self.root.after(0, lambda: self._conversion_error(str(e), "test.pdf"))
    
    def _update_progress(self, progress: int, message: str):
        """更新进度"""
        self.progress_var.set(progress)
        self.status_var.set(message)
        self.log(message)
    
    def _conversion_complete(self, result: Dict[str, Any], filename: str = ""):
        """转换完成"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换完成")
        self.log(f"转换完成: {filename}")
        messagebox.showinfo("完成", f"转换完成: {filename}")
    
    def _conversion_error(self, error: str, filename: str = ""):
        """转换错误"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换失败")
        self.log(f"转换失败: {error}")
        messagebox.showerror("错误", f"转换失败: {error}")
    
    def stop_conversion(self):
        """停止转换"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换已停止")
        self.log("转换已停止")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = SimplePDF2MDGUI()
    app.run()

if __name__ == "__main__":
    main() 