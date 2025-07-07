"""
配置文件管理模块
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config.yaml")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "defaults": {
                "use_gpu": False,
                "workers": 1,
                "verbose": False,
                "estimate_time": True,
                "log_conversions": True
            },
            "paths": {
                "input": "./pdfs",
                "output": "./markdown",
                "log_dir": "./logs"
            },
            "mineru_options": {
                "use_gpu": False
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "file": "conversion.log"
            },
            "time_estimation": {
                "enabled": True,
                "avg_time_per_mb": 2.0,  # 每MB预估秒数
                "min_time_per_file": 1.0,  # 每个文件最少秒数
                "max_time_per_file": 60.0  # 每个文件最多秒数
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                # 深度合并配置
                return self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"警告：加载配置文件失败，使用默认配置: {e}")
                return default_config
        else:
            # 创建默认配置文件
            self._save_config(default_config)
            return default_config
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """深度合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"警告：保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def reload(self) -> None:
        """重新加载配置"""
        self.config = self._load_config()


# 全局配置实例
config = Config() 