# 48终端消息, devid 为 48终端IP
# EV_DEV_ONLINE
# EV_DEV_OFFLINE
# EV_ALARM_MSG

from dao import nms_mysql, nms_redis
from threads.msg_threads import mysql_write_thread
from core.warning import warning_handler


def ev_dev_online(data):
    '''
    {
        "eventid": "EV_DEV_ONLINE",
        "devid": "1.2.1",
        "devtype": "SERVICE_KDV_MT_TS6610",
        "collectorid": "60a44c502a60"
    }
    '''
    r = nms_redis.ev_dev_online_t48(
        data['devid'], data['devtype'], data['collectorid'])
    if r is None:
        return
    warning_handler(
        r['collector_p_server_moid'],
        r['warning_trigger_flag'],
        2016,
        data['rpttime'],
        'p_server',
        **r
    )
    # 48终端上线状态
    mysql_write_thread.push((nms_mysql.online_old_terminal, data['devid']))


def ev_dev_offline(data):
    '''
    {
        "eventid": "EV_DEV_OFFLINE",
        "devid": "1111",
        "devtype": "SERVICE_TS_SRV_MPCD",
        "collectorid": "60a44c502a60"
    }
    '''
    r = nms_redis.ev_dev_offline_t48(
        data['devid'], data['collectorid'])
    if r is None:
        return
    warning_handler(
        r['collector_p_server_moid'],
        r['warning_trigger_flag'],
        2016,
        data['rpttime'],
        'p_server',
        **r
    )
    # 48终端上线状态
    mysql_write_thread.push((nms_mysql.offline_old_terminal, data['devid']))


def ev_alarm_msg(data):
    '''
    {
        "devid": "1.2.2",
        "devtype": "Skywalker for Windows",
        "alarm_info":
        {
            "code_id": 1003,
            "report_time": "2014/05/08:12:08:08",
            "status": 0
        },
        "eventid": "EV_ALARM_MSG"
    }
    '''
    moid = nms_redis.get_terminal_moid(ip=data['devid'])
    warning_handler(
        moid,
        data['alarm_info']['status'],
        data['alarm_info']['code_id'],
        data['rpttime'],
        'terminal',
        device_type=data['devtype']
    )
