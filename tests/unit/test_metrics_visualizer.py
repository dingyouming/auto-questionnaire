import os
import pytest
from datetime import datetime, timedelta
from auto_questionnaire.monitoring.metrics_visualizer import MetricsVisualizer

@pytest.fixture
def sample_metrics_data():
    base_time = datetime.now()
    return {
        'api_calls': [
            {
                'elapsed': 0.5,
                'success': True,
                'timestamp': (base_time - timedelta(minutes=i)).isoformat()
            } for i in range(5)
        ],
        'answer_quality': [
            {
                'score': 0.7 + i * 0.02,
                'timestamp': (base_time - timedelta(minutes=i)).isoformat()
            } for i in range(5)
        ],
        'cache_hits': [
            {
                'hit': i % 2 == 0,
                'timestamp': (base_time - timedelta(minutes=i)).isoformat()
            } for i in range(5)
        ]
    }

def test_generate_report(sample_metrics_data, tmp_path):
    """测试报告生成"""
    # 使用临时目录进行测试
    report_dir = tmp_path / "reports"
    report_dir.mkdir(exist_ok=True)
    
    visualizer = MetricsVisualizer(output_dir=str(report_dir))
    report_path = visualizer.generate_report(sample_metrics_data)
    
    # 打印调试信息
    print(f"\nReport path: {report_path}")
    print(f"API latency file: {os.path.join(report_path, 'api_latency.png')}")
    print(f"Directory contents: {os.listdir(report_path)}")
    
    # 验证报告文件
    assert os.path.exists(report_path)
    assert os.path.exists(os.path.join(report_path, 'api_latency.png'))
    assert os.path.exists(os.path.join(report_path, 'answer_quality.png'))
    assert os.path.exists(os.path.join(report_path, 'cache_hits.png'))
    assert os.path.exists(os.path.join(report_path, 'report.html'))

def test_empty_metrics(tmp_path):
    """测试空指标处理"""
    # 使用临时目录进行测试
    report_dir = tmp_path / "reports"
    report_dir.mkdir(exist_ok=True)
    
    visualizer = MetricsVisualizer(output_dir=str(report_dir))
    report_path = visualizer.generate_report({})
    
    # 验证空报告
    assert os.path.exists(report_path)
    assert os.path.exists(os.path.join(report_path, 'report.html'))
    
    # 验证报告内容
    with open(os.path.join(report_path, 'report.html'), 'r') as f:
        content = f.read()
        assert 'No metrics data available' in content