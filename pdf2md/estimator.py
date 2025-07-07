"""
时间预估模块
"""

import time
from pathlib import Path
from typing import List, Dict, Any


class TimeEstimator:
    """时间预估器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.avg_time_per_mb = config.get('time_estimation', {}).get('avg_time_per_mb', 2.0)
        self.min_time_per_file = config.get('time_estimation', {}).get('min_time_per_file', 1.0)
        self.max_time_per_file = config.get('time_estimation', {}).get('max_time_per_file', 60.0)
    
    def estimate_file_time(self, file_path: Path) -> float:
        """预估单个文件转换时间"""
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            estimated_time = file_size_mb * self.avg_time_per_mb
            
            # 限制在合理范围内
            estimated_time = max(estimated_time, self.min_time_per_file)
            estimated_time = min(estimated_time, self.max_time_per_file)
            
            return estimated_time
        except Exception:
            return self.min_time_per_file
    
    def estimate_total_time(self, pdf_files: List[Path], workers: int = 1) -> Dict[str, Any]:
        """预估总转换时间"""
        if not pdf_files:
            return {
                "total_time": 0, 
                "avg_time_per_file": 0, 
                "total_size_mb": 0,
                "files_count": 0,
                "workers": workers
            }
        
        total_time = 0
        total_size = 0
        
        for file_path in pdf_files:
            file_time = self.estimate_file_time(file_path)
            total_time += file_time
            
            try:
                total_size += file_path.stat().st_size
            except Exception:
                pass
        
        # 考虑并发影响
        if workers > 1:
            total_time = total_time / workers
        
        return {
            "total_time": total_time,
            "avg_time_per_file": total_time / len(pdf_files) if pdf_files else 0,
            "total_size_mb": total_size / (1024 * 1024),
            "files_count": len(pdf_files),
            "workers": workers
        }
    
    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"
    
    def print_estimation(self, pdf_files: List[Path], workers: int = 1) -> None:
        """打印时间预估"""
        if not pdf_files:
            print("没有找到PDF文件")
            return
        
        estimation = self.estimate_total_time(pdf_files, workers)
        
        print(f"\n时间预估:")
        print(f"  文件数量: {estimation['files_count']}")
        print(f"  总大小: {estimation['total_size_mb']:.2f}MB")
        print(f"  预估总时间: {self.format_time(estimation['total_time'])}")
        print(f"  平均时间/文件: {self.format_time(estimation['avg_time_per_file'])}")
        print(f"  并发数: {workers}")
        
        if workers > 1:
            print(f"  (考虑并发加速)") 