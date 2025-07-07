"""
批量处理器模块
支持多进程并行处理PDF文件
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
import multiprocessing as mp

from .logger import ConversionLogger
from .mineru_wrapper import parse_doc


@dataclass
class FileTask:
    """文件任务数据类"""
    file_path: Path
    output_dir: Path
    task_id: int
    total_files: int
    use_gpu: bool


@dataclass
class FileResult:
    """文件处理结果数据类"""
    task_id: int
    file_path: Path
    success: bool
    duration: float
    error_message: Optional[str] = None
    output_path: Optional[Path] = None


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, max_workers: int = 4, use_processes: bool = False):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.progress_lock = threading.Lock()
        self.completed_count = 0
        self.total_count = 0
        
    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        use_gpu: bool = False,
        logger: Optional[ConversionLogger] = None
    ) -> Tuple[int, int, float]:
        """处理整个目录的PDF文件"""
        
        # 查找所有PDF文件
        pdf_files = self._find_pdf_files(input_dir)
        
        if not pdf_files:
            print("警告：在指定目录中未找到PDF文件")
            return 0, 0, 0.0
        
        print(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建任务列表
        tasks = []
        for i, pdf_file in enumerate(pdf_files):
            task = FileTask(
                file_path=pdf_file,
                output_dir=output_dir,
                task_id=i + 1,
                total_files=len(pdf_files),
                use_gpu=use_gpu
            )
            tasks.append(task)
        
        # 选择执行器类型 - 默认使用线程池避免pickle问题
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        start_time = time.time()
        successful = 0
        failed = 0
        
        try:
            with executor_class(max_workers=self.max_workers) as executor:
                # 提交所有任务
                future_to_task = {
                    executor.submit(self._process_single_file, task): task 
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
                                print(f"✓ 成功转换 ({self.completed_count}/{self.total_count}): {task.file_path.name}")
                            else:
                                failed += 1
                                print(f"✗ 转换失败 ({self.completed_count}/{self.total_count}): {task.file_path.name}")
                                if result.error_message:
                                    print(f"  错误: {result.error_message}")
                        
                        # 记录日志
                        if logger:
                            self._log_conversion(logger, task, result)
                            
                    except Exception as e:
                        failed += 1
                        print(f"✗ 任务异常 ({self.completed_count}/{self.total_count}): {task.file_path.name}")
                        print(f"  异常: {str(e)}")
        
        except KeyboardInterrupt:
            print("\n用户中断处理")
            return successful, failed, time.time() - start_time
        
        total_duration = time.time() - start_time
        
        return successful, failed, total_duration
    
    def _find_pdf_files(self, input_dir: Path) -> List[Path]:
        """递归查找PDF文件"""
        pdf_files = []
        if not input_dir.exists():
            print(f"错误：输入目录 '{input_dir}' 不存在")
            return pdf_files
        
        for file_path in input_dir.rglob("*.pdf"):
            if file_path.is_file():
                pdf_files.append(file_path)
        
        return pdf_files
    
    def _process_single_file(self, task: FileTask) -> FileResult:
        """处理单个PDF文件（工作进程/线程函数）"""
        start_time = time.time()
        
        try:
            # 创建输出目录结构
            relative_path = task.file_path.relative_to(task.file_path.parents[len(task.file_path.parts) - len(task.output_dir.parts) - 1])
            output_path = task.output_dir / relative_path.with_suffix('.md')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建临时输出目录
            temp_output_dir = output_path.parent / f"{task.file_path.stem}_temp"
            temp_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 调用mineru进行转换
            parse_doc(
                path_list=[task.file_path],
                output_dir=str(temp_output_dir),
                lang="ch",
                backend="pipeline",
                method="auto"
            )
            
            # 查找生成的markdown文件
            md_file = temp_output_dir / f"{task.file_path.stem}.md"
            if md_file.exists():
                # 移动文件到目标位置
                import shutil
                shutil.move(str(md_file), str(output_path))
                
                # 清理临时目录
                shutil.rmtree(temp_output_dir)
                
                duration = time.time() - start_time
                return FileResult(
                    task_id=task.task_id,
                    file_path=task.file_path,
                    success=True,
                    duration=duration,
                    output_path=output_path
                )
            else:
                raise Exception(f"mineru未生成markdown文件: {md_file}")
                
        except Exception as e:
            duration = time.time() - start_time
            return FileResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=False,
                duration=duration,
                error_message=str(e)
            )
    
    def _log_conversion(
        self, 
        logger: ConversionLogger, 
        task: FileTask, 
        result: FileResult
    ) -> None:
        """记录转换日志"""
        try:
            file_size = task.file_path.stat().st_size
            
            if result.success:
                logger.log_conversion(
                    file_path=str(task.file_path),
                    file_size=file_size,
                    duration=result.duration,
                    success=True,
                    output_path=str(result.output_path) if result.output_path else None,
                    use_gpu=task.use_gpu
                )
            else:
                logger.log_conversion(
                    file_path=str(task.file_path),
                    file_size=file_size,
                    duration=result.duration,
                    success=False,
                    error_message=result.error_message,
                    use_gpu=task.use_gpu
                )
        except Exception as e:
            print(f"记录日志失败: {e}")


def create_batch_processor(
    workers: int = 4,
    use_processes: bool = False,  # 默认使用线程池
    gpu_available: bool = False
) -> BatchProcessor:
    """创建批量处理器"""
    
    # 根据GPU可用性调整策略
    if gpu_available:
        # GPU模式下使用线程池，避免GPU资源冲突
        use_processes = False
        workers = min(workers, 4)  # GPU模式下限制并发数
    else:
        # CPU模式下默认使用线程池，避免pickle问题
        use_processes = False
        workers = min(workers, os.cpu_count() or 4)
    
    return BatchProcessor(
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


def process_pdfs_batch(
    input_dir: Path,
    output_dir: Path,
    use_gpu: bool = False,
    workers: int = 1,
    logger: Optional[ConversionLogger] = None
) -> Tuple[int, int, float]:
    """批量处理PDF文件（主函数）"""
    
    # 创建处理器
    gpu_available = check_gpu_availability() if use_gpu else False
    processor = create_batch_processor(workers, gpu_available=gpu_available)
    
    print(f"使用批量处理 (工作进程数: {workers})")
    if gpu_available:
        print("检测到GPU可用，使用线程池避免GPU资源冲突")
    else:
        print("使用线程池避免pickle序列化问题")
    
    # 处理文件
    return processor.process_directory(input_dir, output_dir, use_gpu, logger) 