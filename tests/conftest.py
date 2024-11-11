import os
import sys
from pathlib import Path

import pytest
from unittest.mock import Mock

# 获取项目根目录
project_root = Path(__file__).parent.parent

# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(project_root))

# 统一导入
from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.ai.prompt_builder import PromptBuilder
from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.utils.performance_monitor import PerformanceMonitor


@pytest.fixture
def mock_groq_handler():
    # 创建 mock 对象
    return Mock(spec=GroqHandler)

@pytest.fixture
def auto_filler(mock_groq_handler):
    return AutoFiller(mock_groq_handler)

@pytest.fixture
def answer_evaluator():
    return AnswerEvaluator()

@pytest.fixture
def prompt_builder():
    return PromptBuilder()

@pytest.fixture
def performance_monitor():
    return PerformanceMonitor()