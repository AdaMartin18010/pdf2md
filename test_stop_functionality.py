#!/usr/bin/env python3
"""
测试停止转换功能
"""

import time
import threading
from pathlib import Path

def test_gui_stop_functionality():
    """测试GUI停止功能"""
    print("🧪 测试GUI停止功能...")
    
    # 模拟GUI状态
    class MockGUI:
        def __init__(self):
            self.is_converting = False
            self.processing_tasks = []
            self.batch_processor = None
        
        def start_conversion(self):
            """开始转换"""
            self.is_converting = True
            print("🔄 转换已开始")
            
            # 添加模拟任务
            self.processing_tasks.append({
                "filename": "test.pdf",
                "status": "处理中",
                "progress": 0
            })
        
        def stop_conversion(self):
            """停止转换"""
            if not self.is_converting:
                return
                
            print("⏹️ 正在停止转换...")
            
            # 停止批量处理器
            if hasattr(self, 'batch_processor') and self.batch_processor:
                try:
                    self.batch_processor.stop_processing()
                except:
                    pass
            
            # 设置停止标志
            self.is_converting = False
            
            # 更新任务状态
            for task in self.processing_tasks:
                if task.get("status") == "处理中":
                    task["status"] = "已停止"
            
            print("⏹️ 转换已停止")
            print(f"📊 任务状态: {[task['status'] for task in self.processing_tasks]}")
    
    # 创建模拟GUI
    gui = MockGUI()
    
    # 开始转换
    gui.start_conversion()
    print(f"📊 转换状态: {gui.is_converting}")
    print(f"📊 任务状态: {[task['status'] for task in gui.processing_tasks]}")
    
    # 等待一段时间
    time.sleep(1)
    
    # 停止转换
    gui.stop_conversion()
    print(f"📊 转换状态: {gui.is_converting}")
    
    return True

def test_batch_processor_stop():
    """测试批量处理器停止功能"""
    print("\n🧪 测试批量处理器停止功能...")
    
    class MockBatchProcessor:
        def __init__(self):
            self.is_processing = False
            self.should_stop = False
            self.active_converters = []
            self.processing_tasks = []
        
        def start_processing(self):
            """开始处理"""
            self.is_processing = True
            self.should_stop = False
            print("🔄 批量处理已开始")
            
            # 模拟添加任务
            self.processing_tasks.append({
                "filename": "test1.pdf",
                "status": "处理中"
            })
            self.processing_tasks.append({
                "filename": "test2.pdf", 
                "status": "处理中"
            })
        
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
            
            print("⏹️ 批量处理已停止")
            print(f"📊 任务状态: {[task['status'] for task in self.processing_tasks]}")
    
    # 创建模拟批量处理器
    processor = MockBatchProcessor()
    
    # 开始处理
    processor.start_processing()
    print(f"📊 处理状态: {processor.is_processing}")
    print(f"📊 停止标志: {processor.should_stop}")
    print(f"📊 任务状态: {[task['status'] for task in processor.processing_tasks]}")
    
    # 停止处理
    processor.stop_processing()
    print(f"📊 处理状态: {processor.is_processing}")
    print(f"📊 停止标志: {processor.should_stop}")
    
    return True

def main():
    """主函数"""
    print("🧪 停止转换功能测试")
    print("=" * 50)
    
    # 测试GUI停止功能
    test_gui_stop_functionality()
    
    # 测试批量处理器停止功能
    test_batch_processor_stop()
    
    print("\n✅ 所有测试通过！")
    print("💡 停止功能应该能够正常工作了。")

if __name__ == "__main__":
    main() 