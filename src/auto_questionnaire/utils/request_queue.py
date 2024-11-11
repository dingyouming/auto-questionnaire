import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any, Callable, List
from loguru import logger
from collections import deque

class RequestQueue:
    def __init__(self, max_concurrent: int = 5, 
                 rate_limit: int = 100, 
                 time_window: int = 60):
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.request_times = deque(maxlen=rate_limit)
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
    def _check_rate_limit(self) -> float:
        """检查并返回需要等待的时间"""
        current_time = time.time()
        
        with self.lock:
            while self.request_times and current_time - self.request_times[0] > self.time_window:
                self.request_times.popleft()
                
            if len(self.request_times) >= self.rate_limit:
                wait_time = self.time_window - (current_time - self.request_times[0])
                return max(0, wait_time)
                
            self.request_times.append(current_time)
            return 0
            
    async def _execute_request(self, func: Callable, *args, **kwargs) -> Any:
        """异步执行请求"""
        wait_time = self._check_rate_limit()
        if wait_time > 0:
            logger.warning(f"达到速率限制，等待 {wait_time:.2f} 秒")
            await asyncio.sleep(wait_time)
            
        # 直接执行同步函数，避免嵌套的事件循环
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"执行请求失败: {str(e)}")
            raise
            
    def add_request(self, func: Callable, *args, **kwargs) -> Any:
        """添加单个请求"""
        wait_time = self._check_rate_limit()
        if wait_time > 0:
            logger.warning(f"达到速率限制，等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)
            
        return func(*args, **kwargs)
            
    async def batch_requests(self, funcs: List[Callable]) -> List[Any]:
        """批量处理请求"""
        tasks = []
        for func in funcs:
            wait_time = self._check_rate_limit()
            if wait_time > 0:
                logger.warning(f"达到速率限制，等待 {wait_time:.2f} 秒")
                await asyncio.sleep(wait_time)
                
            # 使用线程池执行同步函数
            task = self.executor.submit(func)
            tasks.append(task)
            
        # 等待所有任务完成
        results = []
        for task in tasks:
            try:
                results.append(task.result(timeout=5))  # 添加超时
            except Exception as e:
                logger.error(f"任务执行失败: {str(e)}")
                results.append(None)
                
        return results
        
    def __del__(self):
        self.executor.shutdown(wait=False)  # 不等待未完成的任务