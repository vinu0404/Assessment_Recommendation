import sys
from pathlib import Path
from loguru import logger
from app.config import settings


def setup_logger():
    """Configure loguru logger with file and console output"""
    logger.remove()
    
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[name]}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="10 days",
        compression="zip",
    )
    
    return logger

app_logger = setup_logger()


def get_logger(name: str = None):
    if name:
        return app_logger.bind(name=name)
    return app_logger.bind(name="app")  