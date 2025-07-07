#!/usr/bin/env python3
"""
修复版PDF转Markdown GUI
禁用自动预加载，直接启动到功能界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

class FixedPDF2MDGUI:
    """修复版PDF转Markdown GUI主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具 - 修复版")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        self.root.resizable(True, True)
        
        # 配置
        self.config_file = Path("gui_config.json")
        self.config = self.load_config()
        
        # 转换器
        self.converter = None
        self.conversion_thread = None
        self.is_converting = False
        
        # 批量处理器
        self.batch_processor = None
        
        # 处理任务列表
        self.processing_tasks = []
        
        self.setup_ui()
        self.load_config_to_ui()
        
        # 禁用自动预加载，直接显示界面
        self.log("✅ GUI界面已启动（修复版）")
        self.log("📝 已禁用自动预加载，避免启动卡顿")
    
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
            "auto_preload": False,  # 默认禁用自动预加载
            "show_progress": True,
            "theme": "default",
            "device": "cpu",  # 默认使用CPU
            "max_workers": "1"  # 默认单线程
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
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                "input_dir": self.input_dir_var.get(),
                "output_dir": self.output_dir_var.get(),
                "language": self.language_var.get(),
                "backend": self.backend_var.get(),
                "method": self.method_var.get(),
                "enable_formula": self.enable_formula_var.get(),
                "enable_table": self.enable_table_var.get(),
                "cache_dir": self.cache_dir_var.get(),
                "auto_preload": self.auto_preload_var.get(),
                "show_progress": self.show_progress_var.get(),
                "theme": self.theme_var.get(),
                "device": self.device_var.get(),
                "max_workers": self.max_workers_var.get()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.log("✅ 配置已保存")
        except Exception as e:
            self.log(f"❌ 保存配置失败: {e}")
    
    def setup_ui(self):
        """设置主界面UI"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 先初始化日志选项卡，保证log_text已创建
        self.setup_log_tab(self.notebook)
        self.setup_conversion_tab(self.notebook)
        self.setup_settings_tab(self.notebook)
        
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def setup_conversion_tab(self, notebook):
        """设置转换选项卡"""
        conversion_frame = ttk.Frame(notebook, padding="10")
        notebook.add(conversion_frame, text="转换")
        
        # 输入设置
        input_frame = ttk.LabelFrame(conversion_frame, text="输入设置", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
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
        options_frame = ttk.LabelFrame(conversion_frame, text="转换选项", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
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
        
        # 处理设备设置
        ttk.Label(options_frame, text="处理设备:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.device_var = tk.StringVar(value="cpu")
        device_combo = ttk.Combobox(options_frame, textvariable=self.device_var,
                                   values=["cpu", "gpu", "auto"], width=10)
        device_combo.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # 并发设置
        ttk.Label(options_frame, text="并发数:").grid(row=2, column=2, padx=(20, 0), pady=(10, 0), sticky=tk.W)
        self.max_workers_var = tk.StringVar(value="1")
        workers_combo = ttk.Combobox(options_frame, textvariable=self.max_workers_var,
                                    values=["1", "2", "4"], width=10)
        workers_combo.grid(row=2, column=3, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # 控制按钮
        control_frame = ttk.Frame(conversion_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始转换", 
                                      command=self.start_conversion, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止转换", 
                                     command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(conversion_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        conversion_frame.columnconfigure(0, weight=1)
    
    def setup_settings_tab(self, notebook):
        """设置配置选项卡"""
        settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(settings_frame, text="设置")
        
        # 缓存设置
        cache_frame = ttk.LabelFrame(settings_frame, text="缓存设置", padding="10")
        cache_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ttk.Label(cache_frame, text="缓存目录:").grid(row=0, column=0, sticky=tk.W)
        self.cache_dir_var = tk.StringVar()
        cache_entry = ttk.Entry(cache_frame, textvariable=self.cache_dir_var, width=50)
        cache_entry.grid(row=0, column=1, padx=(10, 5), sticky="ew")
        ttk.Button(cache_frame, text="浏览", command=self.browse_cache_dir).grid(row=0, column=2)
        
        self.auto_preload_var = tk.BooleanVar(value=False)  # 默认禁用
        preload_check = ttk.Checkbutton(cache_frame, text="自动预加载模型（不推荐）", 
                                       variable=self.auto_preload_var)
        preload_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        cache_frame.columnconfigure(1, weight=1)
        
        # 界面设置
        ui_frame = ttk.LabelFrame(settings_frame, text="界面设置", padding="10")
        ui_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.show_progress_var = tk.BooleanVar(value=True)
        progress_check = ttk.Checkbutton(ui_frame, text="显示进度条", 
                                        variable=self.show_progress_var)
        progress_check.grid(row=0, column=0, sticky=tk.W)
        
        # 主题设置
        ttk.Label(ui_frame, text="主题:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.theme_var = tk.StringVar(value="default")
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var,
                                   values=["default", "light", "dark"], width=15)
        theme_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="ew")
        
        # 保存按钮
        save_frame = ttk.Frame(settings_frame)
        save_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(save_frame, text="保存设置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(save_frame, text="重置设置", command=self.reset_config).pack(side=tk.LEFT)
        
        settings_frame.columnconfigure(0, weight=1)
    
    def setup_log_tab(self, notebook):
        """设置日志选项卡"""
        log_frame = ttk.Frame(notebook, padding="10")
        notebook.add(log_frame, text="日志")
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_text.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # 日志控制按钮
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(log_buttons_frame, text="清空日志", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_buttons_frame, text="保存日志", 
                  command=self.save_log).pack(side=tk.LEFT)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 初始日志
        self.log("修复版GUI界面已启动")
    
    def load_config_to_ui(self):
        """加载配置到UI"""
        self.input_dir_var.set(self.config.get("input_dir", ""))
        self.output_dir_var.set(self.config.get("output_dir", "./output"))
        self.language_var.set(self.config.get("language", "ch"))
        self.backend_var.set(self.config.get("backend", "pipeline"))
        self.method_var.set(self.config.get("method", "auto"))
        self.enable_formula_var.set(self.config.get("enable_formula", True))
        self.enable_table_var.set(self.config.get("enable_table", True))
        self.device_var.set(self.config.get("device", "cpu"))
        self.max_workers_var.set(self.config.get("max_workers", "1"))
        self.cache_dir_var.set(self.config.get("cache_dir", "./models_cache"))
        self.auto_preload_var.set(self.config.get("auto_preload", False))
        self.show_progress_var.set(self.config.get("show_progress", True))
        self.theme_var.set(self.config.get("theme", "default"))
    
    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择输入目录")
        if directory:
            self.input_dir_var.set(directory)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def browse_cache_dir(self):
        """浏览缓存目录"""
        directory = filedialog.askdirectory(title="选择缓存目录")
        if directory:
            self.cache_dir_var.set(directory)
    
    def log(self, message: str):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        else:
            print(f"[{timestamp}] {message}")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """保存日志"""
        filename = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", "日志已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")
    
    def test_connection(self):
        """测试组件连接"""
        self.log("🔍 测试组件连接...")
        
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
        
        # 测试转换器
        try:
            from stable_mineru_converter import MineruConverter
            converter = MineruConverter()
            results.append("✅ 转换器: 正常")
        except Exception as e:
            results.append(f"❌ 转换器: {str(e)[:50]}")
        
        # 显示结果
        result_text = "\n".join(results)
        messagebox.showinfo("组件测试", f"测试结果:\n\n{result_text}")
        
        self.log("组件测试完成")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            self.config_file.unlink(missing_ok=True)
            self.config = self.load_config()
            self.load_config_to_ui()
            self.log("设置已重置")
    
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
            from enhanced_batch_processor import EnhancedBatchProcessor
            
            input_path = Path(input_dir)
            
            # 获取设备偏好设置
            device_setting = self.device_var.get()
            if device_setting == "auto":
                device_preference = "gpu_first"
            elif device_setting == "gpu":
                device_preference = "gpu_first"
            else:
                device_preference = "cpu_first"
            
            # 获取并发设置
            max_workers = int(self.max_workers_var.get())
            
            # 创建批量处理器
            self.batch_processor = EnhancedBatchProcessor(
                max_workers=max_workers,
                device_preference=device_preference
            )
            
            # 准备转换选项
            options = {
                "language": self.language_var.get(),
                "backend": self.backend_var.get(),
                "method": self.method_var.get(),
                "enable_formula": self.enable_formula_var.get(),
                "enable_table": self.enable_table_var.get()
            }
            
            if input_path.is_file():
                # 转换单个文件
                filename = input_path.name
                self.add_processing_task(filename)
                self.update_task_status(filename, "处理中", 0)
                
                # 添加任务到批量处理器
                self.batch_processor.add_task(input_path, Path(output_dir), options)
                
                # 开始处理
                def progress_callback(progress: int, message: str):
                    self.root.after(0, lambda: self._update_progress(progress, message))
                
                result = self.batch_processor.start_batch_processing(progress_callback)
                
                if result and result["success_count"] > 0:
                    self.root.after(0, lambda: self._conversion_complete(result, filename))
                else:
                    self.root.after(0, lambda: self._conversion_error("转换失败", filename))
            
            elif input_path.is_dir():
                # 批量转换
                pdf_files = list(input_path.glob("*.pdf"))
                
                if not pdf_files:
                    self.root.after(0, lambda: self._conversion_error("未找到PDF文件"))
                    return
                
                # 添加所有任务
                for pdf_file in pdf_files:
                    filename = pdf_file.name
                    self.add_processing_task(filename)
                    self.batch_processor.add_task(pdf_file, Path(output_dir), options)
                
                self.log(f"找到 {len(pdf_files)} 个PDF文件")
                
                # 开始批量处理
                def progress_callback(progress: int, message: str):
                    self.root.after(0, lambda: self._update_progress(progress, message))
                
                result = self.batch_processor.start_batch_processing(progress_callback)
                
                if result and result["success_count"] > 0:
                    self.root.after(0, lambda: self._batch_conversion_complete(result))
                else:
                    self.root.after(0, lambda: self._conversion_error("批量转换失败"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._conversion_error(error_msg))
    
    def _update_progress(self, progress: int, message: str):
        """更新进度"""
        self.progress_var.set(progress)
        self.log(message)
        self.status_var.set(f"转换中... {progress}%")
    
    def _conversion_complete(self, result: Dict[str, Any], filename: str = ""):
        """转换完成"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_var.set("转换完成")
        
        self.log("✅ 转换成功!")
        messagebox.showinfo("成功", "转换完成！")
    
    def _batch_conversion_complete(self, result: Dict[str, Any]):
        """批量转换完成"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_var.set("批量转换完成")
        
        self.log("✅ 批量转换完成!")
        self.log(f"📊 总文件数: {result['total_files']}")
        self.log(f"✅ 成功: {result['success_count']}")
        self.log(f"❌ 失败: {result['failed_count']}")
        
        messagebox.showinfo("成功", f"批量转换完成！\n成功: {result['success_count']}\n失败: {result['failed_count']}")
    
    def _conversion_error(self, error: str, filename: str = ""):
        """转换错误"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换失败")
        
        self.log(f"❌ 转换失败: {error}")
        messagebox.showerror("错误", f"转换失败: {error}")
    
    def stop_conversion(self):
        """停止转换"""
        if self.batch_processor:
            self.batch_processor.stop_processing()
        
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换已停止")
        self.log("⏹️ 转换已停止")
    
    def add_processing_task(self, filename: str):
        """添加处理任务"""
        import datetime
        task = {
            "filename": filename,
            "status": "等待中",
            "progress": 0,
            "start_time": datetime.datetime.now().strftime("%H:%M:%S"),
            "duration": ""
        }
        self.processing_tasks.append(task)
    
    def update_task_status(self, filename: str, status: str, progress: int = 0, duration: str = ""):
        """更新任务状态"""
        for task in self.processing_tasks:
            if task.get("filename") == filename:
                task["status"] = status
                task["progress"] = progress
                if duration:
                    task["duration"] = duration
                break
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动修复版GUI...")
    
    try:
        app = FixedPDF2MDGUI()
        app.run()
    except Exception as e:
        print(f"❌ 修复版GUI启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 