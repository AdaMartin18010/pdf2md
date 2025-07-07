#!/usr/bin/env python3
"""
完整GUI功能测试脚本
测试所有界面功能和交互
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from pathlib import Path

def test_gui_functionality():
    """测试GUI功能"""
    print("开始测试GUI功能...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("GUI功能测试")
    root.geometry("600x400")
    
    # 创建测试框架
    test_frame = ttk.Frame(root, padding="20")
    test_frame.pack(fill=tk.BOTH, expand=True)
    
    # 测试结果
    test_results = []
    
    def run_test(test_name, test_func):
        """运行单个测试"""
        try:
            test_func()
            test_results.append(f"✅ {test_name}: 通过")
            print(f"✅ {test_name}: 通过")
        except Exception as e:
            test_results.append(f"❌ {test_name}: 失败 - {e}")
            print(f"❌ {test_name}: 失败 - {e}")
    
    def test_basic_ui():
        """测试基本UI组件"""
        # 测试标签
        label = ttk.Label(test_frame, text="测试标签")
        label.pack()
        
        # 测试按钮
        button = ttk.Button(test_frame, text="测试按钮")
        button.pack()
        
        # 测试输入框
        entry = ttk.Entry(test_frame)
        entry.pack()
        
        # 测试下拉框
        combo = ttk.Combobox(test_frame, values=["选项1", "选项2", "选项3"])
        combo.pack()
        
        # 测试复选框
        check = ttk.Checkbutton(test_frame, text="测试复选框")
        check.pack()
        
        # 测试进度条
        progress = ttk.Progressbar(test_frame, maximum=100)
        progress.pack()
        
        # 测试文本框
        text = tk.Text(test_frame, height=5)
        text.pack()
    
    def test_file_dialog():
        """测试文件对话框"""
        # 测试目录选择
        directory = filedialog.askdirectory(title="选择测试目录")
        if directory:
            print(f"选择的目录: {directory}")
        
        # 测试文件保存
        filename = filedialog.asksaveasfilename(
            title="保存测试文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            print(f"保存的文件: {filename}")
    
    def test_message_box():
        """测试消息框"""
        # 测试信息框
        messagebox.showinfo("测试", "这是一个信息框测试")
        
        # 测试错误框
        messagebox.showerror("测试", "这是一个错误框测试")
        
        # 测试确认框
        result = messagebox.askyesno("测试", "这是一个确认框测试")
        print(f"确认框结果: {result}")
    
    def test_variables():
        """测试变量绑定"""
        # 字符串变量
        str_var = tk.StringVar(value="测试字符串")
        entry = ttk.Entry(test_frame, textvariable=str_var)
        entry.pack()
        
        # 布尔变量
        bool_var = tk.BooleanVar(value=True)
        check = ttk.Checkbutton(test_frame, text="测试布尔变量", variable=bool_var)
        check.pack()
        
        # 整数变量
        int_var = tk.IntVar(value=50)
        scale = ttk.Scale(test_frame, from_=0, to=100, variable=int_var)
        scale.pack()
    
    def test_threading():
        """测试线程功能"""
        def background_task():
            for i in range(5):
                time.sleep(1)
                print(f"后台任务进度: {i+1}/5")
        
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()
        print("后台线程已启动")
    
    def test_config_operations():
        """测试配置操作"""
        config = {
            "input_dir": "./test_input",
            "output_dir": "./test_output",
            "language": "ch",
            "backend": "pipeline",
            "method": "auto",
            "enable_formula": True,
            "enable_table": True,
            "cache_dir": "./test_cache",
            "auto_preload": True,
            "show_progress": True,
            "theme": "default"
        }
        
        # 测试配置保存
        config_file = Path("test_config.json")
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 测试配置加载
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        # 清理测试文件
        config_file.unlink(missing_ok=True)
        
        assert loaded_config == config
        print("配置操作测试通过")
    
    def test_path_operations():
        """测试路径操作"""
        # 测试路径创建
        test_dir = Path("./test_dir")
        test_dir.mkdir(exist_ok=True)
        
        # 测试文件创建
        test_file = test_dir / "test.txt"
        test_file.write_text("测试内容")
        
        # 测试路径检查
        assert test_dir.exists()
        assert test_file.exists()
        
        # 清理
        test_file.unlink()
        test_dir.rmdir()
        
        print("路径操作测试通过")
    
    # 运行所有测试
    tests = [
        ("基本UI组件", test_basic_ui),
        ("文件对话框", test_file_dialog),
        ("消息框", test_message_box),
        ("变量绑定", test_variables),
        ("线程功能", test_threading),
        ("配置操作", test_config_operations),
        ("路径操作", test_path_operations)
    ]
    
    for test_name, test_func in tests:
        run_test(test_name, test_func)
    
    # 显示测试结果
    result_text = tk.Text(test_frame, height=10)
    result_text.pack(fill=tk.BOTH, expand=True)
    
    for result in test_results:
        result_text.insert(tk.END, result + "\n")
    
    # 添加关闭按钮
    close_button = ttk.Button(test_frame, text="关闭", command=root.destroy)
    close_button.pack()
    
    print(f"\n测试完成! 通过: {len([r for r in test_results if '✅' in r])}/{len(test_results)}")
    
    root.mainloop()

if __name__ == "__main__":
    test_gui_functionality() 