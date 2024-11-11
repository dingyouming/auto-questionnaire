from typing import List
from loguru import logger

from .ai.groq_handler import GroqHandler
from .parser.ui_parser import QuestionnaireParser
from .utils.auto_fill import AutoFiller
from .utils.screenshot import take_screenshot
from .utils.cache_manager import CacheManager
from .utils.request_queue import RequestQueue
from .utils.answer_validator import AnswerValidator
from .utils.performance_monitor import PerformanceMonitor
from .utils.common_questions import load_common_questions


def main():
    try:
        # 初始化组件
        groq_handler = GroqHandler(api_key=ModelConfig.GROQ_API_KEY)
        cache_manager = CacheManager("data/cache.json")
        request_queue = RequestQueue()
        answer_validator = AnswerValidator()
        monitor = PerformanceMonitor()
        
        auto_filler = AutoFiller(
            groq_handler=groq_handler,
            cache_file="data/cache.json",
            monitor=monitor,
            max_retries=3,
            max_workers=3
        )
        
        # 获取并解析问卷
        screenshot_path = take_screenshot()
        parser = QuestionnaireParser()
        elements = parser.parse_page(screenshot_path)
        
        # 预热缓存
        common_questions = load_common_questions()  # 需要实现此函数
        cache_manager.warm_up_cache(common_questions, groq_handler)
        
        # 批量处理问题
        all_questions = []
        for element_type, elements_list in elements.items():
            all_questions.extend(elements_list)
            
        answers = auto_filler.batch_generate_answers(all_questions)
        
        # 处理答案
        for question, (answer, is_cached) in zip(all_questions, answers):
            if answer:
                # 验证答案一致性
                if answer_validator.validate_and_store_answer(
                    question.question_type,
                    question.text,
                    answer
                ):
                    print(f"问题类型: {question.question_type}")
                    print(f"问题: {question.text}")
                    print(f"生成的答案: {answer}")
                    print(f"使用缓存: {is_cached}\n")
                    
        # 清理缓存
        cache_manager.clean_cache()
        
        # 输出性能统计
        stats = monitor.get_statistics()
        logger.info(f"性能统计: {stats}")
        
    except Exception as e:
        logger.error(f"程序执行错误: {e}")

if __name__ == "__main__":
    main() 