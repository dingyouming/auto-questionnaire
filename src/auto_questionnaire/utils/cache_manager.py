from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os
from loguru import logger
from auto_questionnaire.parser.element_finder import QuestionElement

class CacheManager:
    def __init__(self, cache_file: str, ttl: timedelta = timedelta(hours=24)):
        self.cache_file = cache_file
        self.ttl = ttl
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载缓存失败: {str(e)}")
            return {}
            
    def _save_cache(self) -> None:
        """保存缓存"""
        try:
            cache_dir = os.path.dirname(self.cache_file)
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
            
    def warm_up_cache(self, common_questions: List[QuestionElement], 
                     ai_handler) -> None:
        """预热缓存"""
        logger.info("开始预热缓存...")
        for question in common_questions:
            cache_key = self._generate_cache_key(question)
            if cache_key not in self.cache:
                try:
                    answer = ai_handler.generate_response(
                        question.text,
                        context=None
                    )
                    if answer:
                        self.cache[cache_key] = {
                            'answer': answer,
                            'timestamp': datetime.now().isoformat()
                        }
                except Exception as e:
                    logger.error(f"缓存预热失败: {str(e)}")
        self._save_cache()
        logger.info("缓存预热完成")
        
    def clean_cache(self, max_size: int = 1000) -> None:
        """清理过期和超量的缓存"""
        current_time = datetime.now()
        # 清理过期缓存
        expired_keys = [
            key for key, value in self.cache.items()
            if self._is_cache_expired(value, current_time)
        ]
        for key in expired_keys:
            del self.cache[key]
            
        # 如果缓存仍然过大，删除最旧的条目
        if len(self.cache) > max_size:
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: datetime.fromisoformat(x[1]['timestamp'])
            )
            self.cache = dict(sorted_items[-max_size:])
            
        self._save_cache()
        
    def _generate_cache_key(self, question: QuestionElement) -> str:
        """生成缓存键"""
        options = getattr(question, 'options', [])
        options_str = ','.join(options) if options else ''
        return f"{question.question_type}:{question.text}:{options_str}"
        
    def _is_cache_expired(self, cache_entry: Dict, 
                         current_time: Optional[datetime] = None) -> bool:
        """检查缓存是否过期"""
        if 'timestamp' not in cache_entry:
            return True
        current_time = current_time or datetime.now()
        cached_time = datetime.fromisoformat(cache_entry['timestamp'])
        return current_time - cached_time > self.ttl 