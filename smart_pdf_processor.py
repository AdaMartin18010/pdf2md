#!/usr/bin/env python3
"""
智能PDF处理器 - 严格mineru模式
只有mineru能完整处理（包含图片、结构、格式）的PDF才转换，其他的直接跳过
"""

import os
import time
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessorType(Enum):
    """处理器类型"""
    MINERU = "mineru"
    SKIP = "skip"

@dataclass
class ProcessingResult:
    """处理结果"""
    file_path: Path
    success: bool
    processor_used: str
    error_message: Optional[str] = None
    processing_time: float = 0.0
    output_file: Optional[Path] = None
    has_images: bool = False
    has_structure: bool = False

class StrictMineruProcessor:
    """严格mineru处理器 - 只使用mineru，任何错误都跳过"""
    
    def __init__(self):
        self.compatible_files = []
        self.incompatible_files = []
        self.skipped_files = []
        self.processing_results = []
        
    def test_mineru_compatibility(self, pdf_path: Path) -> bool:
        """测试PDF是否与mineru兼容"""
        try:
            # 导入mineru相关模块
            from mineru.utils.pdf_classify import classify
            
            # 尝试分类PDF类型
            pdf_type = classify(str(pdf_path))
            
            # 如果能成功分类，说明PDF与mineru兼容
            return True
            
        except Exception as e:
            # 任何错误都认为不兼容
            logger.debug(f"PDF不兼容mineru: {pdf_path.name} - {str(e)}")
            return False
    
    def process_with_mineru_only(self, pdf_path: Path, output_dir: Path) -> ProcessingResult:
        """严格使用mineru处理PDF，不使用任何备选方案"""
        start_time = time.time()
        
        try:
            # 创建临时输出目录
            temp_output_dir = output_dir / f"temp_{pdf_path.stem}"
            temp_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 直接调用mineru核心函数，不使用wrapper的备选方案
            from mineru.backend.pipeline import pipeline_analyze
            from mineru.cli.common import read_fn
            
            # 读取PDF字节
            pdf_bytes = read_fn(pdf_path)
            
            # 第一步：文档分析
            print(f"  🔍 进行文档分析...")
            pipeline_analyze.doc_analyze(
                pdf_bytes_list=[pdf_bytes],
                lang_list=["ch"],
                parse_method="auto",
                formula_enable=True,
                table_enable=True
            )
            
            # 检查输出结果
            md_file = temp_output_dir / f"{pdf_path.stem}.md"
            images_dir = temp_output_dir / f"{pdf_path.stem}_images"
            
            if not md_file.exists():
                raise Exception("mineru未生成markdown文件")
            
            # 检查是否有图片和结构
            has_images = images_dir.exists() and any(images_dir.iterdir())
            has_structure = self._check_markdown_structure(md_file)
            
            if not has_structure:
                raise Exception("mineru输出缺少结构")
            
            # 移动到最终位置
            final_md_file = output_dir / f"{pdf_path.stem}.md"
            shutil.move(str(md_file), str(final_md_file))
            
            if has_images:
                final_images_dir = output_dir / f"{pdf_path.stem}_images"
                if final_images_dir.exists():
                    shutil.rmtree(final_images_dir)
                shutil.move(str(images_dir), str(final_images_dir))
            
            # 清理临时目录
            if temp_output_dir.exists():
                shutil.rmtree(temp_output_dir)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                file_path=pdf_path,
                success=True,
                processor_used="mineru",
                processing_time=processing_time,
                output_file=final_md_file,
                has_images=has_images,
                has_structure=has_structure
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # 清理临时目录
            if 'temp_output_dir' in locals() and temp_output_dir.exists():
                shutil.rmtree(temp_output_dir)
            
            return ProcessingResult(
                file_path=pdf_path,
                success=False,
                processor_used="mineru",
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _check_markdown_structure(self, md_file: Path) -> bool:
        """检查markdown文件是否有结构"""
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # 检查是否包含基本结构元素
            has_headers = '#' in content
            has_content = len(content.strip()) > 100  # 至少有100个字符的内容
            
            return has_headers and has_content
            
        except Exception:
            return False
    
    def process_pdfs(self, pdf_dir: Path, output_dir: Path) -> List[ProcessingResult]:
        """批量处理PDF文件"""
        print("🚀 开始严格mineru模式批量处理...")
        print("=" * 50)
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 查找所有PDF文件
        pdf_files = list(pdf_dir.rglob("*.pdf"))
        print(f"📁 找到 {len(pdf_files)} 个PDF文件")
        
        results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📄 处理第 {i}/{len(pdf_files)} 个文件: {pdf_file.name}")
            
            # 测试mineru兼容性
            if not self.test_mineru_compatibility(pdf_file):
                print(f"⏭️  跳过: {pdf_file.name} - 与mineru不兼容")
                self.skipped_files.append(pdf_file)
                results.append(ProcessingResult(
                    file_path=pdf_file,
                    success=False,
                    processor_used="skip",
                    error_message="与mineru不兼容"
                ))
                continue
            
            # 尝试用mineru处理
            result = self.process_with_mineru_only(pdf_file, output_dir)
            
            if result.success:
                print(f"✅ 成功: {pdf_file.name}")
                if result.has_images:
                    print(f"   📷 包含图片")
                if result.has_structure:
                    print(f"   📋 包含结构")
                self.compatible_files.append(pdf_file)
            else:
                print(f"❌ 失败: {pdf_file.name} - {result.error_message}")
                self.incompatible_files.append(pdf_file)
            
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[ProcessingResult], output_dir: Path):
        """生成处理报告"""
        report_file = output_dir / "strict_mineru_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("严格mineru模式处理报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 统计信息
            total_files = len(results)
            successful_files = len([r for r in results if r.success])
            skipped_files = len([r for r in results if r.processor_used == "skip"])
            failed_files = total_files - successful_files - skipped_files
            
            f.write(f"总文件数: {total_files}\n")
            f.write(f"成功转换: {successful_files}\n")
            f.write(f"跳过文件: {skipped_files}\n")
            f.write(f"转换失败: {failed_files}\n\n")
            
            # 成功文件列表
            if successful_files > 0:
                f.write("✅ 成功转换的文件:\n")
                for result in results:
                    if result.success:
                        f.write(f"  - {result.file_path.name}\n")
                        if result.has_images:
                            f.write(f"    📷 包含图片\n")
                        if result.has_structure:
                            f.write(f"    📋 包含结构\n")
                f.write("\n")
            
            # 跳过文件列表
            if skipped_files > 0:
                f.write("⏭️  跳过的文件:\n")
                for result in results:
                    if result.processor_used == "skip":
                        f.write(f"  - {result.file_path.name}\n")
                f.write("\n")
            
            # 失败文件列表
            if failed_files > 0:
                f.write("❌ 转换失败的文件:\n")
                for result in results:
                    if not result.success and result.processor_used != "skip":
                        f.write(f"  - {result.file_path.name}: {result.error_message}\n")
                f.write("\n")
        
        print(f"\n📊 处理报告已生成: {report_file}")
        print(f"✅ 成功转换: {successful_files} 个文件")
        print(f"⏭️  跳过: {skipped_files} 个文件")
        print(f"❌ 失败: {failed_files} 个文件")

def main():
    """主函数"""
    # 设置输入和输出目录
    pdf_dir = Path("test_pdfs")
    output_dir = Path("strict_mineru_output")
    
    if not pdf_dir.exists():
        print(f"❌ 输入目录不存在: {pdf_dir}")
        return
    
    # 创建处理器
    processor = StrictMineruProcessor()
    
    # 处理PDF文件
    results = processor.process_pdfs(pdf_dir, output_dir)
    
    # 生成报告
    processor.generate_report(results, output_dir)
    
    print("\n🎉 严格mineru模式处理完成！")

if __name__ == "__main__":
    main() 