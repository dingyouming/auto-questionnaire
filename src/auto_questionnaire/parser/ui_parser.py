from typing import Dict, List

from loguru import logger

from .element_finder import ElementFinder, QuestionElement


class QuestionnaireParser:
    def __init__(self):
        self.element_finder = ElementFinder()
    
    def parse_page(self, image_path: str) -> Dict[str, List[QuestionElement]]:
        """解析问卷页面
        Args:
            image_path: 问卷截图路径
        Returns:
            Dict[str, List[QuestionElement]]: 按类型分类的问题元素
        """
        try:
            # 使用OCR识别问题元素
            elements = self.element_finder.find_elements(image_path)
            
            # 按类型分类
            classified = {
                'radio': [],    # 单选题
                'checkbox': [], # 多选题
                'text': []      # 文本题
            }
            
            # 对识别到的元素进行分类
            for element in elements:
                if element.question_type in classified:
                    classified[element.question_type].append(element)
            
            # 记录解析结果
            logger.info(f"问卷解析完成: "
                       f"单选题 {len(classified['radio'])}个, "
                       f"多选题 {len(classified['checkbox'])}个, "
                       f"文本题 {len(classified['text'])}个")
            
            return classified
            
        except Exception as e:
            logger.error(f"问卷解析失败: {e}")
            return {'radio': [], 'checkbox': [], 'text': []}
    
    def validate_elements(self, elements: Dict[str, List[QuestionElement]]) -> bool:
        """验证解析结果是否有效
        Args:
            elements: 解析得到的问题元素
        Returns:
            bool: 验证结果
        """
        try:
            # 检查是否有任何问题被识别
            total_questions = sum(len(q_list) for q_list in elements.values())
            if total_questions == 0:
                logger.warning("未识别到任何问题")
                return False
            
            # 验证每个问题元素的完整性
            for q_type, q_list in elements.items():
                for element in q_list:
                    if not element.text or not element.position:
                        logger.warning(f"问题元素不完整: {element}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"元素验证失败: {e}")
            return False