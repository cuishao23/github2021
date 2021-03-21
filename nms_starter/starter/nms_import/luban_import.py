import logging
import time

from config.common import LOGGING
from config.types import server_type_judgment 
from dao.mysql import luban_session_scope
from dao.luban import *
from dao.nms_redis import *

logger = logging.getLogger(LOGGING['loggername'])


def luban_importer():
    '''
    luban原始数据导入
    '''
    logger.info('luban importer ...')
    with luban_session_scope() as session:
        luban_machine_room_info_list = get_machine_room_list(session)
        # 物理服务器导入
        p_server_info_list = get_p_server_list(session)
        l_server_info_list = get_l_server_list(session)
        p_max_id = get_machine_info_bak_max_id(session)
        l_max_id = get_server_info_bak_max_id(session)
        if p_max_id is not None:
            del_machine_info_bak(session, p_max_id)
        if l_max_id is not None:
            del_server_info_bak(session, l_max_id)
    logger.info('import machine_room: ' + str(luban_machine_room_info_list))
    logger.info('import physical server:  ' + str(p_server_info_list))
    logger.info('import logic server:  ' + str(l_server_info_list))
    for info in luban_machine_room_info_list:
        add_machine_room(*info)
    for info in p_server_info_list:
        server_type_judgment.add_physical_type(info[2])
        add_p_server(*info)
    for info in l_server_info_list:
        server_type_judgment.add_logical_type(info[2])
        add_l_server(*info)
    logger.info('luban importer ok!')


def luban_bak_importer():
    '''
    bck表监控
    '''
    while True:
        logger.info('luban bak import ...')
        try:
            max_id = None
            with luban_session_scope() as session:
                max_id = get_machine_info_bak_max_id(session)
                logger.info('luban import: machine info max id = %s' % max_id)
                if max_id is not None:
                    info_list = get_machine_info_bak(session)
                    for info in info_list:
                        if info[-1] == 0:
                            server_type_judgment.add_physical_type(info[2])
                            add_p_server(*info)
                        elif info[-1] == 1:
                            update_p_server(*info)
                        elif info[-1] == 2:
                            del_p_server(*info)
                if max_id is not None:
                    del_machine_info_bak(session, max_id)

            max_id = None
            with luban_session_scope() as session:
                max_id = get_server_info_bak_max_id(session)
                logger.info('luban import: server info max id = %s' % max_id)
                if max_id is not None:
                    info_list = get_server_info_bak(session)
                    for info in info_list:
                        if info[-1] == 0:
                            server_type_judgment.add_logical_type(info[2])
                            add_l_server(*info)
                        elif info[-1] == 1:
                            update_l_server(*info)
                        elif info[-1] == 2:
                            del_l_server(*info)
                if max_id is not None:
                    del_server_info_bak(session, max_id)

        except Exception as e:
            logger.error(e)
        time.sleep(30)
