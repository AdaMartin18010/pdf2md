"""
工具函数模块
"""

import os
import hashlib
import time
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


def get_file_hash(file_path: Path) -> str:
    """获取文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size_bytes)
    while size_float >= 1024 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1
    
    return f"{size_float:.1f}{size_names[i]}"


def format_duration(seconds: float) -> str:
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def calculate_progress(current: int, total: int) -> float:
    """计算进度百分比"""
    if total == 0:
        return 0.0
    return (current / total) * 100


def create_backup(file_path: Path) -> Optional[Path]:
    """创建文件备份"""
    try:
        if not file_path.exists():
            return None
        
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None


def restore_backup(backup_path: Path, original_path: Path) -> bool:
    """从备份恢复文件"""
    try:
        if not backup_path.exists():
            return False
        
        import shutil
        shutil.copy2(backup_path, original_path)
        return True
    except Exception:
        return False


def clean_temp_files(temp_dir: Path) -> None:
    """清理临时文件"""
    try:
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
    except Exception:
        pass


def validate_pdf_file(file_path: Path) -> bool:
    """验证PDF文件有效性"""
    try:
        if not file_path.exists():
            return False
        
        # 检查文件大小
        if file_path.stat().st_size == 0:
            return False
        
        # 检查PDF文件头
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header.startswith(b'%PDF')
    except Exception:
        return False


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import psutil
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent
    }


def check_disk_space(path: Path, required_mb: int = 100) -> bool:
    """检查磁盘空间"""
    try:
        import psutil
        usage = psutil.disk_usage(path)
        available_mb = usage.free / (1024 * 1024)
        return available_mb >= required_mb
    except Exception:
        return True  # 如果无法检查，假设有足够空间


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """创建进度条"""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    progress = int((current / total) * width)
    percentage = int((current / total) * 100)
    
    bar = "[" + "=" * progress + " " * (width - progress) + "]"
    return f"{bar} {percentage}%"


def log_with_timestamp(message: str, level: str = "INFO") -> str:
    """带时间戳的日志消息"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {level}: {message}"


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    # 移除或替换不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制长度
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:255-len(ext)] + ext
    return safe_name


def ensure_directory(path: Path) -> bool:
    """确保目录存在"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """获取文件详细信息"""
    try:
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "modified": time.ctime(stat.st_mtime),
            "created": time.ctime(stat.st_ctime),
            "is_valid_pdf": validate_pdf_file(file_path)
        }
    except Exception:
        return {
            "name": file_path.name,
            "size": 0,
            "size_formatted": "0B",
            "modified": "未知",
            "created": "未知",
            "is_valid_pdf": False
        } 