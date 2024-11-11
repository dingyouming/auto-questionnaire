from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import json
import os
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..ai.groq_handler import GroqHandler
from ..parser.element_finder import QuestionElement


class AutoFiller:
    def __init__(self, groq_handler, cache_file: Optional[str] = None, 
                 cache_ttl: Optional[timedelta] = None, 
                 monitor: Optional['PerformanceMonitor'] = None,
                 max_retries: int = 3,
                 max_workers: int = 3):
        self.ai_handler = groq_handler
        self.cache_file = cache_file
        self.cache_ttl = cache_ttl or timedelta(hours=24)
        self.valid_question_types = {'text', 'radio', 'checkbox'}
        self.monitor = monitor
        self.cache = self._load_cache() if cache_file else {}
        self.max_retries = max_retries
        self.max_workers = max_workers
        
    def _save_cache(self):
        if not self.cache_file:
            return
            
        try:
            cache_dir = os.path.dirname(self.cache_file)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
                
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
            
    def _generate_cache_key(self, question_element) -> str:
        options = getattr(question_element, 'options', [])
        options_str = ','.join(options) if options else ''
        return f"{question_element.question_type}:{question_element.text}:{options_str}"
        
    def generate_answer(self, question_element) -> Tuple[str, bool]:
        try:
            # 1. 验证问题类型
            if question_element.question_type not in self.valid_question_types:
                if self.monitor:
                    self.monitor.record_error("无效的问题类型")
                return "", False
                
            # 2. 验证问题内容
            if not question_element.text.strip():
                if self.monitor:
                    self.monitor.record_error("空问题")
                return "", False
                
            # 3. 验证选项（对于单选和多选题）
            if question_element.question_type in ['radio', 'checkbox']:
                if not hasattr(question_element, 'options') or not question_element.options:
                    if self.monitor:
                        self.monitor.record_error("无效的选项列表")
                    return "", False
                    
            # 4. 检查缓存
            cache_key = self._generate_cache_key(question_element)
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if not self._is_cache_expired(cache_entry):
                    if self.monitor:
                        self.monitor.record_cache_access(True)
                    return cache_entry['answer'], True
                    
            # 5. 生成答案
            try:
                answer = self.ai_handler.generate_response(
                    question_element.text,
                    context=None
                )
                
                # 6. 验证答案
                if not answer or not answer.strip():
                    raise Exception("生成的答案为空")
                    
                # 7. 处理单选题答案
                if question_element.question_type == 'radio' and hasattr(question_element, 'options'):
                    if answer not in question_element.options:
                        if len(question_element.options) > 0:
                            answer = question_element.options[0]
                        else:
                            return "", False
                            
                # 8. 处理多选题答案
                elif question_element.question_type == 'checkbox' and hasattr(question_element, 'options'):
                    selected = [opt for opt in answer.split(',') if opt.strip() in question_element.options]
                    if not selected:
                        return "", False
                    answer = ','.join(selected)
                    
                # 9. 更新缓存
                if answer:
                    self.cache[cache_key] = {
                        'answer': answer,
                        'timestamp': datetime.now().isoformat()
                    }
                    self._save_cache()
                    if self.monitor:
                        self.monitor.record_cache_access(False)
                        self.monitor.record_api_call(0.1, True)
                        
                return answer, False
                
            except Exception as e:
                logger.error(f"API调用失败: {str(e)}")
                if self.monitor:
                    self.monitor.record_error(str(e))
                    self.monitor.record_api_call(0.1, False)
                return "", False
                
        except Exception as e:
            logger.error(f"生成答案失败: {str(e)}")
            if self.monitor:
                self.monitor.record_error(str(e))
            return "", False
            
    def _is_cache_expired(self, cache_entry: dict) -> bool:
        if 'timestamp' not in cache_entry:
            return True
        cached_time = datetime.fromisoformat(cache_entry['timestamp'])
        return datetime.now() - cached_time > self.cache_ttl
        
    def _load_cache(self) -> dict:
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载缓存失败: {str(e)}")
            return {}
            
    def _record_error(self, error_message: str):
        if hasattr(self, 'monitor'):
            self.monitor.record_error(error_message)
            
    def batch_generate_answers(self, questions: List[QuestionElement]) -> List[Tuple[str, bool]]:
        """批量生成答案"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.generate_answer_with_retry, q) 
                for q in questions
            ]
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"批量处理失败: {str(e)}")
                    results.append(("", False))
        return results
        
    def generate_answer_with_retry(self, question_element, 
                                 current_retry: int = 0) -> Tuple[str, bool]:
        """带重试机制的答案生成"""
        try:
            answer, is_cached = self.generate_answer(question_element)
            if answer or is_cached:
                return answer, is_cached
                
            # 如果生成失败且未达到最大重试次数，进行重试
            if current_retry < self.max_retries:
                logger.warning(f"第 {current_retry + 1} 次重试生成答案")
                return self.generate_answer_with_retry(
                    question_element, 
                    current_retry + 1
                )
            return "", False
            
        except Exception as e:
            logger.error(f"生成答案失败 (重试 {current_retry}): {str(e)}")
            if current_retry < self.max_retries:
                return self.generate_answer_with_retry(
                    question_element, 
                    current_retry + 1
                )
            return "", False