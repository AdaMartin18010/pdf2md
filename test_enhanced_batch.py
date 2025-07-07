#!/usr/bin/env python3
"""
测试增强版批量处理功能
验证GPU优先选择和多任务处理
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pathlib import Path
from enhanced_batch_processor import EnhancedBatchProcessor

def test_enhanced_batch_processing():
    """测试增强版批量处理"""
    print("测试增强版批量处理功能...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("增强版批量处理测试")
    root.geometry("600x500")
    
    # 创建测试框架
    test_frame = ttk.Frame(root, padding="20")
    test_frame.pack(fill=tk.BOTH, expand=True)
    
    # 设备检测
    device_frame = ttk.LabelFrame(test_frame, text="设备检测", padding="10")
    device_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 创建处理器
    processor = EnhancedBatchProcessor(max_workers=2, device_preference="gpu_first")
    
    # 检测设备
    devices = processor.detect_available_devices()
    selected_device = processor.select_optimal_device(devices)
    
    ttk.Label(device_frame, text=f"可用设备: {devices}").pack(anchor=tk.W)
    ttk.Label(device_frame, text=f"选择设备: {selected_device}").pack(anchor=tk.W)
    
    # 批量处理设置
    settings_frame = ttk.LabelFrame(test_frame, text="批量处理设置", padding="10")
    settings_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 设备偏好
    ttk.Label(settings_frame, text="设备偏好:").grid(row=0, column=0, sticky=tk.W)
    device_preference_var = tk.StringVar(value="gpu_first")
    device_combo = ttk.Combobox(settings_frame, textvariable=device_preference_var,
                               values=["gpu_first", "cpu_first", "auto"], width=15)
    device_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
    
    # 并发数
    ttk.Label(settings_frame, text="最大并发数:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
    max_workers_var = tk.StringVar(value="2")
    workers_entry = ttk.Entry(settings_frame, textvariable=max_workers_var, width=10)
    workers_entry.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
    
    # 测试文件数量
    ttk.Label(settings_frame, text="测试文件数:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
    file_count_var = tk.StringVar(value="3")
    file_count_entry = ttk.Entry(settings_frame, textvariable=file_count_var, width=10)
    file_count_entry.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky=tk.W)
    
    # 任务列表
    tasks_frame = ttk.LabelFrame(test_frame, text="任务列表", padding="10")
    tasks_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # 创建任务列表
    columns = ("文件名", "状态", "进度", "开始时间", "耗时")
    tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show="headings", height=8)
    
    # 设置列标题
    for col in columns:
        tasks_tree.heading(col, text=col)
        tasks_tree.column(col, width=100)
    
    # 添加滚动条
    tasks_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=tasks_tree.yview)
    tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)
    
    tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 进度条
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(test_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, pady=(0, 10))
    
    # 状态标签
    status_var = tk.StringVar(value="准备就绪")
    status_label = ttk.Label(test_frame, textvariable=status_var)
    status_label.pack()
    
    # 控制按钮
    button_frame = ttk.Frame(test_frame)
    button_frame.pack(pady=(10, 0))
    
    def start_batch_test():
        """开始批量测试"""
        try:
            # 清空任务列表
            for item in tasks_tree.get_children():
                tasks_tree.delete(item)
            
            # 创建新的处理器
            max_workers = int(max_workers_var.get())
            device_pref = device_preference_var.get()
            
            processor = EnhancedBatchProcessor(max_workers=max_workers, device_preference=device_pref)
            
            # 模拟添加任务
            file_count = int(file_count_var.get())
            test_files = [Path(f"test{i}.pdf") for i in range(1, file_count + 1)]
            
            options = {
                "language": "ch",
                "backend": "pipeline",
                "method": "auto",
                "enable_formula": True,
                "enable_table": True
            }
            
            # 添加任务到列表
            for i, test_file in enumerate(test_files):
                tasks_tree.insert("", "end", values=(
                    test_file.name,
                    "等待中",
                    0,
                    "",
                    ""
                ))
                processor.add_task(test_file, Path("./output"), options)
            
            status_var.set("开始处理...")
            progress_var.set(0)
            
            # 在新线程中运行处理
            def run_processing():
                def progress_callback(progress: int, message: str):
                    root.after(0, lambda: update_progress(progress, message))
                
                result = processor.start_batch_processing(progress_callback)
                
                root.after(0, lambda: processing_complete(result))
            
            processing_thread = threading.Thread(target=run_processing)
            processing_thread.daemon = True
            processing_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动测试失败: {e}")
    
    def update_progress(progress: int, message: str):
        """更新进度"""
        progress_var.set(progress)
        status_var.set(message)
        
        # 更新任务状态
        tasks = processor.get_task_status()
        for i, task in enumerate(tasks):
            if i < len(tasks_tree.get_children()):
                item = tasks_tree.get_children()[i]
                tasks_tree.set(item, "状态", task["status"])
                tasks_tree.set(item, "进度", f"{task['progress']}%")
                if task["start_time"]:
                    start_time = time.strftime("%H:%M:%S", time.localtime(task["start_time"]))
                    tasks_tree.set(item, "开始时间", start_time)
                if task["end_time"] and task["start_time"]:
                    duration = task["end_time"] - task["start_time"]
                    tasks_tree.set(item, "耗时", f"{duration:.1f}秒")
    
    def processing_complete(result):
        """处理完成"""
        progress_var.set(100)
        status_var.set("处理完成")
        
        messagebox.showinfo("完成", 
                          f"批量处理完成！\n"
                          f"总文件数: {result['total_files']}\n"
                          f"成功: {result['success_count']}\n"
                          f"失败: {result['failed_count']}\n"
                          f"使用设备: {result['device_used']}")
    
    ttk.Button(button_frame, text="开始批量测试", 
               command=start_batch_test).pack(side=tk.LEFT, padx=(0, 10))
    
    ttk.Button(button_frame, text="清空列表", 
               command=lambda: [tasks_tree.delete(item) for item in tasks_tree.get_children()]).pack(side=tk.LEFT)
    
    root.mainloop()

if __name__ == "__main__":
    test_enhanced_batch_processing() 