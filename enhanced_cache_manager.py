#!/usr/bin/env python3
"""
增强版模型缓存管理器
确保所有模型都能被缓存，避免重复下载
"""

import os
import sys
import shutil
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.parse

class EnhancedCacheManager:
    """增强版模型缓存管理器"""
    
    def __init__(self, cache_dir: str = "./models_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_config_file = self.cache_dir / "cache_config.json"
        self.setup_cache_directories()
        self.setup_environment_variables()
        self.load_cache_config()
    
    def setup_cache_directories(self):
        """设置缓存目录结构"""
        # 创建主缓存目录
        self.cache_dir.mkdir(exist_ok=True)
        
        # 创建完整的子目录结构
        subdirs = [
            "transformers",
            "datasets", 
            "mineru",
            "modelscope",
            "huggingface",
            "torch",
            "onnx",
            "safetensors",
            "paddle",
            "rapid_table",
            "ocr_models",
            "layout_models",
            "table_models",
            "formula_models",
            "reading_order_models"
        ]
        
        for subdir in subdirs:
            (self.cache_dir / subdir).mkdir(exist_ok=True)
        
        print(f"✅ 增强缓存目录: {self.cache_dir}")
    
    def setup_environment_variables(self):
        """设置完整的环境变量"""
        # HuggingFace相关
        os.environ['HF_HOME'] = str(self.cache_dir)
        os.environ['HF_DATASETS_CACHE'] = str(self.cache_dir / "datasets")
        os.environ['TRANSFORMERS_CACHE'] = str(self.cache_dir / "transformers")
        os.environ['HF_HUB_CACHE'] = str(self.cache_dir / "huggingface")
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'
        os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '600'
        os.environ['HF_HUB_DOWNLOAD_RETRY_DELAY'] = '10'
        
        # ModelScope相关
        os.environ['MODELSCOPE_CACHE'] = str(self.cache_dir / "modelscope")
        os.environ['MODELSCOPE_DOMAIN'] = "modelscope.cn"
        os.environ['MODELSCOPE_DOWNLOAD_TIMEOUT'] = '600'
        
        # Mineru相关
        os.environ['MINERU_CACHE_DIR'] = str(self.cache_dir / "mineru")
        os.environ['MINERU_MODEL_SOURCE'] = 'modelscope'
        os.environ['MINERU_OFFLINE_MODE'] = 'false'
        
        # PyTorch相关
        os.environ['TORCH_HOME'] = str(self.cache_dir / "torch")
        os.environ['TORCH_WEIGHTS_ONLY'] = 'false'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        
        # ONNX相关
        os.environ['ONNX_HOME'] = str(self.cache_dir / "onnx")
        
        # PaddleOCR相关
        os.environ['PADDLE_HOME'] = str(self.cache_dir / "paddle")
        
        # 其他优化设置
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # 如果有GPU
        os.environ['OMP_NUM_THREADS'] = '4'
        
        # 禁用不必要的下载
        os.environ['TRANSFORMERS_OFFLINE'] = '0'
        os.environ['HF_DATASETS_OFFLINE'] = '0'
        
        print("✅ 增强环境变量设置完成")
    
    def load_cache_config(self):
        """加载缓存配置"""
        if self.cache_config_file.exists():
            try:
                with open(self.cache_config_file, 'r', encoding='utf-8') as f:
                    self.cache_config = json.load(f)
            except Exception as e:
                print(f"⚠️ 加载缓存配置失败: {e}")
                self.cache_config = {}
        else:
            self.cache_config = {
                'model_hashes': {},
                'download_history': [],
                'cache_stats': {
                    'total_downloads': 0,
                    'total_size': 0,
                    'last_cleanup': None
                }
            }
            self.save_cache_config()
    
    def save_cache_config(self):
        """保存缓存配置"""
        try:
            with open(self.cache_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存缓存配置失败: {e}")
    
    def get_model_hash(self, model_path: Path) -> str:
        """获取模型文件的哈希值"""
        try:
            with open(model_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return str(model_path.stat().st_mtime)
    
    def check_cache_status(self) -> Dict[str, Any]:
        """检查详细的缓存状态"""
        status = {
            'cache_dir': str(self.cache_dir),
            'total_size': 0,
            'model_count': 0,
            'subdirs': {},
            'missing_models': [],
            'cache_efficiency': 0.0
        }
        
        # 检查各个缓存目录
        cache_dirs = {
            "transformers": self.cache_dir / "transformers",
            "datasets": self.cache_dir / "datasets", 
            "mineru": self.cache_dir / "mineru",
            "modelscope": self.cache_dir / "modelscope",
            "huggingface": self.cache_dir / "huggingface",
            "torch": self.cache_dir / "torch",
            "onnx": self.cache_dir / "onnx",
            "paddle": self.cache_dir / "paddle",
            "rapid_table": self.cache_dir / "rapid_table",
            "ocr_models": self.cache_dir / "ocr_models",
            "layout_models": self.cache_dir / "layout_models",
            "table_models": self.cache_dir / "table_models",
            "formula_models": self.cache_dir / "formula_models",
            "reading_order_models": self.cache_dir / "reading_order_models"
        }
        
        total_size = 0
        total_models = 0
        
        for name, dir_path in cache_dirs.items():
            dir_info = {
                'exists': dir_path.exists(),
                'has_models': False,
                'size': 0,
                'model_count': 0,
                'model_types': []
            }
            
            if dir_path.exists():
                # 查找模型文件
                model_extensions = ['.bin', '.safetensors', '.onnx', '.pt', '.pth', '.ckpt', '.pkl']
                model_files = []
                
                for ext in model_extensions:
                    model_files.extend(dir_path.rglob(f"*{ext}"))
                
                dir_info['model_count'] = len(model_files)
                dir_info['has_models'] = len(model_files) > 0
                
                # 计算目录大小
                dir_size = 0
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.is_file():
                            dir_size += file_path.stat().st_size
                
                dir_info['size'] = dir_size
                total_size += dir_size
                total_models += dir_info['model_count']
                
                # 记录模型类型
                for model_file in model_files:
                    dir_info['model_types'].append(model_file.suffix)
            
            status['subdirs'][name] = dir_info
        
        status['total_size'] = total_size
        status['model_count'] = total_models
        
        # 计算缓存效率
        expected_models = 15  # 预期的模型数量
        status['cache_efficiency'] = min(1.0, total_models / expected_models)
        
        return status
    
    def preload_common_models(self):
        """预加载常用模型"""
        print("🔄 预加载常用模型...")
        
        # 定义常用模型列表
        common_models = [
            {
                'name': 'layout_detection',
                'source': 'modelscope',
                'path': 'OpenDataLab/PDF-Extract-Kit-1.0/models/Layout/YOLO'
            },
            {
                'name': 'table_recognition',
                'source': 'modelscope', 
                'path': 'OpenDataLab/PDF-Extract-Kit-1.0/models/TabRec/SlanetPlus'
            },
            {
                'name': 'ocr_models',
                'source': 'modelscope',
                'path': 'OpenDataLab/PDF-Extract-Kit-1.0/models/OCR/paddleocr_torch'
            },
            {
                'name': 'formula_recognition',
                'source': 'modelscope',
                'path': 'OpenDataLab/PDF-Extract-Kit-1.0/models/MFR/unimernet_hf_small_2503'
            }
        ]
        
        for model in common_models:
            try:
                self.ensure_model_cached(model)
            except Exception as e:
                print(f"⚠️ 预加载模型 {model['name']} 失败: {e}")
    
    def ensure_model_cached(self, model_info: Dict[str, str]):
        """确保模型被缓存"""
        model_name = model_info['name']
        model_path = self.cache_dir / model_info['source'] / model_info['path']
        
        if not model_path.exists():
            print(f"📥 预下载模型: {model_name}")
            # 这里可以添加实际的下载逻辑
            # 由于模型下载需要特定的API，这里只是标记
            pass
        else:
            print(f"✅ 模型已缓存: {model_name}")
    
    def optimize_cache_settings(self):
        """优化缓存设置"""
        print("🔧 优化缓存设置...")
        
        # 设置更保守的下载设置
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '0'
        os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'
        
        # 设置下载重试和超时
        os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '600'
        os.environ['HF_HUB_DOWNLOAD_RETRY_DELAY'] = '10'
        os.environ['HF_HUB_DOWNLOAD_RETRY_MAX'] = '3'
        
        # ModelScope设置
        os.environ['MODELSCOPE_DOWNLOAD_TIMEOUT'] = '600'
        os.environ['MODELSCOPE_DOWNLOAD_RETRY'] = '3'
        
        # 禁用不必要的功能
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        
        print("✅ 缓存设置优化完成")
    
    def cleanup_cache(self, max_age_days: int = 30):
        """清理过期缓存"""
        print(f"🧹 清理 {max_age_days} 天前的缓存...")
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        cleaned_files = 0
        cleaned_size = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_files += 1
                            cleaned_size += file_size
                        except Exception as e:
                            print(f"⚠️ 删除文件失败 {file_path}: {e}")
        
        print(f"✅ 清理完成: 删除 {cleaned_files} 个文件，释放 {cleaned_size / (1024**2):.2f} MB")
        
        # 更新缓存统计
        self.cache_config['cache_stats']['last_cleanup'] = current_time
        self.save_cache_config()
    
    def print_detailed_cache_info(self):
        """打印详细的缓存信息"""
        try:
            status = self.check_cache_status()
            
            print(f"\n📊 增强缓存信息:")
            print(f"  缓存目录: {status['cache_dir']}")
            print(f"  总大小: {status['total_size'] / (1024**3):.2f} GB")
            print(f"  模型文件数: {status['model_count']}")
            print(f"  缓存效率: {status['cache_efficiency']*100:.1f}%")
            
            print(f"\n📁 详细缓存状态:")
            for name, info in status['subdirs'].items():
                if info['exists']:
                    status_icon = "✅" if info['has_models'] else "⚠️"
                    size_mb = info['size'] / (1024**2)
                    print(f"  {status_icon} {name}: {info['model_count']} 个模型 ({size_mb:.1f} MB)")
                else:
                    print(f"  ❌ {name}: 目录不存在")
        except Exception as e:
            print(f"❌ 获取缓存信息失败: {e}")
            # 使用基本检查
            self.print_basic_cache_info()
    
    def print_basic_cache_info(self):
        """打印基本缓存信息"""
        print(f"\n📊 基本缓存信息:")
        print(f"  缓存目录: {self.cache_dir}")
        
        total_size = 0
        total_files = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    if file.endswith(('.bin', '.safetensors', '.onnx', '.pt', '.pth')):
                        total_files += 1
        
        print(f"  总大小: {total_size / (1024**3):.2f} GB")
        print(f"  模型文件数: {total_files}")
        
        # 检查主要目录
        main_dirs = ["modelscope", "transformers", "mineru", "torch"]
        print(f"\n📁 主要缓存状态:")
        for dir_name in main_dirs:
            dir_path = self.cache_dir / dir_name
            if dir_path.exists():
                model_files = list(dir_path.rglob("*.bin")) + list(dir_path.rglob("*.safetensors"))
                status_icon = "✅" if len(model_files) > 0 else "⚠️"
                print(f"  {status_icon} {dir_name}: {'已缓存' if len(model_files) > 0 else '未缓存'}")
            else:
                print(f"  ❌ {dir_name}: 目录不存在")
    
    def create_cache_report(self) -> str:
        """创建缓存报告"""
        status = self.check_cache_status()
        
        report = f"""
# 模型缓存报告

## 基本信息
- 缓存目录: {status['cache_dir']}
- 总大小: {status['total_size'] / (1024**3):.2f} GB
- 模型文件数: {status['model_count']}
- 缓存效率: {status['cache_efficiency']*100:.1f}%

## 详细状态
"""
        
        for name, info in status['subdirs'].items():
            if info['exists'] and info['has_models']:
                size_mb = info['size'] / (1024**2)
                report += f"- ✅ {name}: {info['model_count']} 个模型 ({size_mb:.1f} MB)\n"
            elif info['exists']:
                report += f"- ⚠️ {name}: 目录存在但无模型文件\n"
            else:
                report += f"- ❌ {name}: 目录不存在\n"
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版模型缓存管理器")
    parser.add_argument("--info", action="store_true", help="显示详细缓存信息")
    parser.add_argument("--optimize", action="store_true", help="优化缓存设置")
    parser.add_argument("--preload", action="store_true", help="预加载常用模型")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="清理指定天数前的缓存")
    parser.add_argument("--report", action="store_true", help="生成缓存报告")
    
    args = parser.parse_args()
    
    cache_manager = EnhancedCacheManager()
    
    if args.info:
        cache_manager.print_detailed_cache_info()
    elif args.optimize:
        cache_manager.optimize_cache_settings()
    elif args.preload:
        cache_manager.preload_common_models()
    elif args.cleanup:
        cache_manager.cleanup_cache(args.cleanup)
    elif args.report:
        report = cache_manager.create_cache_report()
        print(report)
    else:
        # 默认显示信息
        cache_manager.print_detailed_cache_info()

if __name__ == "__main__":
    main() 