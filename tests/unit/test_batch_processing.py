import pytest
from unittest.mock import Mock, patch
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.auto_fill import AutoFiller

@pytest.fixture
def mock_groq_handler():
    handler = Mock()
    handler.generate_response.side_effect = ["答案1", "答案2", "答案3"]
    return handler

def test_batch_generate_answers(mock_groq_handler):
    """测试批量生成答案"""
    auto_filler = AutoFiller(mock_groq_handler, max_workers=2)
    
    # 创建测试问题列表
    questions = [
        QuestionElement(
            text=f"测试问题{i}",
            question_type="text",
            position=(0, 0, 100, 100)
        ) for i in range(3)
    ]
    
    # 测试批量生成
    results = auto_filler.batch_generate_answers(questions)
    
    assert len(results) == 3, "应返回所有问题的答案"
    assert all(answer for answer, _ in results), "所有问题都应该有答案"
    assert mock_groq_handler.generate_response.call_count == 3

def test_retry_mechanism(mock_groq_handler):
    """测试重试机制"""
    # 模拟前两次失败，第三次成功
    mock_groq_handler.generate_response.side_effect = [
        Exception("API错误"),
        Exception("API错误"),
        "最终答案"
    ]
    
    auto_filler = AutoFiller(mock_groq_handler, max_retries=3)
    question = QuestionElement(
        text="需要重试的问题",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    
    answer, is_cached = auto_filler.generate_answer_with_retry(question)
    
    assert answer == "最终答案", "应该返回最后一次成功的答案"
    assert mock_groq_handler.generate_response.call_count == 3 