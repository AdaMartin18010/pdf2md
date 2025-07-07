# 内存和GPU优化指南

## 问题描述

在使用PDF转Markdown工具时，可能会遇到以下问题：

- 内存使用量激增
- GPU显存占用过高
- 程序启动时卡住
- 转换过程中系统变慢

## 原因分析

### 1. 模型预加载

- 自动预加载模型会占用大量内存和GPU显存
- 特别是大型AI模型（如OCR、表格识别、公式识别等）

### 2. 环境变量设置

- 某些环境变量可能导致不必要的模型加载
- GPU相关设置可能影响显存使用

### 3. 并发处理

- 多线程处理可能同时加载多个模型
- 内存累积效应

## 解决方案

### 方案1：使用安全启动器（推荐）

```bash
python safe_gui_launcher.py
```

安全启动器提供三种模式：

- **安全模式**：禁用GPU，限制线程数，避免自动预加载
- **完整模式**：启用所有功能，但可能占用较多资源
- **最小模式**：仅提供基本功能

### 方案2：手动优化环境变量

在启动前设置以下环境变量：

```bash
# 禁用GPU（如果不需要）
set CUDA_VISIBLE_DEVICES=

# 限制线程数
set OMP_NUM_THREADS=2

# 禁用并行处理
set TOKENIZERS_PARALLELISM=false

# 启动GUI
python pdf2md_gui.py
```

### 方案3：修改GUI配置

在GUI中：

1. 进入"设置"选项卡
2. 取消勾选"自动预加载模型"
3. 将"最大并发数"设置为1
4. 将"处理设备"设置为"cpu"

### 方案4：使用命令行版本

如果GUI问题严重，可以使用命令行版本：

```bash
python enhanced_batch_processor.py --input pdfs/ --output output/
```

## 监控工具

### 内存监控

```bash
# 监控30秒
python memory_monitor.py monitor 30

# 测试模型加载影响
python memory_monitor.py test
```

### 系统资源检查

```bash
# 检查当前资源使用
python simple_test.py
```

## 优化建议

### 1. 硬件要求

- **内存**：建议8GB以上
- **GPU**：可选，但需要足够显存（4GB以上）
- **存储**：确保有足够空间存储模型缓存

### 2. 软件配置

- 关闭其他占用内存的程序
- 定期清理模型缓存
- 使用SSD存储模型文件

### 3. 使用策略

- 首次使用时选择安全模式
- 批量处理时使用较小的并发数
- 定期重启程序释放内存

## 故障排除

### 问题1：启动时卡住

**解决方案**：

1. 使用安全启动器
2. 检查是否有其他程序占用GPU
3. 重启系统后重试

### 问题2：转换过程中内存不足

**解决方案**：

1. 减少并发数
2. 使用CPU模式
3. 分批处理文件

### 问题3：GPU显存不足

**解决方案**：

1. 禁用GPU，使用CPU模式
2. 关闭其他GPU程序
3. 重启系统释放显存

## 性能调优

### 内存优化

```python
# 在代码中设置
import os
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
```

### GPU优化

```python
# 限制GPU内存使用
import torch
torch.cuda.empty_cache()
torch.cuda.set_per_process_memory_fraction(0.8)
```

### 缓存优化

```python
# 定期清理缓存
from enhanced_cache_manager import EnhancedCacheManager
cache_manager = EnhancedCacheManager()
cache_manager.cleanup_cache(max_age_days=7)
```

## 联系支持

如果问题仍然存在，请：

1. 运行内存监控工具收集数据
2. 检查系统资源使用情况
3. 提供错误日志和系统信息

---

**注意**：这些优化措施可能会影响转换速度，但能显著降低资源占用。根据实际需求选择合适的优化级别。
