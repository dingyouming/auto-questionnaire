import pytest

from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator


def test_evaluate_radio_answer(answer_evaluator):
    """测试单选题答案评估"""
    score = answer_evaluator.evaluate(
        question_type='radio',
        answer="选项A",
        question="测试问题",
        options=["选项A", "选项B", "选项C"]
    )
    
    assert score.score >= 0 and score.score <= 1
    assert score.details['format'] == 1.0  # 格式正确
    assert "答案" in score.feedback

def test_evaluate_text_answer(answer_evaluator):
    """测试文本题答案评估"""
    score = answer_evaluator.evaluate(
        question_type='text',
        answer="这是一个比较完整的答案，包含了必要的信息和合适的长度。",
        question="请描述你的看法",
        options=None
    )
    
    assert score.score >= 0 and score.score <= 1
    assert score.details['completeness'] > 0
    assert score.details['length'] > 0

def test_evaluate_invalid_answer(answer_evaluator):
    """测试无效答案评估"""
    score = answer_evaluator.evaluate(
        question_type='radio',
        answer="无效选项",
        question="测试问题",
        options=["选项A", "选项B"]
    )
    
    assert score.score < 0.6  # 分数应该较低
    assert "答案需要改进" in score.feedback 