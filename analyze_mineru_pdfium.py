#!/usr/bin/env python3
"""
深入分析mineru的PDFium调用细节
调试"Failed to load document (PDFium: Data format error)"错误
"""

import os
import sys
import traceback
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MineruPDFiumAnalyzer:
    """Mineru PDFium调用分析器"""
    
    def __init__(self):
        self.analysis_results = []
        self.error_details = []
    
    def analyze_pdfium_call(self, pdf_path: Path) -> Dict[str, Any]:
        """分析单个PDF文件的PDFium调用"""
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'file_size': 0,
            'pdfium_success': False,
            'pypdf_success': False,
            'error_details': [],
            'call_stack': [],
            'pdfium_version': None,
            'mineru_version': None
        }
        
        try:
            # 获取文件信息
            result['file_size'] = pdf_path.stat().st_size
            
            # 测试1: 直接使用pypdfium2
            logger.info(f"🔍 分析文件: {pdf_path.name}")
            logger.info(f"📏 文件大小: {result['file_size']} bytes")
            
            # 测试PDFium版本
            try:
                import pypdfium2 as pdfium
                result['pdfium_version'] = pdfium.__version__
                logger.info(f"📦 PDFium版本: {result['pdfium_version']}")
            except Exception as e:
                logger.error(f"无法获取PDFium版本: {e}")
            
            # 测试直接PDFium调用
            pdfium_result = self._test_direct_pdfium(pdf_path)
            result['pdfium_success'] = pdfium_result['success']
            result['error_details'].extend(pdfium_result['errors'])
            
            # 测试pypdf调用
            pypdf_result = self._test_pypdf(pdf_path)
            result['pypdf_success'] = pypdf_result['success']
            result['error_details'].extend(pypdf_result['errors'])
            
            # 测试mineru的PDFium调用
            mineru_result = self._test_mineru_pdfium(pdf_path)
            result['error_details'].extend(mineru_result['errors'])
            result['call_stack'] = mineru_result['call_stack']
            
            # 测试文件头分析
            header_result = self._analyze_pdf_header(pdf_path)
            result['error_details'].extend(header_result['errors'])
            
        except Exception as e:
            result['error_details'].append(f"分析过程异常: {str(e)}")
            logger.error(f"分析过程异常: {e}")
            traceback.print_exc()
        
        return result
    
    def _test_direct_pdfium(self, pdf_path: Path) -> Dict[str, Any]:
        """测试直接PDFium调用"""
        result = {'success': False, 'errors': []}
        
        try:
            logger.info("🔧 测试直接PDFium调用...")
            import pypdfium2 as pdfium
            
            # 方法1: 使用文件路径
            try:
                pdf = pdfium.PdfDocument(str(pdf_path))
                page_count = len(pdf)
                logger.info(f"✅ 直接PDFium成功: {page_count} 页")
                result['success'] = True
                return result
            except Exception as e:
                error_msg = f"直接PDFium调用失败: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
            
            # 方法2: 使用字节数据
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                pdf = pdfium.PdfDocument(pdf_bytes)
                page_count = len(pdf)
                logger.info(f"✅ PDFium字节调用成功: {page_count} 页")
                result['success'] = True
                return result
            except Exception as e:
                error_msg = f"PDFium字节调用失败: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
            
        except ImportError as e:
            error_msg = f"PDFium库未安装: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"PDFium测试异常: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _test_pypdf(self, pdf_path: Path) -> Dict[str, Any]:
        """测试pypdf调用"""
        result = {'success': False, 'errors': []}
        
        try:
            logger.info("🔧 测试pypdf调用...")
            from pypdf import PdfReader
            
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            logger.info(f"✅ pypdf成功: {page_count} 页")
            result['success'] = True
            
        except Exception as e:
            error_msg = f"pypdf调用失败: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _test_mineru_pdfium(self, pdf_path: Path) -> Dict[str, Any]:
        """测试mineru的PDFium调用"""
        result = {'success': False, 'errors': [], 'call_stack': []}
        
        try:
            logger.info("🔧 测试mineru PDFium调用...")
            
            # 导入mineru相关模块
            from mineru.cli.common import read_fn
            from mineru.utils.pdf_classify import classify
            
            # 测试read_fn函数
            try:
                pdf_bytes = read_fn(pdf_path)
                logger.info(f"✅ mineru.read_fn成功: {len(pdf_bytes)} bytes")
            except Exception as e:
                error_msg = f"mineru.read_fn失败: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                return result
            
            # 测试pdf_classify.classify函数
            try:
                logger.info("🔧 测试pdf_classify.classify...")
                pdf_type = classify(pdf_bytes)
                logger.info(f"✅ pdf_classify.classify成功: {pdf_type}")
                result['success'] = True
            except Exception as e:
                error_msg = f"pdf_classify.classify失败: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                
                # 获取详细调用栈
                result['call_stack'] = traceback.format_exc().split('\n')
            
        except ImportError as e:
            error_msg = f"mineru模块导入失败: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"mineru PDFium测试异常: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _analyze_pdf_header(self, pdf_path: Path) -> Dict[str, Any]:
        """分析PDF文件头"""
        result = {'errors': []}
        
        try:
            logger.info("🔧 分析PDF文件头...")
            
            with open(pdf_path, 'rb') as f:
                # 读取前1KB
                header_data = f.read(1024)
            
            # 查找PDF头
            pdf_header_pos = header_data.find(b'%PDF')
            if pdf_header_pos == -1:
                result['errors'].append("未找到PDF文件头")
                logger.error("❌ 未找到PDF文件头")
            else:
                logger.info(f"✅ 找到PDF头位置: {pdf_header_pos}")
                
                # 分析PDF版本
                version_line = header_data[pdf_header_pos:pdf_header_pos+20].decode('ascii', errors='ignore')
                logger.info(f"📄 PDF版本行: {version_line.strip()}")
            
            # 查找EOF标记
            eof_pos = header_data.rfind(b'%%EOF')
            if eof_pos == -1:
                result['errors'].append("未找到PDF EOF标记")
                logger.warning("⚠️ 未找到PDF EOF标记")
            else:
                logger.info(f"✅ 找到EOF位置: {eof_pos}")
            
            # 检查文件完整性
            file_size = pdf_path.stat().st_size
            if file_size < 100:
                result['errors'].append("文件过小，可能不完整")
                logger.error("❌ 文件过小，可能不完整")
            
        except Exception as e:
            error_msg = f"PDF头分析失败: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def analyze_multiple_files(self, pdf_files: List[Path]) -> Dict[str, Any]:
        """分析多个PDF文件"""
        logger.info(f"🔍 开始分析 {len(pdf_files)} 个PDF文件...")
        
        results = {
            'total_files': len(pdf_files),
            'pdfium_success_count': 0,
            'pypdf_success_count': 0,
            'both_success_count': 0,
            'both_failed_count': 0,
            'detailed_results': [],
            'summary': {}
        }
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"📄 分析文件 {i}/{len(pdf_files)}: {pdf_file.name}")
            
            result = self.analyze_pdfium_call(pdf_file)
            results['detailed_results'].append(result)
            
            # 统计成功/失败
            if result['pdfium_success']:
                results['pdfium_success_count'] += 1
            if result['pypdf_success']:
                results['pypdf_success_count'] += 1
            if result['pdfium_success'] and result['pypdf_success']:
                results['both_success_count'] += 1
            if not result['pdfium_success'] and not result['pypdf_success']:
                results['both_failed_count'] += 1
        
        # 生成摘要
        results['summary'] = {
            'total': len(pdf_files),
            'pdfium_success_rate': results['pdfium_success_count'] / len(pdf_files) * 100,
            'pypdf_success_rate': results['pypdf_success_count'] / len(pdf_files) * 100,
            'both_success_rate': results['both_success_count'] / len(pdf_files) * 100,
            'both_failed_rate': results['both_failed_count'] / len(pdf_files) * 100
        }
        
        return results
    
    def generate_detailed_report(self, results: Dict[str, Any], output_file: Path = None):
        """生成详细分析报告"""
        summary = results['summary']
        
        report = f"""
# Mineru PDFium调用详细分析报告

## 📊 统计摘要
- 总文件数: {summary['total']}
- PDFium成功率: {summary['pdfium_success_rate']:.1f}%
- pypdf成功率: {summary['pypdf_success_rate']:.1f}%
- 两者都成功: {summary['both_success_rate']:.1f}%
- 两者都失败: {summary['both_failed_rate']:.1f}%

## 🔍 详细分析结果
"""
        
        for result in results['detailed_results']:
            report += f"\n### {result['file_name']}\n"
            report += f"- 文件大小: {result['file_size']} bytes\n"
            report += f"- PDFium成功: {'✅' if result['pdfium_success'] else '❌'}\n"
            report += f"- pypdf成功: {'✅' if result['pypdf_success'] else '❌'}\n"
            
            if result['error_details']:
                report += f"- 错误详情:\n"
                for error in result['error_details']:
                    report += f"  - {error}\n"
            
            if result['call_stack']:
                report += f"- 调用栈:\n"
                for line in result['call_stack'][:10]:  # 只显示前10行
                    report += f"  {line}\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 详细报告已保存: {output_file}")
        else:
            print(report)
        
        return report

