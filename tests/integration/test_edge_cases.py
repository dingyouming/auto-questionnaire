import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator
from auto_questionnaire.utils.auto_fill import AutoFiller


@pytest.mark.edge
def test_empty_inputs():
    """测试空输入处理"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    evaluator = AnswerEvaluator()
    
    # 空问题
    empty_question = QuestionElement(
        text="",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    answer, is_cached = auto_filler.generate_answer(empty_question)
    assert answer == "", "空问题应该返回空答案"
    
    # 空选项
    empty_options = QuestionElement(
        text="测试问题",
        question_type="radio",
        options=[],
        position=(0, 0, 100, 100)
    )
    answer, is_cached = auto_filler.generate_answer(empty_options)
    assert answer == "", "无选项的单选题应该返回空答案"

@pytest.mark.edge
def test_extreme_lengths():
    """测试极端长度"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    
    # 超长问题
    long_question = QuestionElement(
        text="测" * 1000,  # 1000个字
        question_type="text",
        position=(0, 0, 100, 100)
    )
    answer, _ = auto_filler.generate_answer(long_question)
    assert len(answer) <= 500, "答案长度应该在限制范围内"
    
    # 大量选项
    many_options = QuestionElement(
        text="测试问题",
        question_type="checkbox",
        options=[f"选项{i}" for i in range(100)],
        position=(0, 0, 100, 100)
    )
    answer, _ = auto_filler.generate_answer(many_options)
    selected = answer.split(',') if answer else []
    assert len(selected) <= 10, "多选答案不应选择过多选项"

@pytest.mark.edge
def test_special_characters():
    """测试特殊字符处理"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    
    special_chars = QuestionElement(
        text=r"测试!@#$%^&*()_+{}|:\"<>?[]\;',./～！@#￥%……&*()——+{}|：\"《》？【】、；'，。/",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    answer, _ = auto_filler.generate_answer(special_chars)
    assert answer, "特殊字符不应影响答案生成"

@pytest.mark.edge
def test_invalid_question_type():
    """测试无效问题类型"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    
    invalid_type = QuestionElement(
        text="测试问题",
        question_type="invalid_type",
        position=(0, 0, 100, 100)
    )
    answer, _ = auto_filler.generate_answer(invalid_type)
    assert answer == "", "无效问题类型应该返回空答案"

@pytest.mark.edge
def test_unicode_handling():
    """测试Unicode字符处理"""
    groq_handler = GroqHandler()
    auto_filler = AutoFiller(groq_handler)
    
    unicode_text = QuestionElement(
        text="测试🌟🌈🎉✨⭐️👍",  # Emoji和特殊Unicode字符
        question_type="text",
        position=(0, 0, 100, 100)
    )
    answer, _ = auto_filler.generate_answer(unicode_text)
    assert answer, "Unicode字符不应影响答案生成"