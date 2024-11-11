import pytest
from unittest.mock import Mock
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.utils.cache_manager import CacheManager
from auto_questionnaire.utils.request_queue import RequestQueue
from auto_questionnaire.utils.answer_validator import AnswerValidator
from auto_questionnaire.utils.performance_monitor import PerformanceMonitor
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.ai.groq_handler import GroqHandler

@pytest.fixture
def mock_groq_handler():
    handler = Mock(spec=GroqHandler)
    handler.generate_response.return_value = "测试答案"
    return handler

@pytest.fixture
def temp_cache_file(tmp_path):
    """创建临时缓存文件路径"""
    return str(tmp_path / "test_cache.json")

@pytest.fixture
def cache_manager(temp_cache_file):
    """创建缓存管理器"""
    return CacheManager(temp_cache_file)

@pytest.fixture
def request_queue():
    """创建请求队列"""
    return RequestQueue(max_concurrent=2)

@pytest.fixture
def answer_validator():
    """创建答案验证器"""
    return AnswerValidator(similarity_threshold=0.6)

@pytest.mark.integration
def test_enhanced_workflow(mock_groq_handler, temp_cache_file, 
                         cache_manager, request_queue, answer_validator):
    """测试增强后的完整工作流程"""
    monitor = PerformanceMonitor()
    
    auto_filler = AutoFiller(
        groq_handler=mock_groq_handler,
        cache_file=temp_cache_file,
        monitor=monitor,
        max_retries=3
    )
    
    # 创建测试问题
    questions = [
        QuestionElement(
            text="测试问题1",
            question_type="radio",
            options=["选项A", "选项B"],
            position=(0, 0, 100, 100)
        ),
        QuestionElement(
            text="测试问题2",
            question_type="text",
            position=(0, 0, 100, 100)
        )
    ]
    
    # 预热缓存
    cache_manager.warm_up_cache(questions[:1], mock_groq_handler)
    
    # 批量生成答案
    answers = auto_filler.batch_generate_answers(questions)
    
    # 验证结果
    for question, (answer, is_cached) in zip(questions, answers):
        assert answer, f"问题 '{question.text}' 未生成答案"
        assert answer_validator.validate_and_store_answer(
            question.question_type,
            question.text,
            answer
        ), "答案验证失败"
        
    # 验证性能监控
    stats = monitor.get_statistics()
    assert 'total_calls' in stats
    assert 'cache_hits' in stats
    
    # 清理缓存
    cache_manager.clean_cache() 