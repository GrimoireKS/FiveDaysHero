"""
日志模块

提供统一的日志记录功能，支持控制台和文件输出。
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler

# 日志级别映射
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# 默认日志格式
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger(name, level='debug', backup_count=7):
    """
    获取配置好的日志记录器
    
    Args:
        name (str): 日志记录器名称
        level (str): 日志级别，可选值：debug, info, warning, error, critical
        backup_count (int, optional): 保留的日志文件数量，默认7天（一周）
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 获取日志级别
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(DEFAULT_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 创建按日期轮转的文件处理器
    log_file = 'service.log'
    log_file_path = os.path.join(LOG_DIR, log_file)
    # 使用TimedRotatingFileHandler按天轮转日志
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when='midnight',  # 每天午夜轮转
        interval=1,      # 间隔为1天
        backupCount=backup_count,  # 保留7天的日志
        encoding='utf-8'
    )
    # 设置日志文件后缀格式为 .YYYY-MM-DD
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(DEFAULT_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger
