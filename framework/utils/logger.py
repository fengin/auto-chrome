# https://aibook.ren (AI全书)
import logging
import sys
import os

def setup_logger(name: str, log_file: str = "auto_chrome.log", level: str = "INFO") -> logging.Logger:
    """
    Configures and returns a logger instance.
    配置并返回一个日志记录器实例。
    """
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if logger is reused
    # 如果日志记录器被重用，避免多次添加处理程序
    if logger.hasHandlers():
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to create log file handler: {e}")

    return logger
