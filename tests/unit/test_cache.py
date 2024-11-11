import json
import os
import time
from datetime import timedelta

import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.auto_fill import AutoFiller


@pytest.fixture
def temp_cache_file(tmp_path):
    """创建临时缓存文件"""
    cache_file = tmp_path / "test_cache.json"
    return str(cache_file)

def test_cache_persistence(temp_cache_file):
    """测试缓存持久化"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler, cache_file=temp_cache_file)
    
    # 创建测试问题
    test_question = QuestionElement(
        text="测试缓存问题",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    
    # 首次生成答案
    answer1, is_cached1 = auto_filler.generate_answer(test_question)
    assert not is_cached1, "首次生成不应使用缓存"
    
    # 验证缓存文件存在
    assert os.path.exists(temp_cache_file)
    
    # 创建新的AutoFiller实例
    new_filler = AutoFiller(groq_handler, cache_file=temp_cache_file)
    answer2, is_cached2 = new_filler.generate_answer(test_question)
    
    assert is_cached2, "应该使用缓存"
    assert answer1 == answer2, "缓存答案应该一致"

def test_cache_expiration(temp_cache_file):
    """测试缓存过期"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler, cache_file=temp_cache_file)
    auto_filler.cache_ttl = timedelta(seconds=1)  # 设置1秒过期
    
    test_question = QuestionElement(
        text="测试过期问题",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    
    # 首次生成
    answer1, _ = auto_filler.generate_answer(test_question)
    
    # 等待缓存过期
    time.sleep(1.1)
    
    # 再次生成
    answer2, is_cached = auto_filler.generate_answer(test_question)
    assert not is_cached, "过期缓存不应被使用"

def test_cache_invalidation(temp_cache_file):
    """测试缓存失效"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler, cache_file=temp_cache_file)
    
    # 写入无效的缓存数据
    with open(temp_cache_file, 'w') as f:
        json.dump({"invalid": "data"}, f)
    
    # 应该能够正常处理无效缓存
    test_question = QuestionElement(
        text="测试问题",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    answer, is_cached = auto_filler.generate_answer(test_question)
    assert not is_cached, "无效缓存应该被忽略"
    assert answer, "应该能生成新答案" 