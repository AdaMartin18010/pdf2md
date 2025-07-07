#!/usr/bin/env python3
"""
测试关机功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform
import time

class ShutdownTestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("关机功能测试")
        self.root.geometry("400x300")
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="关机功能测试", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # 测试选项
        test_frame = ttk.LabelFrame(main_frame, text="测试选项", padding="15")
        test_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 关机延迟
        ttk.Label(test_frame, text="关机延迟(秒):").pack(anchor=tk.W)
        self.delay_var = tk.StringVar(value="30")
        delay_entry = ttk.Entry(test_frame, textvariable=self.delay_var, width=10)
        delay_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # 测试按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="测试关机命令", command=self.test_shutdown).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消关机", command=self.cancel_shutdown).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("✅ 关机功能测试界面已启动")
        self.log(f"当前操作系统: {platform.system()}")
    
    def log(self, message: str):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def test_shutdown(self):
        """测试关机命令"""
        try:
            delay = int(self.delay_var.get())
            if delay < 0:
                delay = 30
            
            self.log(f"⏰ 测试关机命令，延迟: {delay} 秒")
            
            # 显示确认对话框
            result = messagebox.askyesno(
                "关机测试确认", 
                f"将在 {delay} 秒后关机。\n\n这只是一个测试，请确保您想继续。\n\n是否继续？",
                icon='warning'
            )
            
            if result:
                self.log("✅ 用户确认关机测试")
                if self.schedule_shutdown(delay):
                    self.log("✅ 关机命令已执行")
                    self.status_var.set(f"关机计划已设置 ({delay}秒)")
                    messagebox.showinfo("测试成功", f"关机命令已执行，系统将在 {delay} 秒后关机")
                else:
                    self.log("❌ 关机命令执行失败")
                    self.status_var.set("关机命令失败")
                    messagebox.showerror("测试失败", "关机命令执行失败")
            else:
                self.log("❌ 用户取消了关机测试")
                self.status_var.set("测试已取消")
                
        except ValueError:
            self.log("❌ 延迟设置无效")
            messagebox.showerror("错误", "延迟设置无效，请输入数字")
    
    def schedule_shutdown(self, delay_seconds: int = 30):
        """计划关机"""
        try:
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
    
    def cancel_shutdown(self):
        """取消关机"""
        try:
            self.log("🔄 取消关机计划...")
            
            if platform.system() == "Windows":
                # Windows取消关机
                cmd = "shutdown /a"
                subprocess.Popen(cmd, shell=True)
                self.log("✅ Windows关机已取消")
            elif platform.system() == "Linux":
                # Linux取消关机
                cmd = "shutdown -c"
                subprocess.Popen(cmd, shell=True)
                self.log("✅ Linux关机已取消")
            elif platform.system() == "Darwin":  # macOS
                # macOS取消关机
                cmd = "sudo killall shutdown"
                subprocess.Popen(cmd, shell=True)
                self.log("✅ macOS关机已取消")
            else:
                self.log("❌ 不支持的操作系统")
                return False
            
            self.status_var.set("关机已取消")
            messagebox.showinfo("成功", "关机计划已取消")
            return True
            
        except Exception as e:
            self.log(f"❌ 取消关机失败: {e}")
            return False
    
    def run(self):
        self.root.mainloop()

def main():
    print("🚀 启动关机功能测试...")
    
    try:
        app = ShutdownTestGUI()
        app.run()
    except Exception as e:
        print(f"❌ 测试启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 