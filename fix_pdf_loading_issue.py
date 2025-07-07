#!/usr/bin/env python3
"""
修复PDF加载问题
解决"Failed to load document (PDFium: Data format error)"错误
"""

import os
import sys
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFLoadingFixer:
    """PDF加载问题修复器"""
    
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        self.skipped_files = []
    
    def check_pdf_file(self, pdf_path: Path) -> Dict[str, Any]:
        """检查PDF文件状态"""
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'exists': False,
            'size': 0,
            'is_valid_pdf': False,
            'can_be_fixed': False,
            'error_type': None,
            'error_message': None
        }
        
        try:
            # 检查文件是否存在
            if not pdf_path.exists():
                result['error_type'] = 'FILE_NOT_FOUND'
                result['error_message'] = '文件不存在'
                return result
            
            result['exists'] = True
            result['size'] = pdf_path.stat().st_size
            
            # 检查文件大小
            if result['size'] == 0:
                result['error_type'] = 'EMPTY_FILE'
                result['error_message'] = '文件为空'
                return result
            
            if result['size'] < 1024:  # 小于1KB
                result['error_type'] = 'FILE_TOO_SMALL'
                result['error_message'] = f'文件过小 ({result["size"]} bytes)'
                return result
            
            # 检查PDF文件头
            with open(pdf_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF'):
                    result['error_type'] = 'INVALID_HEADER'
                    result['error_message'] = '不是有效的PDF文件'
                    return result
            
            # 尝试使用不同的PDF库加载
            result['is_valid_pdf'] = self._test_pdf_libraries(pdf_path)
            
            if result['is_valid_pdf']:
                result['can_be_fixed'] = True
            else:
                result['error_type'] = 'LOAD_ERROR'
                result['error_message'] = 'PDF库无法加载文件'
            
        except Exception as e:
            result['error_type'] = 'UNKNOWN_ERROR'
            result['error_message'] = str(e)
        
        return result
    
    def _test_pdf_libraries(self, pdf_path: Path) -> bool:
        """测试不同的PDF库"""
        libraries = [
            ('pypdf', self._test_pypdf),
            ('pypdfium2', self._test_pypdfium2),
            ('pdfplumber', self._test_pdfplumber),
            ('pymupdf', self._test_pymupdf)
        ]
        
        for lib_name, test_func in libraries:
            try:
                if test_func(pdf_path):
                    logger.info(f"✅ {pdf_path.name} 可以被 {lib_name} 正常加载")
                    return True
            except ImportError:
                logger.debug(f"库 {lib_name} 未安装")
            except Exception as e:
                logger.debug(f"{lib_name} 加载失败: {e}")
        
        return False
    
    def _test_pypdf(self, pdf_path: Path) -> bool:
        """测试pypdf库"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            return len(reader.pages) > 0
        except Exception:
            return False
    
    def _test_pypdfium2(self, pdf_path: Path) -> bool:
        """测试pypdfium2库"""
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(str(pdf_path))
            return len(pdf) > 0
        except Exception:
            return False
    
    def _test_pdfplumber(self, pdf_path: Path) -> bool:
        """测试pdfplumber库"""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages) > 0
        except Exception:
            return False
    
    def _test_pymupdf(self, pdf_path: Path) -> bool:
        """测试pymupdf库"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count > 0
        except Exception:
            return False
    
    def fix_pdf_loading_issue(self, input_dir: Path, output_dir: Path = None) -> Dict[str, Any]:
        """修复PDF加载问题"""
        logger.info(f"🔧 开始修复PDF加载问题...")
        logger.info(f"📁 输入目录: {input_dir}")
        
        if output_dir is None:
            output_dir = input_dir / "fixed_pdfs"
        
        output_dir.mkdir(exist_ok=True)
        logger.info(f"📁 输出目录: {output_dir}")
        
        # 查找所有PDF文件
        pdf_files = list(input_dir.rglob("*.pdf"))
        logger.info(f"📄 找到 {len(pdf_files)} 个PDF文件")
        
        results = {
            'total_files': len(pdf_files),
            'fixed_files': [],
            'failed_files': [],
            'skipped_files': [],
            'summary': {}
        }
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"🔍 检查文件 {i}/{len(pdf_files)}: {pdf_file.name}")
            
            # 检查文件状态
            file_status = self.check_pdf_file(pdf_file)
            
            if file_status['is_valid_pdf']:
                logger.info(f"✅ {pdf_file.name} 文件正常，跳过")
                results['skipped_files'].append(file_status)
                self.skipped_files.append(pdf_file)
                continue
            
            # 尝试修复文件
            fix_result = self._try_fix_pdf_file(pdf_file, output_dir)
            
            if fix_result['success']:
                results['fixed_files'].append(fix_result)
                self.fixed_files.append(pdf_file)
                logger.info(f"✅ {pdf_file.name} 修复成功")
            else:
                results['failed_files'].append(fix_result)
                self.failed_files.append(pdf_file)
                logger.warning(f"❌ {pdf_file.name} 修复失败: {fix_result['error']}")
        
        # 生成摘要
        results['summary'] = {
            'total': len(pdf_files),
            'fixed': len(results['fixed_files']),
            'failed': len(results['failed_files']),
            'skipped': len(results['skipped_files']),
            'fix_rate': len(results['fixed_files']) / len(pdf_files) * 100 if pdf_files else 0
        }
        
        return results
    
    def _try_fix_pdf_file(self, pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
        """尝试修复单个PDF文件"""
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'success': False,
            'error': None,
            'fixed_path': None,
            'method': None
        }
        
        # 方法1: 尝试使用pypdf重新保存
        try:
            fixed_path = output_dir / f"{pdf_path.stem}_fixed.pdf"
            if self._fix_with_pypdf(pdf_path, fixed_path):
                result['success'] = True
                result['fixed_path'] = str(fixed_path)
                result['method'] = 'pypdf_rebuild'
                return result
        except Exception as e:
            logger.debug(f"pypdf修复失败: {e}")
        
        # 方法2: 尝试使用pymupdf重新保存
        try:
            fixed_path = output_dir / f"{pdf_path.stem}_fixed.pdf"
            if self._fix_with_pymupdf(pdf_path, fixed_path):
                result['success'] = True
                result['fixed_path'] = str(fixed_path)
                result['method'] = 'pymupdf_rebuild'
                return result
        except Exception as e:
            logger.debug(f"pymupdf修复失败: {e}")
        
        # 方法3: 尝试修复PDF头
        try:
            fixed_path = output_dir / f"{pdf_path.stem}_fixed.pdf"
            if self._fix_pdf_header(pdf_path, fixed_path):
                result['success'] = True
                result['fixed_path'] = str(fixed_path)
                result['method'] = 'header_fix'
                return result
        except Exception as e:
            logger.debug(f"PDF头修复失败: {e}")
        
        result['error'] = '所有修复方法都失败了'
        return result
    
    def _fix_with_pypdf(self, input_path: Path, output_path: Path) -> bool:
        """使用pypdf修复PDF"""
        try:
            from pypdf import PdfReader, PdfWriter
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 保存修复后的文件
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path.exists() and output_path.stat().st_size > 0
        except Exception:
            return False
    
    def _fix_with_pymupdf(self, input_path: Path, output_path: Path) -> bool:
        """使用pymupdf修复PDF"""
        try:
            import fitz
            
            doc = fitz.open(input_path)
            doc.save(output_path)
            doc.close()
            
            return output_path.exists() and output_path.stat().st_size > 0
        except Exception:
            return False
    
    def _fix_pdf_header(self, input_path: Path, output_path: Path) -> bool:
        """修复PDF文件头"""
        try:
            with open(input_path, 'rb') as f:
                content = f.read()
            
            # 查找PDF头
            pdf_header = b'%PDF'
            if pdf_header in content:
                start_pos = content.find(pdf_header)
                fixed_content = content[start_pos:]
                
                with open(output_path, 'wb') as f:
                    f.write(fixed_content)
                
                return output_path.exists() and output_path.stat().st_size > 0
            
            return False
        except Exception:
            return False
    
    def generate_report(self, results: Dict[str, Any], output_file: Path = None):
        """生成修复报告"""
        summary = results['summary']
        
        report = f"""
# PDF加载问题修复报告

## 📊 统计摘要
- 总文件数: {summary['total']}
- 修复成功: {summary['fixed']}
- 修复失败: {summary['failed']}
- 跳过文件: {summary['skipped']}
- 修复成功率: {summary['fix_rate']:.1f}%

## ✅ 修复成功的文件 ({len(results['fixed_files'])})
"""
        
        for file_info in results['fixed_files']:
            report += f"- {file_info['file_name']} (方法: {file_info['method']})\n"
            report += f"  输出路径: {file_info['fixed_path']}\n\n"
        
        report += f"## ❌ 修复失败的文件 ({len(results['failed_files'])})\n"
        
        for file_info in results['failed_files']:
            report += f"- {file_info['file_name']}\n"
            report += f"  错误: {file_info['error']}\n\n"
        
        report += f"## ⏭️ 跳过的文件 ({len(results['skipped_files'])})\n"
        
        for file_info in results['skipped_files']:
            report += f"- {file_info['file_name']} (文件正常)\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 报告已保存: {output_file}")
        else:
            print(report)
        
        return report

def main():
    """主函数"""
    print("🔧 PDF加载问题修复工具")
    print("=" * 50)
    
    # 获取输入目录
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        input_dir = Path("./test_pdfs")
    
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        print("💡 请提供包含PDF文件的目录路径")
        return
    
    # 创建修复器
    fixer = PDFLoadingFixer()
    
    # 执行修复
    results = fixer.fix_pdf_loading_issue(input_dir)
    
    # 生成报告
    report_file = Path("pdf_fix_report.txt")
    fixer.generate_report(results, report_file)
    
    # 显示结果
    summary = results['summary']
    print(f"\n📊 修复结果:")
    print(f"  总文件数: {summary['total']}")
    print(f"  修复成功: {summary['fixed']}")
    print(f"  修复失败: {summary['failed']}")
    print(f"  跳过文件: {summary['skipped']}")
    print(f"  修复成功率: {summary['fix_rate']:.1f}%")
    
    if summary['fixed'] > 0:
        print(f"\n✅ 修复成功的文件已保存到: {input_dir}/fixed_pdfs/")
        print("💡 请使用修复后的PDF文件进行转换")

if __name__ == "__main__":
    main() 