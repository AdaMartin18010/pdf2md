#!/usr/bin/env python3
"""
高级PDF处理器
集成多种PDF转换库，实现智能自动切换
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessorType(Enum):
    """PDF处理器类型"""
    MINERU = "mineru"
    PYPDF = "pypdf"
    PDFPLUMBER = "pdfplumber"
    PYMUPDF = "pymupdf"
    PYTESSERACT = "pytesseract"
    OCRMYPDF = "ocrmypdf"

@dataclass
class ProcessorResult:
    """处理器结果"""
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None
    processor: Optional[str] = None
    duration: float = 0.0
    page_count: int = 0

class AdvancedPDFProcessor:
    """高级PDF处理器"""
    
    def __init__(self):
        self.processors = {}
        self._init_processors()
    
    def _init_processors(self):
        """初始化所有可用的处理器"""
        # 1. PyPDF处理器
        try:
            from pypdf import PdfReader
            self.processors[ProcessorType.PYPDF] = self._pypdf_processor
            logger.info("✅ PyPDF处理器已加载")
        except ImportError:
            logger.warning("❌ PyPDF处理器不可用")
        
        # 2. PDFPlumber处理器
        try:
            import pdfplumber
            self.processors[ProcessorType.PDFPLUMBER] = self._pdfplumber_processor
            logger.info("✅ PDFPlumber处理器已加载")
        except ImportError:
            logger.warning("❌ PDFPlumber处理器不可用")
        
        # 3. PyMuPDF处理器
        try:
            import pymupdf
            self.processors[ProcessorType.PYMUPDF] = self._pymupdf_processor
            logger.info("✅ PyMuPDF处理器已加载")
        except ImportError:
            logger.warning("❌ PyMuPDF处理器不可用")
        
        # 4. OCR处理器 (需要安装pytesseract)
        try:
            import pytesseract
            from PIL import Image
            self.processors[ProcessorType.PYTESSERACT] = self._pytesseract_processor
            logger.info("✅ PyTesseract OCR处理器已加载")
        except ImportError:
            logger.warning("❌ PyTesseract OCR处理器不可用")
        
        # 5. OCRmyPDF处理器
        try:
            import ocrmypdf
            self.processors[ProcessorType.OCRMYPDF] = self._ocrmypdf_processor
            logger.info("✅ OCRmyPDF处理器已加载")
        except ImportError:
            logger.warning("❌ OCRmyPDF处理器不可用")
    
    def _pypdf_processor(self, pdf_path: Path) -> ProcessorResult:
        """PyPDF处理器"""
        start_time = time.time()
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            
            text_parts = []
            successful_pages = 0
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"# 第 {page_num} 页\n\n{text.strip()}\n")
                        successful_pages += 1
                except Exception as e:
                    logger.debug(f"PyPDF: 第 {page_num} 页提取失败: {e}")
                    continue
            
            duration = time.time() - start_time
            return ProcessorResult(
                success=len(text_parts) > 0,
                text="\n".join(text_parts) if text_parts else None,
                processor="pypdf",
                duration=duration,
                page_count=page_count
            )
        except Exception as e:
            duration = time.time() - start_time
            return ProcessorResult(
                success=False,
                error=str(e),
                processor="pypdf",
                duration=duration
            )
    
    def _pdfplumber_processor(self, pdf_path: Path) -> ProcessorResult:
        """PDFPlumber处理器"""
        start_time = time.time()
        try:
            import pdfplumber
            
            text_parts = []
            successful_pages = 0
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            text_parts.append(f"# 第 {page_num} 页\n\n{text.strip()}\n")
                            successful_pages += 1
                    except Exception as e:
                        logger.debug(f"PDFPlumber: 第 {page_num} 页提取失败: {e}")
                        continue
            
            duration = time.time() - start_time
            return ProcessorResult(
                success=len(text_parts) > 0,
                text="\n".join(text_parts) if text_parts else None,
                processor="pdfplumber",
                duration=duration,
                page_count=len(pdf.pages)
            )
        except Exception as e:
            duration = time.time() - start_time
            return ProcessorResult(
                success=False,
                error=str(e),
                processor="pdfplumber",
                duration=duration
            )
    
    def _pymupdf_processor(self, pdf_path: Path) -> ProcessorResult:
        """PyMuPDF处理器"""
        start_time = time.time()
        try:
            import pymupdf
            
            text_parts = []
            successful_pages = 0
            
            doc = pymupdf.open(pdf_path)
            page_count = len(doc)
            
            for page_num in range(page_count):
                try:
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text and text.strip():
                        text_parts.append(f"# 第 {page_num + 1} 页\n\n{text.strip()}\n")
                        successful_pages += 1
                except Exception as e:
                    logger.debug(f"PyMuPDF: 第 {page_num + 1} 页提取失败: {e}")
                    continue
            
            doc.close()
            duration = time.time() - start_time
            return ProcessorResult(
                success=len(text_parts) > 0,
                text="\n".join(text_parts) if text_parts else None,
                processor="pymupdf",
                duration=duration,
                page_count=page_count
            )
        except Exception as e:
            duration = time.time() - start_time
            return ProcessorResult(
                success=False,
                error=str(e),
                processor="pymupdf",
                duration=duration
            )
    
    def _pytesseract_processor(self, pdf_path: Path) -> ProcessorResult:
        """PyTesseract OCR处理器"""
        start_time = time.time()
        try:
            import pytesseract
            from PIL import Image
            import fitz  # PyMuPDF for PDF to image conversion
            
            text_parts = []
            successful_pages = 0
            
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            
            for page_num in range(page_count):
                try:
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # OCR处理
                    text = pytesseract.image_to_string(img, lang='eng+chi_sim')
                    if text and text.strip():
                        text_parts.append(f"# 第 {page_num + 1} 页 (OCR)\n\n{text.strip()}\n")
                        successful_pages += 1
                except Exception as e:
                    logger.debug(f"PyTesseract: 第 {page_num + 1} 页OCR失败: {e}")
                    continue
            
            doc.close()
            duration = time.time() - start_time
            return ProcessorResult(
                success=len(text_parts) > 0,
                text="\n".join(text_parts) if text_parts else None,
                processor="pytesseract",
                duration=duration,
                page_count=page_count
            )
        except Exception as e:
            duration = time.time() - start_time
            return ProcessorResult(
                success=False,
                error=str(e),
                processor="pytesseract",
                duration=duration
            )
    
    def _ocrmypdf_processor(self, pdf_path: Path) -> ProcessorResult:
        """OCRmyPDF处理器"""
        start_time = time.time()
        try:
            import ocrmypdf
            import tempfile
            
            # 创建临时输出文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                output_path = Path(tmp_file.name)
            
            try:
                # 使用OCRmyPDF处理
                ocrmypdf.ocr(
                    pdf_path,
                    output_path,
                    language=['eng', 'chi_sim'],
                    output_type='pdf',
                    force_ocr=True
                )
                
                # 从OCR处理后的PDF提取文本
                result = self._pypdf_processor(output_path)
                result.processor = "ocrmypdf"
                result.duration = time.time() - start_time
                
                return result
            finally:
                # 清理临时文件
                if output_path.exists():
                    output_path.unlink()
                    
        except Exception as e:
            duration = time.time() - start_time
            return ProcessorResult(
                success=False,
                error=str(e),
                processor="ocrmypdf",
                duration=duration
            )
    
    def process_pdf(self, pdf_path: Path, output_path: Path) -> ProcessorResult:
        """处理PDF文件，自动选择最佳处理器"""
        logger.info(f"开始处理PDF文件: {pdf_path}")
        
        if not pdf_path.exists():
            return ProcessorResult(
                success=False,
                error="PDF文件不存在"
            )
        
        # 按优先级尝试不同的处理器
        processor_order = [
            ProcessorType.PYPDF,
            ProcessorType.PDFPLUMBER,
            ProcessorType.PYMUPDF,
            ProcessorType.OCRMYPDF,
            ProcessorType.PYTESSERACT
        ]
        
        for processor_type in processor_order:
            if processor_type not in self.processors:
                logger.warning(f"处理器 {processor_type.value} 不可用")
                continue
            
            logger.info(f"尝试使用 {processor_type.value} 处理器")
            result = self.processors[processor_type](pdf_path)
            
            if result.success and result.text:
                # 保存为markdown文件
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {pdf_path.stem}\n\n")
                        f.write(result.text)
                    
                    logger.info(f"✅ 使用 {processor_type.value} 成功处理PDF文件")
                    return result
                    
                except Exception as e:
                    logger.error(f"保存文件失败: {e}")
                    result.success = False
                    result.error = f"保存失败: {e}"
                    continue
            else:
                logger.warning(f"❌ {processor_type.value} 处理失败: {result.error}")
        
        # 所有处理器都失败了
        return ProcessorResult(
            success=False,
            error="所有处理器都失败了"
        )

def install_dependencies():
    """安装所有依赖库"""
    dependencies = [
        'pdfplumber',
        'pymupdf',
        'pytesseract',
        'ocrmypdf',
        'Pillow'
    ]
    
    import subprocess
    import sys
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ 安装 {dep} 成功")
        except subprocess.CalledProcessError:
            print(f"❌ 安装 {dep} 失败")

if __name__ == "__main__":
    # 测试高级处理器
    processor = AdvancedPDFProcessor()
    
    print(f"可用的处理器: {list(processor.processors.keys())}")
    
    if not processor.processors:
        print("安装依赖库...")
        install_dependencies()
    else:
        pdf_dir = Path("pdfs")
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if pdf_files:
            test_pdf = pdf_files[0]
            output_file = Path("markdown") / f"{test_pdf.stem}_advanced.md"
            
            print(f"测试处理: {test_pdf}")
            result = processor.process_pdf(test_pdf, output_file)
            
            if result.success:
                print(f"✅ 处理成功，输出文件: {output_file}")
                print(f"使用处理器: {result.processor}")
                print(f"处理时间: {result.duration:.2f}秒")
                print(f"页面数: {result.page_count}")
            else:
                print(f"❌ 处理失败: {result.error}")
        else:
            print("没有找到PDF文件进行测试") 