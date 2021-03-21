#! /usr/bin/env python3
# coding=utf-8

import time
import logging
import sys
import setproctitle
import daemon
import threading

from config.common import LOGGING
from utils.log import init_logger
from nms_import import init_importer
from config import init_config

logger = logging.getLogger(LOGGING['loggername'])

# starter模块初始化


def init():
    try:
        # 初始化日志模块
        init_logger()
        logger.info('nms_starter start up!')
        # 初始化导入模块
        init_importer()
        # 初始化配置模块
        init_config()
        logger.info('init config ok!')
        # 初始化线程模块
        init_thread()
    except Exception as e:
        logger.error('nms_starter init error! %s' % e)
        exit(-1)


# 初始化线程
def init_thread():
    from threading import Thread
    from config.common import BMC_CONSUMER, COLLECTOR_HEARTBEAT_CONSUMER, MEETING_CONSUMER, INSPECT_CONSUMER
    from nms_import.luban_import import luban_bak_importer
    from core.graphite_statistic_handler import periodic_statistic
    from core.heartbeat_msg_handler import offline_all_collector
    from threads.mq_threads import BmcMQThread, HeartbeatMQThread, MeetingMQThread, InspectMQThread, rmq_produce_thread
    from threads.msg_threads import mysql_write_thread, graphite_statistic_thread

    logger.info('init thread...')

    # 下线所有collector
    offline_all_collector()
    # 等待collector超时
    time.sleep(40)

    logger.info('offline all collector ok')
    mysql_write_thread.start()
    rmq_produce_thread.start()
    graphite_statistic_thread.start()
    Thread(name='luban_import_thread',
           target=luban_bak_importer, daemon=True).start()
    Thread(name='periodic_statistic_thread',
           target=periodic_statistic, daemon=True).start()
    BmcMQThread('bmc_mq_thread', BMC_CONSUMER).start()
    MeetingMQThread(
        'meeting_mq_thread', MEETING_CONSUMER).start()
    HeartbeatMQThread(
        'heartbeat_mq_thread', COLLECTOR_HEARTBEAT_CONSUMER).start()
    InspectMQThread('inspect_mq_thread', INSPECT_CONSUMER).start()
    logger.info('thread init ok!')


# 监控线程运行情况
# TODO 扩展状态恢复功能
def monitor():
    from config.types import server_type_judgment
    from utils.cron import cron_task
    monitor = '''Starter Monitor:
        [thread {}]:{}
        [server type]:{}
        [cron]:{}'''.format(
        str(threading.active_count()),
        '\n\t'.join([str(t) for t in threading.enumerate()]),
        str(server_type_judgment),
        str(cron_task)
    )
    logger.info(monitor)


if __name__ == '__main__':
    # # 测试代码块 begin
    # exit()
    # # 测试代码块 end
    with daemon.DaemonContext():
        setproctitle.setproctitle('nms_starter')
        init()
        while True:
            monitor()
            time.sleep(5*60)
