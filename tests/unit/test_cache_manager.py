import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock
from auto_questionnaire.utils.cache_manager import CacheManager
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.ai.groq_handler import GroqHandler

@pytest.fixture
def mock_groq_handler():
    handler = Mock(spec=GroqHandler)
    handler.generate_response.return_value = "测试答案"
    return handler

@pytest.fixture
def temp_cache_file(tmp_path):
    return str(tmp_path / "test_cache.json")

def test_cache_warmup(temp_cache_file, mock_groq_handler):
    """测试缓存预热"""
    cache_manager = CacheManager(temp_cache_file)
    
    # 创建常见问题列表
    common_questions = [
        QuestionElement(
            text="常见问题1",
            question_type="text",
            position=(0, 0, 100, 100)
        ),
        QuestionElement(
            text="常见问题2",
            question_type="radio",
            options=["选项A", "选项B"],
            position=(0, 0, 100, 100)
        )
    ]
    
    # 预热缓存
    cache_manager.warm_up_cache(common_questions, mock_groq_handler)
    
    # 验证缓存文件存在且包含预期内容
    assert os.path.exists(temp_cache_file)
    loaded_cache = cache_manager._load_cache()
    assert len(loaded_cache) == 2

def test_cache_cleanup(temp_cache_file):
    """测试缓存清理"""
    cache_manager = CacheManager(temp_cache_file, ttl=timedelta(hours=1))
    
    # 添加一些测试缓存数据
    old_time = (datetime.now() - timedelta(hours=2)).isoformat()
    new_time = datetime.now().isoformat()
    
    cache_manager.cache = {
        "old_key": {"answer": "旧答案", "timestamp": old_time},
        "new_key": {"answer": "新答案", "timestamp": new_time}
    }
    cache_manager._save_cache()
    
    # 清理缓存
    cache_manager.clean_cache(max_size=1)
    
    # 验证结果
    assert len(cache_manager.cache) == 1
    assert "new_key" in cache_manager.cache
    assert "old_key" not in cache_manager.cache 