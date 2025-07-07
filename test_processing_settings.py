#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理设置和状态功能测试脚本
测试新增的处理设置和状态管理功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path

def test_processing_settings():
    """测试处理设置功能"""
    print("🧪 测试处理设置功能...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("处理设置测试")
    root.geometry("600x400")
    
    # 创建设置框架
    settings_frame = ttk.LabelFrame(root, text="处理设置", padding="10")
    settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 超时设置
    ttk.Label(settings_frame, text="处理超时时间(秒):").grid(row=0, column=0, sticky=tk.W)
    timeout_var = tk.StringVar(value="300")
    timeout_entry = ttk.Entry(settings_frame, textvariable=timeout_var, width=10)
    timeout_entry.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
    
    # 处理设备设置
    ttk.Label(settings_frame, text="处理设备:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
    device_var = tk.StringVar(value="auto")
    device_combo = ttk.Combobox(settings_frame, textvariable=device_var,
                               values=["auto", "cpu", "gpu"], width=10)
    device_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
    
    # 并发设置
    ttk.Label(settings_frame, text="最大并发数:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
    max_workers_var = tk.StringVar(value="2")
    workers_entry = ttk.Entry(settings_frame, textvariable=max_workers_var, width=10)
    workers_entry.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
    
    # 内存限制
    ttk.Label(settings_frame, text="内存限制(GB):").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
    memory_limit_var = tk.StringVar(value="4")
    memory_entry = ttk.Entry(settings_frame, textvariable=memory_limit_var, width=10)
    memory_entry.grid(row=3, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
    
    # 高级选项
    advanced_frame = ttk.LabelFrame(settings_frame, text="高级选项", padding="5")
    advanced_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    enable_optimization_var = tk.BooleanVar(value=True)
    optimization_check = ttk.Checkbutton(advanced_frame, text="启用性能优化", 
                                       variable=enable_optimization_var)
    optimization_check.grid(row=0, column=0, sticky=tk.W)
    
    enable_caching_var = tk.BooleanVar(value=True)
    caching_check = ttk.Checkbutton(advanced_frame, text="启用处理缓存", 
                                   variable=enable_caching_var)
    caching_check.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
    
    enable_retry_var = tk.BooleanVar(value=True)
    retry_check = ttk.Checkbutton(advanced_frame, text="启用失败重试", 
                                 variable=enable_retry_var)
    retry_check.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    enable_logging_var = tk.BooleanVar(value=True)
    logging_check = ttk.Checkbutton(advanced_frame, text="启用详细日志", 
                                   variable=enable_logging_var)
    logging_check.grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(5, 0))
    
    # 测试按钮
    def test_save_config():
        """测试保存配置"""
        config = {
            "timeout": timeout_var.get(),
            "device": device_var.get(),
            "max_workers": max_workers_var.get(),
            "memory_limit": memory_limit_var.get(),
            "enable_optimization": enable_optimization_var.get(),
            "enable_caching": enable_caching_var.get(),
            "enable_retry": enable_retry_var.get(),
            "enable_logging": enable_logging_var.get()
        }
        
        try:
            with open("test_processing_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存到 test_processing_config.json")
            print("✅ 配置保存测试通过")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
            print(f"❌ 配置保存测试失败: {e}")
    
    def test_load_config():
        """测试加载配置"""
        try:
            if os.path.exists("test_processing_config.json"):
                with open("test_processing_config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                timeout_var.set(config.get("timeout", "300"))
                device_var.set(config.get("device", "auto"))
                max_workers_var.set(config.get("max_workers", "2"))
                memory_limit_var.set(config.get("memory_limit", "4"))
                enable_optimization_var.set(config.get("enable_optimization", True))
                enable_caching_var.set(config.get("enable_caching", True))
                enable_retry_var.set(config.get("enable_retry", True))
                enable_logging_var.set(config.get("enable_logging", True))
                
                messagebox.showinfo("成功", "配置已加载")
                print("✅ 配置加载测试通过")
            else:
                messagebox.showwarning("警告", "配置文件不存在，请先保存配置")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败: {e}")
            print(f"❌ 配置加载测试失败: {e}")
    
    # 按钮框架
    button_frame = ttk.Frame(settings_frame)
    button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
    
    ttk.Button(button_frame, text="保存配置", command=test_save_config).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="加载配置", command=test_load_config).pack(side=tk.LEFT)
    
    settings_frame.columnconfigure(1, weight=1)
    
    print("📋 处理设置测试界面已创建")
    print("💡 请测试以下功能:")
    print("   1. 修改各项设置")
    print("   2. 点击'保存配置'按钮")
    print("   3. 点击'加载配置'按钮")
    print("   4. 检查配置文件是否正确保存")
    
    root.mainloop()

def test_processing_status():
    """测试处理状态功能"""
    print("\n🧪 测试处理状态功能...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("处理状态测试")
    root.geometry("800x600")
    
    # 创建状态框架
    status_frame = ttk.LabelFrame(root, text="处理状态", padding="10")
    status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 状态概览
    overview_frame = ttk.Frame(status_frame)
    overview_frame.pack(fill=tk.X, pady=(0, 10))
    
    current_status_var = tk.StringVar(value="空闲")
    device_status_var = tk.StringVar(value="CPU")
    memory_usage_var = tk.StringVar(value="0 MB")
    
    ttk.Label(overview_frame, text="当前状态:").grid(row=0, column=0, sticky=tk.W)
    ttk.Label(overview_frame, textvariable=current_status_var, 
             font=("Arial", 10, "bold")).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
    
    ttk.Label(overview_frame, text="处理设备:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    ttk.Label(overview_frame, textvariable=device_status_var).grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
    
    ttk.Label(overview_frame, text="内存使用:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
    ttk.Label(overview_frame, textvariable=memory_usage_var).grid(row=2, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)
    
    # 任务列表
    tasks_frame = ttk.LabelFrame(status_frame, text="处理任务", padding="10")
    tasks_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    columns = ("文件名", "状态", "进度", "开始时间", "耗时")
    tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show="headings", height=8)
    
    for col in columns:
        tasks_tree.heading(col, text=col)
        tasks_tree.column(col, width=120)
    
    tasks_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=tasks_tree.yview)
    tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)
    
    tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 模拟任务数据
    sample_tasks = [
        ("test1.pdf", "成功", "100%", "10:30:15", "45.2秒"),
        ("test2.pdf", "处理中", "65%", "10:31:20", ""),
        ("test3.pdf", "等待中", "0%", "10:32:00", ""),
        ("test4.pdf", "失败", "0%", "10:29:45", "12.5秒")
    ]
    
    def add_sample_tasks():
        """添加示例任务"""
        for item in tasks_tree.get_children():
            tasks_tree.delete(item)
        
        for task in sample_tasks:
            tasks_tree.insert("", "end", values=task)
        
        print("✅ 示例任务已添加到列表")
    
    def update_status():
        """更新状态"""
        try:
            import psutil
            import torch
            
            # 更新内存使用
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            memory_usage_var.set(f"{memory_mb:.1f} MB")
            
            # 更新设备状态
            try:
                if torch.cuda.is_available():
                    device_status_var.set("GPU (自动检测)")
                else:
                    device_status_var.set("CPU (自动检测)")
            except:
                device_status_var.set("CPU (自动检测)")
            
            print("✅ 状态更新完成")
            
        except Exception as e:
            print(f"❌ 状态更新失败: {e}")
    
    def export_status():
        """导出状态"""
        try:
            import datetime
            
            export_data = {
                "export_time": datetime.datetime.now().isoformat(),
                "current_status": current_status_var.get(),
                "device_status": device_status_var.get(),
                "memory_usage": memory_usage_var.get(),
                "tasks": []
            }
            
            # 获取任务列表
            for item in tasks_tree.get_children():
                values = tasks_tree.item(item)['values']
                export_data["tasks"].append({
                    "filename": values[0],
                    "status": values[1],
                    "progress": values[2],
                    "start_time": values[3],
                    "duration": values[4]
                })
            
            with open("test_processing_status.json", 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", "状态已导出到 test_processing_status.json")
            print("✅ 状态导出测试通过")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
            print(f"❌ 状态导出测试失败: {e}")
    
    # 控制按钮
    button_frame = ttk.Frame(status_frame)
    button_frame.pack(fill=tk.X)
    
    ttk.Button(button_frame, text="添加示例任务", command=add_sample_tasks).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="更新状态", command=update_status).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="导出状态", command=export_status).pack(side=tk.LEFT)
    
    print("📋 处理状态测试界面已创建")
    print("💡 请测试以下功能:")
    print("   1. 点击'添加示例任务'查看任务列表")
    print("   2. 点击'更新状态'查看实时状态")
    print("   3. 点击'导出状态'保存状态到文件")
    print("   4. 检查导出的JSON文件格式")
    
    root.mainloop()

def main():
    """主函数"""
    print("🚀 开始测试处理设置和状态功能")
    print("=" * 50)
    
    # 测试处理设置
    test_processing_settings()
    
    # 测试处理状态
    test_processing_status()
    
    print("\n✅ 所有测试完成")
    print("📁 生成的测试文件:")
    print("   - test_processing_config.json (配置测试)")
    print("   - test_processing_status.json (状态测试)")

if __name__ == "__main__":
    main() 