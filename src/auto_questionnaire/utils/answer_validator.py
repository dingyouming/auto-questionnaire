from typing import List, Dict
from difflib import SequenceMatcher
from loguru import logger
import jieba

class AnswerValidator:
    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        self.previous_answers: Dict[str, List[str]] = {}
        
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度，使用分词后的集合相似度"""
        # 对中文文本进行分词
        words1 = set(jieba.cut(str1))
        words2 = set(jieba.cut(str2))
        
        # 计算词集合的交集和并集
        intersection = words1 & words2
        union = words1 | words2
        
        # 计算 Jaccard 相似度
        jaccard = len(intersection) / len(union) if union else 0
        
        # 计算序列相似度
        sequence = SequenceMatcher(None, str1, str2).ratio()
        
        # 综合两种相似度
        return max(jaccard, sequence)
        
    def check_answer_consistency(self, 
                               question_type: str,
                               question: str,
                               answer: str,
                               previous_answers: List[str]) -> bool:
        """检查答案一致性"""
        if not previous_answers:
            return True
            
        # 对于选择题，检查选项是否一致
        if question_type in ['radio', 'checkbox']:
            return answer in previous_answers
            
        # 对于文本题，检查相似度
        max_similarity = max(
            self._calculate_similarity(answer, prev)
            for prev in previous_answers
        )
        
        logger.debug(f"答案相似度: {max_similarity}")
        return max_similarity >= self.similarity_threshold
        
    def validate_and_store_answer(self, 
                                question_type: str,
                                question: str,
                                answer: str) -> bool:
        """验证并存储答案"""
        if not answer:
            return False
            
        question_key = f"{question_type}:{question}"
        previous = self.previous_answers.get(question_key, [])
        
        # 如果是第一个答案，直接存储
        if not previous:
            self.previous_answers[question_key] = [answer]
            return True
            
        # 检查一致性
        is_consistent = self.check_answer_consistency(
            question_type, question, answer, previous
        )
        
        if is_consistent:
            self.previous_answers[question_key].append(answer)
            return True
            
        logger.warning(f"答案不一致: {question}")
        return False