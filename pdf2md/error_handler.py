"""
错误处理模块
"""

import sys
import traceback
from pathlib import Path
from typing import Optional, Callable, Any
from .utils import log_with_timestamp


class ConversionError(Exception):
    """转换错误基类"""
    def __init__(self, message: str, file_path: Optional[Path] = None):
        self.message = message
        self.file_path = file_path
        super().__init__(self.message)


class PDFValidationError(ConversionError):
    """PDF文件验证错误"""
    pass


class MineruError(ConversionError):
    """Mineru转换错误"""
    pass


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file
        self.error_count = 0
        self.error_details = []
    
    def handle_error(self, error: Exception, context: str = "", file_path: Optional[Path] = None) -> None:
        """处理错误"""
        self.error_count += 1
        
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "file_path": str(file_path) if file_path else None,
            "traceback": traceback.format_exc()
        }
        
        self.error_details.append(error_info)
        
        # 记录错误
        error_message = log_with_timestamp(
            f"错误 {self.error_count}: {error_info['type']} - {error_info['message']}",
            "ERROR"
        )
        
        if context:
            error_message += f" (上下文: {context})"
        
        if file_path:
            error_message += f" (文件: {file_path})"
        
        print(f"❌ {error_message}")
        
        # 写入日志文件
        if self.log_file:
            self._write_error_log(error_info)
    
    def _write_error_log(self, error_info: dict) -> None:
        """写入错误日志"""
        if not self.log_file:
            return
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"错误时间: {log_with_timestamp('', 'ERROR').split(']')[0][1:]}\n")
                f.write(f"错误类型: {error_info['type']}\n")
                f.write(f"错误消息: {error_info['message']}\n")
                if error_info['context']:
                    f.write(f"上下文: {error_info['context']}\n")
                if error_info['file_path']:
                    f.write(f"文件路径: {error_info['file_path']}\n")
                f.write(f"堆栈跟踪:\n{error_info['traceback']}\n")
        except Exception as e:
            print(f"警告：无法写入错误日志: {e}")
    
    def get_error_summary(self) -> dict:
        """获取错误摘要"""
        if not self.error_details:
            return {"total_errors": 0, "error_types": {}}
        
        error_types = {}
        for error in self.error_details:
            error_type = error['type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": self.error_count,
            "error_types": error_types,
            "details": self.error_details
        }
    
    def print_error_summary(self) -> None:
        """打印错误摘要"""
        summary = self.get_error_summary()
        
        if summary['total_errors'] == 0:
            print("✅ 没有发生错误")
            return
        
        print(f"\n❌ 错误摘要:")
        print(f"  总错误数: {summary['total_errors']}")
        
        for error_type, count in summary['error_types'].items():
            print(f"  {error_type}: {count}次")
        
        if self.log_file:
            print(f"  详细日志: {self.log_file}")


def safe_execute(func: Callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """安全执行函数，返回结果和异常"""
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        return None, e


def validate_pdf_with_error_handling(file_path: Path, error_handler: ErrorHandler) -> bool:
    """带错误处理的PDF验证"""
    try:
        from .utils import validate_pdf_file
        return validate_pdf_file(file_path)
    except Exception as e:
        error_handler.handle_error(e, "PDF验证", file_path)
        return False


def create_error_report(error_handler: ErrorHandler, output_path: Path) -> None:
    """创建错误报告"""
    summary = error_handler.get_error_summary()
    
    if summary['total_errors'] == 0:
        return
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("PDF转换错误报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"总错误数: {summary['total_errors']}\n")
            f.write(f"生成时间: {log_with_timestamp('', 'INFO').split(']')[0][1:]}\n\n")
            
            f.write("错误类型统计:\n")
            for error_type, count in summary['error_types'].items():
                f.write(f"  {error_type}: {count}次\n")
            
            f.write("\n详细错误信息:\n")
            for i, error in enumerate(summary['details'], 1):
                f.write(f"\n错误 {i}:\n")
                f.write(f"  类型: {error['type']}\n")
                f.write(f"  消息: {error['message']}\n")
                if error['context']:
                    f.write(f"  上下文: {error['context']}\n")
                if error['file_path']:
                    f.write(f"  文件: {error['file_path']}\n")
                f.write(f"  堆栈:\n{error['traceback']}\n")
        
        print(f"📄 错误报告已保存到: {output_path}")
    except Exception as e:
        print(f"警告：无法创建错误报告: {e}") 