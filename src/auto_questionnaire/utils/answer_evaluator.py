from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class EvaluationResult:
    score: float
    feedback: str
    details: Dict[str, float]
    
    def __ge__(self, other: float) -> bool:
        return self.score >= other
        
    def __lt__(self, other: float) -> bool:
        return self.score < other

class AnswerEvaluator:
    def evaluate(self, question_type: str, answer: str, question: str, options: Optional[list] = None) -> EvaluationResult:
        if not answer:
            return EvaluationResult(
                score=0.0,
                feedback="答案为空",
                details={'completeness': 0.0, 'format': 0.0, 'relevance': 0.0, 'length': 0.0}
            )
            
        if question_type == 'radio':
            if not options:
                return EvaluationResult(
                    score=0.6,
                    feedback="答案基本合格",
                    details={'completeness': 0.6, 'format': 0.6, 'relevance': 0.6, 'length': 0.6}
                )
            if answer in options:
                return EvaluationResult(
                    score=1.0,
                    feedback="答案有效",
                    details={'completeness': 1.0, 'format': 1.0, 'relevance': 1.0, 'length': 1.0}
                )
            return EvaluationResult(
                score=0.3,
                feedback="答案需要改进：不在选项中",
                details={'completeness': 0.3, 'format': 0.3, 'relevance': 0.3, 'length': 0.3}
            )
            
        elif question_type == 'text':
            length_score = min(1.0, len(answer) / 20)
            completeness = self._evaluate_completeness(answer)
            format_score = self._evaluate_format(answer)
            relevance = self._evaluate_relevance(answer, question)
            
            total_score = (length_score + completeness + format_score + relevance) / 4
            total_score = min(1.0, total_score * 1.5)
            
            return EvaluationResult(
                score=total_score,
                feedback=self._generate_feedback(total_score),
                details={
                    'completeness': completeness,
                    'format': format_score,
                    'relevance': relevance,
                    'length': length_score
                }
            )
            
        elif question_type == 'checkbox':
            if not options:
                return EvaluationResult(
                    score=0.0,
                    feedback="无效的选项列表",
                    details={'completeness': 0.0, 'format': 0.0, 'relevance': 0.0, 'length': 0.0}
                )
            answers = answer.split(',')
            valid_answers = [a.strip() for a in answers if a.strip() in options]
            score = len(valid_answers) / len(options) if options else 0
            
            return EvaluationResult(
                score=score,
                feedback=self._generate_feedback(score),
                details={
                    'completeness': score,
                    'format': 1.0 if valid_answers else 0.0,
                    'relevance': 1.0 if valid_answers else 0.0,
                    'length': len(valid_answers) / len(options) if options else 0.0
                }
            )
            
        return EvaluationResult(
            score=0.0,
            feedback="无效的问题类型",
            details={'completeness': 0.0, 'format': 0.0, 'relevance': 0.0, 'length': 0.0}
        )
        
    def _evaluate_completeness(self, answer: str) -> float:
        return min(1.0, len(answer) / 50)
        
    def _evaluate_format(self, answer: str) -> float:
        return 1.0 if len(answer) >= 10 else 0.7
        
    def _evaluate_relevance(self, answer: str, question: str) -> float:
        return 0.8
        
    def _generate_feedback(self, score: float) -> str:
        if score >= 0.8:
            return "答案质量很好"
        elif score >= 0.6:
            return "答案需要改进：基本合格"
        else:
            return "答案需要改进：质量不足"
            
    evaluate_answer = evaluate  # 兼容旧接口