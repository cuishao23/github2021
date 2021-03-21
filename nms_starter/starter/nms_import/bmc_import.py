import logging
import json
import pika
from itertools import chain

from config.common import LOGGING
from dao.mysql import bmc_session_scope, nms_session_scope
from dao import bmc, nms_redis, nms_mysql
from utils.rmq.consumer import ReconnectingConsumer
from threads.msg_threads import mysql_write_thread
logger = logging.getLogger(LOGGING['loggername'])


def bmc_importer():
    logger.info('bmc import ...')
    with bmc_session_scope() as session:
        domain_info_list = bmc.get_domain_list(session)
        license_info_list = bmc.get_domain_license_list(session)
        machine_room_info_list = bmc.get_machine_room_list(session)
        terminal_info_list = bmc.get_terminal_list(session)
        old_terminal_info_list = bmc.get_old_terminal_list(session)
    logger.info('domain: ' + str(domain_info_list))
    for info in domain_info_list:
        nms_redis.add_domain(*info)
    logger.info('license: ' + str(license_info_list))
    for info in license_info_list:
        nms_redis.add_license(*info)
    logger.info('machine_room:  ' + str(machine_room_info_list))
    for info in machine_room_info_list:
        nms_redis.add_machine_room(*info)
    logger.debug('terminal: %s' % len(terminal_info_list))
    for info in terminal_info_list:
        nms_redis.add_terminal(*info)
    logger.debug('old_terminal: %s' % len(old_terminal_info_list))
    for info in old_terminal_info_list:
        nms_redis.add_old_terminal(*info)
        with nms_session_scope() as session:
            nms_mysql.add_old_terminal(
                session, {
                    'moid': info[0],
                    'user_domain_moid': info[1],
                    'name': info[2],
                    'e164': info[3],
                    'ip': info[4]
                }
            )
    logger.info('bmc import ok!')
