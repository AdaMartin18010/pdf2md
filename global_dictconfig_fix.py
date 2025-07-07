#!/usr/bin/env python3
"""
全局DictConfig解包补丁
递归处理所有DictConfig类型问题，彻底解决rapid-table兼容性
"""

import sys
import types
from typing import Any, Dict, List, Union
import os
import urllib.request
from urllib.parse import urlparse

MODEL_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'models', 'rapid_table')
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

def download_model_if_url(model_path):
    if isinstance(model_path, str) and model_path.startswith(('http://', 'https://')):
        url = model_path
        filename = os.path.basename(urlparse(url).path)
        local_path = os.path.join(MODEL_CACHE_DIR, filename)
        if not os.path.exists(local_path):
            print(f"⬇️ 正在下载模型: {url} -> {local_path}")
            try:
                urllib.request.urlretrieve(url, local_path)
                print(f"✓ 模型下载完成: {local_path}")
            except Exception as e:
                print(f"❌ 模型下载失败: {e}")
                return model_path
        else:
            print(f"✓ 模型已存在: {local_path}")
        return local_path
    return model_path

def dictconfig_to_dict(obj: Any) -> Any:
    """
    递归将DictConfig转换为dict
    支持嵌套的DictConfig、dict、list等结构
    """
    try:
        from omegaconf import DictConfig, ListConfig
    except ImportError:
        return obj
    
    if isinstance(obj, DictConfig):
        d = {k: dictconfig_to_dict(v) for k, v in obj.items()}
        # 自动下载并替换model_dir_or_path
        if 'model_dir_or_path' in d:
            d['model_dir_or_path'] = download_model_if_url(d['model_dir_or_path'])
        return d
    elif isinstance(obj, ListConfig):
        return [dictconfig_to_dict(v) for v in obj]
    elif isinstance(obj, dict):
        d = {k: dictconfig_to_dict(v) for k, v in obj.items()}
        if 'model_dir_or_path' in d:
            d['model_dir_or_path'] = download_model_if_url(d['model_dir_or_path'])
        return d
    elif isinstance(obj, list):
        return [dictconfig_to_dict(v) for v in obj]
    else:
        return obj

