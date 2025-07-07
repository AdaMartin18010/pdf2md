# PDF2MD转换器构建指南

## 概述

本指南介绍如何将PDF转Markdown工具编译成独立的可执行文件，支持Windows、Linux和macOS平台。

## 构建方法

### 方法一：使用构建脚本（推荐）

#### 1. 安装构建依赖

```bash
# 安装PyInstaller
pip install pyinstaller

# 安装其他依赖
pip install -r build_requirements.txt
```

#### 2. 运行构建脚本

```bash
python build_executable.py
```

#### 3. 构建结果

- `dist/PDF2MD转换器.exe` - Windows可执行文件
- `install.bat` - Windows安装脚本
- `PDF2MD转换器_便携版/` - 便携版文件夹

### 方法二：手动构建

#### Windows平台

```bash
# 单文件构建
pyinstaller --onefile --windowed --name="PDF2MD转换器" start_gui.py

# 带图标构建
pyinstaller --onefile --windowed --icon=icon.ico --name="PDF2MD转换器" start_gui.py

# 包含数据文件
pyinstaller --onefile --windowed --add-data="gui_config.json;." --add-data="config.yaml;." start_gui.py
```

#### Linux平台

```bash
# 单文件构建
pyinstaller --onefile --name="pdf2md-converter" start_gui.py

# 带图标构建
pyinstaller --onefile --icon=icon.ico --name="pdf2md-converter" start_gui.py
```

#### macOS平台

```bash
# 单文件构建
pyinstaller --onefile --name="PDF2MD转换器" start_gui.py

# 创建.app包
pyinstaller --windowed --name="PDF2MD转换器" start_gui.py
```

## 构建选项说明

### 基本选项

- `--onefile`: 打包成单个可执行文件
- `--windowed`: 不显示控制台窗口（GUI应用）
- `--name`: 指定可执行文件名称
- `--icon`: 指定应用图标

### 数据文件选项

- `--add-data`: 添加数据文件到可执行文件
- `--datas`: 指定数据文件目录

### 导入选项

- `--hidden-import`: 添加隐藏导入
- `--exclude-module`: 排除模块

### 优化选项

- `--upx`: 使用UPX压缩可执行文件
- `--strip`: 去除调试信息

## 平台特定构建

### Windows

```bash
# 基本构建
pyinstaller --onefile --windowed start_gui.py

# 完整构建（包含所有依赖）
pyinstaller --onefile --windowed --hidden-import=tkinter --hidden-import=psutil start_gui.py
```

### Linux

```bash
# 基本构建
pyinstaller --onefile start_gui.py

# 完整构建
pyinstaller --onefile --hidden-import=tkinter --hidden-import=psutil start_gui.py
```

### macOS

```bash
# 基本构建
pyinstaller --onefile start_gui.py

# 创建.app包
pyinstaller --windowed --name="PDF2MD转换器" start_gui.py
```

## 构建配置文件

### pdf2md.spec

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['start_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui_config.json', '.'),
        ('config.yaml', '.'),
        ('enhanced_cache_manager.py', '.'),
        ('stable_mineru_converter.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'psutil',
        'torch',
        'transformers',
        'modelscope',
        'mineru',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDF2MD转换器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
```

## 构建优化

### 减小文件大小

```bash
# 使用UPX压缩
pyinstaller --onefile --upx-dir=/path/to/upx start_gui.py

# 排除不必要的模块
pyinstaller --onefile --exclude-module=matplotlib --exclude-module=numpy start_gui.py
```

### 提高启动速度

```bash
# 使用--onedir模式（多文件）
pyinstaller --onedir start_gui.py

# 优化导入
pyinstaller --onefile --hidden-import=tkinter start_gui.py
```

## 常见问题

### 1. 缺少依赖

**问题**: 运行时提示缺少模块
**解决**: 使用`--hidden-import`添加缺失的模块

### 2. 数据文件找不到

**问题**: 程序找不到配置文件
**解决**: 使用`--add-data`添加数据文件

### 3. 文件过大

**问题**: 可执行文件太大
**解决**:

- 使用`--exclude-module`排除不需要的模块
- 使用UPX压缩
- 使用`--onedir`模式

### 4. 启动慢

**问题**: 程序启动时间过长
**解决**:

- 使用`--onedir`模式
- 优化导入模块
- 减少数据文件大小

## 测试构建结果

### 基本测试

```bash
# 测试可执行文件
./dist/PDF2MD转换器.exe

# 检查文件大小
ls -lh dist/
```

### 功能测试

1. 启动GUI界面
2. 测试文件选择功能
3. 测试转换功能
4. 测试设置保存功能

## 分发方式

### 1. 单文件分发

- 优点：简单，只有一个文件
- 缺点：启动较慢，文件较大

### 2. 目录分发

- 优点：启动快，文件较小
- 缺点：需要多个文件

### 3. 安装包分发

- 优点：专业，支持卸载
- 缺点：需要安装程序

## 自动化构建

### GitHub Actions

```yaml
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install pyinstaller
        pip install -r build_requirements.txt
    
    - name: Build executable
      run: |
        python build_executable.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: pdf2md-converter-${{ runner.os }}
        path: dist/
```

## 版本管理

### 版本号规范

- 主版本号.次版本号.修订号
- 例如：1.0.0

### 构建标签

```bash
# 创建版本标签
git tag v1.0.0

# 推送标签
git push origin v1.0.0
```

## 总结

通过以上方法，您可以将PDF转Markdown工具编译成独立的可执行文件，支持多种平台和分发方式。建议使用构建脚本进行自动化构建，以确保构建过程的一致性和可靠性。
