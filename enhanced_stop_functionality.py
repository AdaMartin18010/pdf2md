#!/usr/bin/env python3
"""
增强版停止转换功能实现
包含优雅停止、确认对话框、状态持久化等功能
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import tkinter as tk
from tkinter import messagebox, ttk

class EnhancedStopFunctionality:
    """增强版停止功能"""
    
    def __init__(self):
        self.is_converting = False
        self.should_stop = False
        self.active_converters = []
        self.processing_tasks = []
        self.completed_files = 0
        self.total_files = 0
        self.stop_callbacks = []
        
    def add_stop_callback(self, callback):
        """添加停止回调函数"""
        self.stop_callbacks.append(callback)
    
    def graceful_stop(self):
        """优雅停止转换"""
        print("⏹️ 正在优雅停止转换...")
        
        # 设置停止标志
        self.should_stop = True
        
        # 等待当前任务完成（给一些时间）
        if self.processing_tasks:
            print("⏳ 等待当前任务完成...")
            time.sleep(2)
        
        # 强制停止所有活动转换器
        self.force_stop_all_converters()
        
        # 更新状态
        self.is_converting = False
        
        # 调用所有停止回调
        for callback in self.stop_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"停止回调执行失败: {e}")
        
        print("✅ 优雅停止完成")
    
    def force_stop_all_converters(self):
        """强制停止所有转换器"""
        print(f"🛑 强制停止 {len(self.active_converters)} 个活动转换器...")
        
        for converter in self.active_converters:
            try:
                converter.stop_conversion()
            except Exception as e:
                print(f"停止转换器失败: {e}")
        
        # 清空活动转换器列表
        self.active_converters.clear()
        
        # 更新所有正在处理的任务状态
        for task in self.processing_tasks:
            if task.get("status") == "处理中":
                task["status"] = "已停止"
        
        print("✅ 所有转换器已停止")
    
    def confirm_stop(self):
        """确认停止转换"""
        if not self.is_converting:
            return False
        
        result = messagebox.askyesno(
            "确认停止", 
            "确定要停止当前转换吗？\n\n已完成的文件将保留，未完成的文件将停止处理。",
            icon='warning'
        )
        
        if result:
            self.graceful_stop()
            return True
        
        return False
    
    def save_stop_state(self):
        """保存停止状态"""
        stop_state = {
            "stopped_at": time.time(),
            "completed_files": self.completed_files,
            "total_files": self.total_files,
            "stopped_tasks": [task for task in self.processing_tasks if task.get("status") == "已停止"],
            "active_converters_count": len(self.active_converters)
        }
        
        try:
            with open("stop_state.json", "w", encoding="utf-8") as f:
                json.dump(stop_state, f, ensure_ascii=False, indent=2)
            print("✅ 停止状态已保存")
        except Exception as e:
            print(f"❌ 保存停止状态失败: {e}")
    
    def load_stop_state(self):
        """加载停止状态"""
        try:
            if os.path.exists("stop_state.json"):
                with open("stop_state.json", "r", encoding="utf-8") as f:
                    stop_state = json.load(f)
                print("✅ 停止状态已加载")
                return stop_state
        except Exception as e:
            print(f"❌ 加载停止状态失败: {e}")
        
        return None
    
    def resume_stopped_tasks(self):
        """恢复未完成的任务"""
        stopped_tasks = [task for task in self.processing_tasks if task.get("status") == "已停止"]
        
        if stopped_tasks:
            result = messagebox.askyesno(
                "恢复任务", 
                f"发现 {len(stopped_tasks)} 个未完成的任务，是否恢复处理？"
            )
            
            if result:
                for task in stopped_tasks:
                    task["status"] = "等待中"
                print(f"✅ 已恢复 {len(stopped_tasks)} 个任务")
                return True
        
        return False
    
    def get_stop_statistics(self):
        """获取停止统计信息"""
        total_tasks = len(self.processing_tasks)
        completed_tasks = len([t for t in self.processing_tasks if t.get("status") == "成功"])
        stopped_tasks = len([t for t in self.processing_tasks if t.get("status") == "已停止"])
        failed_tasks = len([t for t in self.processing_tasks if t.get("status") == "失败"])
        
        return {
            "total": total_tasks,
            "completed": completed_tasks,
            "stopped": stopped_tasks,
            "failed": failed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def log_stop_event(self, reason: str = "用户停止"):
        """记录停止事件"""
        stop_info = {
            "timestamp": time.time(),
            "reason": reason,
            "completed_files": self.completed_files,
            "total_files": self.total_files,
            "active_converters": len(self.active_converters)
        }
        
        print(f"⏹️ 停止事件: {stop_info}")
    
    def monitor_stop_performance(self):
        """监控停止性能"""
        start_time = time.time()
        self.graceful_stop()
        stop_time = time.time() - start_time
        
        print(f"⏱️ 停止耗时: {stop_time:.2f}秒")
        
        if stop_time > 5.0:
            print("⚠️ 停止耗时较长，可能需要优化")
        
        return stop_time
    
    def verify_stop_state(self):
        """验证停止状态"""
        issues = []
        
        if self.is_converting:
            issues.append("转换状态未正确停止")
        
        if self.active_converters:
            issues.append(f"还有 {len(self.active_converters)} 个活动转换器")
        
        if any(task.get("status") == "处理中" for task in self.processing_tasks):
            issues.append("还有任务状态为处理中")
        
        if issues:
            print(f"⚠️ 停止状态检查发现问题: {issues}")
            return False
        else:
            print("✅ 停止状态检查通过")
            return True

class MockConverter:
    """模拟转换器"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_running = False
    
    def start_conversion(self):
        """开始转换"""
        self.is_running = True
        print(f"🔄 {self.name} 开始转换")
    
    def stop_conversion(self):
        """停止转换"""
        self.is_running = False
        print(f"⏹️ {self.name} 停止转换")

