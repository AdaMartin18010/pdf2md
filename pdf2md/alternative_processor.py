#!/usr/bin/env python3
"""
替代的PDF处理器
使用不同的方法来处理PDF文件，避免PyPDFium2的兼容性问题
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AlternativePDFProcessor:
    """替代的PDF处理器"""
    
    def __init__(self):
        self.supported_methods = ['pdfplumber', 'pymupdf', 'pypdf']
    
    def check_dependencies(self):
        """检查依赖库"""
        available_methods = []
        
        try:
            import pdfplumber
            available_methods.append('pdfplumber')
            logger.info("pdfplumber 可用")
        except ImportError:
            logger.warning("pdfplumber 不可用")
        
        try:
            import pymupdf
            available_methods.append('pymupdf')
            logger.info("pymupdf 可用")
        except ImportError:
            logger.warning("pymupdf 不可用")
        
        try:
            import pypdf
            available_methods.append('pypdf')
            logger.info("pypdf 可用")
        except ImportError:
            logger.warning("pypdf 不可用")
        
        return available_methods
    
    def extract_text_with_pdfplumber(self, pdf_path: Path) -> Optional[str]:
        """使用pdfplumber提取文本"""
        try:
            import pdfplumber
            
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"# 第 {page_num} 页\n\n{text}\n")
            
            return "\n".join(text_parts) if text_parts else None
            
        except Exception as e:
            logger.error(f"pdfplumber提取失败: {e}")
            return None
    
    def extract_text_with_pymupdf(self, pdf_path: Path) -> Optional[str]:
        """使用pymupdf提取文本"""
        try:
            import pymupdf
            
            text_parts = []
            doc = pymupdf.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    text_parts.append(f"# 第 {page_num + 1} 页\n\n{text}\n")
            
            doc.close()
            return "\n".join(text_parts) if text_parts else None
            
        except Exception as e:
            logger.error(f"pymupdf提取失败: {e}")
            return None
    
    def extract_text_with_pypdf(self, pdf_path: Path) -> Optional[str]:
        """使用pypdf提取文本"""
        try:
            from pypdf import PdfReader
            
            text_parts = []
            reader = PdfReader(pdf_path)
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_parts.append(f"# 第 {page_num} 页\n\n{text}\n")
            
            return "\n".join(text_parts) if text_parts else None
            
        except Exception as e:
            logger.error(f"pypdf提取失败: {e}")
            return None
    
    def process_pdf(self, pdf_path: Path, output_path: Path) -> bool:
        """处理PDF文件"""
        logger.info(f"开始处理PDF文件: {pdf_path}")
        
        # 检查可用的方法
        available_methods = self.check_dependencies()
        
        if not available_methods:
            logger.error("没有可用的PDF处理方法")
            return False
        
        # 尝试不同的方法
        for method in available_methods:
            logger.info(f"尝试使用 {method} 处理")
            
            text = None
            if method == 'pdfplumber':
                text = self.extract_text_with_pdfplumber(pdf_path)
            elif method == 'pymupdf':
                text = self.extract_text_with_pymupdf(pdf_path)
            elif method == 'pypdf':
                text = self.extract_text_with_pypdf(pdf_path)
            
            if text:
                # 保存为markdown文件
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {pdf_path.stem}\n\n")
                        f.write(text)
                    
                    logger.info(f"成功使用 {method} 处理PDF文件")
                    return True
                    
                except Exception as e:
                    logger.error(f"保存文件失败: {e}")
                    continue
        
        logger.error("所有方法都失败了")
        return False

def install_dependencies():
    """安装依赖库"""
    dependencies = [
        'pdfplumber',
        'pymupdf',
        'pypdf'
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ 安装 {dep} 成功")
        except subprocess.CalledProcessError:
            print(f"❌ 安装 {dep} 失败")

if __name__ == "__main__":
    # 测试处理器
    processor = AlternativePDFProcessor()
    available = processor.check_dependencies()
    print(f"可用的处理方法: {available}")
    
    if not available:
        print("安装依赖库...")
        install_dependencies() 