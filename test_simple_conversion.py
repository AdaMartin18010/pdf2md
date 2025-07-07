#!/usr/bin/env python3
"""
简单的PDF转换测试
"""

import sys
import time
from pathlib import Path

def test_simple_conversion():
    """测试简单的PDF转换"""
    print("🧪 开始简单转换测试")
    print("=" * 40)
    
    # 检查测试文件
    test_file = Path("test_pdfs/test1.pdf")
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"📄 测试文件: {test_file}")
    print(f"📏 文件大小: {test_file.stat().st_size} bytes")
    
    # 创建输出目录
    output_dir = Path("test_simple_output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # 导入转换函数
        print("🔧 导入转换模块...")
        from pdf2md.mineru_wrapper import parse_doc
        
        print("🚀 开始转换...")
        start_time = time.time()
        
        # 执行转换
        parse_doc(
            path_list=[test_file],
            output_dir=str(output_dir),
            lang="ch",
            backend="pipeline",
            method="auto"
        )
        
        duration = time.time() - start_time
        
        # 检查输出文件
        output_file = output_dir / f"{test_file.stem}.md"
        if output_file.exists():
            print(f"✅ 转换成功!")
            print(f"📄 输出文件: {output_file}")
            print(f"📏 文件大小: {output_file.stat().st_size} bytes")
            print(f"⏱️ 转换耗时: {duration:.2f}秒")
            
            # 显示文件内容预览
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n📝 内容预览:")
                print("-" * 40)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 40)
            
            return True
        else:
            print(f"❌ 转换失败: 输出文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 转换过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_simple_conversion()
    
    if success:
        print("\n🎉 测试成功完成!")
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 