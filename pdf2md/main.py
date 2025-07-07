#!/usr/bin/env python3
"""
PDF to Markdown converter main module.

This module provides the command-line interface and core conversion logic
for converting PDF files to Markdown format using mineru.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

import click

from .config import config
from .logger import ConversionLogger
from .estimator import TimeEstimator
from .shutdown import ShutdownManager
from .mineru_wrapper import parse_doc
from .batch_processor import process_pdfs_batch, get_optimal_worker_count
from .estimator import TimeEstimator
from .shutdown import ShutdownManager


def find_pdf_files(input_dir: Path) -> List[Path]:
    """递归查找指定目录下的所有PDF文件。"""
    pdf_files = []
    if not input_dir.exists():
        print(f"错误：输入目录 '{input_dir}' 不存在")
        return pdf_files
    
    for file_path in input_dir.rglob("*.pdf"):
        if file_path.is_file():
            pdf_files.append(file_path)
    
    return pdf_files


def convert_pdf_to_markdown(
    input_path: Path,
    output_dir: Path,
    use_gpu: bool = False,
    logger: Optional[ConversionLogger] = None
) -> Tuple[bool, float]:
    """
    转换单个PDF文件为Markdown
    
    Args:
        input_path: 输入PDF文件路径
        output_dir: 输出目录
        use_gpu: 是否使用GPU
        logger: 日志记录器
        
    Returns:
        (success, duration): 转换是否成功和耗时
    """
    start_time = time.time()
    
    try:
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建临时输出目录
        temp_output_dir = output_dir / f"{input_path.stem}_temp"
        temp_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 导入并调用mineru
        parse_doc(
            path_list=[input_path],
            output_dir=str(temp_output_dir),
            lang="ch",
            backend="pipeline",
            method="auto"
        )
        
        # 查找生成的markdown文件
        md_file = temp_output_dir / f"{input_path.stem}.md"
        if md_file.exists():
            # 移动文件到目标位置
            import shutil
            output_path = output_dir / f"{input_path.stem}.md"
            shutil.move(str(md_file), str(output_path))
            
            # 清理临时目录
            shutil.rmtree(temp_output_dir)
            
            duration = time.time() - start_time
            
            # 记录日志
            if logger:
                file_size = input_path.stat().st_size
                logger.log_conversion(
                    file_path=str(input_path),
                    file_size=file_size,
                    duration=duration,
                    success=True,
                    output_path=str(output_path),
                    use_gpu=use_gpu
                )
            
            return True, duration
        else:
            raise Exception(f"mineru未生成markdown文件: {md_file}")
            
    except Exception as e:
        duration = time.time() - start_time
        
        # 记录错误日志
        if logger:
            try:
                file_size = input_path.stat().st_size
                logger.log_conversion(
                    file_path=str(input_path),
                    file_size=file_size,
                    duration=duration,
                    success=False,
                    error_message=str(e),
                    use_gpu=use_gpu
                )
            except Exception as log_error:
                print(f"记录日志失败: {log_error}")
        
        return False, duration


def convert_directory(
    input_dir: Path,
    output_dir: Path,
    use_gpu: bool = False,
    workers: int = 1,
    logger: Optional[ConversionLogger] = None
) -> Tuple[int, int, float]:
    """
    转换目录中的所有PDF文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        config: 配置对象
        logger: 日志记录器
        
    Returns:
        (successful, failed, total_duration): 成功数、失败数和总耗时
    """
    # 查找所有PDF文件
    pdf_files = list(input_dir.rglob("*.pdf"))
    
    if not pdf_files:
        print("警告：在指定目录中未找到PDF文件")
        return 0, 0, 0.0
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 估算总转换时间
    total_size = sum(f.stat().st_size for f in pdf_files)
    estimator = TimeEstimator({})
    estimated_time = estimator.estimate_total_time(pdf_files, workers)["total_time"]
    print(f"估算总转换时间: {estimated_time:.1f} 秒")
    
    return process_pdfs_batch(
        input_dir=input_dir,
        output_dir=output_dir,
        use_gpu=use_gpu,
        workers=workers,
        logger=logger
    )


@click.command()
@click.option(
    "--input", "-i",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="输入目录路径（包含PDF文件）"
)
@click.option(
    "--output", "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    help="输出目录路径"
)
@click.option(
    "--use-gpu",
    is_flag=True,
    help="使用GPU加速转换"
)
@click.option(
    "--workers", "-w",
    type=int,
    help="并发工作进程数"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="详细输出模式"
)
@click.option(
    "--estimate-time",
    is_flag=True,
    help="显示时间预估"
)
@click.option(
    "--no-log",
    is_flag=True,
    help="禁用转换日志记录"
)
@click.option(
    "--config",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help="指定配置文件路径"
)
@click.option(
    "--shutdown",
    is_flag=True,
    help="转换完成后自动关机"
)
@click.option(
    "--shutdown-delay",
    type=int,
    default=1,
    help="关机延迟时间（分钟，默认1分钟）"
)
@click.option(
    "--shutdown-force",
    is_flag=True,
    help="强制关机（不等待应用程序关闭）"
)
@click.option(
    "--no-shutdown-confirm",
    is_flag=True,
    help="不确认直接关机"
)
def main(
    input_dir: Optional[Path],
    output_dir: Optional[Path],
    use_gpu: bool = False,
    workers: int = 1,
    verbose: bool = False,
    estimate_time: bool = True,
    no_log: bool = False,
    config_file: Optional[Path] = None,
    shutdown: bool = False,
    shutdown_delay: int = 1,
    shutdown_force: bool = False,
    no_shutdown_confirm: bool = False
) -> None:
    """PDF到Markdown转换工具"""
    
    # 重新加载配置（如果指定了配置文件）
    if config_file:
        from .config import Config
        global config
        config = Config(config_file)
    
    # 使用配置文件中的默认值
    if input_dir is None:
        input_dir = Path(config.get('paths.input', './pdfs'))
    if output_dir is None:
        output_dir = Path(config.get('paths.output', './markdown'))
    if not use_gpu:
        use_gpu = config.get('defaults.use_gpu', False)
    if workers == 1:
        workers = config.get('defaults.workers', 1)
    if not verbose:
        verbose = config.get('defaults.verbose', False)
    if estimate_time:
        estimate_time = config.get('defaults.estimate_time', True)
    
    log_conversions = not no_log and config.get('defaults.log_conversions', True)
    
    # 关机设置
    shutdown_enabled = shutdown or config.get('shutdown.enabled', False)
    shutdown_delay = shutdown_delay if shutdown else config.get('shutdown.delay_minutes', 1)
    shutdown_force = shutdown_force or config.get('shutdown.force', False)
    shutdown_confirm = not no_shutdown_confirm and config.get('shutdown.confirm', True)
    
    print("=" * 50)
    print("PDF to Markdown Converter")
    print("=" * 50)
    
    # 显示配置信息
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"使用GPU: {'是' if use_gpu else '否'}")
    print(f"并发数: {workers}")
    print(f"时间预估: {'是' if estimate_time else '否'}")
    print(f"日志记录: {'是' if log_conversions else '否'}")
    print(f"自动关机: {'是' if shutdown_enabled else '否'}")
    if shutdown_enabled:
        print(f"  延迟时间: {shutdown_delay}分钟")
        print(f"  强制关机: {'是' if shutdown_force else '否'}")
    print()
    
    # 开始转换
    try:
        successful, failed, total_duration = process_pdfs_batch(
            input_dir=input_dir,
            output_dir=output_dir,
            use_gpu=use_gpu,
            workers=workers,
            logger=None
        )
        
        # 处理关机
        if shutdown_enabled and successful > 0:
            shutdown_manager = ShutdownManager()
            
            if not shutdown_manager.can_shutdown():
                print("\n警告：没有关机权限，跳过自动关机")
            else:
                if shutdown_confirm:
                    print(f"\n转换完成！系统将在{shutdown_delay}分钟后关机。")
                    print("按 Ctrl+C 可以取消关机...")
                    try:
                        time.sleep(5)  # 给用户5秒时间考虑
                        if shutdown_manager.shutdown_system(shutdown_delay, shutdown_force):
                            print("关机命令已执行")
                        else:
                            print("关机命令执行失败")
                    except KeyboardInterrupt:
                        print("\n用户取消关机")
                        shutdown_manager.cancel_shutdown()
                else:
                    if shutdown_manager.shutdown_system(shutdown_delay, shutdown_force):
                        print("关机命令已执行")
                    else:
                        print("关机命令执行失败")
                        
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 