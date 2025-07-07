"""
Tests for pdf2md main module.
"""

import pytest
from pathlib import Path
from pdf2md.main import find_pdf_files, convert_pdf_to_markdown


def test_find_pdf_files_empty_dir(tmp_path):
    """测试空目录下的PDF文件查找。"""
    pdf_files = find_pdf_files(tmp_path)
    assert len(pdf_files) == 0


def test_find_pdf_files_nonexistent_dir():
    """测试不存在的目录。"""
    pdf_files = find_pdf_files(Path("/nonexistent/path"))
    assert len(pdf_files) == 0


def test_find_pdf_files_with_pdfs(tmp_path):
    """测试包含PDF文件的目录。"""
    # 创建测试PDF文件
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")
    
    pdf_files = find_pdf_files(tmp_path)
    assert len(pdf_files) == 1
    assert pdf_files[0].name == "test.pdf"


def test_find_pdf_files_recursive(tmp_path):
    """测试递归查找PDF文件。"""
    # 创建子目录和PDF文件
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    
    pdf1 = tmp_path / "test1.pdf"
    pdf2 = subdir / "test2.pdf"
    
    pdf1.write_bytes(b"%PDF-1.4\n")
    pdf2.write_bytes(b"%PDF-1.4\n")
    
    pdf_files = find_pdf_files(tmp_path)
    assert len(pdf_files) == 2
    assert any(f.name == "test1.pdf" for f in pdf_files)
    assert any(f.name == "test2.pdf" for f in pdf_files) 