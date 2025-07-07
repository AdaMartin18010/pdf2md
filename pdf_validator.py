#!/usr/bin/env python3
"""
PDF文件验证和修复工具
检测和处理有问题的PDF文件
"""

import os
import sys
from pathlib import Path
import shutil
import logging
from typing import List, Dict, Tuple, Optional
import traceback

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFValidator:
    """PDF文件验证器"""
    
    def __init__(self):
        self.problem_files = []
        self.valid_files = []
        self.fixed_files = []
    
    def validate_pdf_file(self, pdf_path: Path) -> Dict[str, any]:
        """验证单个PDF文件"""
        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'is_valid': False,
            'file_size': 0,
            'error_type': None,
            'error_message': None,
            'can_fix': False,
            'suggestions': []
        }
        
        try:
            # 检查文件是否存在
            if not pdf_path.exists():
                result['error_type'] = 'FILE_NOT_FOUND'
                result['error_message'] = '文件不存在'
                result['suggestions'].append('检查文件路径是否正确')
                return result
            
            # 检查文件大小
            file_size = pdf_path.stat().st_size
            result['file_size'] = file_size
            
            if file_size == 0:
                result['error_type'] = 'EMPTY_FILE'
                result['error_message'] = '文件为空'
                result['suggestions'].append('文件可能损坏，需要重新下载')
                return result
            
            if file_size < 1024:  # 小于1KB
                result['error_type'] = 'FILE_TOO_SMALL'
                result['error_message'] = f'文件过小 ({file_size} bytes)'
                result['suggestions'].append('文件可能不完整或损坏')
                return result
            
            # 检查文件头
            with open(pdf_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF'):
                    result['error_type'] = 'INVALID_HEADER'
                    result['error_message'] = '不是有效的PDF文件'
                    result['suggestions'].append('文件可能不是PDF格式')
                    return result
            
            # 尝试使用pypdfium2加载
            try:
                import pypdfium2 as pdfium
                pdf = pdfium.PdfDocument(str(pdf_path))
                page_count = len(pdf)
                
                if page_count == 0:
                    result['error_type'] = 'NO_PAGES'
                    result['error_message'] = 'PDF文件没有页面'
                    result['suggestions'].append('PDF文件可能损坏')
                    return result
                
                # 尝试访问第一页
                try:
                    page = pdf[0]
                    result['is_valid'] = True
                    result['page_count'] = page_count
                    logger.info(f"✅ 文件有效: {pdf_path.name} ({page_count} 页)")
                    
                except Exception as e:
                    result['error_type'] = 'PAGE_ACCESS_ERROR'
                    result['error_message'] = f'无法访问页面: {str(e)}'
                    result['suggestions'].append('PDF文件可能损坏')
                    
            except Exception as e:
                result['error_type'] = 'LOAD_ERROR'
                result['error_message'] = f'无法加载PDF: {str(e)}'
                result['suggestions'].append('PDF文件可能损坏或格式不支持')
            
        except Exception as e:
            result['error_type'] = 'UNKNOWN_ERROR'
            result['error_message'] = f'未知错误: {str(e)}'
            result['suggestions'].append('检查文件权限和磁盘空间')
        
        return result
    
    def validate_directory(self, directory: Path, recursive: bool = True) -> Dict[str, any]:
        """验证目录中的所有PDF文件"""
        logger.info(f"🔍 开始验证目录: {directory}")
        
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))
        
        logger.info(f"📁 找到 {len(pdf_files)} 个PDF文件")
        
        results = {
            'total_files': len(pdf_files),
            'valid_files': [],
            'problem_files': [],
            'summary': {}
        }
        
        for pdf_file in pdf_files:
            result = self.validate_pdf_file(pdf_file)
            
            if result['is_valid']:
                results['valid_files'].append(result)
                self.valid_files.append(pdf_file)
            else:
                results['problem_files'].append(result)
                self.problem_files.append(pdf_file)
        
        # 生成摘要
        results['summary'] = {
            'total': len(pdf_files),
            'valid': len(results['valid_files']),
            'problem': len(results['problem_files']),
            'valid_rate': len(results['valid_files']) / len(pdf_files) * 100 if pdf_files else 0
        }
        
        return results
    
    def fix_path_issues(self, pdf_path: Path) -> Optional[Path]:
        """修复文件路径问题"""
        try:
            # 检查路径长度
            if len(str(pdf_path)) > 260:  # Windows路径长度限制
                logger.warning(f"⚠️ 路径过长: {pdf_path.name}")
                return None
            
            # 检查特殊字符
            invalid_chars = '<>:"|?*'
            if any(char in pdf_path.name for char in invalid_chars):
                logger.warning(f"⚠️ 文件名包含特殊字符: {pdf_path.name}")
                return None
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"❌ 路径修复失败: {e}")
            return None
    
    def create_backup(self, pdf_path: Path, backup_dir: Path) -> bool:
        """创建文件备份"""
        try:
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"backup_{pdf_path.name}"
            shutil.copy2(pdf_path, backup_path)
            logger.info(f"✅ 备份创建: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            return False
    
    def generate_report(self, results: Dict[str, any], output_file: Path = None):
        """生成验证报告"""
        summary = results['summary']
        
        report = f"""
# PDF文件验证报告

## 📊 统计摘要
- 总文件数: {summary['total']}
- 有效文件: {summary['valid']}
- 问题文件: {summary['problem']}
- 有效率: {summary['valid_rate']:.1f}%

## ✅ 有效文件 ({len(results['valid_files'])})
"""
        
        for file_info in results['valid_files']:
            report += f"- {file_info['file_name']} ({file_info.get('page_count', 'N/A')} 页)\n"
        
        report += f"\n## ❌ 问题文件 ({len(results['problem_files'])})\n"
        
        for file_info in results['problem_files']:
            report += f"- {file_info['file_name']}\n"
            report += f"  - 错误类型: {file_info['error_type']}\n"
            report += f"  - 错误信息: {file_info['error_message']}\n"
            report += f"  - 建议: {', '.join(file_info['suggestions'])}\n\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 报告已保存: {output_file}")
        else:
            print(report)
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF文件验证工具")
    parser.add_argument("input", help="输入目录或PDF文件")
    parser.add_argument("-o", "--output", help="输出报告文件")
    parser.add_argument("--no-recursive", action="store_true", help="不递归查找")
    parser.add_argument("--backup", help="备份目录")
    
    args = parser.parse_args()
    
    validator = PDFValidator()
    input_path = Path(args.input)
    
    if input_path.is_file():
        # 验证单个文件
        result = validator.validate_pdf_file(input_path)
        results = {
            'total_files': 1,
            'valid_files': [result] if result['is_valid'] else [],
            'problem_files': [] if result['is_valid'] else [result],
            'summary': {
                'total': 1,
                'valid': 1 if result['is_valid'] else 0,
                'problem': 0 if result['is_valid'] else 1,
                'valid_rate': 100 if result['is_valid'] else 0
            }
        }
    elif input_path.is_dir():
        # 验证目录
        results = validator.validate_directory(input_path, not args.no_recursive)
    else:
        print(f"❌ 输入路径不存在: {input_path}")
        return 1
    
    # 生成报告
    output_file = Path(args.output) if args.output else None
    validator.generate_report(results, output_file)
    
    # 创建备份（如果需要）
    if args.backup and validator.problem_files:
        backup_dir = Path(args.backup)
        for pdf_file in validator.problem_files:
            validator.create_backup(pdf_file, backup_dir)
    
    # 返回状态码
    if results['summary']['problem'] > 0:
        print(f"\n⚠️ 发现 {results['summary']['problem']} 个问题文件")
        return 1
    else:
        print(f"\n✅ 所有文件验证通过")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 