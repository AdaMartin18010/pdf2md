#!/usr/bin/env python3
"""
修复批量转换问题
处理PDF文件错误和路径问题
"""

import os
import sys
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_pdf_file(pdf_path: Path) -> bool:
    """检查PDF文件是否有效"""
    try:
        # 检查文件是否存在
        if not pdf_path.exists():
            logger.error(f"❌ 文件不存在: {pdf_path}")
            return False
        
        # 检查文件大小
        file_size = pdf_path.stat().st_size
        if file_size == 0:
            logger.error(f"❌ 文件为空: {pdf_path}")
            return False
        
        # 检查文件头
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF'):
                logger.error(f"❌ 不是有效的PDF文件: {pdf_path}")
                return False
        
        # 检查路径长度
        if len(str(pdf_path)) > 260:
            logger.error(f"❌ 路径过长: {pdf_path}")
            return False
        
        logger.info(f"✅ 文件有效: {pdf_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 检查文件失败: {pdf_path} - {e}")
        return False

def filter_valid_pdfs(input_dir: Path) -> list:
    """过滤出有效的PDF文件"""
    valid_files = []
    problem_files = []
    
    logger.info(f"🔍 检查目录: {input_dir}")
    
    # 递归查找所有PDF文件
    pdf_files = list(input_dir.rglob("*.pdf"))
    logger.info(f"📁 找到 {len(pdf_files)} 个PDF文件")
    
    for pdf_file in pdf_files:
        if check_pdf_file(pdf_file):
            valid_files.append(pdf_file)
        else:
            problem_files.append(pdf_file)
    
    logger.info(f"✅ 有效文件: {len(valid_files)}")
    logger.info(f"❌ 问题文件: {len(problem_files)}")
    
    # 显示问题文件
    if problem_files:
        logger.warning("⚠️ 问题文件列表:")
        for file in problem_files:
            logger.warning(f"  - {file}")
    
    return valid_files

def run_safe_batch_conversion(input_dir: str, output_dir: str):
    """运行安全的批量转换"""
    try:
        from stable_mineru_converter import MineruConverter
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            logger.error(f"❌ 输入目录不存在: {input_dir}")
            return False
        
        # 过滤有效文件
        valid_files = filter_valid_pdfs(input_path)
        
        if not valid_files:
            logger.error("❌ 没有找到有效的PDF文件")
            return False
        
        # 创建输出目录
        output_path.mkdir(exist_ok=True)
        
        # 创建转换器
        converter = MineruConverter()
        
        # 转换有效文件
        success_count = 0
        error_count = 0
        
        for pdf_file in valid_files:
            try:
                logger.info(f"🔄 转换: {pdf_file.name}")
                
                def progress_callback(progress: int, message: str):
                    logger.info(f"[{progress}%] {message}")
                
                result = converter.convert_single_pdf(
                    pdf_file,
                    output_path,
                    lang="ch",
                    backend="pipeline",
                    method="auto",
                    enable_formula=True,
                    enable_table=True,
                    progress_callback=progress_callback
                )
                
                if result['success']:
                    logger.info(f"✅ 转换成功: {pdf_file.name}")
                    success_count += 1
                else:
                    logger.error(f"❌ 转换失败: {pdf_file.name} - {result['error']}")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"❌ 转换异常: {pdf_file.name} - {e}")
                error_count += 1
        
        # 输出结果
        logger.info(f"\n📊 转换结果:")
        logger.info(f"✅ 成功: {success_count}")
        logger.info(f"❌ 失败: {error_count}")
        logger.info(f"📁 输出目录: {output_path}")
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ 批量转换失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("使用方法: python fix_batch_conversion.py <输入目录> <输出目录>")
        print("示例: python fix_batch_conversion.py pdfs/ output/")
        return 1
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    logger.info("🚀 开始安全的批量转换")
    
    success = run_safe_batch_conversion(input_dir, output_dir)
    
    if success:
        logger.info("🎉 批量转换完成")
        return 0
    else:
        logger.error("❌ 批量转换失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 