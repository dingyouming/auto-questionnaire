import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.utils.performance_monitor import PerformanceMonitor


@pytest.mark.performance
def test_response_time():
    """测试响应时间"""
    groq_handler = GroqHandler()
    monitor = PerformanceMonitor()
    
    start_time = time.time()
    response = groq_handler.generate_response(
        "这是一个测试问题",
        "这是上下文"
    )
    elapsed = time.time() - start_time
    
    monitor.record_api_call(elapsed, bool(response))
    assert elapsed < 5.0, "响应时间超过5秒"

@pytest.mark.performance
def test_concurrent_requests():
    """测试并发请求处理"""
    groq_handler = GroqHandler()
    monitor = PerformanceMonitor()
    
    def make_request(question: str) -> float:
        start = time.time()
        response = groq_handler.generate_response(question, None)
        elapsed = time.time() - start
        monitor.record_api_call(elapsed, bool(response))
        return elapsed
    
    questions = [f"测试问题{i}" for i in range(5)]
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request, q) for q in questions]
        results = [f.result() for f in as_completed(futures)]
    
    avg_time = sum(results) / len(results)
    assert avg_time < 10.0, "平均响应时间过长"

@pytest.mark.performance
def test_cache_performance():
    """测试缓存性能"""
    groq_handler = GroqHandler()
    cache_file = "test_cache.json"
    auto_filler = AutoFiller(groq_handler, cache_file=cache_file)
    monitor = PerformanceMonitor()
    
    # 创建测试问题
    test_element = QuestionElement(
        text="缓存测试问题",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    
    try:
        # 第一次请求（无缓存）
        start = time.time()
        answer1, is_cached1 = auto_filler.generate_answer(test_element)
        first_request_time = time.time() - start
        
        # 确保缓存已保存
        assert os.path.exists(cache_file), "缓存文件未创建"
        
        # 第二次请求（应该命中缓存）
        start = time.time()
        answer2, is_cached2 = auto_filler.generate_answer(test_element)
        cached_request_time = time.time() - start
        
        assert not is_cached1, "首次请求不应该命中缓存"
        assert is_cached2, "第二次请求应该命中缓存"
        assert cached_request_time < first_request_time, "缓存请求应该更快"
        
    finally:
        # 清理测试缓存文件
        if os.path.exists(cache_file):
            os.remove(cache_file) 