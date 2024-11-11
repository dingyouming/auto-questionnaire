import time

import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.utils.performance_monitor import PerformanceMonitor


@pytest.mark.integration
def test_complete_answer_flow(mock_groq_handler):
    """测试完整的答案生成流程"""
    monitor = PerformanceMonitor()
    auto_filler = AutoFiller(mock_groq_handler, monitor=monitor)
    evaluator = AnswerEvaluator()
    
    # 设置mock返回值
    mock_groq_handler.generate_response.return_value = "1-3年"  # 返回有效的选项
    
    # 创建测试问题
    test_questions = [
        QuestionElement(
            text="你的工作经验是多少年？",
            question_type="radio",
            options=["1-3年", "3-5年", "5年以上"],
            position=(0, 0, 100, 100)
        )
    ]
    
    for question in test_questions:
        start_time = time.time()
        answer, is_cached = auto_filler.generate_answer(question)
        
        elapsed = time.time() - start_time
        
        score = evaluator.evaluate(
            question_type=question.question_type,
            answer=answer,
            question=question.text,
            options=question.options
        )
        monitor.record_answer_quality(score.score)
        
        assert answer, f"问题 '{question.text}' 未生成答案"
        assert score.score >= 0.6, f"答案质量低于阈值: {score.score}"

@pytest.mark.integration
def test_error_handling_flow(mock_groq_handler):
    """测试错误处理流程"""
    monitor = PerformanceMonitor()
    auto_filler = AutoFiller(mock_groq_handler, monitor=monitor)
    
    # 模拟API错误
    mock_groq_handler.generate_response.side_effect = Exception("API错误")
    
    # 创建测试问题
    error_question = QuestionElement(
        text="测试问题",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    
    # 尝试生成答案
    start_time = time.time()
    answer, is_cached = auto_filler.generate_answer(error_question)
    elapsed = time.time() - start_time
    
    # 记录API调用
    monitor.record_api_call(elapsed, bool(answer))
    
    # 验证错误处理
    assert not answer, "应该返回空答案"
    assert not is_cached, "不应该使用缓存"
    
    # 验证错误记录
    stats = monitor.get_statistics()
    assert stats.get('error_rate', 0) > 0, "错误未被记录"