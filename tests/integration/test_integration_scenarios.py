import time

import groq
import matplotlib.pyplot as plt
import pandas as pd
import pytest
import seaborn as sns

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.answer_evaluator import AnswerEvaluator
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.utils.performance_monitor import PerformanceMonitor
