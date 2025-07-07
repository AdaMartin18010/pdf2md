# type: ignore
#!/usr/bin/env python3
"""
PDF转换器命令行界面
提供用户友好的命令行交互
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional
import logging

# 尝试导入 rich，如果失败则使用标准库
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    # 使用标准库替代
    RICH_AVAILABLE = False
    print("⚠️ rich 库未安装，使用标准库界面")

# 创建标准库替代类
if not RICH_AVAILABLE:
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    
    class Progress:
        def __init__(self, *args, **kwargs):
            self.console = Console()
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def add_task(self, description, total):
            return 0
        
        def update(self, task, description=None):
            if description:
                print(f"处理: {description}")
        
        def advance(self, task):
            pass
    
    class Table:
        def __init__(self, title=""):
            self.title = title
            self.columns = []
            self.rows = []
        
        def add_column(self, name, style=""):
            self.columns.append(name)
        
        def add_row(self, *args):
            self.rows.append(args)
        
        def __str__(self):
            result = f"{self.title}\n"
            if self.columns:
                result += " | ".join(self.columns) + "\n"
                result += "-" * len(" | ".join(self.columns)) + "\n"
            for row in self.rows:
                result += " | ".join(str(cell) for cell in row) + "\n"
            return result
    
    class Panel:
        def __init__(self, text, style=""):
            self.text = text
            self.style = style
    
    class Prompt:
        @staticmethod
        def ask(question, choices=None, default=""):
            if choices:
                print(f"{question} (选项: {', '.join(choices)})")
            else:
                print(f"{question}")
            return input().strip() or default
    
    class Confirm:
        @staticmethod
        def ask(question):
            response = input(f"{question} (y/n): ").lower().strip()
            return response in ['y', 'yes', '是']

# 导入处理器模块
try:
    from .advanced_processor import AdvancedPDFProcessor
    from .batch_processor import process_pdfs_batch
except ImportError:
    # 如果模块不存在，创建简单的替代类
    class AdvancedPDFProcessor:
        def __init__(self):
            self.processors = {}
        
        def process_pdf(self, input_file, output_file):
            class Result:
                def __init__(self, success, processor="unknown", error=None):
                    self.success = success
                    self.processor = processor
                    self.error = error
            return Result(False, error="AdvancedPDFProcessor not available")
    
    # 创建兼容的批处理函数
    def process_pdfs_batch(input_dir, output_dir, use_gpu=False, workers=1, logger=None):
        return (0, 0, 0.0)  # 返回元组 (success, failed, duration)

console = Console() if RICH_AVAILABLE else Console()
logger = logging.getLogger(__name__)

class PDFConverterCLI:
    """PDF转换器命令行界面"""
    
    def __init__(self):
        self.processor = AdvancedPDFProcessor()
        self.console = Console() if RICH_AVAILABLE else Console()
    
    def show_banner(self):
        """显示程序横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    PDF转Markdown转换器                        ║
