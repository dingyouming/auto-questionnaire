from unittest.mock import Mock

import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator
from auto_questionnaire.utils.auto_fill import AutoFiller


@pytest.mark.integration
def test_complete_workflow():
    """测试完整工作流程"""
    # 创建 mock GroqHandler
    mock_handler = Mock(spec=GroqHandler)
    mock_handler.generate_response.return_value = "这是一个测试回答"
    
    # 初始化组件
    auto_filler = AutoFiller(mock_handler)
    evaluator = AnswerEvaluator()
    
    # 创建测试问题
    test_element = QuestionElement(
        text="你对人工智能的未来发展有什么看法？",
        question_type="text",
        position=(0, 0, 100, 100)
    )
    
    # 生成答案
    answer, is_cached = auto_filler.generate_answer(test_element)
    assert answer == "这是一个测试回答", "答案生成失败"
    
    # 验证 mock 被正确调用
    mock_handler.generate_response.assert_called_once()
    
    # 评估答案
    score = evaluator.evaluate_answer(
        question_type=test_element.question_type,
        answer=answer,
        question=test_element.text
    )
    assert score >= 0.6, "答案质量不达标" 