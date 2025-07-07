"""
日志记录模块
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ConversionLogger:
    """转换日志记录器"""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.conversion_log = self.log_dir / "conversions.json"
        self.conversions = self._load_conversions()
    
    def _load_conversions(self) -> Dict[str, Any]:
        """加载历史转换记录"""
        if self.conversion_log.exists():
            try:
                with open(self.conversion_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告：加载转换记录失败: {e}")
        return {}
    
    def _save_conversions(self) -> None:
        """保存转换记录"""
        try:
            with open(self.conversion_log, 'w', encoding='utf-8') as f:
                json.dump(self.conversions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告：保存转换记录失败: {e}")
    
    def log_conversion(self, file_path: str, file_size: int, duration: float, 
                      success: bool, output_path: Optional[str] = None, 
                      error_message: Optional[str] = None, use_gpu: bool = False) -> None:
        """记录转换信息"""
        record = {
            "file_path": file_path,
            "file_size": file_size,
            "duration": duration,
            "success": success,
            "output_path": output_path,
            "error_message": error_message,
            "use_gpu": use_gpu,
            "timestamp": datetime.now().isoformat()
        }
        
        record_id = f"{file_path}_{int(time.time())}"
        self.conversions[record_id] = record
        self._save_conversions()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取转换统计信息"""
        if not self.conversions:
            return {}
        
        successful = [r for r in self.conversions.values() if r.get('success', False)]
        failed = [r for r in self.conversions.values() if not r.get('success', False)]
        
        total_files = len(self.conversions)
        total_size = sum(r.get('file_size', 0) for r in self.conversions.values())
        total_time = sum(r.get('duration', 0) for r in self.conversions.values())
        
        return {
            "total_files": total_files,
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / total_files if total_files > 0 else 0,
            "total_size_mb": total_size / (1024 * 1024),
            "total_time_seconds": total_time,
            "avg_time_per_file": total_time / total_files if total_files > 0 else 0
        } 