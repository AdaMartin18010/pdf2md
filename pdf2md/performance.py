"""
性能监控模块
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from .utils import log_with_timestamp


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    active_threads: int


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.interval = 1.0  # 监控间隔（秒）
    
    def start_monitoring(self) -> None:
        """开始性能监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("📊 性能监控已启动")
    
    def stop_monitoring(self) -> None:
        """停止性能监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("📊 性能监控已停止")
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics.append(metrics)
                
                # 写入日志文件
                if self.log_file:
                    self._write_metrics(metrics)
                
                time.sleep(self.interval)
            except Exception as e:
                print(f"性能监控错误: {e}")
                break
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        try:
            # 活跃线程数
            active_threads = threading.active_count()
            
            # 简化的CPU和内存监控
            cpu_percent = 0.0
            memory_percent = 0.0
            
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                active_threads=active_threads
            )
        except Exception as e:
            print(f"收集性能指标失败: {e}")
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                active_threads=0
            )
    
    def _write_metrics(self, metrics: PerformanceMetrics) -> None:
        """写入性能指标到日志文件"""
        try:
            if self.log_file is None:
                print("警告: 日志文件路径未设置")
                return
                
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{metrics.timestamp},{metrics.cpu_percent:.2f},{metrics.memory_percent:.2f},{metrics.active_threads}\n")
        except Exception as e:
            print(f"写入性能指标失败: {e}")
    
    def get_summary(self) -> Dict[str, float]:
        """获取性能摘要"""
        if not self.metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics]
        memory_values = [m.memory_percent for m in self.metrics]
        
        return {
            "avg_cpu_percent": sum(cpu_values) / len(cpu_values),
            "max_cpu_percent": max(cpu_values),
            "avg_memory_percent": sum(memory_values) / len(memory_values),
            "max_memory_percent": max(memory_values),
            "total_samples": len(self.metrics),
            "monitoring_duration": self.metrics[-1].timestamp - self.metrics[0].timestamp
        }
    
    def print_summary(self) -> None:
        """打印性能摘要"""
        summary = self.get_summary()
        
        if not summary:
            print("📊 没有性能数据")
            return
        
        print(f"\n📊 性能监控摘要:")
        print(f"  监控时长: {summary['monitoring_duration']:.1f}秒")
        print(f"  采样次数: {summary['total_samples']}")
        print(f"  平均CPU使用率: {summary['avg_cpu_percent']:.1f}%")
        print(f"  最大CPU使用率: {summary['max_cpu_percent']:.1f}%")
        print(f"  平均内存使用率: {summary['avg_memory_percent']:.1f}%")
        print(f"  最大内存使用率: {summary['max_memory_percent']:.1f}%")


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = {}
    
    def start_profile(self, name: str) -> None:
        """开始性能分析"""
        if name not in self.profiles:
            self.profiles[name] = []
        self.profiles[name].append(time.time())
    
    def end_profile(self, name: str) -> float:
        """结束性能分析，返回耗时"""
        if name not in self.profiles or not self.profiles[name]:
            return 0.0
        
        start_time = self.profiles[name].pop()
        duration = time.time() - start_time
        return duration
    
    def get_profile_summary(self) -> Dict[str, Dict[str, float]]:
        """获取性能分析摘要"""
        summary = {}
        
        for name, times in self.profiles.items():
            if times:
                summary[name] = {
                    "total_time": sum(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "count": len(times)
                }
        
        return summary
    
    def print_profile_summary(self) -> None:
        """打印性能分析摘要"""
        summary = self.get_profile_summary()
        
        if not summary:
            print("📊 没有性能分析数据")
            return
        
        print(f"\n📊 性能分析摘要:")
        for name, stats in summary.items():
            print(f"  {name}:")
            print(f"    总耗时: {stats['total_time']:.3f}秒")
            print(f"    平均耗时: {stats['avg_time']:.3f}秒")
            print(f"    最小耗时: {stats['min_time']:.3f}秒")
            print(f"    最大耗时: {stats['max_time']:.3f}秒")
            print(f"    执行次数: {stats['count']}")


# 全局性能监控器和分析器
performance_monitor = PerformanceMonitor()
performance_profiler = PerformanceProfiler() 