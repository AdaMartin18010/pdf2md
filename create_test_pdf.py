#!/usr/bin/env python3
"""
创建测试PDF文件
"""

import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(output_path: Path, content: str = "这是一个测试PDF文件"):
    """创建测试PDF文件"""
    try:
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        
        # 添加标题
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 100, "测试PDF文件")
        
        # 添加内容
        c.setFont("Helvetica", 12)
        y_position = height - 150
        
        # 分行显示内容
        words = content.split()
        line = ""
        for word in words:
            if len(line + word) < 50:  # 简单的换行逻辑
                line += word + " "
            else:
                c.drawString(100, y_position, line.strip())
                y_position -= 20
                line = word + " "
        
        if line:
            c.drawString(100, y_position, line.strip())
        
        c.save()
        print(f"✅ 创建测试PDF文件: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 创建PDF文件失败: {e}")
        return False

def main():
    """主函数"""
    print("📄 创建测试PDF文件")
    print("=" * 30)
    
    # 创建测试目录
    test_dir = Path("test_pdfs")
    test_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    subdir1 = test_dir / "subdir1"
    subdir1.mkdir(exist_ok=True)
    
    subdir2 = test_dir / "subdir2"
    subdir2.mkdir(exist_ok=True)
    
    nested_dir = subdir1 / "nested"
    nested_dir.mkdir(exist_ok=True)
    
    # 创建测试PDF文件
    test_files = [
        (test_dir / "test1.pdf", "这是第一个测试PDF文件，包含一些中文内容。"),
        (test_dir / "test2.pdf", "这是第二个测试PDF文件，用于测试批量处理功能。"),
        (subdir1 / "sub1_test.pdf", "这是子目录1中的测试PDF文件。"),
        (subdir2 / "sub2_test.pdf", "这是子目录2中的测试PDF文件。"),
        (nested_dir / "nested_test.pdf", "这是嵌套目录中的测试PDF文件。")
    ]
    
    success_count = 0
    for pdf_path, content in test_files:
        if create_test_pdf(pdf_path, content):
            success_count += 1
    
    print(f"\n📊 创建结果:")
    print(f"  成功创建: {success_count}/{len(test_files)} 个文件")
    
    if success_count > 0:
        print(f"\n✅ 测试PDF文件已创建在 {test_dir} 目录中")
        print("💡 现在可以运行PDF转换测试了")

if __name__ == "__main__":
    main() 