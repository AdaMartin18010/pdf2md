#!/usr/bin/env python3
"""
缓存检查功能演示
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class CacheCheckDemo:
    """缓存检查演示"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("缓存检查演示")
        self.root.geometry("600x400")
        
        # 创建界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="缓存检查功能演示", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))
        
        # 检查缓存按钮
        self.check_button = ttk.Button(button_frame, text="检查缓存", command=self.check_cache)
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新按钮
        refresh_button = ttk.Button(button_frame, text="刷新信息", command=self.refresh_cache_info)
        refresh_button.pack(side=tk.LEFT)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(main_frame, height=20, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # 初始日志
        self.log("缓存检查演示已启动")
        self.log("点击'检查缓存'按钮测试功能")
    
    def log(self, message: str):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_cache(self):
        """检查缓存"""
        self.log("🔄 开始检查缓存状态...")
        self.status_var.set("检查中...")
        self.check_button.config(state=tk.DISABLED)
        
        # 在新线程中运行检查
        thread = threading.Thread(target=self._run_cache_check)
        thread.daemon = True
        thread.start()
    
    def _run_cache_check(self):
        """运行缓存检查"""
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            cache_manager = EnhancedCacheManager()
            cache_info = cache_manager.check_cache_status()
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self._update_cache_info(cache_info))
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
    
    def _update_cache_info(self, cache_info):
        """更新缓存信息"""
        self.log("✅ 缓存检查完成!")
        self.log(f"📁 缓存目录: {cache_info['cache_dir']}")
        self.log(f"💾 总大小: {cache_info['total_size'] / (1024**3):.2f} GB")
        self.log(f"📦 模型文件数: {cache_info['model_count']}")
        self.log(f"📈 缓存效率: {cache_info['cache_efficiency']*100:.1f}%")
        
        self.log("\n📋 详细状态:")
        for name, info in cache_info['subdirs'].items():
            if info['exists']:
                status_icon = "✅" if info['has_models'] else "⚠️"
                size_mb = info['size'] / (1024**2)
                self.log(f"  {status_icon} {name}: {info['model_count']} 个模型 ({size_mb:.1f} MB)")
            else:
                self.log(f"  ❌ {name}: 目录不存在")
        
        self.status_var.set("检查完成")
        self.check_button.config(state=tk.NORMAL)
    
    def _show_error(self, error: str):
        """显示错误"""
        self.log(f"❌ 检查缓存失败: {error}")
        self.status_var.set("检查失败")
        self.check_button.config(state=tk.NORMAL)
    
    def refresh_cache_info(self):
        """刷新缓存信息"""
        self.log("🔄 刷新缓存信息...")
        self.check_cache()
    
    def run(self):
        """运行演示"""
        self.root.mainloop()

def main():
    """主函数"""
    demo = CacheCheckDemo()
    demo.run()

if __name__ == "__main__":
    main() 