#!/usr/bin/env python3
"""
测试缓存管理器功能
"""

def test_cache_manager():
    """测试缓存管理器"""
    try:
        from enhanced_cache_manager import EnhancedCacheManager
        
        print("🔄 初始化缓存管理器...")
        cache_manager = EnhancedCacheManager()
        
        print("📊 检查缓存状态...")
        cache_info = cache_manager.check_cache_status()
        
        print("✅ 缓存检查成功!")
        print(f"📁 缓存目录: {cache_info['cache_dir']}")
        print(f"💾 总大小: {cache_info['total_size'] / (1024**3):.2f} GB")
        print(f"📦 模型文件数: {cache_info['model_count']}")
        print(f"📈 缓存效率: {cache_info['cache_efficiency']*100:.1f}%")
        
        print("\n📋 详细状态:")
        for name, info in cache_info['subdirs'].items():
            if info['exists']:
                status_icon = "✅" if info['has_models'] else "⚠️"
                size_mb = info['size'] / (1024**2)
                print(f"  {status_icon} {name}: {info['model_count']} 个模型 ({size_mb:.1f} MB)")
            else:
                print(f"  ❌ {name}: 目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_cache_manager() 