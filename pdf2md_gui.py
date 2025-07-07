#!/usr/bin/env python3
"""
PDF转Markdown GUI界面
整合用户设置和核心功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

class PDF2MDGUI:
    """PDF转Markdown GUI主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具")
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
            "theme": "default",
            "enable_shutdown": False,
            "shutdown_delay": "30"
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
                "language_ui": self.language_ui_var.get(),
                # 处理设置
                "timeout": self.timeout_var.get(),
                "device": self.device_var.get(),
                "max_workers": self.max_workers_var.get(),
                "memory_limit": self.memory_limit_var.get(),
                "enable_optimization": self.enable_optimization_var.get(),
                "enable_caching": self.enable_caching_var.get(),
                "enable_retry": self.enable_retry_var.get(),
                "enable_logging": self.enable_logging_var.get(),
                "enable_shutdown": self.enable_shutdown_var.get(),
                "shutdown_delay": self.shutdown_delay_var.get()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.log("✅ 配置已保存")
        except Exception as e:
            self.log(f"❌ 保存配置失败: {e}")
    
    def setup_ui(self):
        """设置主界面UI"""
        self.root.title("PDF转Markdown工具")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 先初始化日志选项卡，保证log_text已创建
        self.setup_log_tab(self.notebook)
        self.setup_processing_tab(self.notebook)
        self.setup_conversion_tab(self.notebook)
        self.setup_settings_tab(self.notebook)
        self.setup_cache_tab(self.notebook)
        
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
        self.device_var = tk.StringVar(value="auto")
        device_combo = ttk.Combobox(options_frame, textvariable=self.device_var,
                                   values=["auto", "cpu", "gpu"], width=10)
        device_combo.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # 设备说明
        device_info = ttk.Label(options_frame, text="auto: 自动选择(优先GPU), cpu: 强制CPU, gpu: 强制GPU", 
                               font=("Arial", 8), foreground="gray")
        device_info.grid(row=2, column=2, columnspan=2, padx=(10, 0), pady=(10, 0), sticky=tk.W)
        
        # 控制按钮
        control_frame = ttk.Frame(conversion_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始转换", 
                                      command=self.start_conversion, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止转换", 
                                     command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="检查缓存", command=self.check_cache).pack(side=tk.LEFT)
        
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
        
        self.auto_preload_var = tk.BooleanVar(value=True)
        preload_check = ttk.Checkbutton(cache_frame, text="自动预加载模型", 
                                       variable=self.auto_preload_var)
        preload_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        cache_frame.columnconfigure(1, weight=1)
        
        # 处理设置
        processing_frame = ttk.LabelFrame(settings_frame, text="处理设置", padding="10")
        processing_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 超时设置
        ttk.Label(processing_frame, text="处理超时时间(秒):").grid(row=0, column=0, sticky=tk.W)
        self.timeout_var = tk.StringVar(value="300")
        timeout_entry = ttk.Entry(processing_frame, textvariable=self.timeout_var, width=10)
        timeout_entry.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # 并发设置
        ttk.Label(processing_frame, text="最大并发数:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.max_workers_var = tk.StringVar(value="2")
        workers_entry = ttk.Entry(processing_frame, textvariable=self.max_workers_var, width=10)
        workers_entry.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="ew")
        
        # 内存限制
        ttk.Label(processing_frame, text="内存限制(GB):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.memory_limit_var = tk.StringVar(value="4")
        memory_entry = ttk.Entry(processing_frame, textvariable=self.memory_limit_var, width=10)
        memory_entry.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky="ew")
        
        # 高级处理选项
        advanced_frame = ttk.LabelFrame(processing_frame, text="高级选项", padding="5")
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.enable_optimization_var = tk.BooleanVar(value=True)
        optimization_check = ttk.Checkbutton(advanced_frame, text="启用性能优化", 
                                           variable=self.enable_optimization_var)
        optimization_check.grid(row=0, column=0, sticky=tk.W)
        
        self.enable_caching_var = tk.BooleanVar(value=True)
        caching_check = ttk.Checkbutton(advanced_frame, text="启用处理缓存", 
                                       variable=self.enable_caching_var)
        caching_check.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        self.enable_retry_var = tk.BooleanVar(value=True)
        retry_check = ttk.Checkbutton(advanced_frame, text="启用失败重试", 
                                     variable=self.enable_retry_var)
        retry_check.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.enable_logging_var = tk.BooleanVar(value=True)
        logging_check = ttk.Checkbutton(advanced_frame, text="启用详细日志", 
                                       variable=self.enable_logging_var)
        logging_check.grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        
        # 关机选项
        shutdown_frame = ttk.LabelFrame(processing_frame, text="转换完成后操作", padding="5")
        shutdown_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.enable_shutdown_var = tk.BooleanVar(value=False)
        shutdown_check = ttk.Checkbutton(shutdown_frame, text="转换完成后自动关机", 
                                        variable=self.enable_shutdown_var)
        shutdown_check.grid(row=0, column=0, sticky=tk.W)
        
        # 关机延迟设置
        ttk.Label(shutdown_frame, text="关机延迟(秒):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.shutdown_delay_var = tk.StringVar(value="30")
        shutdown_delay_entry = ttk.Entry(shutdown_frame, textvariable=self.shutdown_delay_var, width=10)
        shutdown_delay_entry.grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky="ew")
        
        # 关机提示
        shutdown_info = ttk.Label(shutdown_frame, text="⚠️ 启用后将在转换完成并延迟指定时间后自动关机", 
                                 font=("Arial", 8), foreground="orange")
        shutdown_info.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        processing_frame.columnconfigure(1, weight=1)
        
        # 界面设置
        ui_frame = ttk.LabelFrame(settings_frame, text="界面设置", padding="10")
        ui_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.show_progress_var = tk.BooleanVar(value=True)
        progress_check = ttk.Checkbutton(ui_frame, text="显示进度条", 
                                        variable=self.show_progress_var)
        progress_check.grid(row=0, column=0, sticky=tk.W)
        
        # 语言设置
        ttk.Label(ui_frame, text="界面语言:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.language_ui_var = tk.StringVar(value="zh")
        language_combo = ttk.Combobox(ui_frame, textvariable=self.language_ui_var,
                                     values=["zh", "en"], width=15)
        language_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="ew")
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # 主题设置
        ttk.Label(ui_frame, text="主题:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.theme_var = tk.StringVar(value="default")
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var,
                                   values=["default", "light", "dark"], width=15)
        theme_combo.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky="ew")
        theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # 保存按钮
        save_frame = ttk.Frame(settings_frame)
        save_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(save_frame, text="保存设置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(save_frame, text="重置设置", command=self.reset_config).pack(side=tk.LEFT)
        
        settings_frame.columnconfigure(0, weight=1)
    
    def setup_cache_tab(self, notebook):
        """设置缓存选项卡"""
        cache_frame = ttk.Frame(notebook, padding="10")
        notebook.add(cache_frame, text="缓存管理")
        
        # 缓存信息
        info_frame = ttk.LabelFrame(cache_frame, text="缓存信息", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.cache_info_text = scrolledtext.ScrolledText(info_frame, height=10, width=70)
        self.cache_info_text.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 缓存操作按钮
        cache_buttons_frame = ttk.Frame(cache_frame)
        cache_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(cache_buttons_frame, text="刷新缓存信息", 
                  command=self.refresh_cache_info).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cache_buttons_frame, text="预加载模型", 
                  command=self.preload_models).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cache_buttons_frame, text="清理缓存", 
                  command=self.clear_cache).pack(side=tk.LEFT)
        
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        cache_frame.columnconfigure(0, weight=1)
        cache_frame.rowconfigure(0, weight=1)
        
        # 初始加载缓存信息
        self.refresh_cache_info()
    
    def setup_processing_tab(self, notebook):
        """设置处理状态选项卡"""
        processing_frame = ttk.Frame(notebook, padding="10")
        notebook.add(processing_frame, text="处理状态")
        
        # 处理状态信息
        status_frame = ttk.LabelFrame(processing_frame, text="处理状态", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 状态概览
        overview_frame = ttk.Frame(status_frame)
        overview_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 当前状态
        self.current_status_var = tk.StringVar(value="空闲")
        ttk.Label(overview_frame, text="当前状态:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(overview_frame, textvariable=self.current_status_var, 
                 font=("Arial", 10, "bold")).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # 处理设备
        self.device_status_var = tk.StringVar(value="CPU")
        ttk.Label(overview_frame, text="处理设备:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(overview_frame, textvariable=self.device_status_var).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
        
        # 内存使用
        self.memory_usage_var = tk.StringVar(value="0 MB")
        ttk.Label(overview_frame, text="内存使用:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(overview_frame, textvariable=self.memory_usage_var).grid(row=2, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
        
        # 处理任务列表
        tasks_frame = ttk.LabelFrame(processing_frame, text="处理任务", padding="10")
        tasks_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 创建任务列表
        columns = ("文件名", "状态", "进度", "开始时间", "耗时")
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show="headings", height=8)
        
        # 设置列标题
        for col in columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=100)
        
        # 添加滚动条
        tasks_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)
        
        self.tasks_tree.grid(row=0, column=0, sticky="ew")
        tasks_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 任务控制按钮
        tasks_buttons_frame = ttk.Frame(tasks_frame)
        tasks_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(tasks_buttons_frame, text="刷新状态", 
                  command=self.refresh_processing_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(tasks_buttons_frame, text="清空列表", 
                  command=self.clear_processing_tasks).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(tasks_buttons_frame, text="导出状态", 
                  command=self.export_processing_status).pack(side=tk.LEFT)
        
        # 处理统计
        stats_frame = ttk.LabelFrame(processing_frame, text="处理统计", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 统计信息
        stats_info_frame = ttk.Frame(stats_frame)
        stats_info_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.total_files_var = tk.StringVar(value="0")
        self.success_files_var = tk.StringVar(value="0")
        self.failed_files_var = tk.StringVar(value="0")
        self.avg_time_var = tk.StringVar(value="0秒")
        
        ttk.Label(stats_info_frame, text="总文件数:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(stats_info_frame, textvariable=self.total_files_var).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        ttk.Label(stats_info_frame, text="成功:").grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        ttk.Label(stats_info_frame, textvariable=self.success_files_var).grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        ttk.Label(stats_info_frame, text="失败:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(stats_info_frame, textvariable=self.failed_files_var).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
        
        ttk.Label(stats_info_frame, text="平均耗时:").grid(row=1, column=2, padx=(20, 0), pady=(5, 0), sticky=tk.W)
        ttk.Label(stats_info_frame, textvariable=self.avg_time_var).grid(row=1, column=3, padx=(10, 0), pady=(5, 0), sticky=tk.W)
        
        # 配置网格权重
        status_frame.columnconfigure(0, weight=1)
        tasks_frame.columnconfigure(0, weight=1)
        tasks_frame.rowconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        processing_frame.columnconfigure(0, weight=1)
        processing_frame.rowconfigure(1, weight=1)
        
        # 初始化任务列表
        self.processing_tasks = []
        self.refresh_processing_status()
    
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
        self.log("GUI界面已启动")
    
    def load_config_to_ui(self):
        """加载配置到UI"""
        self.input_dir_var.set(self.config.get("input_dir", ""))
        self.output_dir_var.set(self.config.get("output_dir", "./output"))
        self.language_var.set(self.config.get("language", "ch"))
        self.backend_var.set(self.config.get("backend", "pipeline"))
        self.method_var.set(self.config.get("method", "auto"))
        self.enable_formula_var.set(self.config.get("enable_formula", True))
        self.enable_table_var.set(self.config.get("enable_table", True))
        self.device_var.set(self.config.get("device", "auto"))
        self.cache_dir_var.set(self.config.get("cache_dir", "./models_cache"))
        self.auto_preload_var.set(self.config.get("auto_preload", True))
        self.show_progress_var.set(self.config.get("show_progress", True))
        self.theme_var.set(self.config.get("theme", "default"))
        self.language_ui_var.set(self.config.get("language_ui", "zh"))
        
        # 处理设置
        self.timeout_var.set(self.config.get("timeout", "300"))
        self.max_workers_var.set(self.config.get("max_workers", "2"))
        self.memory_limit_var.set(self.config.get("memory_limit", "4"))
        self.enable_optimization_var.set(self.config.get("enable_optimization", True))
        self.enable_caching_var.set(self.config.get("enable_caching", True))
        self.enable_retry_var.set(self.config.get("enable_retry", True))
        self.enable_logging_var.set(self.config.get("enable_logging", True))
        
        # 关机设置
        self.enable_shutdown_var.set(self.config.get("enable_shutdown", False))
        self.shutdown_delay_var.set(self.config.get("shutdown_delay", "30"))
        
        # 应用当前设置
        self.update_ui_text(self.language_ui_var.get())
        self.apply_theme(self.theme_var.get())
    
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
    
    def check_cache(self):
        """检查缓存"""
        self.log("检查缓存状态...")
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            cache_manager = EnhancedCacheManager()
            cache_info = cache_manager.check_cache_status()
            
            self.log(f"缓存目录: {cache_info['cache_dir']}")
            self.log(f"总大小: {cache_info['total_size'] / (1024**3):.2f} GB")
            self.log(f"模型文件数: {cache_info['model_count']}")
            self.log(f"缓存效率: {cache_info['cache_efficiency']*100:.1f}%")
            
            # 显示详细状态
            for name, info in cache_info['subdirs'].items():
                if info['exists']:
                    status_icon = "✅" if info['has_models'] else "⚠️"
                    size_mb = info['size'] / (1024**2)
                    self.log(f"{status_icon} {name}: {info['model_count']} 个模型 ({size_mb:.1f} MB)")
                else:
                    self.log(f"❌ {name}: 目录不存在")
            
            self.status_var.set("缓存检查完成")
        except Exception as e:
            self.log(f"检查缓存失败: {e}")
            self.status_var.set("缓存检查失败")
    
    def refresh_cache_info(self):
        """刷新缓存信息"""
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            cache_manager = EnhancedCacheManager()
            cache_info = cache_manager.check_cache_status()
            
            info_text = f"""缓存信息:
目录: {cache_info['cache_dir']}
总大小: {cache_info['total_size'] / (1024**3):.2f} GB
模型文件数: {cache_info['model_count']}
缓存效率: {cache_info['cache_efficiency']*100:.1f}%

详细状态:
"""
            
            for name, info in cache_info['subdirs'].items():
                if info['exists']:
                    status_icon = "✅" if info['has_models'] else "⚠️"
                    size_mb = info['size'] / (1024**2)
                    info_text += f"{status_icon} {name}: {info['model_count']} 个模型 ({size_mb:.1f} MB)\n"
                else:
                    info_text += f"❌ {name}: 目录不存在\n"
            
            self.cache_info_text.delete(1.0, tk.END)
            self.cache_info_text.insert(1.0, info_text)
            
        except Exception as e:
            self.cache_info_text.delete(1.0, tk.END)
            self.cache_info_text.insert(1.0, f"获取缓存信息失败: {e}")
    
    def preload_models(self):
        """预加载模型"""
        self.log("开始预加载模型...")
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            cache_manager = EnhancedCacheManager()
            cache_manager.preload_common_models()
            self.log("模型预加载完成")
            self.refresh_cache_info()
        except Exception as e:
            self.log(f"预加载模型失败: {e}")
    
    def clear_cache(self):
        """清理缓存"""
        if messagebox.askyesno("确认", "确定要清理所有缓存吗？这将删除所有模型文件。"):
            self.log("开始清理缓存...")
            try:
                from enhanced_cache_manager import EnhancedCacheManager
                cache_manager = EnhancedCacheManager()
                
                # 手动清理所有缓存文件
                import shutil
                cache_dir = Path(cache_manager.cache_dir)
                
                if cache_dir.exists():
                    # 删除所有子目录
                    for item in cache_dir.iterdir():
                        if item.is_dir():
                            shutil.rmtree(item)
                        elif item.is_file():
                            item.unlink()
                    
                    # 重新创建目录结构
                    cache_manager.setup_cache_directories()
                
                self.log("缓存清理完成")
                self.refresh_cache_info()
            except Exception as e:
                self.log(f"清理缓存失败: {e}")
    
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
                device_preference = "gpu_first"  # 自动选择时优先GPU
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
                    if not self.is_converting:  # 检查是否被停止
                        return
                    self.root.after(0, lambda: self._update_progress(progress, message))
                
                result = self.batch_processor.start_batch_processing(progress_callback)
                
                if not self.is_converting:  # 检查是否被停止
                    return
                
                if result and result["success_count"] > 0:
                    self.root.after(0, lambda: self._conversion_complete(result, filename))
                else:
                    self.root.after(0, lambda: self._conversion_error("转换失败", filename))
            
            elif input_path.is_dir():
                # 批量转换 - 递归查找所有PDF文件
                pdf_files = list(input_path.rglob("*.pdf"))
                
                if not pdf_files:
                    self.root.after(0, lambda: self._conversion_error("未找到PDF文件"))
                    return
                
                # 添加所有任务
                for pdf_file in pdf_files:
                    if not self.is_converting:  # 检查是否被停止
                        return
                    filename = pdf_file.name
                    self.add_processing_task(filename)
                    self.batch_processor.add_task(pdf_file, Path(output_dir), options)
                
                self.log(f"找到 {len(pdf_files)} 个PDF文件")
                
                # 开始批量处理
                def progress_callback(progress: int, message: str):
                    if not self.is_converting:  # 检查是否被停止
                        return
                    self.root.after(0, lambda: self._update_progress(progress, message))
                
                result = self.batch_processor.start_batch_processing(progress_callback)
                
                if not self.is_converting:  # 检查是否被停止
                    return
                
                if result and result["success_count"] > 0:
                    self.root.after(0, lambda: self._batch_conversion_complete(result))
                else:
                    self.root.after(0, lambda: self._conversion_error("批量转换失败"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._conversion_error(error_msg))
    
    def _update_progress(self, progress: int, message: str):
        """更新进度"""
        if not self.is_converting:  # 检查是否被停止
            return
            
        self.progress_var.set(progress)
        self.log(message)
        self.status_var.set(f"转换中... {progress}%")
        
        # 更新当前处理任务的状态
        if self.processing_tasks:
            current_task = self.processing_tasks[-1]
            if current_task.get("status") == "处理中":
                current_task["progress"] = progress
                self.update_tasks_list()
    
    def _conversion_complete(self, result: Dict[str, Any], filename: str = ""):
        """转换完成"""
        if not self.is_converting:  # 检查是否被停止
            return
            
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_var.set("转换完成")
        
        # 更新任务状态
        if filename:
            self.update_task_status(filename, "成功", 100, f"{result['processing_time']:.1f}秒")
        
        self.log("✅ 转换成功!")
        self.log(f"📄 输出文件: {result['output_file']}")
        self.log(f"🖼️ 图片目录: {result['images_dir']}")
        self.log(f"📊 图片数量: {result['image_count']}")
        self.log(f"⏱️ 处理时间: {result['processing_time']:.2f}秒")
        
        messagebox.showinfo("成功", "转换完成！")
        
        # 检查是否需要关机
        self.check_and_shutdown()
    
    def _batch_conversion_complete(self, result: Dict[str, Any]):
        """批量转换完成"""
        if not self.is_converting:  # 检查是否被停止
            return
            
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_var.set("批量转换完成")
        
        # 更新所有任务状态
        for task in self.processing_tasks:
            if task.get("status") == "处理中":
                task["status"] = "成功"
                task["progress"] = 100
        
        self.update_tasks_list()
        self.update_processing_stats()
        
        self.log("✅ 批量转换完成!")
        self.log(f"📊 总文件数: {result['total_files']}")
        self.log(f"✅ 成功: {result['success_count']}")
        self.log(f"❌ 失败: {result['error_count']}")
        
        messagebox.showinfo("成功", f"批量转换完成！\n成功: {result['success_count']}\n失败: {result['error_count']}")
        
        # 检查是否需要关机
        self.check_and_shutdown()
    
    def _conversion_error(self, error: str, filename: str = ""):
        """转换错误"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换失败")
        
        # 更新任务状态
        if filename:
            self.update_task_status(filename, "失败", 0)
        
        self.log(f"❌ 转换失败: {error}")
        messagebox.showerror("错误", f"转换失败: {error}")
    
    def stop_conversion(self):
        """停止转换"""
        if not self.is_converting:
            return
            
        self.log("⏹️ 正在停止转换...")
        
        # 停止批量处理器
        if hasattr(self, 'batch_processor') and self.batch_processor:
            try:
                self.batch_processor.stop_processing()
            except:
                pass
        
        # 设置停止标志
        self.is_converting = False
        
        # 更新UI状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换已停止")
        self.log("⏹️ 转换已停止")
        
        # 更新所有正在处理的任务状态
        for task in self.processing_tasks:
            if task.get("status") == "处理中":
                task["status"] = "已停止"
                self.update_tasks_list()
    
    def schedule_shutdown(self, delay_seconds: int = 30):
        """计划关机"""
        try:
            import subprocess
            import platform
            
            self.log(f"⏰ 计划在 {delay_seconds} 秒后关机...")
            
            if platform.system() == "Windows":
                # Windows关机命令
                cmd = f"shutdown /s /t {delay_seconds}"
                subprocess.Popen(cmd, shell=True)
                self.log("✅ Windows关机命令已执行")
            elif platform.system() == "Linux":
                # Linux关机命令
                cmd = f"shutdown -h {delay_seconds//60}"
                subprocess.Popen(cmd, shell=True)
                self.log("✅ Linux关机命令已执行")
            elif platform.system() == "Darwin":  # macOS
                # macOS关机命令
                cmd = f"sudo shutdown -h +{delay_seconds//60}"
                subprocess.Popen(cmd, shell=True)
                self.log("✅ macOS关机命令已执行")
            else:
                self.log("❌ 不支持的操作系统")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"❌ 关机命令执行失败: {e}")
            return False
    
    def check_and_shutdown(self):
        """检查并执行关机"""
        if self.enable_shutdown_var.get():
            try:
                delay = int(self.shutdown_delay_var.get())
                if delay < 0:
                    delay = 30
                
                self.log(f"🔄 转换完成，准备关机...")
                self.log(f"⏰ 将在 {delay} 秒后关机")
                
                # 显示关机确认对话框
                result = messagebox.askyesno(
                    "关机确认", 
                    f"转换已完成！\n\n将在 {delay} 秒后自动关机。\n\n是否继续？",
                    icon='warning'
                )
                
                if result:
                    # 用户确认关机
                    if self.schedule_shutdown(delay):
                        self.log("✅ 关机计划已设置")
                        messagebox.showinfo("关机计划", f"系统将在 {delay} 秒后自动关机")
                    else:
                        self.log("❌ 关机计划设置失败")
                        messagebox.showerror("错误", "关机计划设置失败，请手动关机")
                else:
                    # 用户取消关机
                    self.log("❌ 用户取消了关机计划")
                    
            except ValueError:
                self.log("❌ 关机延迟设置无效，使用默认30秒")
                if self.schedule_shutdown(30):
                    self.log("✅ 关机计划已设置（默认30秒）")
    
    def on_language_change(self, event=None):
        """语言切换事件"""
        language = self.language_ui_var.get()
        self.log(f"切换界面语言: {language}")
        
        # 更新界面文本
        self.update_ui_text(language)
        
        # 保存设置
        self.save_config()
    
    def on_theme_change(self, event=None):
        """主题切换事件"""
        theme = self.theme_var.get()
        self.log(f"切换主题: {theme}")
        
        # 应用主题
        self.apply_theme(theme)
        
        # 保存设置
        self.save_config()
    
    def update_ui_text(self, language: str):
        """更新界面文本"""
        if language == "zh":
            # 中文界面
            self.root.title("PDF转Markdown工具")
            # 更新选项卡标题
            self.notebook.tab(0, text="转换")
            self.notebook.tab(1, text="设置")
            self.notebook.tab(2, text="缓存管理")
            self.notebook.tab(3, text="处理状态")
            self.notebook.tab(4, text="日志")
            
            # 更新按钮文本
            self.start_button.config(text="开始转换")
            self.stop_button.config(text="停止转换")
            
        elif language == "en":
            # 英文界面
            self.root.title("PDF to Markdown Tool")
            # 更新选项卡标题
            self.notebook.tab(0, text="Convert")
            self.notebook.tab(1, text="Settings")
            self.notebook.tab(2, text="Cache")
            self.notebook.tab(3, text="Processing")
            self.notebook.tab(4, text="Log")
            
            # 更新按钮文本
            self.start_button.config(text="Start Convert")
            self.stop_button.config(text="Stop Convert")
    
    def apply_theme(self, theme: str):
        """应用主题"""
        try:
            if theme == "light":
                # 浅色主题
                self.root.configure(bg='#f0f0f0')
                style = ttk.Style()
                style.theme_use('clam')
                
            elif theme == "dark":
                # 深色主题
                self.root.configure(bg='#2b2b2b')
                style = ttk.Style()
                style.theme_use('clam')
                # 设置深色样式
                style.configure('TFrame', background='#2b2b2b')
                style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
                style.configure('TButton', background='#404040', foreground='#ffffff')
                
            else:  # default
                # 默认主题
                self.root.configure(bg='#ffffff')
                style = ttk.Style()
                style.theme_use('default')
            
            self.log(f"主题已切换为: {theme}")
            
        except Exception as e:
            self.log(f"主题切换失败: {e}")
    
    def run(self):
        """运行GUI"""
        # 自动预加载模型（可选）
        if self.auto_preload_var.get():
            self.log("自动预加载模型...")
            try:
                from enhanced_cache_manager import EnhancedCacheManager
                cache_manager = EnhancedCacheManager()
                # 只检查缓存状态，不预加载
                cache_info = cache_manager.check_cache_status()
                self.log(f"缓存状态检查完成: {cache_info['model_count']} 个模型")
            except Exception as e:
                self.log(f"缓存检查失败: {e}")
        
        self.root.mainloop()

    def refresh_processing_status(self):
        """刷新处理状态"""
        try:
            import psutil
            import time
            
            # 更新当前状态
            if self.is_converting:
                self.current_status_var.set("处理中")
            else:
                self.current_status_var.set("空闲")
            
            # 更新处理设备
            device = self.device_var.get()
            if device == "auto":
                # 检测GPU可用性
                try:
                    import torch
                    if torch.cuda.is_available():
                        self.device_status_var.set("GPU (自动检测)")
                    else:
                        self.device_status_var.set("CPU (自动检测)")
                except:
                    self.device_status_var.set("CPU (自动检测)")
            else:
                self.device_status_var.set(device.upper())
            
            # 更新内存使用
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.memory_usage_var.set(f"{memory_mb:.1f} MB")
            
            # 更新任务列表
            self.update_tasks_list()
            
            # 更新统计信息
            self.update_processing_stats()
            
        except Exception as e:
            self.log(f"刷新处理状态失败: {e}")
    
    def update_tasks_list(self):
        """更新任务列表"""
        # 清空现有项目
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        # 添加任务
        for task in self.processing_tasks:
            self.tasks_tree.insert("", "end", values=(
                task.get("filename", ""),
                task.get("status", "未知"),
                f"{task.get('progress', 0)}%",
                task.get("start_time", ""),
                task.get("duration", "")
            ))
    
    def update_processing_stats(self):
        """更新处理统计"""
        total = len(self.processing_tasks)
        success = len([t for t in self.processing_tasks if t.get("status") == "成功"])
        failed = len([t for t in self.processing_tasks if t.get("status") == "失败"])
        
        self.total_files_var.set(str(total))
        self.success_files_var.set(str(success))
        self.failed_files_var.set(str(failed))
        
        # 计算平均耗时
        completed_tasks = [t for t in self.processing_tasks if t.get("duration")]
        if completed_tasks:
            avg_duration = sum(float(t.get("duration", "0").replace("秒", "")) for t in completed_tasks) / len(completed_tasks)
            self.avg_time_var.set(f"{avg_duration:.1f}秒")
        else:
            self.avg_time_var.set("0秒")
    
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
        self.update_tasks_list()
        self.update_processing_stats()
    
    def update_task_status(self, filename: str, status: str, progress: int = 0, duration: str = ""):
        """更新任务状态"""
        for task in self.processing_tasks:
            if task.get("filename") == filename:
                task["status"] = status
                task["progress"] = progress
                if duration:
                    task["duration"] = duration
                break
        
        self.update_tasks_list()
        self.update_processing_stats()
    
    def clear_processing_tasks(self):
        """清空处理任务列表"""
        self.processing_tasks.clear()
        self.update_tasks_list()
        self.update_processing_stats()
        self.log("处理任务列表已清空")
    
    def export_processing_status(self):
        """导出处理状态"""
        filename = filedialog.asksaveasfilename(
            title="导出处理状态",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            try:
                import json
                import datetime
                
                export_data = {
                    "export_time": datetime.datetime.now().isoformat(),
                    "current_status": self.current_status_var.get(),
                    "device_status": self.device_status_var.get(),
                    "memory_usage": self.memory_usage_var.get(),
                    "statistics": {
                        "total_files": self.total_files_var.get(),
                        "success_files": self.success_files_var.get(),
                        "failed_files": self.failed_files_var.get(),
                        "avg_time": self.avg_time_var.get()
                    },
                    "tasks": self.processing_tasks
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("成功", "处理状态已导出")
                self.log(f"处理状态已导出到: {filename}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")
                self.log(f"导出处理状态失败: {e}")

def main():
    """主函数"""
    app = PDF2MDGUI()
    app.run()

if __name__ == "__main__":
    main() 