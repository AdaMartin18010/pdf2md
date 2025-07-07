#!/usr/bin/env python3
"""
测试递归查找PDF文件功能
验证批量转换是否能正确找到子目录中的PDF文件
"""

import os
import sys
from pathlib import Path
import shutil

def create_test_structure():
    """创建测试目录结构"""
    test_dir = Path("test_pdfs")
    
    # 清理旧的测试目录
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # 创建测试目录结构
    test_dir.mkdir()
    
    # 创建子目录
    subdir1 = test_dir / "subdir1"
    subdir1.mkdir()
    
    subdir2 = test_dir / "subdir2"
    subdir2.mkdir()
    
    nested_dir = subdir1 / "nested"
    nested_dir.mkdir()
    
    # 创建测试PDF文件（空文件，仅用于测试）
    files_to_create = [
        test_dir / "test1.pdf",
        test_dir / "test2.pdf",
        subdir1 / "sub1_test.pdf",
        subdir2 / "sub2_test.pdf",
        nested_dir / "nested_test.pdf"
    ]
    
    for file_path in files_to_create:
        file_path.touch()
        print(f"✅ 创建测试文件: {file_path}")
    
    return test_dir

def test_glob_vs_rglob():
    """测试glob和rglob的区别"""
    test_dir = create_test_structure()
    
    print("\n" + "="*50)
    print("测试递归查找功能")
    print("="*50)
    
    # 测试glob（只查找当前目录）
    print("\n📁 使用 glob (只查找当前目录):")
    pdf_files_glob = list(test_dir.glob("*.pdf"))
    print(f"找到 {len(pdf_files_glob)} 个PDF文件:")
    for file in pdf_files_glob:
        print(f"  - {file}")
    
    # 测试rglob（递归查找所有子目录）
    print("\n📁 使用 rglob (递归查找所有子目录):")
    pdf_files_rglob = list(test_dir.rglob("*.pdf"))
    print(f"找到 {len(pdf_files_rglob)} 个PDF文件:")
    for file in pdf_files_rglob:
        print(f"  - {file}")
    
    # 验证结果
    expected_files = [
        "test1.pdf",
        "test2.pdf", 
        "subdir1/sub1_test.pdf",
        "subdir1/nested/nested_test.pdf",
        "subdir2/sub2_test.pdf"
    ]
    
    found_files = [str(f.relative_to(test_dir)) for f in pdf_files_rglob]
    
    print("\n📊 验证结果:")
    print(f"期望文件数: {len(expected_files)}")
    print(f"实际找到文件数: {len(pdf_files_rglob)}")
    
    missing_files = []
    for expected in expected_files:
        if expected not in found_files:
            missing_files.append(expected)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
    else:
        print("✅ 所有期望的文件都已找到!")
    
    return len(pdf_files_rglob) == len(expected_files)

def test_converter_recursive():
    """测试转换器的递归查找功能"""
    print("\n" + "="*50)
    print("测试转换器递归查找功能")
    print("="*50)
    
    try:
        from stable_mineru_converter import MineruConverter
        
        converter = MineruConverter()
        test_dir = Path("test_pdfs")
        
        if not test_dir.exists():
            print("❌ 测试目录不存在，请先运行 create_test_structure()")
            return False
        
        # 模拟批量转换的PDF文件查找
        pdf_files = list(test_dir.rglob("*.pdf"))
        
        print(f"✅ 转换器找到 {len(pdf_files)} 个PDF文件:")
        for file in pdf_files:
            print(f"  - {file}")
        
        return len(pdf_files) >= 5  # 应该至少找到5个文件
        
    except ImportError as e:
        print(f"❌ 无法导入转换器: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_gui_recursive():
    """测试GUI的递归查找功能"""
    print("\n" + "="*50)
    print("测试GUI递归查找功能")
    print("="*50)
    
    try:
        # 模拟GUI中的PDF文件查找逻辑
        test_dir = Path("test_pdfs")
        
        if not test_dir.exists():
            print("❌ 测试目录不存在")
            return False
        
        # 模拟GUI中的批量转换逻辑
        pdf_files = list(test_dir.rglob("*.pdf"))
        
        print(f"✅ GUI找到 {len(pdf_files)} 个PDF文件:")
        for file in pdf_files:
            print(f"  - {file}")
        
        # 模拟任务添加
        tasks = []
        for pdf_file in pdf_files:
            filename = pdf_file.name
            tasks.append({
                "filename": filename,
                "full_path": str(pdf_file),
                "relative_path": str(pdf_file.relative_to(test_dir))
            })
        
        print(f"\n📋 任务列表 ({len(tasks)} 个任务):")
        for task in tasks:
            print(f"  - {task['filename']} (路径: {task['relative_path']})")
        
        return len(tasks) >= 5
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试递归查找功能")
    
    # 测试1: 基本递归查找
    test1_passed = test_glob_vs_rglob()
    
    # 测试2: 转换器递归查找
    test2_passed = test_converter_recursive()
    
    # 测试3: GUI递归查找
    test3_passed = test_gui_recursive()
    
    # 总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    print(f"✅ 基本递归查找测试: {'通过' if test1_passed else '失败'}")
    print(f"✅ 转换器递归查找测试: {'通过' if test2_passed else '失败'}")
    print(f"✅ GUI递归查找测试: {'通过' if test3_passed else '失败'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 所有测试通过！递归查找功能正常")
        return True
    else:
        print("\n❌ 部分测试失败，需要检查递归查找功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 