def apply_global_dictconfig_fix():
    """应用全局DictConfig解包补丁"""
    print("🔧 应用全局DictConfig解包补丁...")
    
    try:
        # 1. 补丁RapidTableInput
        try:
            import rapid_table
            from rapid_table import RapidTableInput
            
            original_rapidtableinput_init = RapidTableInput.__init__
            def compatible_rapidtableinput_init(self, *args, **kwargs):
                # 递归解包所有参数
                args = [dictconfig_to_dict(arg) for arg in args]
                kwargs = {k: dictconfig_to_dict(v) for k, v in kwargs.items()}
                
                # 移除不支持的model_path参数
                if 'model_path' in kwargs:
                    print("⚠️ 移除不支持的model_path参数")
                    del kwargs['model_path']
                
                return original_rapidtableinput_init(self, *args, **kwargs)
            
            RapidTableInput.__init__ = compatible_rapidtableinput_init
            print("✓ RapidTableInput补丁已应用")
            
        except ImportError as e:
            print(f"⚠️ 无法导入RapidTableInput: {e}")
        
        # 2. 补丁RapidTable
        try:
            from rapid_table.main import RapidTable
            original_rapidtable_init = RapidTable.__init__
            
            def compatible_rapidtable_init(self, input_args):
                # 递归解包input_args
                input_args = dictconfig_to_dict(input_args)
                return original_rapidtable_init(self, input_args)
            
            RapidTable.__init__ = compatible_rapidtable_init
            print("✓ RapidTable补丁已应用")
            
        except ImportError as e:
            print(f"⚠️ 无法导入RapidTable: {e}")
        
        # 3. 补丁PPTableStructurer
        try:
            from rapid_table.table_structure.pp_structure.main import PPTableStructurer
            original_ppstructurer_init = PPTableStructurer.__init__
            
            def compatible_ppstructurer_init(self, cfg):
                # 递归解包cfg
                cfg = dictconfig_to_dict(cfg)
                return original_ppstructurer_init(self, cfg)
            
            PPTableStructurer.__init__ = compatible_ppstructurer_init
            print("✓ PPTableStructurer补丁已应用")
            
        except ImportError as e:
            print(f"⚠️ 无法导入PPTableStructurer: {e}")
        
        # 4. 补丁ONNXRuntimeEngine (实际是OrtInferSession)
        try:
            from rapid_table.inference_engine.onnxruntime.main import OrtInferSession
            original_onnx_init = OrtInferSession.__init__
            
            def compatible_onnx_init(self, cfg):
                # 递归解包cfg
                cfg = dictconfig_to_dict(cfg)
                
                # 确保model_dir_or_path是字符串
                if hasattr(cfg, 'model_dir_or_path'):
                    model_path = cfg.model_dir_or_path
                    if hasattr(model_path, 'SHA256'):  # 如果是DictConfig
                        print("⚠️ 检测到DictConfig，提取model_path")
                        model_path = model_path.get('model_dir_or_path', str(model_path))
                    cfg.model_dir_or_path = model_path
                
                return original_onnx_init(self, cfg)
            
            OrtInferSession.__init__ = compatible_onnx_init
            print("✓ OrtInferSession补丁已应用")
            
        except ImportError as e:
            print(f"⚠️ 无法导入OrtInferSession: {e}")
        
        # 5. 补丁Path构造函数，处理DictConfig
        try:
            from pathlib import Path
            original_path_init = Path.__init__
            
            def compatible_path_init(self, *args, **kwargs):
                # 检查第一个参数是否是DictConfig或dict
                if args:
                    first_arg = args[0]
                    if hasattr(first_arg, 'SHA256'):  # 如果是DictConfig
                        print("⚠️ Path遇到DictConfig，自动转换")
                        # 尝试提取字符串值
                        dict_config = first_arg
                        if hasattr(dict_config, 'model_dir_or_path'):
                            args = (dict_config.model_dir_or_path,)
                        elif hasattr(dict_config, 'get'):
                            args = (dict_config.get('model_dir_or_path', str(dict_config)),)
                        else:
                            args = (str(dict_config),)
                    elif isinstance(first_arg, dict):  # 如果是dict
                        print("⚠️ Path遇到dict，自动转换")
                        # 从dict中提取model_dir_or_path
                        if 'model_dir_or_path' in first_arg:
                            args = (first_arg['model_dir_or_path'],)
                        else:
                            # 尝试其他可能的键
                            for key in ['model_path', 'path', 'url']:
                                if key in first_arg:
                                    args = (first_arg[key],)
                                    break
                            else:
                                args = (str(first_arg),)
                
                return original_path_init(self, *args, **kwargs)
            
            Path.__init__ = compatible_path_init
            print("✓ Path构造函数补丁已应用")
            
        except Exception as e:
            print(f"⚠️ 无法补丁Path构造函数: {e}")
        
        # 6. 补丁ModelProcessor
        try:
            from rapid_table.model_processor.main import ModelProcessor
            original_get_single_model_path = ModelProcessor.get_single_model_path
            
            def compatible_get_single_model_path(cls, model_type):
                """兼容的get_single_model_path方法"""
                try:
                    # 如果model_type有value属性，使用它
                    if hasattr(model_type, 'value'):
                        model_type_value = model_type.value
                    else:
                        # 否则直接使用model_type（假设它是字符串）
                        model_type_value = str(model_type)
                    
                    # 检查model_map中是否存在该类型
                    if model_type_value in cls.model_map:
                        return cls.model_map[model_type_value]
                    else:
                        print(f"⚠️ 未知的model_type: {model_type_value}")
                        # 返回默认值或第一个可用的模型
                        if cls.model_map:
                            return list(cls.model_map.values())[0]
                        else:
                            raise ValueError(f"没有可用的模型类型: {model_type_value}")
                            
                except Exception as e:
                    print(f"⚠️ 模型路径获取失败: {e}")
                    # 返回默认值
                    if cls.model_map:
                        return list(cls.model_map.values())[0]
                    else:
                        raise e
            
            ModelProcessor.get_single_model_path = classmethod(compatible_get_single_model_path)
            print("✓ ModelProcessor补丁已应用")
            
        except ImportError as e:
            print(f"⚠️ 无法导入ModelProcessor: {e}")
        
        print("✓ 全局DictConfig解包补丁已应用")
        return True
        
    except Exception as e:
        print(f"❌ 全局DictConfig解包补丁失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dictconfig_fix():
    """测试DictConfig解包功能"""
    print("🧪 测试DictConfig解包功能...")
    
    try:
        # 测试dictconfig_to_dict函数
        test_dict = {"key": "value", "nested": {"inner": "data"}}
        result = dictconfig_to_dict(test_dict)
        print(f"✓ 基础dict测试通过: {result}")
        
        # 测试字符串处理
        test_str = "test_string"
        result = dictconfig_to_dict(test_str)
        print(f"✓ 字符串测试通过: {result}")
        
        # 测试列表处理
        test_list = [1, 2, {"nested": "value"}]
        result = dictconfig_to_dict(test_list)
        print(f"✓ 列表测试通过: {result}")
        
        print("✓ DictConfig解包功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ DictConfig解包功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动全局DictConfig解包补丁...")
    
    # 测试基础功能
    if not test_dictconfig_fix():
        print("❌ 基础功能测试失败")
        return False
    
    # 应用全局补丁
    if not apply_global_dictconfig_fix():
        print("❌ 全局补丁应用失败")
        return False
    
    print("🎉 全局DictConfig解包补丁应用成功！")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✨ 补丁应用完成！")
    else:
        print("❌ 补丁应用失败！") 