║                    高级命令行界面                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        if RICH_AVAILABLE:
            self.console.print(Panel(banner, style="bold blue"))
        else:
            print(banner)
    
    def show_processor_info(self):
        """显示处理器信息"""
        if RICH_AVAILABLE:
            table = Table(title="可用处理器")
            table.add_column("处理器", style="cyan")
            table.add_column("状态", style="green")
            table.add_column("描述", style="white")
        else:
            table = Table(title="可用处理器")
            table.add_column("处理器")
            table.add_column("状态")
            table.add_column("描述")
        
        processors_info = {
            "pypdf": "PyPDF - 纯Python实现，兼容性好",
            "pdfplumber": "PDFPlumber - 强大的文本提取工具",
            "pymupdf": "PyMuPDF - 高性能PDF处理库",
            "pytesseract": "PyTesseract - OCR文字识别",
            "ocrmypdf": "OCRmyPDF - 专业OCR处理"
        }
        
        for processor_type in self.processor.processors.keys():
            status = "✅ 可用"
            description = processors_info.get(processor_type.value, "未知处理器")
            table.add_row(processor_type.value, status, description)
        
        if RICH_AVAILABLE:
            self.console.print(table)
        else:
            print(str(table))
    
    def interactive_mode(self):
        """交互模式"""
        self.show_banner()
        self.show_processor_info()
        
        while True:
            if RICH_AVAILABLE:
                self.console.print("\n" + "="*60)
                self.console.print("[bold cyan]请选择操作:[/bold cyan]")
            else:
                print("\n" + "="*60)
                print("请选择操作:")
            
            print("1. 选择PDF文件进行转换")
            print("2. 选择文件夹批量转换")
            print("3. 查看处理器信息")
            print("4. 安装依赖库")
            print("5. 退出程序")
            
            choice = Prompt.ask("请输入选项", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.convert_files_interactive()
            elif choice == "2":
                self.convert_folder_interactive()
            elif choice == "3":
                self.show_processor_info()
            elif choice == "4":
                self.install_dependencies_interactive()
            elif choice == "5":
                if RICH_AVAILABLE:
                    self.console.print("[green]感谢使用！[/green]")
                else:
                    print("感谢使用！")
                break
    
    def convert_files_interactive(self):
        """交互式文件转换"""
        if RICH_AVAILABLE:
            self.console.print("\n[bold yellow]文件转换模式[/bold yellow]")
        else:
            print("\n文件转换模式")
        
        # 获取文件路径
        file_paths = []
        while True:
            file_path = Prompt.ask("请输入PDF文件路径 (输入 'done' 完成)")
            if file_path.lower() == 'done':
                break
            
            path = Path(file_path)
            if not path.exists():
                if RICH_AVAILABLE:
                    self.console.print(f"[red]文件不存在: {file_path}[/red]")
                else:
                    print(f"文件不存在: {file_path}")
                continue
            
            if not path.suffix.lower() == '.pdf':
                if RICH_AVAILABLE:
                    self.console.print(f"[red]不是PDF文件: {file_path}[/red]")
                else:
                    print(f"不是PDF文件: {file_path}")
                continue
            
            file_paths.append(path)
            if RICH_AVAILABLE:
                self.console.print(f"[green]已添加: {path.name}[/green]")
            else:
                print(f"已添加: {path.name}")
        
        if not file_paths:
            if RICH_AVAILABLE:
                self.console.print("[yellow]没有选择任何文件[/yellow]")
            else:
                print("没有选择任何文件")
            return
        
        # 获取输出目录
        output_dir = Prompt.ask("请输入输出目录", default="markdown")
        output_path = Path(output_dir)
        
        # 确认转换
        if RICH_AVAILABLE:
            self.console.print(f"\n[bold]转换设置:[/bold]")
        else:
            print(f"\n转换设置:")
        print(f"文件数量: {len(file_paths)}")
        print(f"输出目录: {output_path}")
        
        if not Confirm.ask("确认开始转换?"):
            return
        
        # 执行转换
        self.convert_files(file_paths, output_path)
    
    def convert_folder_interactive(self):
        """交互式文件夹转换"""
        if RICH_AVAILABLE:
            self.console.print("\n[bold yellow]文件夹批量转换模式[/bold yellow]")
        else:
            print("\n文件夹批量转换模式")
        
        # 获取文件夹路径
        folder_path = Prompt.ask("请输入包含PDF文件的文件夹路径")
        folder = Path(folder_path)
        
        if not folder.exists():
            if RICH_AVAILABLE:
                self.console.print(f"[red]文件夹不存在: {folder_path}[/red]")
            else:
                print(f"文件夹不存在: {folder_path}")
            return
        
        if not folder.is_dir():
            if RICH_AVAILABLE:
                self.console.print(f"[red]不是文件夹: {folder_path}[/red]")
            else:
                print(f"不是文件夹: {folder_path}")
            return
        
        # 查找PDF文件
        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            if RICH_AVAILABLE:
                self.console.print(f"[yellow]在 {folder_path} 中没有找到PDF文件[/yellow]")
            else:
                print(f"在 {folder_path} 中没有找到PDF文件")
            return
        
        if RICH_AVAILABLE:
            self.console.print(f"[green]找到 {len(pdf_files)} 个PDF文件[/green]")
        else:
            print(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 获取输出目录
        output_dir = Prompt.ask("请输入输出目录", default="markdown")
        output_path = Path(output_dir)
        
        # 确认转换
        if RICH_AVAILABLE:
            self.console.print(f"\n[bold]转换设置:[/bold]")
        else:
            print(f"\n转换设置:")
        print(f"源文件夹: {folder}")
        print(f"PDF文件数: {len(pdf_files)}")
        print(f"输出目录: {output_path}")
        
        if not Confirm.ask("确认开始批量转换?"):
            return
        
        # 执行转换
        self.convert_files(pdf_files, output_path)
    
    def convert_files(self, files: List[Path], output_dir: Path):
        """转换文件"""
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 显示进度
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                
                task = progress.add_task("转换PDF文件", total=len(files))
                
                success_count = 0
                failed_count = 0
                start_time = time.time()
                
                for i, pdf_file in enumerate(files):
                    progress.update(task, description=f"处理 {pdf_file.name}")
                    
                    try:
                        output_file = output_dir / f"{pdf_file.stem}.md"
                        result = self.processor.process_pdf(pdf_file, output_file)
                        
                        if result.success:
                            success_count += 1
                            progress.console.print(f"[green]✅ {pdf_file.name} (使用 {result.processor})[/green]")
                        else:
                            failed_count += 1
                            progress.console.print(f"[red]❌ {pdf_file.name} - {result.error}[/red]")
                    
                    except Exception as e:
                        failed_count += 1
                        progress.console.print(f"[red]❌ {pdf_file.name} - 异常: {str(e)}[/red]")
                    
                    progress.advance(task)
                
                duration = time.time() - start_time
                
                # 显示结果
                self.show_conversion_results(success_count, failed_count, duration)
        else:
            # 标准库版本
            success_count = 0
            failed_count = 0
            start_time = time.time()
            
            for i, pdf_file in enumerate(files):
                print(f"处理 {pdf_file.name} ({i+1}/{len(files)})")
                
                try:
                    output_file = output_dir / f"{pdf_file.stem}.md"
                    result = self.processor.process_pdf(pdf_file, output_file)
                    
                    if result.success:
                        success_count += 1
                        print(f"✅ {pdf_file.name} (使用 {result.processor})")
                    else:
                        failed_count += 1
                        print(f"❌ {pdf_file.name} - {result.error}")
                
                except Exception as e:
                    failed_count += 1
                    print(f"❌ {pdf_file.name} - 异常: {str(e)}")
            
            duration = time.time() - start_time
            
            # 显示结果
            self.show_conversion_results(success_count, failed_count, duration)
    
    def show_conversion_results(self, success_count: int, failed_count: int, duration: float):
        """显示转换结果"""
        if RICH_AVAILABLE:
            table = Table(title="转换结果")
            table.add_column("项目", style="cyan")
            table.add_column("数值", style="white")
        else:
            table = Table(title="转换结果")
            table.add_column("项目")
            table.add_column("数值")
        
        table.add_row("成功文件", str(success_count))
        table.add_row("失败文件", str(failed_count))
        table.add_row("总耗时", f"{duration:.2f}秒")
        table.add_row("成功率", f"{success_count/(success_count+failed_count)*100:.1f}%" if (success_count+failed_count) > 0 else "0%")
        
        if RICH_AVAILABLE:
            self.console.print(table)
        else:
            print(str(table))
        
        if success_count > 0:
            if RICH_AVAILABLE:
                self.console.print(f"[green]✅ 转换完成！成功转换 {success_count} 个文件[/green]")
            else:
                print(f"✅ 转换完成！成功转换 {success_count} 个文件")
        else:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ 转换失败！没有成功转换任何文件[/red]")
            else:
                print(f"❌ 转换失败！没有成功转换任何文件")
    
    def install_dependencies_interactive(self):
        """交互式安装依赖"""
        if RICH_AVAILABLE:
            self.console.print("\n[bold yellow]依赖库安装[/bold yellow]")
        else:
            print("\n依赖库安装")
        
        dependencies = [
            ("pdfplumber", "PDF文本提取库"),
            ("pymupdf", "高性能PDF处理库"),
            ("pytesseract", "OCR文字识别库"),
            ("ocrmypdf", "专业OCR处理库"),
            ("Pillow", "图像处理库")
        ]
        
        if RICH_AVAILABLE:
            table = Table(title="可选依赖库")
            table.add_column("库名", style="cyan")
            table.add_column("描述", style="white")
            table.add_column("状态", style="green")
        else:
            table = Table(title="可选依赖库")
            table.add_column("库名")
            table.add_column("描述")
            table.add_column("状态")
        
        for lib_name, description in dependencies:
            try:
                __import__(lib_name.lower().replace('-', '_'))
                status = "✅ 已安装"
            except ImportError:
                status = "❌ 未安装"
            
            table.add_row(lib_name, description, status)
        
        if RICH_AVAILABLE:
            self.console.print(table)
        else:
            print(str(table))
        
        if Confirm.ask("是否安装缺失的依赖库?"):
            self.install_dependencies()
    
    def install_dependencies(self):
        """安装依赖库"""
        dependencies = ['pdfplumber', 'pymupdf', 'pytesseract', 'ocrmypdf', 'Pillow']
        
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                
                task = progress.add_task("安装依赖库", total=len(dependencies))
                
                for dep in dependencies:
                    progress.update(task, description=f"安装 {dep}")
                    
                    try:
                        import subprocess
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                        progress.console.print(f"[green]✅ {dep} 安装成功[/green]")
                    except subprocess.CalledProcessError:
                        progress.console.print(f"[red]❌ {dep} 安装失败[/red]")
                    
                    progress.advance(task)
            
            self.console.print("[green]依赖库安装完成！[/green]")
        else:
            # 标准库版本
            for dep in dependencies:
                print(f"安装 {dep}")
                
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                    print(f"✅ {dep} 安装成功")
                except subprocess.CalledProcessError:
                    print(f"❌ {dep} 安装失败")
            
            print("依赖库安装完成！")
    
    def command_line_mode(self, args):
        """命令行模式"""
        if args.files:
            files = [Path(f) for f in args.files]
            output_dir = Path(args.output or "markdown")
            self.convert_files(files, output_dir)
        elif args.folder:
            folder = Path(args.folder)
            pdf_files = list(folder.glob("*.pdf"))
            output_dir = Path(args.output or "markdown")
            self.convert_files(pdf_files, output_dir)
        else:
            self.interactive_mode()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PDF转Markdown转换器")
    parser.add_argument('-f', '--files', nargs='+', help='PDF文件路径列表')
    parser.add_argument('-d', '--folder', help='包含PDF文件的文件夹路径')
    parser.add_argument('-o', '--output', help='输出目录路径')
    parser.add_argument('-i', '--interactive', action='store_true', help='启动交互模式')
    
    args = parser.parse_args()
    
    cli = PDFConverterCLI()
    
    if args.interactive or (not args.files and not args.folder):
        cli.interactive_mode()
    else:
        cli.command_line_mode(args)

if __name__ == "__main__":
    main() 