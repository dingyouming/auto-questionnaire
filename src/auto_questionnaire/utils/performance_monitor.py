from datetime import datetime
from collections import defaultdict
import threading
from typing import Dict

class PerformanceMonitor:
    def __init__(self):
        self._metrics = defaultdict(list)
        self._error_count = 0
        self._api_call_count = 0
        self._metrics_lock = threading.RLock()  # 使用可重入锁
        
    def record_api_call(self, elapsed: float, success: bool):
        with self._metrics_lock:
            self._api_call_count += 1
            self._metrics['api_calls'].append({
                'timestamp': datetime.now().isoformat(),
                'elapsed': elapsed,
                'success': success
            })
            if not success:
                self._error_count += 1
                
    def record_error(self, error_message: str):
        with self._metrics_lock:
            self._error_count += 1
            self._metrics['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'message': error_message
            })
                
    def record_cache_access(self, hit: bool):
        with self._metrics_lock:
            self._metrics['cache_hits'].append({
                'timestamp': datetime.now().isoformat(),
                'hit': hit
            })
                
    def record_answer_quality(self, score: float):
        with self._metrics_lock:
            self._metrics['answer_quality'].append({
                'timestamp': datetime.now().isoformat(),
                'score': score
            })
                
    def get_statistics(self) -> Dict:
        with self._metrics_lock:
            total_calls = max(1, self._api_call_count)
            return {
                'api_calls': list(self._metrics['api_calls']),
                'cache_hits': list(self._metrics['cache_hits']),
                'answer_quality': list(self._metrics['answer_quality']),
                'errors': list(self._metrics['errors']),
                'error_rate': float(self._error_count) / total_calls,
                'total_errors': self._error_count,
                'total_calls': total_calls
            }