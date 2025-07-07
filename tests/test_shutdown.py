"""
关机功能测试
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from pdf2md.shutdown import ShutdownManager


class TestShutdownManager:
    """关机管理器测试类"""
    
    def test_init(self):
        """测试初始化"""
        manager = ShutdownManager()
        assert hasattr(manager, 'system')
        assert manager.system in ['windows', 'linux', 'darwin']
    
    @patch('platform.system')
    def test_windows_system(self, mock_system):
        """测试Windows系统检测"""
        mock_system.return_value = "Windows"
        manager = ShutdownManager()
        assert manager.system == "windows"
    
    @patch('platform.system')
    def test_linux_system(self, mock_system):
        """测试Linux系统检测"""
        mock_system.return_value = "Linux"
        manager = ShutdownManager()
        assert manager.system == "linux"
    
    @patch('subprocess.run')
    def test_can_shutdown_windows_success(self, mock_run):
        """测试Windows关机权限检查成功"""
        mock_run.return_value.returncode = 0
        
        with patch('platform.system', return_value="Windows"):
            manager = ShutdownManager()
            assert manager.can_shutdown() is True
    
    @patch('subprocess.run')
    def test_can_shutdown_windows_failure(self, mock_run):
        """测试Windows关机权限检查失败"""
        mock_run.return_value.returncode = 1
        
        with patch('platform.system', return_value="Windows"):
            manager = ShutdownManager()
            assert manager.can_shutdown() is False
    
    @patch('subprocess.run')
    def test_can_shutdown_linux_success(self, mock_run):
        """测试Linux关机权限检查成功"""
        mock_run.return_value.returncode = 0
        
        with patch('platform.system', return_value="Linux"):
            manager = ShutdownManager()
            assert manager.can_shutdown() is True
    
    @patch('subprocess.run')
    def test_can_shutdown_linux_failure(self, mock_run):
        """测试Linux关机权限检查失败"""
        mock_run.return_value.returncode = 1
        
        with patch('platform.system', return_value="Linux"):
            manager = ShutdownManager()
            assert manager.can_shutdown() is False
    
    @patch('subprocess.run')
    def test_shutdown_windows_immediate(self, mock_run):
        """测试Windows立即关机"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        with patch('platform.system', return_value="Windows"):
            manager = ShutdownManager()
            result = manager.shutdown_system(delay_minutes=0, force=False)
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_shutdown_windows_delayed(self, mock_run):
        """测试Windows延迟关机"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        with patch('platform.system', return_value="Windows"):
            manager = ShutdownManager()
            result = manager.shutdown_system(delay_minutes=5, force=False)
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_shutdown_linux_immediate(self, mock_run):
        """测试Linux立即关机"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        with patch('platform.system', return_value="Linux"):
            manager = ShutdownManager()
            result = manager.shutdown_system(delay_minutes=0, force=False)
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_shutdown_linux_delayed(self, mock_run):
        """测试Linux延迟关机"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        with patch('platform.system', return_value="Linux"):
            manager = ShutdownManager()
            result = manager.shutdown_system(delay_minutes=5, force=False)
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_shutdown_failure(self, mock_run):
        """测试关机失败"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "权限不足"
        
        with patch('platform.system', return_value="Windows"):
            manager = ShutdownManager()
            result = manager.shutdown_system(delay_minutes=0, force=False)
            assert result is False
    
    @patch('subprocess.run')
    def test_cancel_shutdown_windows(self, mock_run):
        """测试Windows取消关机"""
        mock_run.return_value.returncode = 0
        
        with patch('platform.system', return_value="Windows"):
            manager = ShutdownManager()
            result = manager.cancel_shutdown()
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_cancel_shutdown_linux(self, mock_run):
        """测试Linux取消关机"""
        mock_run.return_value.returncode = 0
        
        with patch('platform.system', return_value="Linux"):
            manager = ShutdownManager()
            result = manager.cancel_shutdown()
            assert result is True
            mock_run.assert_called_once()
    
    def test_get_system_info(self):
        """测试获取系统信息"""
        manager = ShutdownManager()
        info = manager.get_system_info()
        
        assert 'system' in info
        assert 'platform' in info
        assert 'can_shutdown' in info
        assert isinstance(info['can_shutdown'], bool) 