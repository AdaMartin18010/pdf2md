#!/usr/bin/env python3
"""
PDF转换器GUI界面
提供用户友好的图形界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
from pathlib import Path
from typing import List, Optional
import logging

from .advanced_processor import AdvancedPDFProcessor
from .batch_processor import process_pdfs_batch

logger = logging.getLogger(__name__)

class PDFConverterGUI:
    """PDF转换器GUI界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown转换器")
        self.root.geometry("800x600")
        
        # 初始化处理器
        self.processor = AdvancedPDFProcessor()
        self.processing_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        title_label = ttk.Label(self.root, text="PDF转Markdown转换器", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # 文件选择区域
        self.setup_file_selection()
        
        # 处理器选择区域
        self.setup_processor_selection()
        
        # 输出设置区域
        self.setup_output_settings()
        
        # 进度显示区域
        self.setup_progress_display()
        
        # 控制按钮区域
        self.setup_control_buttons()
        
        # 日志显示区域
        self.setup_log_display()
    
    def setup_file_selection(self):
        """设置文件选择区域"""
        file_frame = ttk.LabelFrame(self.root, text="文件选择", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        # 文件列表
        self.file_listbox = tk.Listbox(file_frame, height=6, selectmode='extended')
        self.file_listbox.pack(fill='x', pady=5)
        
        # 文件操作按钮
        file_btn_frame = ttk.Frame(file_frame)
        file_btn_frame.pack(fill='x')
        
        ttk.Button(file_btn_frame, text="选择文件", command=self.select_files).pack(side='left', padx=5)
        ttk.Button(file_btn_frame, text="选择文件夹", command=self.select_folder).pack(side='left', padx=5)
        ttk.Button(file_btn_frame, text="清空列表", command=self.clear_files).pack(side='left', padx=5)
        
        # 文件统计
        self.file_count_label = ttk.Label(file_frame, text="已选择: 0 个文件")
        self.file_count_label.pack(pady=5)
    
    def setup_processor_selection(self):
        """设置处理器选择区域"""
        processor_frame = ttk.LabelFrame(self.root, text="处理器设置", padding=10)
        processor_frame.pack(fill='x', padx=10, pady=5)
        
        # 处理器选择
        processor_btn_frame = ttk.Frame(processor_frame)
        processor_btn_frame.pack(fill='x')
        
        self.processor_var = tk.StringVar(value="auto")
        ttk.Radiobutton(processor_btn_frame, text="自动选择", variable=self.processor_var, value="auto").pack(side='left', padx=5)
        ttk.Radiobutton(processor_btn_frame, text="PyPDF", variable=self.processor_var, value="pypdf").pack(side='left', padx=5)
        ttk.Radiobutton(processor_btn_frame, text="PDFPlumber", variable=self.processor_var, value="pdfplumber").pack(side='left', padx=5)
        ttk.Radiobutton(processor_btn_frame, text="PyMuPDF", variable=self.processor_var, value="pymupdf").pack(side='left', padx=5)
        
        # 并发设置
        concurrent_frame = ttk.Frame(processor_frame)
        concurrent_frame.pack(fill='x', pady=5)
        
        ttk.Label(concurrent_frame, text="并发数:").pack(side='left')
        self.concurrent_var = tk.StringVar(value="4")
        concurrent_spinbox = ttk.Spinbox(concurrent_frame, from_=1, to=16, textvariable=self.concurrent_var, width=5)
        concurrent_spinbox.pack(side='left', padx=5)
    
    def setup_output_settings(self):
        """设置输出设置区域"""
        output_frame = ttk.LabelFrame(self.root, text="输出设置", padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)
        
        # 输出目录
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill='x')
        
        ttk.Label(output_dir_frame, text="输出目录:").pack(side='left')
        self.output_dir_var = tk.StringVar(value="markdown")
        output_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=40)
        output_entry.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(output_dir_frame, text="浏览", command=self.select_output_dir).pack(side='left', padx=5)
    
    def setup_progress_display(self):
        """设置进度显示区域"""
        progress_frame = ttk.LabelFrame(self.root, text="处理进度", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
        
        # 状态标签
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack(pady=5)
        
        # 统计信息
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill='x')
        
        self.success_count_label = ttk.Label(stats_frame, text="成功: 0")
        self.success_count_label.pack(side='left', padx=10)
        
        self.failed_count_label = ttk.Label(stats_frame, text="失败: 0")
        self.failed_count_label.pack(side='left', padx=10)
        
        self.time_label = ttk.Label(stats_frame, text="耗时: 0秒")
        self.time_label.pack(side='left', padx=10)
    
    def setup_control_buttons(self):
        """设置控制按钮区域"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="开始转换", command=self.start_conversion)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_conversion, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="打开输出目录", command=self.open_output_dir).pack(side='right', padx=5)
    
    def setup_log_display(self):
        """设置日志显示区域"""
        log_frame = ttk.LabelFrame(self.root, text="处理日志", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=8, wrap='word')
        log_scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
    
    def select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        
        for file in files:
            if file not in self.file_listbox.get(0, tk.END):
                self.file_listbox.insert(tk.END, file)
        
        self.update_file_count()
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含PDF文件的文件夹")
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            for pdf_file in pdf_files:
                if str(pdf_file) not in self.file_listbox.get(0, tk.END):
                    self.file_listbox.insert(tk.END, str(pdf_file))
            
            self.update_file_count()
    
    def clear_files(self):
        """清空文件列表"""
        self.file_listbox.delete(0, tk.END)
        self.update_file_count()
    
    def update_file_count(self):
        """更新文件计数"""
        count = self.file_listbox.size()
        self.file_count_label.config(text=f"已选择: {count} 个文件")
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def log_message(self, message: str, level: str = "info"):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        level_icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        icon = level_icons.get(level, "ℹ️")
        
        log_entry = f"[{timestamp}] {icon} {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日志行数
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", "500.0")
    
    def start_conversion(self):
        """开始转换"""
        files = list(self.file_listbox.get(0, tk.END))
        if not files:
            messagebox.showwarning("警告", "请先选择要转换的PDF文件")
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 禁用开始按钮，启用停止按钮
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # 重置进度
        self.progress_var.set(0)
        self.success_count = 0
        self.failed_count = 0
        self.start_time = time.time()
        
        # 清空日志
        self.log_text.delete("1.0", tk.END)
        
        # 启动转换线程
        self.conversion_thread = threading.Thread(
            target=self.conversion_worker,
            args=(files, output_dir)
        )
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
        
        # 启动进度更新
        self.update_progress()
    
    def conversion_worker(self, files: List[str], output_dir: str):
        """转换工作线程"""
        try:
            self.log_message("开始批量转换...", "info")
            
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            total_files = len(files)
            
            for i, file_path in enumerate(files):
                if hasattr(self, 'stop_requested') and self.stop_requested:
                    self.log_message("用户停止转换", "warning")
                    break
                
                try:
                    pdf_path = Path(file_path)
                    output_file = output_path / f"{pdf_path.stem}.md"
                    
                    self.log_message(f"处理文件: {pdf_path.name}", "info")
                    
                    # 使用高级处理器
                    result = self.processor.process_pdf(pdf_path, output_file)
                    
                    if result.success:
                        self.success_count += 1
                        self.log_message(f"✅ 成功: {pdf_path.name} (使用 {result.processor})", "success")
                    else:
                        self.failed_count += 1
                        self.log_message(f"❌ 失败: {pdf_path.name} - {result.error}", "error")
                    
                    # 更新进度
                    progress = ((i + 1) / total_files) * 100
                    self.processing_queue.put(('progress', progress))
                    
                except Exception as e:
                    self.failed_count += 1
                    self.log_message(f"❌ 处理异常: {file_path} - {str(e)}", "error")
            
            # 转换完成
            duration = time.time() - self.start_time
            self.processing_queue.put(('complete', duration))
            
        except Exception as e:
            self.log_message(f"❌ 转换过程异常: {str(e)}", "error")
            self.processing_queue.put(('error', str(e)))
    
    def update_progress(self):
        """更新进度显示"""
        try:
            while True:
                msg_type, data = self.processing_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_var.set(data)
                    self.status_label.config(text=f"处理中... {data:.1f}%")
                
                elif msg_type == 'complete':
                    duration = data
                    self.progress_var.set(100)
                    self.status_label.config(text="转换完成")
                    self.log_message(f"转换完成! 成功: {self.success_count}, 失败: {self.failed_count}, 耗时: {duration:.1f}秒", "success")
                    
                    # 恢复按钮状态
                    self.start_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                    
                    # 显示完成消息
                    messagebox.showinfo("完成", f"转换完成!\n成功: {self.success_count} 个文件\n失败: {self.failed_count} 个文件\n耗时: {duration:.1f} 秒")
                    return
                
                elif msg_type == 'error':
                    self.status_label.config(text="转换失败")
                    self.log_message(f"转换失败: {data}", "error")
                    self.start_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                    return
                    
        except queue.Empty:
            pass
        
        # 更新统计信息
        self.success_count_label.config(text=f"成功: {self.success_count}")
        self.failed_count_label.config(text=f"失败: {self.failed_count}")
        
        if hasattr(self, 'start_time'):
            duration = time.time() - self.start_time
            self.time_label.config(text=f"耗时: {duration:.1f}秒")
        
        # 继续更新
        self.root.after(100, self.update_progress)
    
    def stop_conversion(self):
        """停止转换"""
        self.stop_requested = True
        self.status_label.config(text="正在停止...")
        self.log_message("用户请求停止转换", "warning")
    
    def open_output_dir(self):
        """打开输出目录"""
        output_dir = self.output_dir_var.get()
        if output_dir and Path(output_dir).exists():
            import os
            os.startfile(output_dir)
        else:
            messagebox.showwarning("警告", "输出目录不存在")
    
    def run(self):
        """运行GUI"""
        self.log_message("PDF转换器已启动", "info")
        self.log_message(f"可用处理器: {list(self.processor.processors.keys())}", "info")
        self.root.mainloop()

def main():
    """主函数"""
    app = PDFConverterGUI()
    app.run()

if __name__ == "__main__":
    main() 