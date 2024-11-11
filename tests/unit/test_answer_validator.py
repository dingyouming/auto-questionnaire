import pytest
from auto_questionnaire.utils.answer_validator import AnswerValidator

def test_answer_consistency():
    """测试答案一致性检查"""
    validator = AnswerValidator(similarity_threshold=0.6)
    
    # 测试选择题一致性
    assert validator.check_answer_consistency(
        question_type="radio",
        question="测试问题",
        answer="选项A",
        previous_answers=["选项A", "选项B"]
    )
    
    # 测试文本答案相似度 - 相似的答案
    assert validator.check_answer_consistency(
        question_type="text",
        question="描述问题",
        answer="这是一个很好的答案",
        previous_answers=["这是一个不错的答案"]
    )
    
    # 测试文本答案相似度 - 不相似的答案
    assert not validator.check_answer_consistency(
        question_type="text",
        question="描述问题",
        answer="完全不相关的回答",
        previous_answers=["这是一个很好的答案"]
    )

def test_answer_storage():
    """测试答案存储和验证"""
    validator = AnswerValidator()
    
    # 存储并验证第一个答案
    assert validator.validate_and_store_answer(
        question_type="text",
        question="测试问题",
        answer="第一个答案"
    )
    
    # 存储并验证相似的答案
    assert validator.validate_and_store_answer(
        question_type="text",
        question="测试问题",
        answer="第一个答案的变体"
    )
    
    # 验证不相似的答案
    assert not validator.validate_and_store_answer(
        question_type="text",
        question="测试问题",
        answer="完全不同的答案"
    ) 