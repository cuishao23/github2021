import time
import logging
from retry import retry
from dao.mysql import nms_session_scope
from dao import nms_mysql, nms_redis, graphite_statistic
from config.common import LOGGING

logger = logging.getLogger(LOGGING['loggername'])


@retry(logger=logger, tries=3, delay=1)
def server_warning():
    '''
    获取服务器未修复告警数量
    '''
    logger.info('server warning statistic')
    data = False
    with nms_session_scope() as session:
        data = nms_mysql.get_server_warning_unrepaired(session)
    if data:
        timestamp = int(time.time())
        for info in data:
            graphite_statistic.add_server_warning_statistic(
                info[0], info[1], timestamp)


@retry(logger=logger, tries=3, delay=1)
def terminal_warning():
    '''
    获取终端未修复告警数量
    '''
    logger.info('terminal warning statistic')
    data = False
    with nms_session_scope() as session:
        data = nms_mysql.get_terminal_warning_unrepaired(session)
    if data:
        timestamp = int(time.time())
        for info in data:
            graphite_statistic.add_terminal_warning_statistic(
                info[0], info[1], timestamp)


@retry(logger=logger, tries=3, delay=1)
def meeting_statistic():
    '''
    会议统计
    '''
    logger.info('meeting statistic')
    r = nms_redis.meeting_statistic()
    timestamp = int(time.time())
    if r:
        for domain_moid, value in r.items():
            multi_meeting_number = value.get('t_meeting', 0) + value.get(
                'p_meeting', 0) + value.get('sfu_meeting', 0) + value.get('mix_meeting', 0)
            graphite_statistic.add_multi_meeting_statistic(
                domain_moid, multi_meeting_number, timestamp)
            graphite_statistic.add_p2p_meeting_statistic(
                domain_moid, value.get('p2p_meeting', 0), timestamp)
            graphite_statistic.add_appointment_meeting_statistic(
                domain_moid, value.get('a_meeting', 0), timestamp)


@retry(logger=logger, tries=3, delay=1)
def meeting_terminal_statistic():
    '''
    会议终端统计
    '''
    logger.info('meeting terminal statistic')
    r = nms_redis.meeting_terminal_statistic()
    timestamp = int(time.time())
    if r:
        for domain_moid, value in r.items():
            graphite_statistic.add_p2p_meeting_terminal_statistic(
                domain_moid, value.get('p2p', 0), timestamp)
            graphite_statistic.add_multi_meeting_terminal_statistic(
                domain_moid, value.get('multiple', 0), timestamp)


@retry(logger=logger, tries=3, delay=1)
def pas_statistic():
    '''
    pas终端统计
    '''
    logger.info('pas terminal statistic')
    r = nms_redis.pas_statistic()
    timestamp = int(time.time())
    if r:
        for domain_moid, value in r.items():
            graphite_statistic.add_sip_count_statistic(
                domain_moid, value.get('sip', 0), timestamp)
            graphite_statistic.add_h323_count_statistic(
                domain_moid, value.get('h323', 0), timestamp)
            graphite_statistic.add_rtc_count_statistic(
                domain_moid, value.get('rtc', 0), timestamp)


@retry(logger=logger, tries=3, delay=1)
def server_online():
    '''
    服务器在线统计
    '''
    logger.info('server online statistic')
    r = nms_redis.server_online_statistic()
    timestamp = int(time.time())
    if r:
        for machine_room_moid, value in r.items():
            graphite_statistic.add_online_server_statistic(
                machine_room_moid, value.get('online', 0), timestamp)
            graphite_statistic.add_offline_server_statistic(
                machine_room_moid, value.get('total', 0) - value.get('online', 0), timestamp)


@retry(logger=logger, tries=3, delay=1)
def terminal_online():
    '''
    终端在线统计
    '''
    logger.info('terminal online statistic')
    r = nms_redis.terminal_online_statistic()
    timestamp = int(time.time())
    if r:
        for domain_moid, value in r.items():
            graphite_statistic.add_online_terminal_statistic(
                domain_moid, value.get('online', 0), timestamp)
            graphite_statistic.add_offline_terminal_statistic(
                domain_moid, value.get('total', 0) - value.get('online', 0), timestamp)


def periodic_statistic():
    from core.license import update_license_warning
    logger.info('graphite statistic task start')
    timer = 0
    while True:
        # license 告警检查 23*60
        timer = timer % (23*60)
        if timer == 0:
            update_license_warning()
        timer += 1
        # 按邮件要求一分钟统计一次
        time.sleep(60)
        try:
            server_warning()
            terminal_warning()
            meeting_statistic()
            meeting_terminal_statistic()
            pas_statistic()
            server_online()
            terminal_online()
        except Exception as e:
            logger.error(e)
