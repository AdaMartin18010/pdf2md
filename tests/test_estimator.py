"""
时间预估测试
"""

import tempfile
from pathlib import Path
from pdf2md.estimator import TimeEstimator


class TestTimeEstimator:
    """时间预估器测试类"""
    
    def test_init(self):
        """测试初始化"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        assert estimator.avg_time_per_mb == 2.0
        assert estimator.min_time_per_file == 1.0
        assert estimator.max_time_per_file == 60.0
    
    def test_estimate_file_time_small_file(self):
        """测试小文件时间预估"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            file_path = Path(f.name)
        
        try:
            estimated_time = estimator.estimate_file_time(file_path)
            # 小文件应该使用最小时间
            assert estimated_time == 1.0
        finally:
            file_path.unlink()
    
    def test_estimate_file_time_large_file(self):
        """测试大文件时间预估"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # 创建10MB的文件
            f.write(b"x" * (10 * 1024 * 1024))
            file_path = Path(f.name)
        
        try:
            estimated_time = estimator.estimate_file_time(file_path)
            # 10MB * 2秒/MB = 20秒，应该在范围内
            assert 1.0 <= estimated_time <= 60.0
        finally:
            file_path.unlink()
    
    def test_estimate_file_time_very_large_file(self):
        """测试超大文件时间预估（应该被限制）"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # 创建100MB的文件
            f.write(b"x" * (100 * 1024 * 1024))
            file_path = Path(f.name)
        
        try:
            estimated_time = estimator.estimate_file_time(file_path)
            # 应该被限制在最大时间
            assert estimated_time == 60.0
        finally:
            file_path.unlink()
    
    def test_estimate_total_time_empty_list(self):
        """测试空列表的总时间预估"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        result = estimator.estimate_total_time([], workers=1)
        
        assert result['total_time'] == 0
        assert result['avg_time_per_file'] == 0
        assert result['total_size_mb'] == 0
        assert result['files_count'] == 0
        assert result['workers'] == 1
    
    def test_estimate_total_time_with_files(self):
        """测试有文件的总时间预估"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        # 创建测试文件
        files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"x" * (1024 * 1024))  # 1MB
                files.append(Path(f.name))
        
        try:
            result = estimator.estimate_total_time(files, workers=1)
            
            assert result['files_count'] == 3
            assert result['total_size_mb'] == 3.0
            assert result['workers'] == 1
            assert result['total_time'] > 0
            assert result['avg_time_per_file'] > 0
        finally:
            for file_path in files:
                file_path.unlink()
    
    def test_estimate_total_time_with_workers(self):
        """测试多工作进程的时间预估"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        # 创建测试文件
        files = []
        for i in range(4):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"x" * (1024 * 1024))  # 1MB
                files.append(Path(f.name))
        
        try:
            # 单进程
            result_single = estimator.estimate_total_time(files, workers=1)
            # 多进程
            result_multi = estimator.estimate_total_time(files, workers=4)
            
            # 多进程应该比单进程快
            assert result_multi['total_time'] < result_single['total_time']
            assert result_multi['workers'] == 4
        finally:
            for file_path in files:
                file_path.unlink()
    
    def test_format_time(self):
        """测试时间格式化"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        # 测试秒
        assert "30.0秒" in estimator.format_time(30)
        
        # 测试分钟
        assert "分钟" in estimator.format_time(90)
        
        # 测试小时
        assert "小时" in estimator.format_time(7200)
    
    def test_print_estimation(self, capsys):
        """测试打印预估信息"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        
        # 创建测试文件
        files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"x" * (1024 * 1024))  # 1MB
                files.append(Path(f.name))
        
        try:
            estimator.print_estimation(files, workers=2)
            captured = capsys.readouterr()
            
            assert "时间预估:" in captured.out
            assert "文件数量: 2" in captured.out
            assert "并发数: 2" in captured.out
        finally:
            for file_path in files:
                file_path.unlink()
    
    def test_print_estimation_empty(self, capsys):
        """测试空列表的预估打印"""
        config = {
            'time_estimation': {
                'avg_time_per_mb': 2.0,
                'min_time_per_file': 1.0,
                'max_time_per_file': 60.0
            }
        }
        
        estimator = TimeEstimator(config)
        estimator.print_estimation([], workers=1)
        captured = capsys.readouterr()
        
        assert "没有找到PDF文件" in captured.out 