# 处理设置和状态功能说明

## 功能概述

添加了完整的处理设置和状态管理功能，包括超时时间、CPU/GPU处理、并发控制、内存限制等设置，以及实时处理状态监控。

## 新增功能

### 1. 处理设置选项卡

**位置**: 设置选项卡中的"处理设置"部分

#### 基本设置

- **处理超时时间**: 设置每个文件的最大处理时间（默认300秒）
- **处理设备**: 选择CPU、GPU或自动检测
- **最大并发数**: 设置同时处理的最大文件数（默认2）
- **内存限制**: 设置最大内存使用量（默认4GB）

#### 高级选项

- **启用性能优化**: 开启处理性能优化
- **启用处理缓存**: 开启处理结果缓存
- **启用失败重试**: 开启失败自动重试
- **启用详细日志**: 开启详细处理日志

### 2. 处理状态选项卡

**位置**: 新增的"处理状态"选项卡

#### 状态概览

- **当前状态**: 显示空闲/处理中状态
- **处理设备**: 显示当前使用的处理设备
- **内存使用**: 实时显示内存使用量

#### 处理任务列表

- **文件名**: 显示正在处理的文件名
- **状态**: 显示任务状态（等待中/处理中/成功/失败）
- **进度**: 显示处理进度百分比
- **开始时间**: 显示任务开始时间
- **耗时**: 显示任务处理耗时

#### 处理统计

- **总文件数**: 显示总处理文件数
- **成功**: 显示成功处理的文件数
- **失败**: 显示失败的文件数
- **平均耗时**: 显示平均处理时间

#### 控制功能

- **刷新状态**: 手动刷新处理状态
- **清空列表**: 清空任务列表
- **导出状态**: 导出处理状态到JSON文件

## 技术实现

### 1. 处理设置管理

```python
# 超时设置
self.timeout_var = tk.StringVar(value="300")

# 处理设备设置
self.device_var = tk.StringVar(value="auto")

# 并发设置
self.max_workers_var = tk.StringVar(value="2")

# 内存限制
self.memory_limit_var = tk.StringVar(value="4")

# 高级选项
self.enable_optimization_var = tk.BooleanVar(value=True)
self.enable_caching_var = tk.BooleanVar(value=True)
self.enable_retry_var = tk.BooleanVar(value=True)
self.enable_logging_var = tk.BooleanVar(value=True)
```

### 2. 状态监控

```python
def refresh_processing_status(self):
    """刷新处理状态"""
    # 更新当前状态
    if self.is_converting:
        self.current_status_var.set("处理中")
    else:
        self.current_status_var.set("空闲")
    
    # 检测GPU可用性
    try:
        import torch
        if torch.cuda.is_available():
            self.device_status_var.set("GPU (自动检测)")
        else:
            self.device_status_var.set("CPU (自动检测)")
    except:
        self.device_status_var.set("CPU (自动检测)")
    
    # 更新内存使用
    process = psutil.Process()
    memory_mb = process.memory_info().rss / (1024 * 1024)
    self.memory_usage_var.set(f"{memory_mb:.1f} MB")
```

### 3. 任务管理

```python
def add_processing_task(self, filename: str):
    """添加处理任务"""
    task = {
        "filename": filename,
        "status": "等待中",
        "progress": 0,
        "start_time": datetime.datetime.now().strftime("%H:%M:%S"),
        "duration": ""
    }
    self.processing_tasks.append(task)
    self.update_tasks_list()
    self.update_processing_stats()

def update_task_status(self, filename: str, status: str, progress: int = 0, duration: str = ""):
    """更新任务状态"""
    for task in self.processing_tasks:
        if task.get("filename") == filename:
            task["status"] = status
            task["progress"] = progress
            if duration:
                task["duration"] = duration
            break
```

### 4. 配置持久化

```python
def save_config(self):
    config = {
        # ... 其他配置
        "timeout": self.timeout_var.get(),
        "device": self.device_var.get(),
        "max_workers": self.max_workers_var.get(),
        "memory_limit": self.memory_limit_var.get(),
        "enable_optimization": self.enable_optimization_var.get(),
        "enable_caching": self.enable_caching_var.get(),
        "enable_retry": self.enable_retry_var.get(),
        "enable_logging": self.enable_logging_var.get()
    }
```

## 功能特性

### 1. 实时监控

- ✅ **状态监控**: 实时显示处理状态
- ✅ **进度跟踪**: 实时更新处理进度
- ✅ **资源监控**: 监控内存使用情况
- ✅ **设备检测**: 自动检测GPU可用性

### 2. 任务管理

- ✅ **任务列表**: 显示所有处理任务
- ✅ **状态更新**: 实时更新任务状态
- ✅ **统计信息**: 显示处理统计
- ✅ **导出功能**: 导出处理状态

### 3. 配置管理

- ✅ **设置保存**: 自动保存处理设置
- ✅ **设置加载**: 启动时加载设置
- ✅ **配置验证**: 验证设置有效性

### 4. 性能优化

- ✅ **超时控制**: 防止处理卡死
- ✅ **并发控制**: 控制同时处理数量
- ✅ **内存限制**: 防止内存溢出
- ✅ **设备选择**: 优化处理设备

## 使用方法

### 1. 配置处理设置

1. 打开"设置"选项卡
2. 在"处理设置"部分配置参数：
   - 设置超时时间（秒）
   - 选择处理设备（CPU/GPU/自动）
   - 设置最大并发数
   - 设置内存限制
   - 启用/禁用高级选项

### 2. 监控处理状态

1. 打开"处理状态"选项卡
2. 查看状态概览：
   - 当前处理状态
   - 使用的处理设备
   - 内存使用情况
3. 查看任务列表：
   - 文件名和状态
   - 处理进度
   - 开始时间和耗时
4. 查看处理统计：
   - 总文件数和成功率
   - 平均处理时间

### 3. 管理任务

- **刷新状态**: 点击"刷新状态"按钮
- **清空列表**: 点击"清空列表"按钮
- **导出状态**: 点击"导出状态"按钮保存到文件

## 配置参数说明

### 超时时间

- **默认值**: 300秒
- **作用**: 防止单个文件处理时间过长
- **建议**: 根据文件大小和复杂度调整

### 处理设备

- **auto**: 自动检测GPU可用性
- **cpu**: 强制使用CPU处理
- **gpu**: 强制使用GPU处理（如果可用）

### 并发数

- **默认值**: 2
- **作用**: 控制同时处理的文件数
- **建议**: 根据系统性能调整

### 内存限制

- **默认值**: 4GB
- **作用**: 限制处理时的内存使用
- **建议**: 根据系统内存调整

## 相关文件

- `pdf2md_gui.py` - 主GUI界面（已更新）
- `gui_config.json` - GUI配置文件（包含处理设置）

## 状态

✅ **已实现** - 完整的处理设置和状态管理功能
✅ **已集成** - 与现有转换功能完全集成
✅ **已测试** - 功能测试通过
✅ **已优化** - 支持实时监控和配置管理
