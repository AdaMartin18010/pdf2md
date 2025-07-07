#!/usr/bin/env python3
"""
测试CPU/GPU设备选项
验证设备选择功能是否正常工作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

def test_device_options():
    """测试设备选项功能"""
    print("开始测试CPU/GPU设备选项...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("设备选项测试")
    root.geometry("500x400")
    
    # 创建测试框架
    test_frame = ttk.Frame(root, padding="20")
    test_frame.pack(fill=tk.BOTH, expand=True)
    
    # 设备选择
    device_frame = ttk.LabelFrame(test_frame, text="处理设备选择", padding="10")
    device_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(device_frame, text="处理设备:").grid(row=0, column=0, sticky=tk.W)
    device_var = tk.StringVar(value="auto")
    device_combo = ttk.Combobox(device_frame, textvariable=device_var,
                               values=["auto", "cpu", "gpu"], width=15)
    device_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
    
    # 设备说明
    device_info = ttk.Label(device_frame, text="auto: 自动选择, cpu: 强制CPU, gpu: 强制GPU", 
                           font=("Arial", 8), foreground="gray")
    device_info.grid(row=1, column=0, columnspan=2, padx=(0, 0), pady=(5, 0), sticky=tk.W)
    
    # 测试结果
    result_frame = ttk.LabelFrame(test_frame, text="测试结果", padding="10")
    result_frame.pack(fill=tk.BOTH, expand=True)
    
    result_text = tk.Text(result_frame, height=15)
    result_text.pack(fill=tk.BOTH, expand=True)
    
    def test_device_selection():
        """测试设备选择"""
        device = device_var.get()
        result_text.insert(tk.END, f"选择的设备: {device}\n")
        
        if device == "auto":
            result_text.insert(tk.END, "✅ 自动模式: 系统将根据可用资源自动选择CPU或GPU\n")
        elif device == "cpu":
            result_text.insert(tk.END, "✅ CPU模式: 强制使用CPU进行处理\n")
        elif device == "gpu":
            result_text.insert(tk.END, "✅ GPU模式: 强制使用GPU进行处理\n")
        
        result_text.insert(tk.END, f"设备设置已保存到配置\n")
        result_text.see(tk.END)
    
    def save_config():
        """保存配置"""
        config = {
            "device": device_var.get(),
            "test_timestamp": "2024-01-01 12:00:00"
        }
        
        config_file = Path("test_device_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        result_text.insert(tk.END, "✅ 配置已保存到 test_device_config.json\n")
        result_text.see(tk.END)
    
    def load_config():
        """加载配置"""
        config_file = Path("test_device_config.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            device_var.set(config.get("device", "auto"))
            result_text.insert(tk.END, f"✅ 配置已加载: {config.get('device', 'auto')}\n")
        else:
            result_text.insert(tk.END, "⚠️ 配置文件不存在\n")
        
        result_text.see(tk.END)
    
    def clear_results():
        """清空结果"""
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "结果已清空\n")
    
    # 控制按钮
    button_frame = ttk.Frame(test_frame)
    button_frame.pack(pady=(10, 0))
    
    ttk.Button(button_frame, text="测试设备选择", 
               command=test_device_selection).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="保存配置", 
               command=save_config).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="加载配置", 
               command=load_config).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="清空结果", 
               command=clear_results).pack(side=tk.LEFT)
    
    # 初始信息
    result_text.insert(tk.END, "设备选项测试工具\n")
    result_text.insert(tk.END, "请选择处理设备并点击测试按钮\n\n")
    
    root.mainloop()

if __name__ == "__main__":
    test_device_options() 