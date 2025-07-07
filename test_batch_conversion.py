#!/usr/bin/env python3
"""
测试批量转换功能
"""

import os
import sys
from pathlib import Path

def test_batch_processor():
    """测试批量处理器"""
    print("🔍 测试批量处理器...")
    
    try:
        from enhanced_batch_processor import EnhancedBatchProcessor
        
        # 创建批量处理器
        processor = EnhancedBatchProcessor(max_workers=1, device_preference="cpu_first")
        print("✅ 批量处理器创建成功")
        
        # 检测设备
        devices = processor.detect_available_devices()
        print(f"可用设备: {devices}")
        
        # 选择设备
        selected_device = processor.select_optimal_device(devices)
        print(f"选择设备: {selected_device}")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mineru_converter():
    """测试Mineru转换器"""
    print("\n🔍 测试Mineru转换器...")
    
    try:
        from stable_mineru_converter import MineruConverter
        
        # 创建转换器
        converter = MineruConverter()
        print("✅ Mineru转换器创建成功")
        
        # 检查缓存状态
        cache_status = converter.check_cache_status()
        print(f"缓存状态: {cache_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mineru转换器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_conversion():
    """测试单个文件转换"""
    print("\n🔍 测试单个文件转换...")
    
    try:
        from stable_mineru_converter import MineruConverter
        
        # 创建转换器
        converter = MineruConverter()
        
        # 查找测试PDF文件
        test_pdfs = list(Path(".").glob("*.pdf"))
        if not test_pdfs:
            test_pdfs = list(Path("pdfs").glob("*.pdf"))
        
        if not test_pdfs:
            print("⚠️ 未找到测试PDF文件")
            return False
        
        test_pdf = test_pdfs[0]
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        print(f"使用测试文件: {test_pdf}")
        print(f"输出目录: {output_dir}")
        
        # 执行转换
        def progress_callback(progress: int, message: str):
            print(f"进度: {progress}% - {message}")
        
        result = converter.convert_single_pdf(
            test_pdf,
            output_dir,
            lang="ch",
            backend="pipeline",
            method="auto",
            enable_formula=True,
            enable_table=True,
            progress_callback=progress_callback
        )
        
        print(f"转换结果: {result}")
        
        if result['success']:
            print("✅ 单个文件转换成功")
            return True
        else:
            print(f"❌ 单个文件转换失败: {result['error']}")
            return False
        
    except Exception as e:
        print(f"❌ 单个文件转换测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_conversion():
    """测试批量转换"""
    print("\n🔍 测试批量转换...")
    
    try:
        from enhanced_batch_processor import EnhancedBatchProcessor
        
        # 创建批量处理器
        processor = EnhancedBatchProcessor(max_workers=1, device_preference="cpu_first")
        
        # 查找PDF文件
        pdf_dir = Path("pdfs")
        if not pdf_dir.exists():
            print("⚠️ pdfs目录不存在，创建测试目录")
            pdf_dir.mkdir(exist_ok=True)
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            print("⚠️ 未找到PDF文件，跳过批量转换测试")
            return True
        
        output_dir = Path("test_batch_output")
        output_dir.mkdir(exist_ok=True)
        
        # 准备转换选项
        options = {
            "language": "ch",
            "backend": "pipeline",
            "method": "auto",
            "enable_formula": True,
            "enable_table": True
        }
        
        # 添加任务
        for pdf_file in pdf_files[:2]:  # 只测试前2个文件
            processor.add_task(pdf_file, output_dir, options)
            print(f"添加任务: {pdf_file.name}")
        
        # 开始处理
        def progress_callback(progress: int, message: str):
            print(f"批量进度: {progress}% - {message}")
        
        result = processor.start_batch_processing(progress_callback)
        
        print(f"批量转换结果: {result}")
        
        if result and result["success_count"] > 0:
            print("✅ 批量转换成功")
            return True
        else:
            print(f"❌ 批量转换失败: {result}")
            return False
        
    except Exception as e:
        print(f"❌ 批量转换测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_integration():
    """测试GUI集成"""
    print("\n🔍 测试GUI集成...")
    
    try:
        # 模拟GUI的转换调用
        from enhanced_batch_processor import EnhancedBatchProcessor
        
        # 创建批量处理器（模拟GUI中的创建）
        processor = EnhancedBatchProcessor(
            max_workers=1,
            device_preference="cpu_first"
        )
        
        # 准备转换选项（模拟GUI中的设置）
        options = {
            "language": "ch",
            "backend": "pipeline", 
            "method": "auto",
            "enable_formula": True,
            "enable_table": True
        }
        
        # 模拟添加任务
        test_pdf = Path("test.pdf")
        if test_pdf.exists():
            processor.add_task(test_pdf, Path("test_output"), options)
            print("✅ GUI集成测试通过")
            return True
        else:
            print("⚠️ 未找到测试文件，跳过GUI集成测试")
            return True
        
    except Exception as e:
        print(f"❌ GUI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始测试批量转换功能...")
    print("=" * 50)
    
    # 逐步测试
    tests = [
        ("批量处理器", test_batch_processor),
        ("Mineru转换器", test_mineru_converter),
        ("单个文件转换", test_single_conversion),
        ("批量转换", test_batch_conversion),
        ("GUI集成", test_gui_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！批量转换功能正常")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")

if __name__ == "__main__":
    main() 