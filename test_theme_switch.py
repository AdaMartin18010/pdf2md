#!/usr/bin/env python3
"""
主题切换功能测试
"""

import tkinter as tk
from tkinter import ttk
import json

class ThemeTestGUI:
    """主题切换测试GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("主题切换测试")
        self.root.geometry("500x400")
        
        # 配置
        self.config_file = "theme_test_config.json"
        self.load_config()
        
        self.setup_ui()
        self.apply_current_settings()
    
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "language_ui": "zh",
                "theme": "default"
            }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✅ 配置已保存")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="主题切换测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="界面设置", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 语言设置
        ttk.Label(settings_frame, text="界面语言:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.language_var = tk.StringVar(value=self.config.get("language_ui", "zh"))
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var,
                                     values=["zh", "en"], width=15)
        language_combo.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky=tk.W)
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # 主题设置
        ttk.Label(settings_frame, text="主题:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.theme_var = tk.StringVar(value=self.config.get("theme", "default"))
        theme_combo = ttk.Combobox(settings_frame, textvariable=self.theme_var,
                                   values=["default", "light", "dark"], width=15)
        theme_combo.grid(row=1, column=1, padx=(10, 0), pady=(0, 10), sticky=tk.W)
        theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # 测试按钮
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(pady=(0, 20))
        
        self.test_button = ttk.Button(test_frame, text="测试按钮", command=self.test_function)
        self.test_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(test_frame, text="保存设置", command=self.save_config).pack(side=tk.LEFT)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(fill=tk.X, pady=(20, 0))
    
    def on_language_change(self, event=None):
        """语言切换事件"""
        language = self.language_var.get()
        print(f"切换语言: {language}")
        
        self.update_ui_text(language)
        self.config["language_ui"] = language
        self.save_config()
    
    def on_theme_change(self, event=None):
        """主题切换事件"""
        theme = self.theme_var.get()
        print(f"切换主题: {theme}")
        
        self.apply_theme(theme)
        self.config["theme"] = theme
        self.save_config()
    
    def update_ui_text(self, language: str):
        """更新界面文本"""
        if language == "zh":
            self.root.title("主题切换测试")
            self.test_button.config(text="测试按钮")
            self.status_var.set("中文界面")
        elif language == "en":
            self.root.title("Theme Switch Test")
            self.test_button.config(text="Test Button")
            self.status_var.set("English Interface")
    
    def apply_theme(self, theme: str):
        """应用主题"""
        try:
            if theme == "light":
                # 浅色主题
                self.root.configure(bg='#f0f0f0')
                style = ttk.Style()
                style.theme_use('clam')
                print("✅ 应用浅色主题")
                
            elif theme == "dark":
                # 深色主题
                self.root.configure(bg='#2b2b2b')
                style = ttk.Style()
                style.theme_use('clam')
                # 设置深色样式
                style.configure('TFrame', background='#2b2b2b')
                style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
                style.configure('TButton', background='#404040', foreground='#ffffff')
                print("✅ 应用深色主题")
                
            else:  # default
                # 默认主题
                self.root.configure(bg='#ffffff')
                style = ttk.Style()
                style.theme_use('default')
                print("✅ 应用默认主题")
            
        except Exception as e:
            print(f"❌ 主题切换失败: {e}")
    
    def apply_current_settings(self):
        """应用当前设置"""
        self.update_ui_text(self.language_var.get())
        self.apply_theme(self.theme_var.get())
    
    def test_function(self):
        """测试功能"""
        print("🎯 测试按钮被点击")
        self.status_var.set("测试成功!")
    
    def run(self):
        """运行测试"""
        self.root.mainloop()

def main():
    """主函数"""
    app = ThemeTestGUI()
    app.run()

if __name__ == "__main__":
    main() 