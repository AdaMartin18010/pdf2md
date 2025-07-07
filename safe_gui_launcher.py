#!/usr/bin/env python3
"""
安全GUI启动器 - 避免内存和GPU占用过高
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys

class SafeGUILauncher:
    """安全GUI启动器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具 - 安全启动器")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="PDF转Markdown工具", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="安全启动器 - 避免内存和GPU占用过高", font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # 系统检查框架
        check_frame = ttk.LabelFrame(main_frame, text="系统检查", padding="15")
        check_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 检查结果
        self.check_results = {}
        self.check_labels = {}
        
        checks = [
            ("python_env", "Python环境"),
            ("tkinter", "GUI界面"),
            ("cache_manager", "缓存管理器"),
            ("batch_processor", "批量处理器"),
            ("memory_status", "内存状态"),
            ("gpu_status", "GPU状态")
        ]
        
        for check_id, check_name in checks:
            frame = ttk.Frame(check_frame)
            frame.pack(fill=tk.X, pady=2)
            
            status_label = ttk.Label(frame, text="⏳ 检查中...", foreground="orange")
            status_label.pack(side=tk.LEFT)
            
            name_label = ttk.Label(frame, text=check_name, font=("Arial", 9))
            name_label.pack(side=tk.LEFT, padx=(10, 0))
            
            self.check_labels[check_id] = status_label
        
        # 启动选项框架
        options_frame = ttk.LabelFrame(main_frame, text="启动选项", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 启动模式选择
        self.launch_mode = tk.StringVar(value="safe")
        
        ttk.Radiobutton(options_frame, text="安全模式 (推荐)", 
                       variable=self.launch_mode, value="safe").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="完整模式 (可能占用较多内存)", 
                       variable=self.launch_mode, value="full").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="最小模式 (仅基本功能)", 
                       variable=self.launch_mode, value="minimal").pack(anchor=tk.W)
        
        # 启动按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.launch_button = ttk.Button(button_frame, text="启动GUI", 
                                       command=self.launch_gui, state=tk.DISABLED)
        self.launch_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar(value="正在检查系统...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 开始系统检查
        self.start_system_check()
    
    def start_system_check(self):
        """开始系统检查"""
        def check_system():
            try:
                # 检查Python环境
                self.update_check_status("python_env", "✅ 正常", "green")
                
                # 检查tkinter
                try:
                    import tkinter
                    self.update_check_status("tkinter", "✅ 正常", "green")
                except:
                    self.update_check_status("tkinter", "❌ 不可用", "red")
                
                # 检查缓存管理器
                try:
                    from enhanced_cache_manager import EnhancedCacheManager
                    cache_manager = EnhancedCacheManager()
                    self.update_check_status("cache_manager", "✅ 正常", "green")
                except Exception as e:
                    self.update_check_status("cache_manager", f"❌ 错误: {str(e)[:30]}", "red")
                
                # 检查批量处理器
                try:
                    from enhanced_batch_processor import EnhancedBatchProcessor
                    processor = EnhancedBatchProcessor()
                    self.update_check_status("batch_processor", "✅ 正常", "green")
                except Exception as e:
                    self.update_check_status("batch_processor", f"❌ 错误: {str(e)[:30]}", "red")
                
                # 检查内存状态
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                    memory_percent = memory.percent
                    if memory_percent < 80:
                        self.update_check_status("memory_status", f"✅ 正常 ({memory_percent:.1f}%)", "green")
                    else:
                        self.update_check_status("memory_status", f"⚠️ 较高 ({memory_percent:.1f}%)", "orange")
                except:
                    self.update_check_status("memory_status", "❓ 未知", "gray")
                
                # 检查GPU状态
                try:
                    import torch
                    if torch.cuda.is_available():
                        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                        self.update_check_status("gpu_status", f"✅ 可用 ({gpu_memory:.1f}GB)", "green")
                    else:
                        self.update_check_status("gpu_status", "❌ 不可用", "red")
                except:
                    self.update_check_status("gpu_status", "❓ 未知", "gray")
                
                # 检查完成
                self.root.after(0, self.check_complete)
                
            except Exception as e:
                self.status_var.set(f"系统检查失败: {e}")
        
        # 在新线程中运行检查
        check_thread = threading.Thread(target=check_system)
        check_thread.daemon = True
        check_thread.start()
    
    def update_check_status(self, check_id, status, color):
        """更新检查状态"""
        def update():
            if check_id in self.check_labels:
                self.check_labels[check_id].config(text=status, foreground=color)
        self.root.after(0, update)
    
    def check_complete(self):
        """检查完成"""
        self.status_var.set("系统检查完成，可以启动GUI")
        self.launch_button.config(state=tk.NORMAL)
    
    def launch_gui(self):
        """启动GUI"""
        launch_mode = self.launch_mode.get()
        
        if launch_mode == "safe":
            self.launch_safe_gui()
        elif launch_mode == "full":
            self.launch_full_gui()
        else:  # minimal
            self.launch_minimal_gui()
    
    def launch_safe_gui(self):
        """启动安全模式GUI"""
        try:
            self.root.destroy()
            
            # 设置安全环境变量
            os.environ['CUDA_VISIBLE_DEVICES'] = ''  # 禁用GPU
            os.environ['OMP_NUM_THREADS'] = '2'  # 限制线程数
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            
            # 导入并启动GUI
            from pdf2md_gui import PDF2MDGUI
            app = PDF2MDGUI()
            
            # 禁用自动预加载
            app.auto_preload_var.set(False)
            
            app.run()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动安全模式GUI失败: {e}")
    
    def launch_full_gui(self):
        """启动完整模式GUI"""
        try:
            self.root.destroy()
            
            # 设置完整环境
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # 启用GPU
            os.environ['OMP_NUM_THREADS'] = '4'
            
            from pdf2md_gui import PDF2MDGUI
            app = PDF2MDGUI()
            app.run()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动完整模式GUI失败: {e}")
    
    def launch_minimal_gui(self):
        """启动最小模式GUI"""
        try:
            self.root.destroy()
            
            # 创建最小GUI
            root = tk.Tk()
            root.title("PDF转Markdown工具 - 最小模式")
            root.geometry("500x300")
            
            main_frame = ttk.Frame(root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="最小模式GUI", font=("Arial", 16)).pack(pady=20)
            ttk.Label(main_frame, text="此模式仅提供基本功能，避免内存占用过高").pack(pady=10)
            
            def convert_file():
                from tkinter import filedialog
                filename = filedialog.askopenfilename(
                    title="选择PDF文件",
                    filetypes=[("PDF文件", "*.pdf")]
                )
                if filename:
                    messagebox.showinfo("提示", f"选择了文件: {filename}\n\n在完整模式下可以执行转换")
            
            ttk.Button(main_frame, text="选择PDF文件", command=convert_file).pack(pady=10)
            ttk.Button(main_frame, text="退出", command=root.quit).pack(pady=10)
            
            root.mainloop()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动最小模式GUI失败: {e}")
    
    def run(self):
        """运行启动器"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动安全GUI启动器...")
    
    try:
        launcher = SafeGUILauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ 启动器失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 