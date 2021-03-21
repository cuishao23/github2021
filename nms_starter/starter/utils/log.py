# coding=utf-8
import logging
import os
from retry import retry
from config.common import LOGGING


@retry(tries=3, delay=5)
def init_logger():
    '''
    初始化日志模块
    :return: logger
    '''
    logger = logging.getLogger(name=LOGGING['loggername'])
    logger.setLevel(LOGGING['level'])
    # 检查日志目录是否存在
    if not os.path.exists(LOGGING['log_path']):
        os.mkdir(LOGGING['log_path'])
    loggername = os.path.join(
        LOGGING['log_path'], LOGGING['loggername'] + '.log')
    log_file_handler = logging.FileHandler(loggername, encoding='utf-8')
    formatter = logging.Formatter(fmt=LOGGING['format'])
    log_file_handler.setFormatter(formatter)
    logger.addHandler(log_file_handler)