def test_enhanced_stop_functionality():
    """测试增强版停止功能"""
    print("🧪 测试增强版停止功能")
    print("=" * 50)
    
    # 创建增强版停止功能
    stop_func = EnhancedStopFunctionality()
    
    # 模拟添加任务
    stop_func.processing_tasks = [
        {"filename": "test1.pdf", "status": "处理中"},
        {"filename": "test2.pdf", "status": "成功"},
        {"filename": "test3.pdf", "status": "处理中"}
    ]
    
    # 模拟添加转换器
    converter1 = MockConverter("转换器1")
    converter2 = MockConverter("转换器2")
    stop_func.active_converters = [converter1, converter2]
    
    # 设置状态
    stop_func.is_converting = True
    stop_func.completed_files = 1
    stop_func.total_files = 3
    
    print("📊 初始状态:")
    print(f"  转换状态: {stop_func.is_converting}")
    print(f"  活动转换器: {len(stop_func.active_converters)}")
    print(f"  任务状态: {[task['status'] for task in stop_func.processing_tasks]}")
    
    # 测试优雅停止
    print("\n🔄 测试优雅停止...")
    stop_func.graceful_stop()
    
    print("\n📊 停止后状态:")
    print(f"  转换状态: {stop_func.is_converting}")
    print(f"  活动转换器: {len(stop_func.active_converters)}")
    print(f"  任务状态: {[task['status'] for task in stop_func.processing_tasks]}")
    
    # 测试统计信息
    print("\n📊 停止统计信息:")
    stats = stop_func.get_stop_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试状态验证
    print("\n🔍 状态验证:")
    stop_func.verify_stop_state()
    
    # 测试状态保存和加载
    print("\n💾 测试状态持久化...")
    stop_func.save_stop_state()
    loaded_state = stop_func.load_stop_state()
    if loaded_state:
        print(f"  加载的停止时间: {loaded_state['stopped_at']}")
        print(f"  完成文件数: {loaded_state['completed_files']}")
    
    print("\n✅ 增强版停止功能测试完成!")

def create_stop_confirmation_dialog():
    """创建停止确认对话框"""
    root = tk.Tk()
    root.title("停止确认")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # 居中显示
    root.eval('tk::PlaceWindow . center')
    
    # 主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 图标和标题
    icon_label = ttk.Label(main_frame, text="⏹️", font=("Arial", 24))
    icon_label.pack(pady=(0, 10))
    
    title_label = ttk.Label(main_frame, text="确认停止转换", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 10))
    
    # 消息
    message_label = ttk.Label(
        main_frame, 
        text="确定要停止当前转换吗？\n\n已完成的文件将保留，\n未完成的文件将停止处理。",
        justify=tk.CENTER
    )
    message_label.pack(pady=(0, 20))
    
    # 按钮框架
    button_frame = ttk.Frame(main_frame)
    button_frame.pack()
    
    result = {"confirmed": False}
    
    def on_confirm():
        result["confirmed"] = True
        root.destroy()
    
    def on_cancel():
        result["confirmed"] = False
        root.destroy()
    
    # 按钮
    confirm_button = ttk.Button(button_frame, text="确认停止", command=on_confirm, style="Accent.TButton")
    confirm_button.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
    cancel_button.pack(side=tk.LEFT)
    
    # 绑定回车键和ESC键
    root.bind('<Return>', lambda e: on_confirm())
    root.bind('<Escape>', lambda e: on_cancel())
    
    # 设置焦点
    confirm_button.focus_set()
    
    root.mainloop()
    return result["confirmed"]

def test_stop_confirmation_dialog():
    """测试停止确认对话框"""
    print("🧪 测试停止确认对话框...")
    
    result = create_stop_confirmation_dialog()
    
    if result:
        print("✅ 用户确认停止")
    else:
        print("❌ 用户取消停止")

if __name__ == "__main__":
    print("🔧 增强版停止功能测试工具")
    print("=" * 50)
    
    # 测试增强版停止功能
    test_enhanced_stop_functionality()
    
    print("\n" + "=" * 50)
    
    # 测试停止确认对话框
    test_stop_confirmation_dialog()
    
    print("\n✅ 所有测试完成！") 