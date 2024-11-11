import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from auto_questionnaire.utils.request_queue import RequestQueue

def test_rate_limiting():
    """测试请求限流"""
    queue = RequestQueue(rate_limit=3, time_window=1)
    
    def dummy_request():
        return "success"
    
    start_time = time.time()
    results = []
    
    for _ in range(5):
        result = queue.add_request(dummy_request)
        results.append(result)
        
    end_time = time.time()
    
    execution_time = end_time - start_time
    assert execution_time >= 1, f"执行时间应该大于1秒，实际为 {execution_time} 秒"
    assert all(result == "success" for result in results)
    assert len(results) == 5

@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求处理"""
    queue = RequestQueue(max_concurrent=3)
    
    def slow_request(delay):
        time.sleep(delay)
        return f"completed after {delay}s"
    
    requests = [
        lambda: slow_request(0.1)
        for _ in range(3)
    ]
    
    start_time = time.time()
    results = await queue.batch_requests(requests)
    end_time = time.time()
    
    execution_time = end_time - start_time
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    assert all("completed after 0.1s" in result for result in results)
    assert execution_time < 0.2, f"执行时间应该小于0.2秒，实际为 {execution_time} 秒"

@pytest.mark.asyncio
async def test_mixed_requests():
    """测试混合同步请求"""
    queue = RequestQueue(max_concurrent=3, rate_limit=5)
    
    def sync_request():
        time.sleep(0.1)
        return "sync completed"
    
    # 只使用同步请求
    requests = [sync_request for _ in range(3)]
    
    start_time = time.time()
    results = await queue.batch_requests(requests)
    end_time = time.time()
    
    execution_time = end_time - start_time
    assert len(results) == 3
    assert all(result == "sync completed" for result in results)
    assert execution_time < 0.2, f"执行时间应该小于0.2秒，实际为 {execution_time} 秒"

@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    queue = RequestQueue(max_concurrent=2)
    
    def failing_request():
        raise ValueError("测试错误")
        
    def success_request():
        return "success"
    
    requests = [failing_request, success_request]
    
    results = await queue.batch_requests(requests)
    assert len(results) == 2
    assert results[0] is None  # 失败的请求
    assert results[1] == "success"  # 成功的请求