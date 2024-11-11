import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.auto_fill import AutoFiller


@pytest.mark.concurrent
def test_concurrent_requests():
    """测试并发请求处理"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    
    def make_request(question_text: str):
        question = QuestionElement(
            text=question_text,
            question_type="text",
            position=(0, 0, 100, 100)
        )
        return auto_filler.generate_answer(question)
    
    # 创建多个并发请求
    questions = [f"并发测试问题{i}" for i in range(5)]
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request, q) for q in questions]
        results = [f.result() for f in as_completed(futures)]
    
    # 验证所有请求都得到了答案
    assert all(answer for answer, _ in results)

@pytest.mark.concurrent
def test_thread_safety():
    """测试线程安全性"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    
    # 用于存储测试结果
    results = []
    lock = threading.Lock()
    
    def worker():
        question = QuestionElement(
            text="线程安全测试",
            question_type="text",
            position=(0, 0, 100, 100)
        )
        answer, is_cached = auto_filler.generate_answer(question)
        with lock:
            results.append(answer)
    
    # 创建多个线程
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # 验证所有线程都得到了答案
    assert len(results) == 5
    assert all(results) 