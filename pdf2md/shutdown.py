"""
关机管理模块
"""

import os
import platform
import subprocess
import time
from typing import Optional


class ShutdownManager:
    """关机管理器"""
    
    def __init__(self):
        self.system = platform.system().lower()
    
    def can_shutdown(self) -> bool:
        """检查是否有关机权限"""
        try:
            if self.system == "windows":
                # Windows: 检查是否有关机权限
                result = subprocess.run(
                    ["shutdown", "/?", "/nologo"], 
                    capture_output=True, 
                    text=True
                )
                return result.returncode == 0
            else:
                # Linux/macOS: 检查是否有sudo权限
                result = subprocess.run(
                    ["sudo", "-n", "true"], 
                    capture_output=True
                )
                return result.returncode == 0
        except Exception:
            return False
    
    def shutdown_system(self, delay_minutes: int = 0, force: bool = False) -> bool:
        """
        执行关机操作
        
        Args:
            delay_minutes: 延迟关机时间（分钟），0表示立即关机
            force: 是否强制关机
            
        Returns:
            bool: 是否成功执行关机命令
        """
        try:
            if self.system == "windows":
                return self._shutdown_windows(delay_minutes, force)
            else:
                return self._shutdown_unix(delay_minutes, force)
        except Exception as e:
            print(f"关机失败: {e}")
            return False
    
    def _shutdown_windows(self, delay_minutes: int, force: bool) -> bool:
        """Windows系统关机"""
        cmd = ["shutdown", "/s"]
        
        if delay_minutes > 0:
            cmd.extend(["/t", str(delay_minutes * 60)])
        
        if force:
            cmd.append("/f")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if delay_minutes == 0:
                print("系统将在1分钟内关机...")
            else:
                print(f"系统将在{delay_minutes}分钟后关机...")
            return True
        else:
            print(f"关机命令执行失败: {result.stderr}")
            return False
    
    def _shutdown_unix(self, delay_minutes: int, force: bool) -> bool:
        """Unix系统关机（Linux/macOS）"""
        if delay_minutes == 0:
            cmd = ["sudo", "shutdown", "-h", "now"]
        else:
            cmd = ["sudo", "shutdown", "-h", f"+{delay_minutes}"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if delay_minutes == 0:
                print("系统将立即关机...")
            else:
                print(f"系统将在{delay_minutes}分钟后关机...")
            return True
        else:
            print(f"关机命令执行失败: {result.stderr}")
            return False
    
    def cancel_shutdown(self) -> bool:
        """取消关机计划"""
        try:
            if self.system == "windows":
                cmd = ["shutdown", "/a"]
            else:
                cmd = ["sudo", "shutdown", "-c"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("已取消关机计划")
                return True
            else:
                print("取消关机失败")
                return False
        except Exception as e:
            print(f"取消关机失败: {e}")
            return False
    
    def get_system_info(self) -> dict:
        """获取系统信息"""
        return {
            "system": self.system,
            "platform": platform.platform(),
            "can_shutdown": self.can_shutdown()
        } 