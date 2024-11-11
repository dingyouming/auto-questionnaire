import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool

import pytest

from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.parser.element_finder import QuestionElement
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.utils.performance_monitor import PerformanceMonitor
