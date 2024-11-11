import json
import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger


class LogConfig:
    def __init__(self, config_file: str = "config/logging_config.json"):
        self.config = self._load_config(config_file)
        self._setup_logger()
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载日志配置"""
        default_config = {
            "log_path": "logs",
            "rotation": "500 MB",
            "retention": "30 days",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                     "<level>{level: <8}</level> | "
                     "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                     "<level>{message}</level>",
            "levels": {
                "DEBUG": {"color": "<cyan>"},
                "INFO": {"color": "<green>"},
                "WARNING": {"color": "<yellow>"},
                "ERROR": {"color": "<red>"},
                "CRITICAL": {"color": "<RED>"}
            }
        }
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            return default_config
        except Exception as e:
            logger.warning(f"加载日志配置失败: {e}, 使用默认配置")
            return default_config
            
    def _setup_logger(self) -> None:
        """配置日志系统"""
        # 移除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format=self.config["format"],
            level="INFO",
            colorize=True
        )
        
        # 添加文件处理器
        log_path = Path(self.config["log_path"])
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 普通日志
        logger.add(
            log_path / "app.log",
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            format=self.config["format"],
            level="INFO",
            encoding="utf-8"
        )
        
        # 错误日志
        logger.add(
            log_path / "error.log",
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            format=self.config["format"],
            level="ERROR",
            encoding="utf-8"
        )
        
        # API调用日志
        logger.add(
            log_path / "api.log",
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            format=self.config["format"],
            filter=lambda record: "api" in record["extra"],
            encoding="utf-8"
        )
        
    def get_logger(self, name: str = None):
        """获取带上下文的logger"""
        return logger.bind(context=name) 