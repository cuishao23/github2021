import logging
import json
from config.common import LOGGING
from dao.mysql import nms_session_scope
from dao.nms_mysql import get_resource_limit, get_server_resource_limit, get_warning_stop, get_warning_notify
from dao.nms_redis import init_warning_code, init_warning_global_limit, init_warning_global_limit, init_warning_notify, init_warning_server_limit, init_warning_stop


logger = logging.getLogger(LOGGING['loggername'])


def warning_settings_importer():
    logger.info('warning settings import ...')
    init_warning_code()
    import_global_resource_limit()
    import_server_resource_limit()
    import_warning_notify()
    import_warning_stop()
    logger.info('warning settings import ok!')


def import_global_resource_limit():
    '''
    导入全局阈值设置
    :return:
    '''
    logger.info('import_global_resource_limit')
    with nms_session_scope() as session:
        r = get_resource_limit(session)
    # 默认值
    default = [500, 400, 1000, 80]
    if r:
        args = [r[i] if r[i] else default[i] for i in range(4)]
    else:
        args = default
    init_warning_global_limit(*args)
    logger.info('import_global_resource_limit ok!')


def import_server_resource_limit():
    '''
    导入服务器阈值设置
    :return:
    '''
    with nms_session_scope() as session:
        r = get_server_resource_limit(session)

    logger.info('import_server_resource_limit: %s' % r)
    for i in r:
        init_warning_server_limit(*i)
    logger.info('import_server_resource_limit import ok!')


def import_warning_notify():
    '''
    导入告警通知规则
    '''
    logger.info('import_warning_notify')
    with nms_session_scope() as session:
        r = get_warning_notify(session)

    init_warning_notify(json.dumps(r))


def import_warning_stop():
    '''
    导入暂停告警设置
    '''
    with nms_session_scope() as session:
        r = get_warning_stop(session)
    logger.info('import_warning_stop: %s' % r)
    init_warning_stop(*(len(r), *[info[0] for info in r]))
    logger.info('import_warning_stop ok!')
