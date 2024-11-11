import json
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel


class AlertConfig(BaseModel):
    email_recipients: List[str]
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    alert_thresholds: Dict[str, float] = {
        "error_rate": 0.1,        # 错误率阈值
        "api_latency": 5.0,       # API延迟阈值(秒)
        "cache_hit_rate": 0.5,    # 缓存命中率阈值
        "answer_quality": 0.7     # 答案质量阈值
    }

class AlertManager:
    def __init__(self, config_file: str = "config/alert_config.json"):
        self.config = self._load_config(config_file)
        self.alert_history: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(hours=1)  # 告警冷却时间
        
    def check_metrics(self, metrics: Dict) -> None:
        """检查指标并触发告警"""
        for metric_name, threshold in self.config.alert_thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if self._should_alert(metric_name, value, threshold):
                    self._send_alert(
                        f"指标 {metric_name} 超出阈值",
                        f"当前值: {value}, 阈值: {threshold}"
                    )
    
    def _should_alert(self, metric: str, value: float, threshold: float) -> bool:
        """判断是否应该发送告警"""
        # 检查是否超出阈值
        should_alert = False
        
        if metric == "error_rate":
            should_alert = value > threshold
        elif metric == "api_latency":
            should_alert = value > threshold
        elif metric in ["cache_hit_rate", "answer_quality"]:
            should_alert = value < threshold
            
        # 检查冷却时间
        if should_alert:
            last_alert = self.alert_history.get(metric)
            if last_alert and datetime.now() - last_alert < self.alert_cooldown:
                return False
            self.alert_history[metric] = datetime.now()
            return True
            
        return False
        
    def _send_alert(self, subject: str, message: str) -> None:
        """发送告警邮件"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = f"[问卷系统告警] {subject}"
            msg['From'] = self.config.smtp_user
            msg['To'] = ', '.join(self.config.email_recipients)
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)
                
            logger.info(f"已发送告警: {subject}")
            
        except Exception as e:
            logger.error(f"发送告警失败: {e}")
            
    def _load_config(self, config_file: str) -> AlertConfig:
        """加载告警配置"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return AlertConfig(**config_data)
            else:
                logger.warning(f"未找到告警配置文件: {config_file}")
                return AlertConfig(
                    email_recipients=[],
                    smtp_server="",
                    smtp_port=587,
                    smtp_user="",
                    smtp_password=""
                )
        except Exception as e:
            logger.error(f"加载告警配置失败: {e}")
            raise 