#!/usr/bin/env python3
"""
增强版批量处理器
支持真正的多任务处理和GPU优先选择
"""

import os
import sys
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class EnhancedBatchProcessor:
    """增强版批量处理器"""
    
    def __init__(self, max_workers: int = 2, device_preference: str = "gpu_first"):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大并发数
            device_preference: 设备偏好 ("gpu_first", "cpu_first", "auto")
        """
        self.max_workers = max_workers
        self.device_preference = device_preference
        self.is_processing = False
        self.should_stop = False  # 添加停止标志
        self.processing_tasks = []
        self.task_queue = queue.Queue()
        self.results = {}
        self.active_converters = []  # 跟踪活动的转换器
        
        # 任务状态
        self.total_files = 0
        self.completed_files = 0
        self.success_files = 0
        self.failed_files = 0
        
    def detect_available_devices(self) -> Dict[str, bool]:
        """检测可用设备"""
        devices = {
            "cpu": True,  # CPU总是可用
            "gpu": False
        }
        
        try:
            import torch
            devices["gpu"] = torch.cuda.is_available()
        except ImportError:
            pass
        
        return devices
    
    def select_optimal_device(self, available_devices: Dict[str, bool]) -> str:
        """选择最优设备"""
        if self.device_preference == "gpu_first":
            if available_devices["gpu"]:
                return "gpu"
            else:
                return "cpu"
        elif self.device_preference == "cpu_first":
            return "cpu"
        else:  # auto
            if available_devices["gpu"]:
                return "gpu"
            else:
                return "cpu"
    
    def add_task(self, input_file: Path, output_dir: Path, options: Dict[str, Any]):
        """添加转换任务"""
        task = {
            "input_file": input_file,
            "output_dir": output_dir,
            "options": options,
            "status": "等待中",
            "progress": 0,
            "start_time": None,
            "end_time": None,
            "error": None
        }
        self.processing_tasks.append(task)
        self.task_queue.put(task)
    
    def process_single_file(self, task: Dict[str, Any], device: str) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            from stable_mineru_converter import MineruConverter
            
            # 检查是否应该停止
            if self.should_stop:
                task["status"] = "已停止"
                return {"success": False, "task": task, "error": "用户停止"}
            
            # 更新任务状态
            task["status"] = "处理中"
            task["start_time"] = time.time()
            
            # 创建转换器
            converter = MineruConverter()
            
            # 添加到活动转换器列表
            self.active_converters.append(converter)
            
            # 设置设备
            if device == "gpu":
                # 强制使用GPU
                os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            elif device == "cpu":
                # 强制使用CPU
                os.environ["CUDA_VISIBLE_DEVICES"] = ""
            
            # 进度回调
            def progress_callback(progress: int, message: str):
                if self.should_stop:
                    return  # 如果应该停止，不更新进度
                task["progress"] = progress
                task["message"] = message
            
            # 执行转换
            result = converter.convert_single_pdf(
                task["input_file"],
                task["output_dir"],
                task["options"]["language"],
                task["options"]["backend"],
                task["options"]["method"],
                enable_formula=task["options"]["enable_formula"],
                enable_table=task["options"]["enable_table"],
                progress_callback=progress_callback
            )
            
            # 从活动转换器列表中移除
            if converter in self.active_converters:
                self.active_converters.remove(converter)
            
            # 检查是否应该停止
            if self.should_stop:
                task["status"] = "已停止"
                return {"success": False, "task": task, "error": "用户停止"}
            
            # 更新任务状态
            task["end_time"] = time.time()
            task["processing_time"] = task["end_time"] - task["start_time"]
            
            if result["success"]:
                task["status"] = "成功"
                task["progress"] = 100
                task["output_file"] = result["output_file"]
                task["images_dir"] = result["images_dir"]
                task["image_count"] = result["image_count"]
                return {"success": True, "task": task}
            else:
                task["status"] = "失败"
                task["error"] = result["error"]
                return {"success": False, "task": task, "error": result["error"]}
                
        except Exception as e:
            # 从活动转换器列表中移除
            if 'converter' in locals() and converter in self.active_converters:
                self.active_converters.remove(converter)
                
            task["status"] = "失败"
            task["error"] = str(e)
            task["end_time"] = time.time()
            return {"success": False, "task": task, "error": str(e)}
    
    def start_batch_processing(self, progress_callback: Optional[Callable] = None):
        """开始批量处理"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.should_stop = False  # 重置停止标志
        self.total_files = len(self.processing_tasks)
        self.completed_files = 0
        self.success_files = 0
        self.failed_files = 0
        
        # 检测可用设备
        available_devices = self.detect_available_devices()
        selected_device = self.select_optimal_device(available_devices)
        
        print(f"可用设备: {available_devices}")
        print(f"选择设备: {selected_device}")
        
        # 使用线程池进行并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for task in self.processing_tasks:
                if self.should_stop:  # 检查是否应该停止
                    break
                future = executor.submit(self.process_single_file, task, selected_device)
                future_to_task[future] = task
            
            # 处理完成的任务
            for future in as_completed(future_to_task):
                if self.should_stop:  # 检查是否应该停止
                    break
                    
                task = future_to_task[future]
                result = future.result()
                
                self.completed_files += 1
                
                if result["success"]:
                    self.success_files += 1
                    print(f"✅ 完成: {task['input_file'].name}")
                else:
                    self.failed_files += 1
                    print(f"❌ 失败: {task['input_file'].name} - {result['error']}")
                
                # 调用进度回调
                if progress_callback and not self.should_stop:
                    progress = (self.completed_files / self.total_files) * 100
                    progress_callback(progress, f"已完成 {self.completed_files}/{self.total_files}")
        
        self.is_processing = False
        
        return {
            "total_files": self.total_files,
            "success_count": self.success_files,
            "failed_count": self.failed_files,
            "device_used": selected_device
        }
    
    def get_task_status(self) -> List[Dict[str, Any]]:
        """获取任务状态"""
        return self.processing_tasks
    
    def stop_processing(self):
        """停止处理"""
        self.should_stop = True
        self.is_processing = False
        
        # 停止所有活动的转换器
        for converter in self.active_converters:
            try:
                converter.stop_conversion()
            except:
                pass
        
        # 清空活动转换器列表
        self.active_converters.clear()
        
        # 更新所有正在处理的任务状态
        for task in self.processing_tasks:
            if task.get("status") == "处理中":
                task["status"] = "已停止"
    
    def clear_tasks(self):
        """清空任务列表"""
        self.processing_tasks.clear()
        while not self.task_queue.empty():
            self.task_queue.get()

def test_enhanced_batch_processor():
    """测试增强版批量处理器"""
    print("测试增强版批量处理器...")
    
    # 创建处理器
    processor = EnhancedBatchProcessor(max_workers=2, device_preference="gpu_first")
    
    # 检测设备
    devices = processor.detect_available_devices()
    print(f"可用设备: {devices}")
    
    # 选择设备
    selected_device = processor.select_optimal_device(devices)
    print(f"选择设备: {selected_device}")
    
    # 模拟添加任务
    test_files = [
        Path("test1.pdf"),
        Path("test2.pdf"),
        Path("test3.pdf")
    ]
    
    options = {
        "language": "ch",
        "backend": "pipeline",
        "method": "auto",
        "enable_formula": True,
        "enable_table": True
    }
    
    for test_file in test_files:
        processor.add_task(test_file, Path("./output"), options)
    
    print(f"添加了 {len(processor.processing_tasks)} 个任务")
    
    # 获取任务状态
    status = processor.get_task_status()
    print(f"任务状态: {status}")
    
    print("测试完成!")

if __name__ == "__main__":
    test_enhanced_batch_processor() 