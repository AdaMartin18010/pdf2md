"""
配置管理测试
"""

import tempfile
import yaml
from pathlib import Path
from pdf2md.config import Config


class TestConfig:
    """配置管理测试类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = Config()
        assert config.get('defaults.use_gpu') is True
        assert config.get('defaults.workers') == 1
        assert config.get('paths.input') == "./pdfs"
        assert config.get('paths.output') == "./markdown"
    
    def test_custom_config_path(self):
        """测试自定义配置文件路径"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            custom_config = {
                "defaults": {
                    "use_gpu": True,
                    "workers": 4
                },
                "paths": {
                    "input": "/custom/input",
                    "output": "/custom/output"
                }
            }
            yaml.dump(custom_config, f)
            config_path = Path(f.name)
        
        try:
            config = Config(config_path)
            assert config.get('defaults.use_gpu') is True
            assert config.get('defaults.workers') == 4
            assert config.get('paths.input') == "/custom/input"
            assert config.get('paths.output') == "/custom/output"
        finally:
            config_path.unlink()
    
    def test_merge_config(self):
        """测试配置合并"""
        config = Config()
        
        # 测试深度合并
        user_config = {
            "defaults": {
                "use_gpu": True
            },
            "shutdown": {
                "enabled": True,
                "delay_minutes": 5
            }
        }
        
        merged = config._merge_config(config.config, user_config)
        assert merged['defaults']['use_gpu'] is True
        assert merged['defaults']['workers'] == 1  # 保持默认值
        assert merged['shutdown']['enabled'] is True
        assert merged['shutdown']['delay_minutes'] == 5
    
    def test_get_nested_key(self):
        """测试获取嵌套配置项"""
        config = Config()
        
        # 测试存在的键
        assert config.get('defaults.use_gpu') is True
        assert config.get('paths.input') == "./pdfs"
        
        # 测试不存在的键
        assert config.get('nonexistent.key', "default") == "default"
        assert config.get('defaults.nonexistent', 123) == 123
    
    def test_set_config(self):
        """测试设置配置项"""
        config = Config()
        
        # 设置新值
        config.set('defaults.use_gpu', True)
        assert config.get('defaults.use_gpu') is True
        
        # 设置嵌套值
        config.set('custom.new_key', "test_value")
        assert config.get('custom.new_key') == "test_value"
    
    def test_reload_config(self):
        """测试重新加载配置"""
        config = Config()
        original_value = config.get('defaults.use_gpu')
        
        # 修改配置
        config.set('defaults.use_gpu', True)
        assert config.get('defaults.use_gpu') is True
        
        # 重新加载
        config.reload()
        assert config.get('defaults.use_gpu') == original_value 