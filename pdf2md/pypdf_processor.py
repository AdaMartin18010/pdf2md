#!/usr/bin/env python3
"""
基于pypdf的PDF处理器
用于替代mineru处理PDF文件
"""

import os
import time
from pathlib import Path
from typing import List, Optional, Tuple
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

class PypdfProcessor:
    """基于pypdf的PDF处理器"""
    
    def __init__(self):
        self.name = "pypdf"
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """从PDF文件提取文本"""
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            
            if page_count == 0:
                logger.warning(f"PDF文件没有页面: {pdf_path}")
                return None
            
            text_parts = []
            successful_pages = 0
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"# 第 {page_num} 页\n\n{text.strip()}\n")
                        successful_pages += 1
                    else:
                        logger.debug(f"第 {page_num} 页没有文本内容")
                except Exception as e:
                    logger.warning(f"提取第 {page_num} 页文本失败: {e}")
                    continue
            
            if not text_parts:
                logger.warning(f"PDF文件没有可提取的文本: {pdf_path}")
                return None
            
            logger.info(f"成功提取 {successful_pages}/{page_count} 页的文本")
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"处理PDF文件失败 {pdf_path}: {e}")
            return None
    
    def process_pdf_to_markdown(self, pdf_path: Path, output_path: Path) -> bool:
        """将PDF转换为Markdown"""
        logger.info(f"开始处理PDF文件: {pdf_path}")
        start_time = time.time()
        
        try:
            # 提取文本
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                logger.error(f"无法从PDF提取文本: {pdf_path}")
                return False
            
            # 创建输出目录
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入markdown文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {pdf_path.stem}\n\n")
                f.write(text)
            
            duration = time.time() - start_time
            logger.info(f"成功处理PDF文件: {pdf_path} (耗时: {duration:.2f}秒)")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"处理PDF文件失败 {pdf_path}: {e} (耗时: {duration:.2f}秒)")
            return False

def parse_doc_with_pypdf(
    path_list: List[Path],
    output_dir: str,
    lang: str = "ch",
    backend: str = "pypdf",
    method: str = "auto"
) -> bool:
    """
    使用pypdf处理PDF文件
    
    Args:
        path_list: PDF文件路径列表
        output_dir: 输出目录
        lang: 语言（pypdf不支持，保留参数兼容性）
        backend: 后端（pypdf不支持，保留参数兼容性）
        method: 方法（pypdf不支持，保留参数兼容性）
    
    Returns:
        bool: 是否成功
    """
    processor = PypdfProcessor()
    output_path = Path(output_dir)
    
    success_count = 0
    total_count = len(path_list)
    
    for pdf_path in path_list:
        if not pdf_path.exists():
            logger.error(f"PDF文件不存在: {pdf_path}")
            continue
        
        # 生成输出文件路径
        output_file = output_path / f"{pdf_path.stem}.md"
        
        if processor.process_pdf_to_markdown(pdf_path, output_file):
            success_count += 1
        else:
            logger.error(f"处理失败: {pdf_path}")
    
    logger.info(f"处理完成: {success_count}/{total_count} 个文件成功")
    return success_count > 0

if __name__ == "__main__":
    # 测试处理器
    processor = PypdfProcessor()
    
    pdf_dir = Path("pdfs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if pdf_files:
        test_pdf = pdf_files[0]
        output_file = Path("markdown") / f"{test_pdf.stem}_pypdf.md"
        
        print(f"测试处理: {test_pdf}")
        success = processor.process_pdf_to_markdown(test_pdf, output_file)
        
        if success:
            print(f"✅ 处理成功，输出文件: {output_file}")
        else:
            print("❌ 处理失败")
    else:
        print("没有找到PDF文件进行测试") 