#!/usr/bin/env python3
"""
PDF转换性能监控工具
监控转换过程中的系统资源使用情况
"""

import psutil
import time
import threading
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.performance_data = {
            'timestamps': [],
            'cpu_percent': [],
            'memory_percent': [],
            'memory_mb': [],
            'gpu_percent': [],
            'gpu_memory_mb': []
        }
        self.start_time = None
        
    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring:
            self.monitoring = True
            self.start_time = datetime.now()
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("✅ 性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("✅ 性能监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # 内存使用
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_mb = memory.used / (1024 * 1024)
                
                # GPU使用率（如果可用）
                gpu_percent = 0
                gpu_memory_mb = 0
                try:
                    import torch
                    if torch.cuda.is_available():
                        gpu_percent = torch.cuda.utilization()
                        gpu_memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
                except:
                    pass
                
                # 记录数据
                timestamp = datetime.now()
                self.performance_data['timestamps'].append(timestamp)
                self.performance_data['cpu_percent'].append(cpu_percent)
                self.performance_data['memory_percent'].append(memory_percent)
                self.performance_data['memory_mb'].append(memory_mb)
                self.performance_data['gpu_percent'].append(gpu_percent)
                self.performance_data['gpu_memory_mb'].append(gpu_memory_mb)
                
                time.sleep(1)
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(1)
    
    def get_current_stats(self) -> Dict[str, float]:
        """获取当前统计信息"""
        if not self.performance_data['timestamps']:
            return {}
        
        return {
            'cpu_percent': self.performance_data['cpu_percent'][-1] if self.performance_data['cpu_percent'] else 0,
            'memory_percent': self.performance_data['memory_percent'][-1] if self.performance_data['memory_percent'] else 0,
            'memory_mb': self.performance_data['memory_mb'][-1] if self.performance_data['memory_mb'] else 0,
            'gpu_percent': self.performance_data['gpu_percent'][-1] if self.performance_data['gpu_percent'] else 0,
            'gpu_memory_mb': self.performance_data['gpu_memory_mb'][-1] if self.performance_data['gpu_memory_mb'] else 0
        }
    
    def save_performance_report(self, filename: Optional[str] = None):
        """保存性能报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report = {
            'monitor_start_time': self.start_time.isoformat() if self.start_time else None,
            'monitor_end_time': datetime.now().isoformat(),
            'total_samples': len(self.performance_data['timestamps']),
            'performance_data': {
                'timestamps': [t.isoformat() for t in self.performance_data['timestamps']],
                'cpu_percent': self.performance_data['cpu_percent'],
                'memory_percent': self.performance_data['memory_percent'],
                'memory_mb': self.performance_data['memory_mb'],
                'gpu_percent': self.performance_data['gpu_percent'],
                'gpu_memory_mb': self.performance_data['gpu_memory_mb']
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 性能报告已保存: {filename}")
        return filename

def main():
    """主函数"""
    monitor = PerformanceMonitor()
    
    print("🚀 性能监控工具")
    print("按 Ctrl+C 停止监控")
    
    try:
        monitor.start_monitoring()
        
        while True:
            stats = monitor.get_current_stats()
            if stats:
                print(f"\rCPU: {stats.get('cpu_percent', 0):.1f}% | "
                      f"内存: {stats.get('memory_percent', 0):.1f}% ({stats.get('memory_mb', 0):.1f}MB) | "
                      f"GPU: {stats.get('gpu_percent', 0):.1f}% ({stats.get('gpu_memory_mb', 0):.1f}MB)", 
                      end="", flush=True)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n✅ 监控已停止")
        monitor.stop_monitoring()
        
        # 保存报告
        filename = monitor.save_performance_report()
        print(f"📊 性能报告已保存: {filename}")

if __name__ == "__main__":
    main() 