#!/usr/bin/env python3
"""
简单测试脚本
"""

print("🔍 开始简单测试...")

try:
    print("1. 测试导入缓存管理器...")
    from enhanced_cache_manager import EnhancedCacheManager
    print("✅ 缓存管理器导入成功")
    
    print("2. 测试创建实例...")
    cache_manager = EnhancedCacheManager()
    print("✅ 缓存管理器实例创建成功")
    
    print("3. 测试检查缓存状态...")
    status = cache_manager.check_cache_status()
    print(f"✅ 缓存状态检查成功: {status['cache_dir']}")
    
    print("4. 测试GUI导入...")
    import pdf2md_gui
    print("✅ GUI模块导入成功")
    
    print("✅ 所有测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc() 