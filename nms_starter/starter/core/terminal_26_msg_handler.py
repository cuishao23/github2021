# 26终端消息处理
# 2.6终端的e164号码是设备id的后13位(第20位到32位)
# EV_DEV_ONLINE
# EV_DEV_OFFLINE
# EV_MT_INFO
# EV_ALARM_MSG

import json
from dao import nms_redis, nms_mysql
from core.warning import warning_handler
from threads.msg_threads import mysql_write_thread


def ev_dev_online(data):
    '''
    {
        "eventid": "EV_DEV_ONLINE",
        "devid": "1.2.1",
        "devtype": "SERVICE_KDV_MT_TS6610",
        "collectorid": "60a44c502a60"
    }
    '''
    e164 = data['devid'][20:33]
    r = nms_redis.ev_dev_online_t(e164, data['devtype'], data['collectorid'])
    if r:
        warning_handler(
            r['collector_p_server_moid'],
            r['warning_trigger_flag'],
            2016,
            data['rpttime'],
            'p_server',
            **r
        )


def ev_dev_offline(data):
    '''
    {
        "eventid": "EV_DEV_OFFLINE",
        "devid": "1111",
        "devtype": "SERVICE_TS_SRV_MPCD",
        "collectorid": "60a44c502a60"
    }
    '''
    e164 = data['devid'][20:33]
    r = nms_redis.ev_dev_offline_t(
        e164, data['devtype'], data['collectorid'])
    # nms接入数量阈值告警
    if r is not None:
        return
    warning_handler(
        r['collector_p_server_moid'],
        r['warning_trigger_flag'],
        2016,
        data['rpttime'],
        'p_server',
        **r
    )


def ev_mt_info(data):
    '''
    {
        'devid': '1.2.2',
        'devtype': 'Skywalker for Windows',
        'eventid': 'EV_MT_INFO',
        'mt_info': {
            "aps_addr": {
                "domain": "172.16.72.84",
                "ip": "218.22.22.23"
            },
            "cpu_type": "i7",
            "cpu_freq": 5,
            "cpu_num": 4,
            "devname": "longweitest",
            "devver": "20141215",
            "oem": "dddd",
            "memory": 4000,
            "os": "XP",
            "netinfo": {
                "dns": "172.16.0.65",
                "nat_ip": "172.16.72.84",
                "ip": "172.16.72.84"
            }
        }
    }
    '''
    mt_info = data['mt_info']
    netinfo = mt_info.get('netinfo', {})
    aps_addr = mt_info.get('aps_addr', {})
    cpu_freq = str(mt_info['cpu_freq']) + 'MHz' if mt_info.get('cpu_freq') else ''
    memory = '%.2fGB' % (
        int(mt_info['memory'])/1024) if mt_info.get('memory') else ''
    info = {}
    info['runninginfo'] = {
        'version': mt_info.get('devver', ''),
        'os': mt_info.get('os', ''),
        'cpu_type': mt_info.get('cpu_type', ''),
        'cpu_freq': cpu_freq,
        'cpu_num': mt_info.get('cpu_num', ''),
        'memory': memory
    }
    info['netinfo'] = {
        'ip': netinfo.get('ip', ''),
        'nat_ip': netinfo.get('nat_ip', ''),
        'dns': netinfo.get('dns', ''),
        'aps_domain': aps_addr.get('domain', ''),
        'aps_ip': aps_addr.get('ip', '')
    }
    e164 = data['devid'][20:33]
    nms_redis.ev_mt_info(e164, data['devtype'], json.dumps(info))


def ev_alarm_msg(data):
    '''
    {
        "devid": "1.2.2",
        "devtype": "Skywalker for Windows",
        "alarm_info": {
            "code_id": 1003,
            "report_time": "2014/05/08:12:08:08",
            "status": 0
        },
        "eventid": "EV_ALARM_MSG"
    }
    '''
    e164 = data['devid'][20:33]
    moid = nms_redis.get_terminal_moid(e164=e164)
    warning_handler(
        moid,
        data['alarm_info']['status'],
        data['alarm_info']['code_id'],
        data['rpttime'],
        'terminal',
        device_type=data['devtype']
    )
