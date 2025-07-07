#!/usr/bin/env python3
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
    print(f"\n📊 可用符号: {list(symbols.keys())}")
