#!/usr/bin/env python3
"""
内存和GPU监控脚本
"""

import time
import psutil
import os
import sys

def get_memory_info():
    """获取内存信息"""
    try:
        memory = psutil.virtual_memory()
        return {
            'total': memory.total / (1024**3),  # GB
            'available': memory.available / (1024**3),  # GB
            'used': memory.used / (1024**3),  # GB
            'percent': memory.percent
        }
    except:
        return None

def get_gpu_info():
    """获取GPU信息"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            cached = torch.cuda.memory_reserved(0) / (1024**3)
            return {
                'available': gpu_memory,
                'allocated': allocated,
                'cached': cached,
                'free': gpu_memory - allocated
            }
        else:
            return None
    except:
        return None

def monitor_resources(duration=60, interval=2):
    """监控资源使用情况"""
    print(f"🔍 开始监控资源使用情况 ({duration}秒)...")
    print("=" * 60)
    
    start_time = time.time()
    max_memory = 0
    max_gpu = 0
    
    while time.time() - start_time < duration:
        # 获取内存信息
        memory_info = get_memory_info()
        if memory_info:
            print(f"💾 内存: {memory_info['used']:.1f}GB / {memory_info['total']:.1f}GB ({memory_info['percent']:.1f}%)")
            max_memory = max(max_memory, memory_info['used'])
        
        # 获取GPU信息
        gpu_info = get_gpu_info()
        if gpu_info:
            print(f"🎮 GPU: {gpu_info['allocated']:.1f}GB / {gpu_info['available']:.1f}GB (缓存: {gpu_info['cached']:.1f}GB)")
            max_gpu = max(max_gpu, gpu_info['allocated'])
        else:
            print("🎮 GPU: 不可用")
        
        # 获取进程信息
        try:
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024**2)  # MB
            print(f"📊 当前进程: {process_memory:.1f}MB")
        except:
            print("📊 当前进程: 未知")
        
        print("-" * 40)
        time.sleep(interval)
    
    print("=" * 60)
    print(f"📈 监控完成!")
    print(f"💾 最大内存使用: {max_memory:.1f}GB")
    if max_gpu > 0:
        print(f"🎮 最大GPU使用: {max_gpu:.1f}GB")

def test_model_loading():
    """测试模型加载对内存的影响"""
    print("🧪 测试模型加载对内存的影响...")
    
    # 记录初始状态
    initial_memory = get_memory_info()
    initial_gpu = get_gpu_info()
    
    print("📊 初始状态:")
    if initial_memory:
        print(f"  内存: {initial_memory['used']:.1f}GB")
    if initial_gpu:
        print(f"  GPU: {initial_gpu['allocated']:.1f}GB")
    
    try:
        print("\n🔄 尝试导入缓存管理器...")
        from enhanced_cache_manager import EnhancedCacheManager
        cache_manager = EnhancedCacheManager()
        
        # 记录导入后状态
        after_import_memory = get_memory_info()
        after_import_gpu = get_gpu_info()
        
        print("📊 导入缓存管理器后:")
        if after_import_memory and initial_memory:
            memory_diff = after_import_memory['used'] - initial_memory['used']
            print(f"  内存变化: {memory_diff:+.1f}GB")
        if after_import_gpu and initial_gpu:
            gpu_diff = after_import_gpu['allocated'] - initial_gpu['allocated']
            print(f"  GPU变化: {gpu_diff:+.1f}GB")
        
        print("\n🔄 尝试检查缓存状态...")
        cache_info = cache_manager.check_cache_status()
        
        # 记录检查后状态
        after_check_memory = get_memory_info()
        after_check_gpu = get_gpu_info()
        
        print("📊 检查缓存后:")
        if after_check_memory and initial_memory:
            memory_diff = after_check_memory['used'] - initial_memory['used']
            print(f"  内存变化: {memory_diff:+.1f}GB")
        if after_check_gpu and initial_gpu:
            gpu_diff = after_check_gpu['allocated'] - initial_gpu['allocated']
            print(f"  GPU变化: {gpu_diff:+.1f}GB")
        
        print("\n✅ 模型加载测试完成")
        
    except Exception as e:
        print(f"❌ 模型加载测试失败: {e}")

def main():
    """主函数"""
    print("🚀 内存和GPU监控工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "monitor":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            monitor_resources(duration)
        elif command == "test":
            test_model_loading()
        else:
            print("用法:")
            print("  python memory_monitor.py monitor [持续时间秒]")
            print("  python memory_monitor.py test")
    else:
        # 默认运行监控
        monitor_resources(30)

if __name__ == "__main__":
    main() 