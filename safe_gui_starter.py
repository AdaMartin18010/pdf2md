#!/usr/bin/env python3
"""
安全GUI启动器 - 避免内存和GPU占用过高
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
import time

class SafeGUIStarter:
    """安全GUI启动器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF转Markdown工具 - 安全启动器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="PDF转Markdown工具", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="安全启动器 - 避免内存和GPU占用过高", font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # 系统信息框架
        info_frame = ttk.LabelFrame(main_frame, text="系统信息", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 显示系统信息
        self.system_info_text = tk.Text(info_frame, height=6, width=60)
        self.system_info_text.pack(fill=tk.X)
        
        # 启动选项框架
        options_frame = ttk.LabelFrame(main_frame, text="启动选项", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 启动模式选择
        self.launch_mode = tk.StringVar(value="safe")
        
        ttk.Radiobutton(options_frame, text="安全模式 (推荐) - 禁用GPU，限制内存", 
                       variable=self.launch_mode, value="safe").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="标准模式 - 平衡性能和资源", 
                       variable=self.launch_mode, value="standard").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="完整模式 - 所有功能，可能占用较多资源", 
                       variable=self.launch_mode, value="full").pack(anchor=tk.W)
        
        # 启动按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.launch_button = ttk.Button(button_frame, text="启动GUI", 
                                       command=self.launch_gui)
        self.launch_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="刷新系统信息", 
                  command=self.refresh_system_info).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 初始化系统信息
        self.refresh_system_info()
        
    def refresh_system_info(self):
        """刷新系统信息"""
        try:
            import psutil
            
            # 获取内存信息
            memory = psutil.virtual_memory()
            memory_info = f"内存: {memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB ({memory.percent:.1f}%)"
            
            # 获取CPU信息
            cpu_info = f"CPU: {psutil.cpu_count()} 核心, 使用率: {psutil.cpu_percent()}%"
            
            # 获取GPU信息
            gpu_info = "GPU: 检查中..."
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    allocated = torch.cuda.memory_allocated(0) / (1024**3)
                    gpu_info = f"GPU: {allocated:.1f}GB / {gpu_memory:.1f}GB"
                else:
                    gpu_info = "GPU: 不可用"
            except:
                gpu_info = "GPU: 未知"
            
            # 获取磁盘信息
            disk = psutil.disk_usage('.')
            disk_info = f"磁盘: {disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB"
            
            # 更新显示
            info_text = f"""系统信息:
{memory_info}
{cpu_info}
{gpu_info}
{disk_info}

建议: 如果内存使用率超过80%，建议选择安全模式启动。
"""
            
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info_text)
            
        except Exception as e:
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, f"获取系统信息失败: {e}")
    
    def launch_gui(self):
        """启动GUI"""
        launch_mode = self.launch_mode.get()
        
        self.status_var.set(f"正在启动{launch_mode}模式...")
        self.launch_button.config(state=tk.DISABLED)
        
        # 在新线程中启动GUI
        def start_gui():
            try:
                # 根据模式设置环境变量
                if launch_mode == "safe":
                    # 安全模式：禁用GPU，限制内存
                    os.environ['CUDA_VISIBLE_DEVICES'] = ''
                    os.environ['OMP_NUM_THREADS'] = '2'
                    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
                    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:64'
                    
                elif launch_mode == "standard":
                    # 标准模式：平衡设置
                    os.environ['OMP_NUM_THREADS'] = '4'
                    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
                    
                else:  # full
                    # 完整模式：启用所有功能
                    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
                    os.environ['OMP_NUM_THREADS'] = '8'
                
                # 关闭当前窗口
                self.root.after(0, self.root.destroy)
                
                # 启动GUI
                from pdf2md_gui import PDF2MDGUI
                app = PDF2MDGUI()
                
                # 根据模式调整设置
                if launch_mode == "safe":
                    app.auto_preload_var.set(False)  # 禁用自动预加载
                    app.max_workers_var.set("1")     # 限制并发数
                    app.device_var.set("cpu")        # 强制使用CPU
                
                app.run()
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"启动GUI失败: {e}"))
        
        # 启动线程
        gui_thread = threading.Thread(target=start_gui)
        gui_thread.daemon = True
        gui_thread.start()
    
    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        self.launch_button.config(state=tk.NORMAL)
        self.status_var.set("启动失败")
    
    def run(self):
        """运行启动器"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动安全GUI启动器...")
    
    try:
        starter = SafeGUIStarter()
        starter.run()
    except Exception as e:
        print(f"❌ 启动器失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 