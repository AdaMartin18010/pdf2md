#!/usr/bin/env python3
"""
快速停止功能验证脚本
测试停止功能在实际GUI中的表现
"""

import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class QuickStopVerification:
    """快速停止验证"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("停止功能验证")
        self.root.geometry("500x400")
        
        self.is_converting = False
        self.should_stop = False
        self.progress = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="停止功能验证工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(pady=(0, 10))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(pady=(0, 20))
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.log_text = tk.Text(log_frame, height=10, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        self.start_button = ttk.Button(button_frame, text="开始模拟转换", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止转换", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="清除日志", command=self.clear_log).pack(side=tk.LEFT)
        
        # 测试按钮
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(pady=(10, 0))
        
        ttk.Button(test_frame, text="测试停止确认", command=self.test_stop_confirmation).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(test_frame, text="测试优雅停止", command=self.test_graceful_stop).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(test_frame, text="测试强制停止", command=self.test_force_stop).pack(side=tk.LEFT)
    
    def log(self, message: str):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete("1.0", tk.END)
    
    def start_simulation(self):
        """开始模拟转换"""
        if self.is_converting:
            return
        
        self.is_converting = True
        self.should_stop = False
        self.progress = 0
        self.progress_var.set(0)
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("转换中...")
        
        self.log("🔄 开始模拟转换...")
        self.log("📄 模拟处理文件: document1.pdf")
        self.log("📄 模拟处理文件: document2.pdf")
        self.log("📄 模拟处理文件: document3.pdf")
        
        # 在新线程中运行模拟转换
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def run_simulation(self):
        """运行模拟转换"""
        try:
            for i in range(100):
                if self.should_stop:
                    self.log("⏹️ 检测到停止信号，退出转换")
                    break
                
                # 模拟处理时间
                time.sleep(0.1)
                self.progress = i + 1
                
                # 更新进度
                self.root.after(0, self.update_progress, self.progress)
                
                # 模拟一些处理步骤
                if i % 20 == 0:
                    self.log(f"📊 处理进度: {self.progress}%")
            
            if not self.should_stop:
                self.log("✅ 转换完成!")
                self.root.after(0, self.conversion_complete)
            else:
                self.log("⏹️ 转换已停止")
                self.root.after(0, self.conversion_stopped)
                
        except Exception as e:
            self.log(f"❌ 转换出错: {e}")
            self.root.after(0, self.conversion_error, str(e))
    
    def update_progress(self, progress: int):
        """更新进度"""
        self.progress_var.set(progress)
        self.status_var.set(f"转换中... {progress}%")
    
    def conversion_complete(self):
        """转换完成"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换完成")
        self.progress_var.set(100)
    
    def conversion_stopped(self):
        """转换停止"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换已停止")
    
    def conversion_error(self, error: str):
        """转换错误"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("转换失败")
        self.log(f"❌ 转换失败: {error}")
    
    def stop_simulation(self):
        """停止模拟转换"""
        if not self.is_converting:
            return
        
        self.log("⏹️ 用户请求停止转换...")
        
        # 设置停止标志
        self.should_stop = True
        
        # 更新UI状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("正在停止...")
        
        self.log("⏹️ 停止信号已发送")
    
    def test_stop_confirmation(self):
        """测试停止确认"""
        self.log("🧪 测试停止确认对话框...")
        
        result = messagebox.askyesno(
            "确认停止", 
            "确定要停止当前转换吗？\n\n已完成的文件将保留，未完成的文件将停止处理。",
            icon='warning'
        )
        
        if result:
            self.log("✅ 用户确认停止")
            if self.is_converting:
                self.stop_simulation()
        else:
            self.log("❌ 用户取消停止")
    
    def test_graceful_stop(self):
        """测试优雅停止"""
        self.log("🧪 测试优雅停止...")
        
        if not self.is_converting:
            self.log("⚠️ 没有正在进行的转换")
            return
        
        self.log("⏳ 等待当前任务完成...")
        time.sleep(1)  # 模拟等待
        
        self.log("🛑 强制停止所有活动转换器...")
        self.should_stop = True
        
        self.log("✅ 优雅停止完成")
    
    def test_force_stop(self):
        """测试强制停止"""
        self.log("🧪 测试强制停止...")
        
        if not self.is_converting:
            self.log("⚠️ 没有正在进行的转换")
            return
        
        self.log("🛑 立即强制停止...")
        self.should_stop = True
        self.is_converting = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("强制停止")
        
        self.log("✅ 强制停止完成")
    
    def run(self):
        """运行验证工具"""
        self.log("🚀 停止功能验证工具已启动")
        self.log("💡 点击'开始模拟转换'来测试停止功能")
        self.log("💡 在转换过程中点击'停止转换'来测试停止效果")
        
        self.root.mainloop()

def main():
    """主函数"""
    print("🔧 快速停止功能验证工具")
    print("=" * 50)
    print("💡 这个工具用于验证停止功能在实际GUI中的表现")
    print("💡 启动后会打开一个GUI窗口，可以测试各种停止场景")
    print("=" * 50)
    
    # 创建验证工具
    verification = QuickStopVerification()
    verification.run()

if __name__ == "__main__":
    main() 