def main():
    """主函数"""
    print("🔍 Mineru PDFium调用详细分析工具")
    print("=" * 50)
    
    # 获取PDF文件列表
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        input_dir = Path("./test_pdfs")
    
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 查找PDF文件
    pdf_files = list(input_dir.rglob("*.pdf"))
    if not pdf_files:
        print(f"❌ 在 {input_dir} 中没有找到PDF文件")
        return
    
    print(f"📄 找到 {len(pdf_files)} 个PDF文件")
    
    # 创建分析器
    analyzer = MineruPDFiumAnalyzer()
    
    # 执行分析
    results = analyzer.analyze_multiple_files(pdf_files)
    
    # 生成报告
    report_file = Path("mineru_pdfium_analysis.txt")
    analyzer.generate_detailed_report(results, report_file)
    
    # 显示摘要
    summary = results['summary']
    print(f"\n📊 分析结果摘要:")
    print(f"  总文件数: {summary['total']}")
    print(f"  PDFium成功率: {summary['pdfium_success_rate']:.1f}%")
    print(f"  pypdf成功率: {summary['pypdf_success_rate']:.1f}%")
    print(f"  两者都成功: {summary['both_success_rate']:.1f}%")
    print(f"  两者都失败: {summary['both_failed_rate']:.1f}%")
    
    # 显示关键发现
    if summary['pdfium_success_rate'] < summary['pypdf_success_rate']:
        print(f"\n🔍 关键发现:")
        print(f"  PDFium成功率 ({summary['pdfium_success_rate']:.1f}%) 低于 pypdf成功率 ({summary['pypdf_success_rate']:.1f}%)")
        print(f"  这表明PDFium对某些PDF格式的兼容性不如pypdf")
        print(f"  建议使用pypdf作为PDFium的备选方案")

if __name__ == "__main__":
    main() 