import time
from pathlib import Path

from loguru import logger
from PIL import ImageGrab


def take_screenshot(region=None, save_dir="data/screenshots"):
    """获取屏幕截图
    Args:
        region: 截图区域 (left, top, right, bottom)
        save_dir: 保存目录
    Returns:
        str: 截图文件路径，失败返回None
    """
    try:
        # 确保保存目录存在
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        # 获取截图
        screenshot = ImageGrab.grab(bbox=region)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"{save_dir}/screenshot_{timestamp}.png"
        
        # 保存截图
        screenshot.save(screenshot_path)
        logger.info(f"截图已保存: {screenshot_path}")
        return screenshot_path
        
    except Exception as e:
        logger.error(f"截图错误: {e}")
        return None

def get_screen_size():
    """获取屏幕尺寸"""
    try:
        screen = ImageGrab.grab()
        return screen.size
    except Exception as e:
        logger.error(f"获取屏幕尺寸失败: {e}")
        return None 