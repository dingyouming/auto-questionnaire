import importlib.util
import sys

import pytest


def test_required_packages():
    """检查必要的包是否已安装"""
    required_packages = {
        'groq': 'groq',
        'python-dotenv': 'dotenv',  # 修改为正确的导入名
        'pydantic': 'pydantic',
        'loguru': 'loguru',
        'pytesseract': 'pytesseract',
        'opencv-python': 'cv2',
        'numpy': 'numpy',
        'pillow': 'PIL'
    }
    
    for package, import_name in required_packages.items():
        spec = importlib.util.find_spec(import_name)
        assert spec is not None, f"{package} (import name: {import_name}) 未安装"

def test_tesseract_installation():
    """检查 Tesseract OCR 是否可用"""
    import pytesseract
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        pytest.fail(f"Tesseract OCR 未正确安装: {str(e)}")
