import logging
from dao import nms_mysql, nms_redis
from config.common import LOGGING
from utils.exceptions import *
from threads.msg_threads import mysql_write_thread

logger = logging.getLogger(LOGGING['loggername'])


def warning_handler(device_moid, warning_flag, code, time, server_type, **extra_info):
    '''
    触发告警/修复告警流程
    参数: extra_info: 用于传递阈值告警信息, 对于终端, 还需要包含device_type,device_ip;
    '''
    # 是否暂停告警
    logger.info('warning_handler: {}')
    all_info = nms_redis.get_all_warning_info(device_moid, code, server_type, extra_info.get('device_type'))
    if all_info and all_info.get('warning_info') and all_info['server_info'].get('moid'):
        unrepaired = all_info['warning_unrepaired']
        if warning_flag and not unrepaired:
            # 告警流程
            warning_trigger(
                time, server_type, all_info['server_info'], all_info['warning_info'], extra_info)
            warning_notice(server_type, warning_flag, all_info['notify_info'],
                           all_info['server_info'], all_info['warning_info'], extra_info)
        if not warning_flag and unrepaired:
            # 修复告警流程
            warning_repair(device_moid, code, time, server_type)
            warning_notice(server_type, warning_flag, all_info['notify_info'],
                           all_info['server_info'], all_info['warning_info'], extra_info)


def warning_trigger(start_time, server_type, server_info, warning_info, extra_info):
    '''
    产生告警流程
    '''
    # mysql
    if server_type == 'terminal':
        mysql_write_thread.push((nms_mysql.add_terminal_warning_unrepaired, {
            'device_moid': server_info.get('moid'),
            'device_name': server_info.get('name'),
            'device_type': extra_info.get('device_type'),
            'device_ip': server_info.get('device_ip'),
            'device_e164': server_info.get('e164'),
            'domain_moid': server_info.get('domain_moid'),
            'domain_name': server_info.get('domain_name'),
            'start_time': start_time,
            ** warning_info
        }))
    else:
        mysql_write_thread.push((nms_mysql.add_server_warning_unrepaired, {
            'device_moid': server_info.get('moid'),
            'device_name': server_info.get('name'),
            'device_type': server_info.get('type'),
            'device_ip': server_info.get('ip'),
            'machine_room_moid': server_info.get('machine_room_moid'),
            'machine_room_name': server_info.get('machine_room_name'),
            'start_time': start_time,
            'server_type': 0 if server_type == 'p_server' else 1,
            ** warning_info
        }))

    # redis
    nms_redis.add_warning_unrepaired(
        server_type, server_info['moid'], warning_info['code'], warning_info['level'])


def warning_repair(device_moid, code, resolve_time, server_type):
    '''
    告警修复流程
    '''
    # mysql
    if server_type == 'terminal':
        mysql_write_thread.push((nms_mysql.add_terminal_warning_repaired, {
            'device_moid': device_moid,
            'code': code,
            'resolve_time': resolve_time
        }))
    else:
        mysql_write_thread.push((nms_mysql.add_server_warning_repaired, {
            'device_moid': device_moid,
            'code': code,
            'resolve_time': resolve_time
        }))
    # redis
    nms_redis.del_warning_unrepaired(server_type, device_moid, code)


def warning_notice(server_type, warning_flag, notify_info, server_info, warning_info, extra_info):
    from core.warning_mail import send_warning_mail
    from core.warning_shortmsg import send_warning_shortmsg
    from core.warning_wechat import send_warning_wechat
    try:
        threshold_value = extra_info.get('threshold_value')
        current_value = extra_info.get('current_value')
        logger.info('email')
        if notify_info.get('email'):
            send_warning_mail(notify_info['email'], server_type, warning_flag,
                            server_info, warning_info, threshold_value, current_value)
        logger.info('phone')
        if notify_info.get('phone'):
            send_warning_shortmsg(notify_info['phone'], server_type, warning_flag,
                                server_info, warning_info, threshold_value, current_value)
        logger.info('wechat')
        if notify_info.get('wechat'):
            send_warning_wechat(notify_info['wechat'], server_type, warning_flag,
                                server_info, warning_info, threshold_value, current_value)
    except Exception as e:
        logger.error(e)