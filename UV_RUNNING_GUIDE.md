# UV运行指南

## 🎯 为什么使用UV运行

使用 `uv` 运行程序有以下优势：

1. **依赖管理**: 自动使用项目配置的虚拟环境
2. **环境隔离**: 避免全局环境冲突
3. **版本一致性**: 确保使用正确的依赖版本
4. **简化部署**: 不需要手动管理虚拟环境

## 🚀 运行方式

### 1. 基本运行命令

```bash
# 运行GUI程序
uv run python pdf2md_gui.py

# 运行命令行转换器
uv run python stable_mineru_converter.py input.pdf -o output/

# 运行测试脚本
uv run python test_recursive_search.py
uv run python test_conversion_simple.py
```

### 2. 批量转换示例

```bash
# 递归转换目录中的所有PDF文件
uv run python stable_mineru_converter.py pdfs/ -o output/

# 显示缓存信息
uv run python stable_mineru_converter.py --cache-info

# 转换单个文件
uv run python stable_mineru_converter.py "pdfs/example.pdf" -o output/
```

### 3. 测试和验证

```bash
# 测试递归查找功能
uv run python test_recursive_search.py

# 测试基本转换功能
uv run python test_conversion_simple.py

# 测试GUI功能
uv run python test_gui_complete.py

# 测试关机功能
uv run python test_shutdown_feature.py
```

## 📋 常用命令列表

### GUI相关

```bash
# 启动主GUI
uv run python pdf2md_gui.py

# 启动简化版GUI
uv run python test_main_gui.py

# 诊断GUI问题
uv run python diagnose_gui.py
```

### 转换相关

```bash
# 命令行转换
uv run python stable_mineru_converter.py input.pdf -o output/

# 批量转换
uv run python stable_mineru_converter.py pdfs/ -o output/

# 检查缓存状态
uv run python enhanced_cache_manager.py --info

# 预加载模型
uv run python enhanced_cache_manager.py --preload
```

### 测试相关

```bash
# 功能测试
uv run python test_recursive_search.py
uv run python test_conversion_simple.py
uv run python test_gui_complete.py

# 性能监控
uv run python performance_monitor.py

# 内存监控
uv run python memory_monitor.py
```

## 🔧 UV环境管理

### 1. 检查UV环境

```bash
# 查看当前环境
uv venv

# 查看已安装的包
uv pip list
```

### 2. 添加依赖

```bash
# 添加生产依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name

# 添加特定版本
uv add "package_name>=1.0.0"
```

### 3. 更新依赖

```bash
# 更新所有依赖
uv lock --upgrade

# 同步依赖
uv sync
```

## 📊 项目脚本

### 1. 使用项目脚本

```bash
# 直接运行项目脚本（如果配置了）
uv run pdf2md input.pdf -o output/
```

### 2. 自定义脚本

可以在 `pyproject.toml` 中添加自定义脚本：

```toml
[project.scripts]
pdf2md = "pdf2md.main:main"
pdf2md-gui = "pdf2md_gui:main"
test-all = "test_runner:main"
```

然后使用：

```bash
uv run pdf2md input.pdf -o output/
uv run pdf2md-gui
uv run test-all
```

## 🎯 最佳实践

### 1. 开发环境

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 代码格式化
uv run black .
uv run isort .
```

### 2. 生产环境

```bash
# 只安装生产依赖
uv sync

# 运行程序
uv run python pdf2md_gui.py
```

### 3. 调试模式

```bash
# 启用详细日志
uv run python -v pdf2md_gui.py

# 使用调试器
uv run python -m pdb pdf2md_gui.py
```

## ⚠️ 注意事项

### 1. 环境变量

```bash
# 设置环境变量
uv run --env VAR=value python script.py

# 或者使用.env文件
uv run --env-file .env python script.py
```

### 2. 性能优化

```bash
# 使用GPU（如果可用）
uv run --env CUDA_VISIBLE_DEVICES=0 python script.py

# 限制内存使用
uv run --env PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128 python script.py
```

### 3. 错误处理

```bash
# 捕获错误输出
uv run python script.py 2>&1 | tee error.log

# 设置超时
timeout 300 uv run python script.py
```

## 📈 性能对比

### 使用UV vs 直接Python

| 方面 | UV运行 | 直接Python |
|------|--------|------------|
| 环境隔离 | ✅ 完全隔离 | ❌ 可能冲突 |
| 依赖管理 | ✅ 自动管理 | ❌ 手动管理 |
| 版本一致性 | ✅ 保证一致 | ❌ 可能不一致 |
| 部署简化 | ✅ 一键部署 | ❌ 复杂配置 |
| 性能 | ✅ 优化启动 | ⚠️ 标准启动 |

## 🎉 总结

使用 `uv run` 运行程序是推荐的方式，因为它：

1. **简化了环境管理**
2. **确保了依赖一致性**
3. **提高了部署可靠性**
4. **减少了环境冲突**

建议在所有情况下都使用 `uv run` 来运行PDF转Markdown程序。

---

*使用UV运行程序，享受更好的依赖管理和环境隔离体验！*
