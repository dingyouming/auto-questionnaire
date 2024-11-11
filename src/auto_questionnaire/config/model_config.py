import os
from typing import Optional

class ModelConfig:
    def __init__(self):
        # 读取并立即转换温度值
        temp_str = os.getenv('TEMPERATURE', '0.7')
        try:
            self.TEMPERATURE = float(temp_str)
        except ValueError:
            raise ValueError(f"Invalid TEMPERATURE value: {temp_str}")
            
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.MODEL_NAME = os.getenv('MODEL_NAME', 'mixtral-8x7b-32768')
        
        # 初始化时立即验证
        self.validate()
    
    def validate(self) -> None:
        """验证配置参数的有效性"""
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
            
        if not self.MODEL_NAME:
            raise ValueError("MODEL_NAME is required")
            
        if not 0 <= self.TEMPERATURE <= 1.0:
            raise ValueError(f"TEMPERATURE must be between 0 and 1, got {self.TEMPERATURE}")