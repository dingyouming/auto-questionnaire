from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator
from auto_questionnaire.ai.groq_handler import GroqHandler

def test_features():
    # 1. 直接使用类名，等待自动提示或按 Ctrl + Space
    groq_handler = GroqHandler()
    
    # 2. 使用 from 导入，输入 auto_q 后按 Ctrl + Space
    from auto_questionnaire.utils.auto_fill import AutoFiller

    # 3. 使用未导入的类，将光标放在类名上按 Ctrl + .
    evaluator = AnswerEvaluator() 