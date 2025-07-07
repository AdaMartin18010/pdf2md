#!/usr/bin/env python3
"""
模型缓存管理器
确保模型只下载一次，避免重复下载
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

class ModelCacheManager:
    """模型缓存管理器"""
    
    def __init__(self, cache_dir: str = "./models_cache"):
        self.cache_dir = Path(cache_dir)
        self.setup_cache_directories()
        self.setup_environment_variables()
    
    def setup_cache_directories(self):
        """设置缓存目录结构"""
        # 创建主缓存目录
        self.cache_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        subdirs = [
            "transformers",
            "datasets", 
            "mineru",
            "modelscope",
            "huggingface",
            "torch",
            "onnx",
            "safetensors"
        ]
        
        for subdir in subdirs:
            (self.cache_dir / subdir).mkdir(exist_ok=True)
        
        print(f"✅ 模型缓存目录: {self.cache_dir}")
    
    def setup_environment_variables(self):
        """设置环境变量"""
        # HuggingFace相关
        os.environ['HF_HOME'] = str(self.cache_dir)
        os.environ['HF_DATASETS_CACHE'] = str(self.cache_dir / "datasets")
        os.environ['TRANSFORMERS_CACHE'] = str(self.cache_dir / "transformers")
        os.environ['HF_HUB_CACHE'] = str(self.cache_dir / "huggingface")
        
        # ModelScope相关
        os.environ['MODELSCOPE_CACHE'] = str(self.cache_dir / "modelscope")
        os.environ['MODELSCOPE_DOMAIN'] = "modelscope.cn"
        
        # Mineru相关
        os.environ['MINERU_CACHE_DIR'] = str(self.cache_dir / "mineru")
        os.environ['MINERU_MODEL_SOURCE'] = 'modelscope'
        
        # PyTorch相关
        os.environ['TORCH_HOME'] = str(self.cache_dir / "torch")
        os.environ['TORCH_WEIGHTS_ONLY'] = 'false'
        
        # ONNX相关
        os.environ['ONNX_HOME'] = str(self.cache_dir / "onnx")
        
        # 其他优化设置
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        
        print("✅ 环境变量设置完成")
    
    def check_cache_status(self) -> Dict[str, bool]:
        """检查缓存状态"""
        status = {}
        
        # 检查各个缓存目录
        cache_dirs = {
            "transformers": self.cache_dir / "transformers",
            "datasets": self.cache_dir / "datasets", 
            "mineru": self.cache_dir / "mineru",
            "modelscope": self.cache_dir / "modelscope",
            "huggingface": self.cache_dir / "huggingface",
            "torch": self.cache_dir / "torch"
        }
        
        for name, dir_path in cache_dirs.items():
            if dir_path.exists():
                # 检查是否有模型文件
                model_files = list(dir_path.rglob("*.bin")) + list(dir_path.rglob("*.safetensors")) + list(dir_path.rglob("*.onnx"))
                status[name] = len(model_files) > 0
            else:
                status[name] = False
        
        return status
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        info = {
            "cache_dir": str(self.cache_dir),
            "total_size": 0,
            "model_count": 0,
            "status": self.check_cache_status()
        }
        
        # 计算总大小
        total_size = 0
        model_count = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    if file.endswith(('.bin', '.safetensors', '.onnx', '.pt', '.pth')):
                        model_count += 1
        
        info["total_size"] = total_size
        info["model_count"] = model_count
        
        return info
    
    def print_cache_info(self):
        """打印缓存信息"""
        info = self.get_cache_info()
        status = info["status"]
        
        print(f"\n📊 模型缓存信息:")
        print(f"  缓存目录: {info['cache_dir']}")
        print(f"  总大小: {info['total_size'] / (1024**3):.2f} GB")
        print(f"  模型文件数: {info['model_count']}")
        
        print(f"\n📁 缓存状态:")
        for name, has_models in status.items():
            status_icon = "✅" if has_models else "❌"
            print(f"  {status_icon} {name}: {'已缓存' if has_models else '未缓存'}")
    
    def clear_cache(self, confirm: bool = False):
        """清空缓存"""
        if not confirm:
            print("⚠️ 这将删除所有缓存的模型文件")
            response = input("确认清空缓存? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ 取消清空缓存")
                return False
        
        try:
            import shutil
            shutil.rmtree(self.cache_dir)
            self.setup_cache_directories()
            print("✅ 缓存已清空")
            return True
        except Exception as e:
            print(f"❌ 清空缓存失败: {e}")
            return False
    
    def optimize_for_first_run(self):
        """优化首次运行"""
        print("🔧 优化首次运行设置...")
        
        # 设置更保守的下载设置
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '0'
        os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'
        
        # 设置下载重试
        os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '300'
        os.environ['HF_HUB_DOWNLOAD_RETRY_DELAY'] = '5'
        
        print("✅ 首次运行优化完成")
        print("💡 首次运行将下载必要的模型，请耐心等待...")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="模型缓存管理器")
    parser.add_argument("--info", action="store_true", help="显示缓存信息")
    parser.add_argument("--clear", action="store_true", help="清空缓存")
    parser.add_argument("--optimize", action="store_true", help="优化首次运行")
    
    args = parser.parse_args()
    
    cache_manager = ModelCacheManager()
    
    if args.info:
        cache_manager.print_cache_info()
    elif args.clear:
        cache_manager.clear_cache()
    elif args.optimize:
        cache_manager.optimize_for_first_run()
    else:
        # 默认显示信息
        cache_manager.print_cache_info()

if __name__ == "__main__":
    main() 