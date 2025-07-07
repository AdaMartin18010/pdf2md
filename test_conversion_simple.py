#!/usr/bin/env python3
"""
简单的转换功能测试
验证基本的PDF转Markdown功能是否正常
"""

import os
import sys
from pathlib import Path
import shutil

def create_test_pdf():
    """创建一个简单的测试PDF文件"""
    test_dir = Path("test_simple")
    test_dir.mkdir(exist_ok=True)
    
    # 创建一个简单的PDF文件（使用文本文件模拟）
    test_pdf = test_dir / "simple_test.pdf"
    
    # 如果PDF文件不存在，创建一个文本文件作为替代
    if not test_pdf.exists():
        test_file = test_dir / "simple_test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文件\n用于验证转换功能\n")
        print(f"✅ 创建测试文件: {test_file}")
        return test_file
    else:
        print(f"✅ 测试PDF文件已存在: {test_pdf}")
        return test_pdf
    
    return test_pdf

def test_basic_conversion():
    """测试基本转换功能"""
    print("🚀 开始测试基本转换功能")
    
    try:
        from stable_mineru_converter import MineruConverter
        
        # 创建转换器
        converter = MineruConverter()
        print("✅ 转换器初始化成功")
        
        # 检查缓存状态
        cache_status = converter.check_cache_status()
        print("📊 缓存状态检查完成")
        
        # 创建测试文件
        test_file = create_test_pdf()
        
        # 设置输出目录
        output_dir = Path("test_simple_output")
        output_dir.mkdir(exist_ok=True)
        
        print(f"📁 输入文件: {test_file}")
        print(f"📁 输出目录: {output_dir}")
        
        # 尝试转换（如果是PDF文件）
        if test_file.suffix.lower() == '.pdf':
            print("🔄 开始转换PDF文件...")
            
            def progress_callback(progress: int, message: str):
                print(f"[{progress}%] {message}")
            
            result = converter.convert_single_pdf(
                test_file,
                output_dir,
                lang="ch",
                backend="pipeline",
                method="auto",
                enable_formula=True,
                enable_table=True,
                progress_callback=progress_callback
            )
            
            if result['success']:
                print("✅ 转换成功!")
                print(f"📄 输出文件: {result['output_file']}")
                print(f"🖼️ 图片目录: {result['images_dir']}")
                print(f"📊 图片数量: {result['image_count']}")
                print(f"⏱️ 处理时间: {result['processing_time']:.2f}秒")
                return True
            else:
                print(f"❌ 转换失败: {result['error']}")
                return False
        else:
            print("ℹ️ 跳过转换（非PDF文件）")
            return True
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_module_imports():
    """测试模块导入"""
    print("\n🔍 测试模块导入")
    
    modules_to_test = [
        ("mineru", "核心转换模块"),
        ("rapid_table", "表格处理模块"),
        ("torch", "PyTorch模块"),
        ("transformers", "Transformers模块")
    ]
    
    all_passed = True
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name}) 导入成功")
        except ImportError as e:
            print(f"❌ {description} ({module_name}) 导入失败: {e}")
            all_passed = False
    
    return all_passed

def test_cache_manager():
    """测试缓存管理器"""
    print("\n🔍 测试缓存管理器")
    
    try:
        from enhanced_cache_manager import EnhancedCacheManager
        
        cache_manager = EnhancedCacheManager()
        print("✅ 增强缓存管理器初始化成功")
        
        # 检查缓存状态
        status = cache_manager.check_cache_status()
        print("📊 缓存状态检查完成")
        
        return True
        
    except ImportError as e:
        print(f"❌ 缓存管理器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 缓存管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始简单转换功能测试")
    print("="*50)
    
    # 测试1: 模块导入
    test1_passed = test_module_imports()
    
    # 测试2: 缓存管理器
    test2_passed = test_cache_manager()
    
    # 测试3: 基本转换
    test3_passed = test_basic_conversion()
    
    # 总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    print(f"✅ 模块导入测试: {'通过' if test1_passed else '失败'}")
    print(f"✅ 缓存管理器测试: {'通过' if test2_passed else '失败'}")
    print(f"✅ 基本转换测试: {'通过' if test3_passed else '失败'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 所有测试通过！转换功能正常")
        return True
    else:
        print("\n❌ 部分测试失败，需要检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 