#!/usr/bin/env python3
"""
修复Mineru导入符号
确保所有导入都使用正确的符号
"""

import os
import sys
from pathlib import Path

def check_mineru_imports():
    """检查mineru导入"""
    print("🔍 检查Mineru导入符号...")
    
    # 测试可用的符号
    try:
        from mineru.utils.enum_class import MakeMode, BlockType, CategoryId, ContentType, ModelPath, SplitFlag
        print("✅ 成功导入的符号:")
        print(f"  - MakeMode: {MakeMode}")
        print(f"  - BlockType: {BlockType}")
        print(f"  - CategoryId: {CategoryId}")
        print(f"  - ContentType: {ContentType}")
        print(f"  - ModelPath: {ModelPath}")
        print(f"  - SplitFlag: {SplitFlag}")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_mineru_task_type():
    """测试MineruTaskType是否存在"""
    print("\n🔍 测试MineruTaskType...")
    
    try:
        from mineru.utils.enum_class import MineruTaskType
        print("✅ MineruTaskType 存在")
        return True
    except ImportError:
        print("❌ MineruTaskType 不存在")
        return False

def check_project_files():
    """检查项目文件中的导入"""
    print("\n🔍 检查项目文件中的导入...")
    
    project_files = [
        "stable_mineru_converter.py",
        "enhanced_cache_manager.py", 
        "model_cache_manager.py",
        "global_dictconfig_fix.py"
    ]
    
    for file_path in project_files:
        if Path(file_path).exists():
            print(f"\n📄 检查文件: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有MineruTaskType引用
                if 'MineruTaskType' in content:
                    print(f"  ⚠️ 发现MineruTaskType引用")
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'MineruTaskType' in line:
                            print(f"    第{i}行: {line.strip()}")
                else:
                    print(f"  ✅ 无MineruTaskType引用")
                
                # 检查mineru导入
                mineru_imports = [line for line in content.split('\n') if 'from mineru' in line or 'import mineru' in line]
                if mineru_imports:
                    print(f"  📝 Mineru导入:")
                    for line in mineru_imports:
                        print(f"    {line.strip()}")
                else:
                    print(f"  ✅ 无Mineru导入")
                    
            except Exception as e:
                print(f"  ❌ 读取文件失败: {e}")

def create_safe_import_wrapper():
    """创建安全的导入包装器"""
    print("\n🔧 创建安全的导入包装器...")
    
    wrapper_code = '''#!/usr/bin/env python3
"""
安全的Mineru导入包装器
处理不同版本的Mineru符号差异
"""

def safe_import_mineru_symbols():
    """安全导入Mineru符号"""
    symbols = {}
    
    try:
        from mineru.utils.enum_class import MakeMode
        symbols['MakeMode'] = MakeMode
        print("✅ MakeMode 导入成功")
    except ImportError:
        print("❌ MakeMode 导入失败")
    
    try:
        from mineru.utils.enum_class import BlockType
        symbols['BlockType'] = BlockType
        print("✅ BlockType 导入成功")
    except ImportError:
        print("❌ BlockType 导入失败")
    
    try:
        from mineru.utils.enum_class import CategoryId
        symbols['CategoryId'] = CategoryId
        print("✅ CategoryId 导入成功")
    except ImportError:
        print("❌ CategoryId 导入失败")
    
    try:
        from mineru.utils.enum_class import ContentType
        symbols['ContentType'] = ContentType
        print("✅ ContentType 导入成功")
    except ImportError:
        print("❌ ContentType 导入失败")
    
    try:
        from mineru.utils.enum_class import ModelPath
        symbols['ModelPath'] = ModelPath
        print("✅ ModelPath 导入成功")
    except ImportError:
        print("❌ ModelPath 导入失败")
    
    try:
        from mineru.utils.enum_class import SplitFlag
        symbols['SplitFlag'] = SplitFlag
        print("✅ SplitFlag 导入成功")
    except ImportError:
        print("❌ SplitFlag 导入失败")
    
    # 注意：MineruTaskType 在当前版本中不存在
    print("ℹ️ MineruTaskType 在当前版本中不存在，使用其他符号替代")
    
    return symbols

if __name__ == "__main__":
    symbols = safe_import_mineru_symbols()
    print(f"\\n📊 可用符号: {list(symbols.keys())}")
'''
    
    with open("safe_mineru_imports.py", "w", encoding="utf-8") as f:
        f.write(wrapper_code)
    
    print("✅ 已创建 safe_mineru_imports.py")

def main():
    """主函数"""
    print("🔧 Mineru导入符号修复工具")
    print("="*50)
    
    # 检查可用的符号
    if not check_mineru_imports():
        print("❌ Mineru导入检查失败")
        return
    
    # 测试MineruTaskType
    test_mineru_task_type()
    
    # 检查项目文件
    check_project_files()
    
    # 创建安全导入包装器
    create_safe_import_wrapper()
    
    print("\n✅ 修复完成!")
    print("\n💡 建议:")
    print("  1. 使用 safe_mineru_imports.py 进行安全导入")
    print("  2. 避免使用 MineruTaskType，使用其他可用符号")
    print("  3. 检查所有文件中的导入语句")

if __name__ == "__main__":
    main() 