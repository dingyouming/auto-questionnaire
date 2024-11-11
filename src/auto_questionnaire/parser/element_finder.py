from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import pytesseract
from loguru import logger


@dataclass
class QuestionElement:
    question_type: str
    text: str
    position: Tuple[int, int, int, int]  # x1, y1, x2, y2
    options: Optional[List[str]] = None

class ElementFinder:
    def __init__(self):
        self.ocr_config = '--psm 6 -l chi_sim'
        
    def find_elements(self, image_path: str) -> List[QuestionElement]:
        """识别图片中的问题元素"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片")
                
            # OCR识别
            text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=self.ocr_config)
            
            elements = []
            current_text = []
            current_box = None
            
            # 分析OCR结果
            for i, text in enumerate(text_data['text']):
                if text.strip():
                    x, y, w, h = (text_data['left'][i], text_data['top'][i],
                                text_data['width'][i], text_data['height'][i])
                    
                    if not current_box:
                        current_box = [x, y, x + w, y + h]
                    else:
                        current_box[2] = max(current_box[2], x + w)
                        current_box[3] = max(current_box[3], y + h)
                    
                    current_text.append(text)
                    
                elif current_text:
                    # 识别问题类型并创建元素
                    full_text = ' '.join(current_text)
                    q_type = self._identify_question_type(full_text)
                    if q_type:
                        elements.append(QuestionElement(
                            question_type=q_type,
                            text=full_text,
                            position=tuple(current_box),
                            options=self._extract_options(full_text) if q_type in ['radio', 'checkbox'] else None
                        ))
                    current_text = []
                    current_box = None
            
            logger.info(f"识别到 {len(elements)} 个问题元素")
            return elements
            
        except Exception as e:
            logger.error(f"元素识别错误: {e}")
            return []
    
    def _identify_question_type(self, text: str) -> str:
        """识别问题类型"""
        text = text.lower()
        if '[]' in text or '【】' in text:
            return 'checkbox' if text.count('[]') > 1 or text.count('【】') > 1 else 'radio'
        return 'text'
    
    def _extract_options(self, text: str) -> List[str]:
        """提取选项"""
        return [opt.strip() for opt in text.split('[]') if opt.strip()] 