# https://aibook.ren (AI全书)
import yaml
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from framework.utils.logger import setup_logger

@dataclass
class Config:
    chrome: Dict[str, Any]
    logging: Dict[str, Any]
    tasks: Dict[str, Any]

    @classmethod
    def load(cls, path: str) -> 'Config':
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        return cls(
            chrome=data.get('chrome', {}),
            logging=data.get('logging', {}),
            tasks=data.get('tasks', {})
        )

class Context:
    def __init__(self, config_path: str):
        self.config = Config.load(config_path)
        self.logger = setup_logger(
            "AutoChrome", 
            log_file=self.config.logging.get("file", "auto_chrome.log"),
            level=self.config.logging.get("level", "INFO")
        )
        self.driver = None # Initialized later / 稍后初始化

    def get_logger(self, name: str):
        return setup_logger(
            name,
            log_file=self.config.logging.get("file", "auto_chrome.log"),
            level=self.config.logging.get("level", "INFO")
        )
