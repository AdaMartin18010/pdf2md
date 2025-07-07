#!/usr/bin/env python3
"""
稳定的Mineru PDF转换器
确保转换功能完全正常，为UI提供可靠的基础
"""

import os
import sys
import time
import shutil
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List, Tuple, Union
import argparse
from loguru import logger

# 设置环境变量
os.environ['MINERU_MODEL_SOURCE'] = 'modelscope'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['TORCH_WEIGHTS_ONLY'] = 'false'

from pdf2md.mineru_wrapper import convert_pdf_to_markdown

class MineruConverter:
    """稳定的Mineru转换器类"""
    
    def __init__(self, output_dir: Union[str, Path]):
        """
        初始化 MineruConverter
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.setup_environment()
        self.conversion_status = {
            'is_running': False,
            'current_file': None,
            'total_files': 0,
            'processed_files': 0,
            'success_count': 0,
            'failed_files': []
        }
        self._stop_conversion = False
    
    def setup_environment(self):
        """设置环境"""
        # 使用增强版缓存管理器
        try:
            from enhanced_cache_manager import EnhancedCacheManager
            self.cache_manager = EnhancedCacheManager()
            print("✅ 增强版模型缓存管理器已初始化")
        except ImportError:
            try:
                from model_cache_manager import ModelCacheManager
                self.cache_manager = ModelCacheManager()
                print("✅ 基础模型缓存管理器已初始化")
            except ImportError:
                print("⚠️ 无法导入缓存管理器，使用默认设置")
                self.setup_basic_cache()
        
        # 应用兼容性修复
        try:
            from global_dictconfig_fix import apply_global_dictconfig_fix
            apply_global_dictconfig_fix()
        except Exception as e:
            print(f"⚠️ 兼容性修复失败: {e}")
    
    def setup_basic_cache(self):
        """基本缓存设置（备用方案）"""
        cache_dir = Path("./models_cache")
        cache_dir.mkdir(exist_ok=True)
        
        os.environ['HF_HOME'] = str(cache_dir)
        os.environ['TRANSFORMERS_CACHE'] = str(cache_dir / "transformers")
        os.environ['HF_DATASETS_CACHE'] = str(cache_dir / "datasets")
        os.environ['MINERU_CACHE_DIR'] = str(cache_dir / "mineru")
        os.environ['MODELSCOPE_CACHE'] = str(cache_dir / "modelscope")
        
        for subdir in ["transformers", "datasets", "mineru", "modelscope"]:
            (cache_dir / subdir).mkdir(exist_ok=True)
    
    def check_cache_status(self):
        """检查缓存状态"""
        if hasattr(self, 'cache_manager'):
            return self.cache_manager.check_cache_status()
        else:
            # 基本检查
            cache_dir = Path("./models_cache")
            status = {}
            for subdir in ["transformers", "datasets", "mineru", "modelscope"]:
                subdir_path = cache_dir / subdir
                if subdir_path.exists():
                    model_files = list(subdir_path.rglob("*.bin")) + list(subdir_path.rglob("*.safetensors"))
                    status[subdir] = len(model_files) > 0
                else:
                    status[subdir] = False
            return status
    
    def preload_models(self):
        """预加载模型"""
        if hasattr(self, 'cache_manager'):
            if hasattr(self.cache_manager, 'preload_common_models'):
                self.cache_manager.preload_common_models()
            else:
                print("⚠️ 当前缓存管理器不支持预加载功能")
        else:
            print("⚠️ 缓存管理器未初始化")

    def convert_single_pdf(
        self,
        input_file: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        strict_mode: bool = True
    ) -> Tuple[bool, str, Optional[List[str]]]:
        """
        转换单个 PDF 文件
        
        Args:
            input_file: 输入 PDF 文件路径
            output_dir: 输出目录路径（可选，默认使用实例的输出目录）
            strict_mode: 是否严格模式（只使用 mineru，失败时不使用备选方案）
            
        Returns:
            Tuple[bool, str, Optional[List[str]]]: (是否成功, 消息, 生成的文件列表)
        """
        try:
            # 使用指定的输出目录或默认输出目录
            target_dir = Path(output_dir) if output_dir else self.output_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 调用转换函数
            return convert_pdf_to_markdown(input_file, target_dir, strict_mode)
            
        except Exception as e:
            logger.error(f"转换 {input_file} 时出错: {str(e)}")
            return False, f"转换失败: {str(e)}", None
    
    def convert_batch(
        self,
        pdf_files: List[Path],
        output_dir: Path,
        strict_mode: bool = True
    ) -> List[Tuple[bool, str, Optional[List[str]]]]:
        """
        批量转换 PDF 文件
        
        Args:
            pdf_files: PDF 文件路径列表
            output_dir: 输出目录路径
            strict_mode: 是否严格模式
            
        Returns:
            List[Tuple[bool, str, Optional[List[str]]]]: 转换结果列表
        """
        results = []
        self.conversion_status['is_running'] = True
        self.conversion_status['total_files'] = len(pdf_files)
        self.conversion_status['processed_files'] = 0
        self.conversion_status['success_count'] = 0
        self.conversion_status['failed_files'] = []
        
        for pdf_file in pdf_files:
            if not self.conversion_status['is_running']:
                break
                
            self.conversion_status['current_file'] = pdf_file.name
            result = self.convert_single_pdf(pdf_file, output_dir, strict_mode)
            results.append(result)
            
            if result[0]:
                self.conversion_status['success_count'] += 1
            else:
                self.conversion_status['failed_files'].append(pdf_file.name)
                
            self.conversion_status['processed_files'] += 1
            
        self.conversion_status['is_running'] = False
        return results
    
    def stop_conversion(self):
        """停止转换过程"""
        self.conversion_status['is_running'] = False
    
    def get_status(self) -> Dict:
        """获取当前转换状态"""
        return self.conversion_status.copy()

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="稳定的Mineru PDF转换器")
    parser.add_argument("input", nargs='?', help="输入PDF文件或目录")
    parser.add_argument("-o", "--output", default="./output", help="输出目录")
    parser.add_argument("-l", "--lang", default="ch", help="语言代码")
    parser.add_argument("-b", "--backend", default="pipeline", help="后端类型")
    parser.add_argument("-m", "--method", default="auto", help="解析方法")
    parser.add_argument("--no-formula", action="store_true", help="禁用公式解析")
    parser.add_argument("--no-table", action="store_true", help="禁用表格解析")
    parser.add_argument("--cache-info", action="store_true", help="显示缓存信息")
    
    args = parser.parse_args()
    
    print("🚀 稳定的Mineru PDF转换器")
    print("="*50)
    
    # 创建转换器
    converter = MineruConverter(args.output)
    
    # 显示缓存信息
    if args.cache_info:
        cache_status = converter.check_cache_status()
        print("\n📊 缓存状态:")
        for name, has_models in cache_status.items():
            status_icon = "✅" if has_models else "❌"
            print(f"  {status_icon} {name}: {'已缓存' if has_models else '未缓存'}")
        return
    
    # 如果没有提供输入路径，显示帮助
    if not args.input:
        parser.print_help()
        return
    
    # 准备路径
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    def progress_callback(progress: int, message: str):
        print(f"[{progress}%] {message}")
    
    if input_path.is_file():
        # 转换单个文件
        result = converter.convert_single_pdf(
            input_path,
            output_dir,
            args.lang,
            args.backend,
            args.method,
            enable_formula=not args.no_formula,
            enable_table=not args.no_table,
            progress_callback=progress_callback
        )
        
        if result[0]:
            print(f"✅ 转换成功!")
            print(f"📄 输出文件: {result[1]}")
            print(f"🖼️ 图片目录: {result[2]}")
            print(f"📊 图片数量: {len(result[2]) if result[2] else '未知'}")
        else:
            print(f"❌ 转换失败: {result[1]}")
            sys.exit(1)
    
    elif input_path.is_dir():
        # 批量转换
        pdf_files = list(input_path.rglob("*.pdf"))
        result = converter.convert_batch(
            pdf_files, output_dir,
            args.lang, args.backend, args.method,
            progress_callback=progress_callback
        )
        
        if result['success']:
            print(f"\n✅ 批量转换完成!")
            print(f"📊 总文件数: {result['total_files']}")
            print(f"✅ 成功: {result['success_count']}")
            print(f"❌ 失败: {result['error_count']}")
        else:
            print(f"❌ 批量转换失败: {result['error']}")
            sys.exit(1)
    
    else:
        print(f"❌ 输入路径不存在: {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    main() 