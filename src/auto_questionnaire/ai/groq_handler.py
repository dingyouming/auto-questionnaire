from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from loguru import logger
import threading
import queue

class GroqHandler:
    def __init__(self, timeout: int = 5, max_workers: int = 3):
        self.timeout = timeout
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._request_queue = queue.Queue()
        self._response_cache = {}
        self._lock = threading.Lock()
        
    def generate_response(self, question: str, context: Optional[str] = None) -> str:
        try:
            # 使用问题作为缓存键
            cache_key = f"{question}:{context or ''}"
            
            with self._lock:
                if cache_key in self._response_cache:
                    return self._response_cache[cache_key]
            
            # 提交任务到线程池
            future = self._executor.submit(self._make_api_call, question, context)
            response = future.result(timeout=self.timeout)
            
            # 缓存响应
            with self._lock:
                self._response_cache[cache_key] = response
                
            return response
            
        except Exception as e:
            logger.error(f"API调用失败: {str(e)}")
            return ""
            
    def _make_api_call(self, question: str, context: Optional[str] = None) -> str:
        # 模拟API调用
        return "这是一个测试回答"
        
    def __del__(self):
        self._executor.shutdown(wait=False)