"""
并发处理模块
提供真正的多进程/多线程PDF转换功能
"""

import os
import time
import signal
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import threading
from queue import Queue

from .logger import ConversionLogger
from .mineru_wrapper import parse_doc


@dataclass
class ConversionTask:
    """转换任务数据类"""
    pdf_path: Path
    output_dir: Path
    use_gpu: bool
    task_id: int
    total_tasks: int


@dataclass
class ConversionResult:
    """转换结果数据类"""
    task_id: int
    pdf_path: Path
    success: bool
    duration: float
    error_message: Optional[str] = None
    output_path: Optional[Path] = None


class ConcurrentProcessor:
    """并发处理器"""
    
    def __init__(self, max_workers: int = 4, use_processes: bool = True):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.results_queue = Queue()
        self.progress_lock = threading.Lock()
        self.completed_count = 0
        self.total_count = 0
        
    def process_pdfs_concurrent(
        self,
        pdf_files: List[Path],
        output_dir: Path,
        use_gpu: bool = False,
        logger: Optional[ConversionLogger] = None
    ) -> Tuple[int, int, float]:
        """并发处理PDF文件"""
        
        if not pdf_files:
            return 0, 0, 0.0
        
        self.total_count = len(pdf_files)
        self.completed_count = 0
        
        # 创建任务列表
        tasks = []
        for i, pdf_file in enumerate(pdf_files):
            task = ConversionTask(
                pdf_path=pdf_file,
                output_dir=output_dir,
                use_gpu=use_gpu,
                task_id=i + 1,
                total_tasks=len(pdf_files)
            )
            tasks.append(task)
        
        # 选择执行器类型
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        start_time = time.time()
        successful = 0
        failed = 0
        
        try:
            with executor_class(max_workers=self.max_workers) as executor:
                # 提交所有任务
                future_to_task = {
                    executor.submit(self._convert_single_pdf, task): task 
                    for task in tasks
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        
                        with self.progress_lock:
                            self.completed_count += 1
                            if result.success:
                                successful += 1
                                print(f"✓ 成功转换 ({self.completed_count}/{self.total_count}): {task.pdf_path.name}")
                            else:
                                failed += 1
                                print(f"✗ 转换失败 ({self.completed_count}/{self.total_count}): {task.pdf_path.name}")
                                if result.error_message:
                                    print(f"  错误: {result.error_message}")
                        
                        # 记录日志
                        if logger:
                            self._log_conversion(logger, task, result)
                            
                    except Exception as e:
                        failed += 1
                        print(f"✗ 任务异常 ({self.completed_count}/{self.total_count}): {task.pdf_path.name}")
                        print(f"  异常: {str(e)}")
        
        except KeyboardInterrupt:
            print("\n用户中断处理")
            return successful, failed, time.time() - start_time
        
        total_duration = time.time() - start_time
        
        return successful, failed, total_duration
    
    def _convert_single_pdf(self, task: ConversionTask) -> ConversionResult:
        """转换单个PDF文件（工作进程/线程函数）"""
        start_time = time.time()
        
        try:
            # 创建输出目录结构
            relative_path = task.pdf_path.relative_to(task.pdf_path.parents[len(task.pdf_path.parts) - len(task.output_dir.parts) - 1])
            output_path = task.output_dir / relative_path.with_suffix('.md')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建临时输出目录
            temp_output_dir = output_path.parent / f"{task.pdf_path.stem}_temp"
            temp_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 调用mineru进行转换
            parse_doc(
                path_list=[task.pdf_path],
                output_dir=str(temp_output_dir),
                lang="ch",
                backend="pipeline",
                method="auto"
            )
            
            # 查找生成的markdown文件
            md_file = temp_output_dir / f"{task.pdf_path.stem}.md"
            if md_file.exists():
                # 移动文件到目标位置
                import shutil
                shutil.move(str(md_file), str(output_path))
                
                # 清理临时目录
                shutil.rmtree(temp_output_dir)
                
                duration = time.time() - start_time
                return ConversionResult(
                    task_id=task.task_id,
                    pdf_path=task.pdf_path,
                    success=True,
                    duration=duration,
                    output_path=output_path
                )
            else:
                raise Exception(f"mineru未生成markdown文件: {md_file}")
                
        except Exception as e:
            duration = time.time() - start_time
            return ConversionResult(
                task_id=task.task_id,
                pdf_path=task.pdf_path,
                success=False,
                duration=duration,
                error_message=str(e)
            )
    
    def _log_conversion(
        self, 
        logger: ConversionLogger, 
        task: ConversionTask, 
        result: ConversionResult
    ) -> None:
        """记录转换日志"""
        try:
            file_size = task.pdf_path.stat().st_size
            
            if result.success:
                logger.log_conversion(
                    file_path=str(task.pdf_path),
                    file_size=file_size,
                    duration=result.duration,
                    success=True,
                    output_path=str(result.output_path) if result.output_path else None,
                    use_gpu=task.use_gpu
                )
            else:
                logger.log_conversion(
                    file_path=str(task.pdf_path),
                    file_size=file_size,
                    duration=result.duration,
                    success=False,
                    error_message=result.error_message,
                    use_gpu=task.use_gpu
                )
        except Exception as e:
            print(f"记录日志失败: {e}")


def create_concurrent_processor(
    workers: int = 4,
    use_processes: bool = True,
    gpu_available: bool = False
) -> ConcurrentProcessor:
    """创建并发处理器"""
    
    # 根据GPU可用性调整策略
    if gpu_available:
        # GPU模式下使用线程池，避免GPU资源冲突
        use_processes = False
        workers = min(workers, 4)  # GPU模式下限制并发数
    else:
        # CPU模式下使用进程池，充分利用多核
        use_processes = True
        workers = min(workers, os.cpu_count() or 4)
    
    return ConcurrentProcessor(
        max_workers=workers,
        use_processes=use_processes
    )


def check_gpu_availability() -> bool:
    """检查GPU是否可用"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_optimal_worker_count() -> int:
    """获取最优工作进程数"""
    cpu_count = os.cpu_count() or 4
    
    # 根据CPU核心数确定最优并发数
    if cpu_count <= 2:
        return 1
    elif cpu_count <= 4:
        return 2
    elif cpu_count <= 8:
        return 4
    else:
        return min(cpu_count, 8)  # 限制最大并发数 