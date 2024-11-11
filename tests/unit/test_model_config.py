import os
import pytest
from dotenv import load_dotenv

from auto_questionnaire.config.model_config import ModelConfig

def test_model_config_initialization():
    """测试模型配置初始化"""
    config = ModelConfig()
    assert hasattr(config, 'GROQ_API_KEY')
    assert hasattr(config, 'MODEL_NAME')
    assert hasattr(config, 'TEMPERATURE')

def test_environment_variables():
    """测试环境变量加载"""
    load_dotenv()
    import auto_questionnaire.config as config

    # 检查必要的环境变量
    assert os.getenv('GROQ_API_KEY') is not None
    assert os.getenv('MODEL_NAME') is not None
    
def test_model_config_validation():
    """测试配置验证"""
    # 保存原始环境变量
    original_temp = os.getenv('TEMPERATURE')
    
    try:
        # 设置无效的环境变量
        os.environ['TEMPERATURE'] = '2.0'
        # 创建新的配置实例以触发验证
        with pytest.raises(ValueError, match="TEMPERATURE must be between 0 and 1"):
            ModelConfig()
    finally:
        # 恢复原始环境变量
        if original_temp is not None:
            os.environ['TEMPERATURE'] = original_temp
        else:
            del os.environ['TEMPERATURE']