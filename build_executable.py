#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转Markdown工具可执行文件构建脚本
使用PyInstaller将GUI应用打包成独立的可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """检查构建依赖"""
    print("🔍 检查构建依赖...")
    
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装完成")
    
    # 检查必要的Python包
    required_packages = [
        "tkinter",
        "json",
        "pathlib",
        "datetime",
        "psutil"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 可用")
        except ImportError:
            print(f"❌ {package} 不可用")

def create_spec_file():
    """创建PyInstaller规范文件"""
    print("\n📝 创建PyInstaller规范文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
        ('safe_mineru_imports.py', '.'),
        ('README.md', '.'),
        ('USER_GUIDE.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        'pathlib',
        'datetime',
        'psutil',
        'threading',
        'concurrent.futures',
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
'''
    
    with open('pdf2md.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 规范文件已创建: pdf2md.spec")

def create_launcher_script():
    """创建启动脚本"""
    print("\n📝 创建启动脚本...")
    
    launcher_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转Markdown工具启动脚本
用于PyInstaller打包后的可执行文件
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 设置环境变量
os.environ['PYTHONPATH'] = str(current_dir)

# 导入并启动GUI
try:
    from pdf2md_gui import PDF2MDGUI
    
    def main():
        """主函数"""
        app = PDF2MDGUI()
        app.run()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖文件都在正确位置")
    input("按回车键退出...")
except Exception as e:
    print(f"启动错误: {e}")
    input("按回车键退出...")
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ 启动脚本已创建: launcher.py")

def create_icon():
    """创建应用图标"""
    print("\n🎨 创建应用图标...")
    
    # 检查是否已有图标
    if os.path.exists('icon.ico'):
        print("✅ 图标文件已存在: icon.ico")
        return
    
    # 创建简单的图标文件（如果需要）
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的图标
        img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的PDF图标
        draw.rectangle([50, 50, 206, 206], outline=(255, 0, 0), width=8)
        draw.text((80, 100), "PDF", fill=(255, 0, 0), font=None)
        draw.text((80, 150), "→MD", fill=(0, 0, 255), font=None)
        
        img.save('icon.ico', format='ICO')
        print("✅ 图标文件已创建: icon.ico")
        
    except ImportError:
        print("⚠️ PIL未安装，跳过图标创建")
    except Exception as e:
        print(f"⚠️ 图标创建失败: {e}")

def build_executable():
    """构建可执行文件"""
    print("\n🔨 开始构建可执行文件...")
    
    # 使用PyInstaller构建
    cmd = [
        'pyinstaller',
        '--onefile',  # 单文件
        '--windowed',  # 无控制台窗口
        '--name=PDF2MD转换器',  # 可执行文件名称
        '--add-data=gui_config.json;.',  # 添加配置文件
        '--add-data=config.yaml;.',
        '--add-data=enhanced_cache_manager.py;.',
        '--add-data=stable_mineru_converter.py;.',
        '--add-data=safe_mineru_imports.py;.',
        '--add-data=README.md;.',
        '--add-data=USER_GUIDE.md;.',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=json',
        '--hidden-import=pathlib',
        '--hidden-import=datetime',
        '--hidden-import=psutil',
        '--hidden-import=threading',
        '--hidden-import=concurrent.futures',
        '--hidden-import=torch',
        '--hidden-import=transformers',
        '--hidden-import=modelscope',
        '--hidden-import=mineru',
        'start_gui.py'
    ]
    
    # 如果有图标，添加图标参数
    if os.path.exists('icon.ico'):
        cmd.extend(['--icon=icon.ico'])
    
    try:
        print("执行构建命令...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_installer_script():
    """创建安装脚本"""
    print("\n📦 创建安装脚本...")
    
    installer_content = '''@echo off
echo 正在安装PDF2MD转换器...

REM 创建安装目录
set INSTALL_DIR=%PROGRAMFILES%\\PDF2MD转换器
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM 复制可执行文件
copy "dist\\PDF2MD转换器.exe" "%INSTALL_DIR%\\"

REM 复制配置文件
copy "gui_config.json" "%INSTALL_DIR%\\"
copy "config.yaml" "%INSTALL_DIR%\\"

REM 创建桌面快捷方式
set DESKTOP=%USERPROFILE%\\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\\PDF2MD转换器.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\PDF2MD转换器.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "PDF转Markdown工具" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo 安装完成！
echo 可执行文件位置: %INSTALL_DIR%\\PDF2MD转换器.exe
pause
'''
    
    with open('install.bat', 'w', encoding='gbk') as f:
        f.write(installer_content)
    
    print("✅ 安装脚本已创建: install.bat")

def create_portable_package():
    """创建便携版打包"""
    print("\n📦 创建便携版打包...")
    
    # 创建便携版目录
    portable_dir = Path("PDF2MD转换器_便携版")
    portable_dir.mkdir(exist_ok=True)
    
    # 复制必要文件
    files_to_copy = [
        "dist/PDF2MD转换器.exe",
        "gui_config.json",
        "config.yaml",
        "README.md",
        "USER_GUIDE.md"
    ]
    
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            shutil.copy2(file_path, portable_dir)
            print(f"✅ 已复制: {file_path}")
    
    # 创建启动说明
    readme_content = '''# PDF2MD转换器 - 便携版

## 使用说明

1. 双击 "PDF2MD转换器.exe" 启动程序
2. 选择要转换的PDF文件或目录
3. 设置输出目录和转换选项
4. 点击"开始转换"按钮

## 功能特性

- 支持单个PDF文件转换
- 支持批量目录转换
- 实时进度显示
- 处理状态监控
- 配置保存和加载
- 缓存管理

## 系统要求

- Windows 7/8/10/11
- 至少2GB内存
- 至少1GB可用磁盘空间

## 注意事项

- 首次运行可能需要下载模型文件
- 建议在有网络连接的环境下使用
- 转换大文件时请耐心等待

## 技术支持

如有问题，请查看README.md和USER_GUIDE.md文件。
'''
    
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 便携版已创建: {portable_dir}")

def main():
    """主函数"""
    print("🚀 开始构建PDF2MD转换器可执行文件")
    print("=" * 50)
    
    # 检查依赖
    check_dependencies()
    
    # 创建必要文件
    create_spec_file()
    create_launcher_script()
    create_icon()
    
    # 构建可执行文件
    if build_executable():
        print("\n✅ 构建成功!")
        
        # 创建安装脚本
        create_installer_script()
        
        # 创建便携版
        create_portable_package()
        
        print("\n📁 生成的文件:")
        print("   - dist/PDF2MD转换器.exe (主程序)")
        print("   - install.bat (安装脚本)")
        print("   - PDF2MD转换器_便携版/ (便携版)")
        print("   - pdf2md.spec (构建配置)")
        
        print("\n💡 使用说明:")
        print("   1. 直接运行 dist/PDF2MD转换器.exe")
        print("   2. 或运行 install.bat 进行安装")
        print("   3. 或使用便携版文件夹")
        
    else:
        print("\n❌ 构建失败，请检查错误信息")

if __name__ == "__main__":
    main() 