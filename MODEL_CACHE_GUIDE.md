# 模型缓存使用指南

## 问题说明

每次转换PDF时都重新下载模型是一个常见问题，这会导致：

- 转换速度慢
- 网络带宽浪费
- 重复下载相同模型

## 解决方案

### 1. 模型缓存管理器

我们创建了专门的模型缓存管理器来解决这个问题：

```bash
# 查看缓存状态
python model_cache_manager.py --info

# 优化首次运行
python model_cache_manager.py --optimize

# 清空缓存（谨慎使用）
python model_cache_manager.py --clear
```

### 2. 缓存目录结构

```text
models_cache/
├── transformers/     # HuggingFace模型
├── datasets/         # 数据集缓存
├── mineru/           # Mineru模型
├── modelscope/       # ModelScope模型（主要）
├── huggingface/      # HuggingFace Hub缓存
├── torch/            # PyTorch模型
├── onnx/             # ONNX模型
└── safetensors/      # SafeTensors格式
```

### 3. 环境变量设置

缓存管理器会自动设置以下环境变量：

```python
# HuggingFace相关
os.environ['HF_HOME'] = str(cache_dir)
os.environ['HF_DATASETS_CACHE'] = str(cache_dir / "datasets")
os.environ['TRANSFORMERS_CACHE'] = str(cache_dir / "transformers")
os.environ['HF_HUB_CACHE'] = str(cache_dir / "huggingface")

# ModelScope相关
os.environ['MODELSCOPE_CACHE'] = str(cache_dir / "modelscope")
os.environ['MODELSCOPE_DOMAIN'] = "modelscope.cn"

# Mineru相关
os.environ['MINERU_CACHE_DIR'] = str(cache_dir / "mineru")
os.environ['MINERU_MODEL_SOURCE'] = 'modelscope'

# PyTorch相关
os.environ['TORCH_HOME'] = str(cache_dir / "torch")
os.environ['TORCH_WEIGHTS_ONLY'] = 'false'
```

### 4. 使用步骤

#### 首次使用

1. **运行缓存管理器**：

   ```bash
   python model_cache_manager.py --optimize
   ```

2. **查看缓存状态**：

   ```bash
   python model_cache_manager.py --info
   ```

3. **首次转换**（会下载模型）：

   ```bash
   python stable_mineru_converter.py input.pdf -o output/
   ```

#### 后续使用

1. **检查缓存状态**：

   ```bash
   python stable_mineru_converter.py --cache-info
   ```

2. **正常转换**（使用缓存模型）：

   ```bash
   python stable_mineru_converter.py input.pdf -o output/
   ```

### 5. 缓存状态说明

- ✅ **已缓存**：模型文件已存在，转换时不会重新下载
- ❌ **未缓存**：模型文件不存在，首次使用时会下载

### 6. 常见问题

#### Q: 为什么还是显示"未缓存"？

A: 检查以下几点：

- 缓存目录是否存在
- 网络连接是否正常
- 是否有足够的磁盘空间

#### Q: 如何强制重新下载模型？

A: 清空缓存后重新转换：

```bash
python model_cache_manager.py --clear
python stable_mineru_converter.py input.pdf -o output/
```

#### Q: 缓存目录占用空间太大怎么办？

A: 可以手动删除不需要的模型文件，或者使用：

```bash
python model_cache_manager.py --clear
```

### 7. 性能优化建议

1. **首次运行**：
   - 确保网络稳定
   - 耐心等待模型下载
   - 建议在空闲时间进行

2. **后续运行**：
   - 模型已缓存，转换速度会显著提升
   - 可以批量处理多个PDF文件

3. **磁盘空间**：
   - 模型缓存可能占用几GB空间
   - 确保有足够的磁盘空间

### 8. 验证缓存效果

转换时观察输出信息：

- 首次运行：会显示下载进度
- 后续运行：直接开始转换，无下载信息

### 9. 故障排除

如果遇到缓存问题：

1. **检查网络连接**
2. **验证磁盘空间**
3. **重新初始化缓存**：

   ```bash
   python model_cache_manager.py --clear
   python model_cache_manager.py --optimize
   ```

4. **查看详细日志**：

   ```bash
   python stable_mineru_converter.py input.pdf -o output/ --verbose
   ```

## 总结

通过使用模型缓存管理器，您可以：

- ✅ 避免重复下载模型
- ✅ 显著提升转换速度
- ✅ 节省网络带宽
- ✅ 提高使用体验

建议在首次使用前先运行缓存管理器进行优化设置。
