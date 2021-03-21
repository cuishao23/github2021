import uuid
import logging
import json
from dao import nms_redis, nms_mysql
from core.warning import warning_handler
from config.warning import *
from config.common import LOGGING
from config import enum
from threads.msg_threads import mysql_write_thread

# 入会终端类型
MT_TYPE_SSMMCU = 2  # 简单下级级联会议
MT_TYPE_MT = 3  # 普通终端
MT_TYPE_MMMCU = 4  # 上级级联会议
MT_TYPE_CSMMCU = 5  # 复杂下级级联会议
MT_TYPE_PHONE = 6  # 电话终端
MT_TYPE_SATD = 7  # 卫星终端
MT_TYPE_VRSREC = 8  # vrs录像机
MT_TYPE_IPC = 21  # IPC监控前

# 会议类型

logger = logging.getLogger(LOGGING['loggername'])


def ev_dev_online(data):
    '''
    逻辑服务器上线
    {
        "eventid": "EV_DEV_ONLINE",
        "devid": "1111",
        "devtype": "SERVICE_TS_SRV_MPCD",
        "collectorid": "xxxx"
    }
    '''
    r = nms_redis.ev_dev_online_l(
        data['devid'], data['devtype'], data['collectorid'])
    # nms接入数量阈值告警
    warning_handler(r['collector_p_server_moid'], r['warning_trigger_flag'],
                    2016, data['rpttime'], 'p_server', **r)

    # 下线告警
    warning_handler(data['devid'], False, 2015, data['rpttime'], 'l_server')


def ev_dev_offline(data):
    '''
    逻辑服务器下线
    {
        "eventid": "EV_DEV_OFFLINE",
        "devid": "1111",
        "devtype": "SERVICE_TS_SRV_MPCD",
        "collectorid": "60a44c502a60"
    }
    '''
    if data['devtype'] == 'pas':
        nms_redis.offline_pas(data['devid'], data['collectorid'])
    elif data['devtype'] == 'ejabberd':
        nms_redis.offline_ejabberd(data['devid'], data['collectorid'])
    elif data['devtype'] == 'media-worker':
        nms_redis.offline_mediaworker(data['devid'], data['collectorid'])
    elif data['devtype'] == 'vrs':
        nms_redis.offline_vrs(data['devid'], data['collectorid'])
    elif data['devtype'] == 'cmu':
        nms_redis.offline_cmu(data['devid'], data['collectorid'])
    elif data['devtype'] == 'dcs':
        nms_redis.offline_dcs(data['devid'], data['collectorid'])

    r = nms_redis.ev_dev_offline_l(
        data['devid'], data['collectorid'])

    # nms接入数量阈值告警
    warning_handler(r['collector_p_server_moid'], r['warning_trigger_flag'],
                    2016, data['rpttime'], 'p_server', **r)

    # 下线告警
    warning_handler(data['devid'], True, 2015, data['rpttime'], 'l_server')


# TODO 优化, ev_ejabberd_info
def ev_xmpp_info(data):
    '''
    xmpp在线数
    {
        "eventid":"EV_XMPP_INFO",
        "devid":"1111"
        "devtype":"ejabberd",
        "rpttime":"2014/06/16:09:57:50",
        "version":"5.0.1",
        "xmppinfo":
        {
            "onlinecount":100
        }
    }
    '''
    nms_redis.ev_xmpp_info(data['devid'], data['xmppinfo']['onlinecount'])


# TODO 资源统计
def ev_mediaresource_info(data):
    '''
    端口会议资源
    {
        "eventid": "EV_MEDIARESOURCE_INFO",
        "devid": "1111"
        "devtype": "media-worker",
        "rpttime": "2014/06/16:09:57:50",
        "mediaresource_info":
        {
            "ceu_guid": "23456789", // CEU板卡的GUID
            "total_port": 64, // h.264端口资源总数
            "used_port": 32, // 已经使用的h.264端口数
            "h265_total_port": 64, // h.265端口资源总数
            "h265_used_port": 28, // 已经使用的h.265端口数
            "total_vmp": 32, // 合成器总数
            "used_vmp": 16, // 已使用的合成器数
            "total_mixer": 64, // 混音器总数
            "used_mixer": 48, // 已使用的混音器数
            "conf_count": 12, // 会议数
            "conf_info": [
                {
                    "conf_e164": "0513**88" // 会议E164号码
                },
                {
                    "conf_e164": "0513**99"
                }
            ]
        }
    }
    '''
    r = nms_redis.ev_mediaresource_info(
        data['devid'],
        json.dumps(data['mediaresource_info'])
    )

    # 端口使用率
    total = int(data['mediaresource_info']['total_port'])
    used = int(data['mediaresource_info']['used_port'])
    port_usage = 0 if total == 0 else used/total * 100

    # H265端口使用率
    total = int(data['mediaresource_info']['h265_total_port'])
    used = int(data['mediaresource_info']['h265_used_port'])
    h265_port_usage = 0 if total == 0 else used/total * 100

    # vmp使用率
    total = int(data['mediaresource_info']['total_vmp'])
    used = int(data['mediaresource_info']['used_vmp'])
    vmp_usage = 0 if total == 0 else used/total * 100

    # mixer使用率
    total = int(data['mediaresource_info']['total_mixer'])
    used = int(data['mediaresource_info']['used_mixer'])
    mixer_usage = 0 if total == 0 else used/total * 100

    r['current_value'] = max(port_usage, h265_port_usage)
    warning_handler(data['devid'], r['threshold_value'] <=
                    r['current_value'], 2007, data['rpttime'], 'l_server', **r)

    # r['current_value'] = h265_port_usage
    # warning_handler(data['devid'], r['threshold_value'] >=
    #                 port_usage, 2007, data['rpttime'], 'l_server', **r)

    r['current_value'] = vmp_usage
    warning_handler(data['devid'], r['threshold_value'] <=
                    vmp_usage, 2026, data['rpttime'], 'l_server', **r)

    r['current_value'] = mixer_usage
    warning_handler(data['devid'], r['threshold_value'] <=
                    mixer_usage, 2025, data['rpttime'], 'l_server', **r)


def ev_mps_info(data):
    '''
    传统会议资源
    {
        "eventid": "EV_MPS_INFO",
        "devid": "1111"
        "devtype": "mps",
        "rpttime": "2014/06/16:09:57:50",
        "mps_resource_info":
        {
            "mps_guid": "12345678", // MPU的GUID
            "total_vmp": 8, // 此MPU上的合成器总数
            "used_vmp": 2, // 此MPU上已经使用的合成器数
            "total_mixer": 8, // 此MPU上的混音器总数
            "used_mixer": 4, // 此MPU上已经使用的的混音器数
            "total_abas": 16, // 此MPU上总的ABas数
            "used_abas": 8, // 此MPU上已经使用的ABas数
            "total_vbas": 8, // 此MPU上总的VBas数
            "used_vbas": 2, // 此MPU上已经使用的VBas数
            "dev_type": "JD2000", // 外设的类型，JD2000/JD6000/JD10000/PHYSICALSERVER
            "dev_ip": "172.16.81.101", // 外设的ip地址
            "conf_count": 2 // 此MPU上的会议数
            "conf_info": [
                {
                    "conf_e164": "0513**77", // 会议E164号
                    "used_vbas": 2, // 此会议使用的VBas数
                    "used_abas": 2, // 此会议使用的ABas数
                    "used_vmp": 2, // 此会议使用的合成器数
                    "used_mixer": 2 // 此会议使用的的混音器数
                }
            ]
        }
    }
    '''
    r = nms_redis.ev_mps_info(
        data['devid'],
        json.dumps(data['mps_resource_info'])
    )

    # vmp使用率
    total = int(data['mps_resource_info']['total_vmp'])
    used = int(data['mps_resource_info']['used_vmp'])
    vmp_usage = 0 if total == 0 else used/total * 100

    # mixer使用率
    total = int(data['mps_resource_info']['total_mixer'])
    used = int(data['mps_resource_info']['used_mixer'])
    mixer_usage = 0 if total == 0 else used/total * 100

    r['current_value'] = vmp_usage
    warning_handler(data['devid'], r['threshold_value'] <=
                    vmp_usage, 2026, data['rpttime'], 'l_server', **r)

    r['current_value'] = mixer_usage
    warning_handler(data['devid'], r['threshold_value'] <=
                    mixer_usage, 2025, data['rpttime'], 'l_server', **r)


def ev_pas_info(data):
    '''
    pas上的终端在线详情
    {
        "eventid": " EV_PAS_INFO ",
        "devid": "1111",
        "devtype": "pas",
        "rpttime": "2014/06/16:09:57:50",
        "version": "1.06",
        "pasinfo": {
            "maxcallcount": 1234, // 支持的最大呼叫数
            "maxonlinecount": 123, // 支持的最大注册数
            "curonlinecount": 123,  // 当前注册的终端总数
            "h323onlinecount": 123, // H323类型的终端注册数
            "siponlinecount": 123,  // SIP类型的终端注册数
            "monitoronlinecount": 123, // 监控类型的终端在线数
            "callingcount": 123, // 当前的总呼叫数
            "rtconlinecount":123, //rtc类型终端在线数
            "confmtcount": 123
        }
    }
    '''
    r = nms_redis.ev_pas_info(
        data['devid'],
        data['pasinfo'].get('h323onlinecount', 0),
        data['pasinfo'].get('siponlinecount', 0),
        data['pasinfo'].get('monitoronlinecount', 0),
        data['pasinfo'].get('rtconlinecount', 0),
        data['pasinfo'].get('maxcallcount', 0),
        data['pasinfo'].get('callingcount', 0),
        data['pasinfo'].get('maxonlinecount', 0),
        data['pasinfo'].get('curonlinecount', 0)
    )

    # 呼叫对阈值告警
    threshold_value = int(r['callpair'])
    current_value = int(data['pasinfo']['callingcount'])
    warning_handler(data['devid'], threshold_value <= current_value,
                    2006, data['rpttime'], 'l_server', threshold_value=threshold_value, current_value=current_value)

    # pas接入阈值告警
    threshold_value = int(r['pas'])
    current_value = int(data['pasinfo']['curonlinecount'])
    warning_handler(data['devid'], threshold_value <= current_value,
                    2005, data['rpttime'], 'l_server', threshold_value=threshold_value, current_value=current_value)


def ev_mcu_conf_create(data):
    '''
    多点会议创建消息
    {
        "eventid": "EV_MCU_CONF_CREATE",
        "devid": "1111"
        "devtype": "cmu",
        "rpttime": "2014/06/16:09:57:50",
        "confinfo":
        {
            "mtcount": 8, // 与会终端数
            "conftype": 0, // 会议类型(0: 传统会议 1: 端口会议)
            "confbandwidth": 7, // 会议带宽
            "confe164": "0513**77", // 会议E164号
            "confname": " conf-AA", // 会议名称
            "domainmoid": "1234567890oofjg", // 会议所属域的MOID
            "domainname": "用户域1", // 会议所属域的名称
            "begintime": "2014/06/16:09:57:50", // 会议开始时间
            "endtime": "2014/06/16:10:57:50", // 会议结束时间
            "scale": 16, // 会议规模
            "organizer": "zhangsan", // 会议发起人
            "manager": "lisi", // 会议管理方
            "speaker": "wangwu", // 会议发言方
            "encryption": 7, // 会议加密算法
            "guest_mode": 7, // 来宾模式
            "call_type": 7, // 呼叫方式
            "resolution": 7, // 分辨率
            "frame": 7, // 帧率
            "bitrate": 7, // 比特率
            "format": 7 // 视频格式
        },
        "mt_info": [ // 与会终端
            {
                "mttype": 4,  // 终端类型
                "mtip": "1.1.1.1", // IP地址
                "mtaccount": "0512111885701", // 终端账号, 普通终端就是e164号码，电话终端就是电话号码，级联会议就是会议e164号
                "mtname": "123456", // 终端名称，可以为空
                "softversion": "1.2.1", // 终端软件版本号
                "begintime": "2014/06/16:09:57:50" // 终端入会时间
            }
        ]
    }
    '''
    meeting_info = {
        'domain_moid': data['confinfo']['domainmoid'],
        'conf_type': data['confinfo']['conftype'],
        'e164': data['confinfo']['confe164'],
        'name': data['confinfo']['confname'],
        'bandwidth': data['confinfo']['confbandwidth'],
        'start_time': data['confinfo']['begintime'],
        'stop_time': data['confinfo'].get('endtime', ''),
        'scale': data['confinfo'].get('scale', ''),
        'organizer': data['confinfo'].get('organizer', ''),
        'encryption': enum.LOGICAL_ENCRYPTION.get(data['confinfo'].get('encryption'), 'unkown'),
        'guest_mode': data['confinfo'].get('guest_mode', ''),
        'call_type': enum.CALL_TYPE.get(data['confinfo'].get('call_type'), 'unkown'),
        'resolution': enum.RESOLUTION.get(data['confinfo'].get('resolution'), 'unkown'),
        'frame': data['confinfo'].get('frame', ''),
        'bitrate': data['confinfo'].get('bitrate', ''),
        'format': enum.FORMAT.get(data['confinfo'].get('format'), 'unkown'),
        'cms': data['devid']
    }
    mt_info = []
    for info in data['mt_info']:
        arg = terminal_data_collation(info)
        if arg:
            mt_info.append(arg)

    meeting_type = enum.MEETING_TYPE[data['confinfo']['conftype']]
    # nms负责生成会议moid, 作为唯一标识
    conf_e164 = data['confinfo']['confe164']
    begin_time = data['confinfo']['begintime']
    meeting_moid = str(uuid.uuid3(uuid.NAMESPACE_DNS, conf_e164+begin_time))
    nms_redis.ev_mcu_conf_create(
        meeting_type, meeting_moid, json.dumps(meeting_info))
    r = nms_redis.add_meeting_terminal(
        data['confinfo']['confe164'], json.dumps(mt_info))

    for info in data['mt_info']:
        if info.get('mtaccount', '') not in r['terminals']:
            add_terminal_statistic(
                info,
                meeting_moid,
                r['meeting_moid']
            )


def ev_mcu_conf_destroy(data):
    '''
    结会消息
    {
        "eventid": "EV_MCU_CONF_DESTROY",
        "devid": "1111"
        "devtype": "cmu",
        "rpttime": "2014/06/16:09:57:50",
        "confinfo":
        {
            "confe164": "0513**77", // 会议E164号
            "endtime": "2014/06/16:10:57:50",
            "conftype": 1 // 会议类型(0: 传统会议 1: 端口会议)
        }
    }
    '''
    # 统计会议信息
    # 统计终端信息
    # 清除会议相关信息
    terminal_info_list = nms_redis.del_meeting_terminal(
        data['confinfo']['confe164'], data['rpttime'])

    r = nms_redis.ev_mcu_conf_destroy(
        data['confinfo']['confe164'], data['confinfo']['endtime'])

    # 会议信息
    if r.get('meeting_info'):
        mysql_write_thread.push(
            (nms_mysql.add_multi_meeting_statistic, r['meeting_info']))
    else:
        logger.error('ev_mcu_conf_destroy: lost meeting info')

    # 离会原因
    if r.get('leave_reason'):
        for info in r['leave_reason']:
            mysql_write_thread.push(
                (nms_mysql.add_terminal_leave_meeting_reason, info))

    # 终端会议评分记录
    if r.get('score_info'):
        for info in r['score_info']:
            mysql_write_thread.push(
                (nms_mysql.add_terminal_meeting_socre, info))

    # 终端信息
    for terminal_info in terminal_info_list:
        if terminal_info:
            mysql_write_thread.push(
                (nms_mysql.add_meeting_terminal_detail_statistic, terminal_info['terminal_detail']))
            for privideo in terminal_info['privideo']:
                mysql_write_thread.push(
                    (nms_mysql.add_terminal_meeting_privideo, privideo))
            for assvideo in terminal_info['assvideo']:
                mysql_write_thread.push(
                    (nms_mysql.add_terminal_meeting_assvideo, assvideo))


def ev_mcu_mt_add(data):
    '''
    终端入会消息
    {
        "eventid": "EV_MCU_MT_ADD",
        "devid": "1111"
        "devtype": "cmu",
        "rpttime": "2014/06/16:09:57:50",
        "mtinfo":
        {
            "confe164": "0513**77", // 会议E164号码
            "conftype": 1, // 会议类型(0: 传统会议 1: 端口会议)
            "mttype": 2, // 终端设备类型
            "mtip": "172.16.81.101", // 终端设备IP
            "mtaccount": "05121111888", // 终端账号
                # //普通终端就是e164号码
                # //电话终端就是电话号码
                # //级联会议就是会议e164号
            "mtname": "zhouyanhua", // 终端名称
            "softversion": "1.0.2.3", // 终端软件版本号
            "begintime": " 2014/06/16:10:57:50"//终端入会时间
        }
    }
    '''
    mt_info = terminal_data_collation(data['mtinfo'])

    r = nms_redis.add_meeting_terminal(
        data['mtinfo']['confe164'], json.dumps([mt_info])
    )
    if data['mtinfo'].get('mtaccount') not in r['terminals']:
        add_terminal_statistic(
            data['mtinfo'],
            r['meeting_moid'].get(data['mtinfo']['confe164'], ''),
            r['meeting_moid']
        )


def ev_mcu_mt_del(data):
    '''
    终端离会
    {
        "eventid": "EV_MCU_MT_DEL",
        "devid": "1111"
        "devtype": "cmu",
        "rpttime": "2014/06/16:09:57:50",
        "mtinfo":
        {
            "confe164": "0513**77", // 会议E164号
            "conftype": 1, // 会议类型(0: 传统会议 1: 端口会议)
            "mttype": 2, // 终端设备类型
            "mtaccount": "05121111888", // 终端账号
            # //普通终端就是e164号码
            # // 电话终端就是电话号码
            # // 级联会议就是会议e164号
            "mtip": "1.1.1.1",
            "endtime": "2014/06/16:10:57:50"
            "leavereason": 1 // 离会原因
        }
    }
    '''
    e164_or_ip = data['mtinfo'].get('mtaccount') if data['mtinfo'].get(
        'mtaccount', '') else data['mtinfo'].get('mtip', '')
    if e164_or_ip:
        r = nms_redis.del_meeting_terminal(
            data['mtinfo']['confe164'],
            data['mtinfo']['endtime'],
            e164_or_ip,
            data['mtinfo']['leavereason']
        )
        if r:
            mysql_write_thread.push(
                (nms_mysql.add_meeting_terminal_detail_statistic, r['terminal_detail']))
            for privideo in r['privideo']:
                mysql_write_thread.push(
                    (nms_mysql.add_terminal_meeting_privideo, privideo))
            for assvideo in r['assvideo']:
                mysql_write_thread.push(
                    (nms_mysql.add_terminal_meeting_assvideo, assvideo))


def ev_mcu_conf_update(data):
    '''
    会议信息更新
    {
        "eventid": "EV_MCU_CONF_UPDATE",
        "devid": "1111"
        "devtype": "cmu",
        "rpttime": "2014/06/16:09:57:50",
        "confinfo":
        {
            "confe164": "0513**77", // 会议E164号
            "conftype": 1, // 会议类型(0: 传统会议 1: 端口会议)
            "confname": "平台例会"
        }
    }
    '''
    meeting_type = enum.MEETING_TYPE[data['confinfo']['conftype']]
    nms_redis.ev_mcu_conf_update(
        meeting_type, data['confinfo']['confe164'], data['confinfo']['confname'])


def ev_mcu_conf_time_change(data):
    '''
    会议时间修改
    {
        "eventid":"EV_MCU_CONF_TIME_CHANGE",
        "devid":"1111"
        "devtype":"cmu",
        "rpttime":"2014/06/16:09:57:50",
        "confinfo":
        {
            "confe164":"0513**77", //会议E164号
            "conftype":1, //会议类型(0:传统会议 1:端口会议)
            "conf_endtime":"2014/06/16:10:57:50"
        }
    }
    '''
    meeting_type = enum.MEETING_TYPE[data['confinfo']['conftype']]
    nms_redis.ev_mcu_conf_time_change(
        meeting_type, data['confinfo']['confe164'], data['confinfo']['conf_endtime'])


def ev_pas_p2pconf_create(data):
    '''
    点对点创会消息
    {
        "eventid": "EV_PAS_P2PCONF_CREATE",
        "devid": "1111",
        "devtype": "pas",
        "rpttime": "2014/06/16:09:57:50",
        "confinfo": {
            "caller": {
                "devtype": "Skywalker for iPad", // 主叫方终端类型
                "devname": "AAA", // 主叫方终端别名
                "deve164": "051255566" // 主叫方终端E164号码
            },
            "callee": {
                "devtype": "Skywalker for iPad", // 被叫方终端类型
                "devname": "BBB", // 被叫方终端别名
                "deve164"："051255567" // 被叫方终端E164号码
            },
            "time"："2014/06/16:09:57:50", // 会议开始时间
            "bitrate": 256 // 会议码率
        }
    }
    '''
    # nms负责生成会议moid, 作为唯一标识
    conf_e164 = data['confinfo']['caller']['deve164']
    begin_time = data['confinfo']['time']
    meeting_moid = str(uuid.uuid3(uuid.NAMESPACE_DNS, conf_e164+begin_time))
    nms_redis.ev_pas_p2pconf_create(
        data['devid'], meeting_moid, json.dumps(data['confinfo']))


def ev_pas_p2pconf_destroy(data):
    '''
    点对点会议销毁
    {
        "eventid": "EV_PAS_P2PCONF_DESTROY",
        "devid": "1111",
        "devtype": "pas",
        "rpttime": "2014/06/16:09:57:50",
        "confinfo": {
                "callerE164": "051255566", // 主叫方终端E164号码
                "calleeE164": "051255567" // 被叫方终端E164号码
        }
    }
    '''
    r = nms_redis.ev_pas_p2pconf_destroy(
        data['devid'], data['confinfo']['callerE164'], data['confinfo']['calleeE164'], data['rpttime'])
    if r:
        mysql_write_thread.push(
            (nms_mysql.add_p2p_meeting_statistic, r['meeting_info']))
        for info in r['terminal_info'].values():
            mysql_write_thread.push(
                (nms_mysql.add_meeting_terminal_detail_statistic, info['terminal_detail']))
            for privideo in info['privideo']:
                mysql_write_thread.push(
                    (nms_mysql.add_terminal_meeting_privideo, privideo))
            for assvideo in info['assvideo']:
                mysql_write_thread.push(
                    (nms_mysql.add_terminal_meeting_assvideo, assvideo))


def ev_pas_mt_encryption(data):
    '''
    终端加密类型
    {
        "eventid":"EV_PAS_MT_ENCRYPTION",
        "devid":"1111"
        "devtype":"pas",
        "rpttime":"2014/06/16:09:57:50",
        "mt_info":[
            {
                    "mt_e164":"051255566" //终端e164号码
                    "mt_encryption":"AES128" // 终端加密方式
            },
            {
                    "mt_e164":"051255567"
                    "mt_encryption":"SM4"
            }
        ]
    }
    '''
    nms_redis.ev_pas_mt_encryption(json.dumps(data.get('mt_info', {})))


def ev_pas_all_online_stat(data):
    '''
    用户域终端在线统计
    {
        "eventid":" EV_PAS_ALL_ONLINE_STAT ",
        "devid":"1111"
        "devtype":"pas",
        "rpttime":"2014/06/16:09:57:50",
        "online_stat_list":[
            {
                "domain_moid":"xxxxxxxxxxxx", //用户域moid
                "sip_count":128, //SIP在线数
                "h323_count":10, //H323在线数
                "rtc_count":10 //H323在线数
            },
            {
                "domain_moid":"yyyyyyyyyyyy",
                "sip_count":128,
                "h323_count":10,
                "rtc_count":10
            }
        ]
    }
    '''
    nms_redis.ev_pas_all_online_stat(
        data['devid'], json.dumps(data['online_stat_list']))


def ev_modb_warning_info(data):
    '''
    MODB告警
    {
        "eventid":"EV_MODB_WARNING_INFO",
        "devid":"1111"
        "devtype":"modb",
        "rpttime":"2014/06/16:09:57:50",
        "version":"5.0.1",
        "warning_info":
        {
            "status":1, //告警状态 0:修复告警，1：产生告警
            'last_right_ver":" A:123,B:22,C:11",// 最近一次正确的版本号
            "srv_ip":"172.16.81.90" //服务器IP
        }
    }
    '''
    r = nms_redis.ev_modb_warning_info(data['devid'])
    warning_handler(
        data['devid'],
        data['warning_info']['status'],
        2020,
        data['rpttime'],
        'l_server'
    )
    # 通知BMC, 鬼知道为啥... :(
    if data['warning_info']['status']:
        from threads.mq_threads import rmq_produce_thread
        msg = {
            'type': 'NmsModbWarnging',
            'serverMoid': data['devid'],
            'fromIp': data['warning_info']['srv_ip'],
            'serviceDomainMoid': r,
            'lastUpdateFullVersion': data['warning_info']['last_right_ver']
        }
        rmq_produce_thread.push(
            ('movision.nms.ex', 'movision.warning.k', json.dumps(msg))
        )


def ev_aps_all_mt_info(data):
    '''
    上报所有终端运营商消息
    {
        "eventid":"EV_APS_ALL_MT_INFO",
        "devid":"1111"
        "devtype":"aps",
        "rpttime":"2014/06/16:09:57:50",
        "mt_info:[
            {
                "mt_moid":"000122222111111",
                "operator_type":7
            },
            {
                "mt_moid":"000122222111111",
                "operator_type":4
            }
        ]
    }
    '''
    nms_redis.ev_aps_all_mt_info(json.dumps(data['mt_info']))


def ev_aps_add_mt_info(data):
    '''
    终端添加消息
    {
        "eventid":" EV_APS_ADD_MT_INFO",
        "devid":"1111"
        "devtype":"aps",
        "rpttime":"2014/06/16:09:57:50",
        "mt_moid":"000122222111111",
        "operator_type":7
    }
    '''
    nms_redis.ev_aps_add_mt_info(data['mt_moid'], data['operator_type'])


def ev_vrs_info(data):
    '''
    上报VRS信息
    {
        "eventid":"EV_VRS_INFO",
        "devid":"1111"
        "devtype":"vrs",
        "rpttime":"2014/06/16:09:57:50",
        "vrs_info":
        {
            "vrs_recroomocp":20, // 录像室已使用数
            "vrs_recroomtotal ":30, // 录像室总数
            "vrs_html5lcastocp":7, // html5直播资源占用数
            "vrs_html5lcasttotal":15, // html5直播资源总数
            "vrs_lcastocp":10, // asf直播资源占用数
            "vrs_lcasttotal":25 // asf直播资源总数
        }
    }
    '''
    # 消已删除, 不处理
    pass


def ev_vrs_create_live_info(data):
    '''
    直播创建消息
    {
    "eventid":"EV_VRS_CREATE_LIVE_INFO",
    "devid":"1111"
    "devtype":"vrs",
    "rpttime":"2014/06/16:09:57:50",
    "create_live_info":
        {
        "conf_e164":"1230209", //会议E164号码
        "live_name":"xxxxxx", //直播名称
        "live_start_time":"2018/2/8 09:10:00", //直播开始时间
        "encmode":1, //节目加密类型(1.不加密 2.标准加密 3.国密加密)
        "authmode":2 //认证类型(1.普通 2.强认证)
        }
    }
    '''
    nms_redis.ev_vrs_create_live_info(
        data['devid'],
        data['create_live_info']['conf_e164'],
        str(uuid.uuid1()),
        data['create_live_info'].get('live_name', ''),
        data['create_live_info']['live_start_time'],
        data['create_live_info'].get('encmode', 1),
        data['create_live_info'].get('authmode', 1)
    )


def ev_vrs_update_user_info(data):
    '''
    更新直播用户信息
    {
        "eventid":"EV_VRS_UPDATE_USER_INFO",
        "devid":"1111"
        "devtype":"vrs",
        "rpttime":"2014/06/16:09:57:50",
        "update_user_info":
        {
            "conf_e164":”1230209”, // 会议E164号
            "user_e164":"ter_a_e164", // 用户E164号码，有就填，否则设置为 ""
            "user_moid":"ter_a_moid", // 用户moid，非游客必填，游客为 ""
            "user_name":"ter_a_name", // 用户名称，必填
            "change_time":"2018/2/8 09:20:00", //更新时间
            "user_state":1 //用户状态，0-下线 1-上线
        }
    }
    '''
    r = nms_redis.ev_vrs_update_user_info(
        data['update_user_info'].get('user_moid', str(uuid.uuid1())),
        data['update_user_info']['conf_e164'],
        data['update_user_info'].get('user_e164', ''),
        data['update_user_info']['user_name'],
        data['update_user_info']['change_time'],
        data['update_user_info']['user_state']
    )
    if r:
        mysql_write_thread.push((nms_mysql.add_live_user_info, r))


def ev_vrs_destroy_live_info(data):
    '''
    直播结束消息
    {
        "eventid":"EV_VRS_DESTROY_LIVE_INFO",
        "devid":"1111"
        "devtype":"vrs",
        "rpttime":"2014/06/16:09:57:50",
        "destroy_live_info":
        {
            "conf_e164":"1230209", // 会议E164号
            "end_time":"2018/2/8 09:20:00"  //结束时间
        }
    }
    '''
    r = nms_redis.ev_vrs_destroy_live_info(
        data['devid'],
        data['destroy_live_info']['conf_e164'],
        data['destroy_live_info']['end_time']
    )
    mysql_write_thread.push(
        (nms_mysql.add_live_info, r['live_info'])
    )
    for info in r['live_users']:
        mysql_write_thread.push(
            (nms_mysql.add_live_user_info, info)
        )


def ev_vrs_create_aplive_info(data):
    '''
    预约直播创建
    {
        "eventid":"EV_VRS_CREATE_APLIVE_INFO",
        "devid":"1111"
        "devtype":"vrs",
        "rpttime":"2014/06/16:09:57:50",
        "create_aplive_info":
        {
            "user_domain_moid":"moid", //用户所属域Moid
            "conf_e164":"1230209", // 会议E164号
            "live_name":"live_name", //直播名称
            "live_start_time":"2018/2/8 09:20:00", //直播开始时间
            "encmode":1 //节目加密类型(1.不加密 2.标准加密 3.国密加密)
        }
    }
    '''
    nms_redis.ev_vrs_create_aplive_info(
        data['create_aplive_info']['user_domain_moid'],
        data['create_aplive_info']['conf_e164'],
        data['create_aplive_info']['live_name'],
        data['create_aplive_info']['live_start_time'],
        data['create_aplive_info']['encmode']
    )


def ev_vrs_destroy_aplive_info(data):
    '''
    预约直播销毁消息
    {
        "eventid":"EV_VRS_DESTROY_APLIVE_INFO",
        "devid":"1111"
        "devtype":"vrs",
        "rpttime":"2014/06/16:09:57:50",
        "destroy_aplive_info":
        {
            "conf_e164":"1230209", // 会议E164号
            "live_start_time":"2018/2/8 09:20:00" //直播开始时间
        }
    }
    '''
    nms_redis.ev_vrs_destroy_aplive_info(
        data['destroy_aplive_info']['conf_e164'])


def ev_alarm_report(data):
    '''
    安全告警信息上报
    告警流程:
        1. 如果有多个模块上报同一告警, 只告警一次, 再收到同样的告警码, 不再继续告警;
        2. 如果收到告警解除, 只有所有模块的告警都解除后, 才能解除告警;
    {
        "eventid":"EV_ALARM_REPORT",
        "devid":"1111"
        "devtype":"pas",
        "rpttime":"2014/06/16:09:57:50",
        "alarm_info":
        {
            "module_type":"xxxx", //内部模块
            "alarm_code":2003, //告警码
            "alarm_status":1 //告警状态,0:解除告警，1:产生告警
        }
    }
    '''
    r = nms_redis.ev_alarm_report(
        data['devid'],
        data['alarm_info']['module_type'],
        data['alarm_info']['alarm_code'],
        data['alarm_info']['alarm_status']
    )
    if r:
        warning_handler(
            data['devid'],
            r['warning_trigger_flag'],
            data['alarm_info']['alarm_code'],
            data['rpttime'],
            'l_server'
        )


def ev_dcs_create_conf_info(data):
    '''
    数据会议创建信息
    {
        "eventid":"EV_DCS_CREATE_CONF_INFO",
        "devid":"1111"
        "devtype":"dcs",
        "rpttime":"2014/06/16:09:57:50",
        "createconf ":
        {
            "conftype":1, //会议类型(1-多点会议，0-点对点会议)
            "dcsmode":0, //DCS模式, 0-自由模式/1-管理方模式
            "mtcount":7, //与会终端总数
            "confe164":"1230209", //会议E164号码
            "begintime":"2018/2/8 09:20:00", //会议开始时间
            "mtinfo":[ //终端列表
                {
                    "mtaccount":"05121118883", //终端e164号码
                    "onlinestate":1,//终端在线状态0-离线，1-在线
                    "coopstate":1  //协作状态0-未参与协作， 1-参与协作
                },
                {
                    "mtaccount":"05121118884", //终端e164号码
                    "onlinestate":1, //终端在线状态0-离线，1-在线
                    "coopstate":0  //协作状态0-未参与协作， 1-参与协作
                }
            ]
        }
    }
    '''
    nms_redis.ev_dcs_create_conf_info(
        str(uuid.uuid1()),
        data['createconf']['confe164'],
        data['createconf']['dcsmode'],
        data['createconf']['begintime'],
        json.dumps(data['createconf'].get('mtinfo', []))
    )


def ev_dcs_online_state_change_info(data):
    '''
    终端在线状态改变消息
    {
        "eventid":"ev_dcs_online_state_change_info",
        "devid":"1111"
        "devtype":"dcs",
        "rpttime":"2014/06/16:09:57:50",
        "onlinestate":
        {
            "mtaccount":”05121118883”, //终端e164号码
            "confe164":”1230209”, //终端所属会议的e164号
            "conftype":1, //会议类型(1-多点会议，0-点对点会议)
            "changetime":"2018/2/8 09:20:00", //状态改变时间
            "onlinestate": 0//终端在线状态0-离线，1-在线
        }
    }
    '''
    pass


def ev_dcs_coop_state_change_info(data):
    '''
    终端协作状态改变消息
    {
        "eventid": "EV_DCS_COOP_STATE_CHANGE_INFO",
        "devid": "1111"
        "devtype": "dcs",
        "rpttime": "2014/06/16:09:57:50",
        "coopstate":
        {
            "mtaccount": "05121118883", // 终端e164号码
            "confe164": "1230209", // 终端所属会议的E164号
            "conftype": 1, // 会议类型(1-多点会议，0-点对点会议)
            "changetime": "2018/2/8 09:20:00", // 状态改变时间
            "coopstate": 0//终端协作状态0-未参与协作， 1-参与协作
        }
    }
    '''
    r = nms_redis.ev_dcs_coop_state_change_info(
        data['coopstate']['confe164'],
        data['coopstate']['mtaccount'],
        data['coopstate']['changetime'],
        data['coopstate']['coopstate']
    )
    if r:
        mysql_write_thread.push(
            (nms_mysql.add_terminal_info_for_dcs, r)
        )


def ev_dcs_conf_mt_del_info(data):
    '''
    删除数据会议终端消息
    {
        "eventid":"EV_DCS_CONF_MT_DEL_INFO",
        "devid":"1111"
        "devtype":"dcs",
        "rpttime":"2014/06/16:09:57:50",
        "delmt":
        {
            "mtaccount":"05121118883", //终端e164号码
            "confe164":"1230209", //终端所属会议的E164号
            "conftype":1, //会议类型(1-多点会议，0-点对点会议)
            "deltime":"2018/2/8 09:20:00",//终端删除时间
        }
    }
    '''
    r = nms_redis.ev_dcs_conf_mt_del_info(
        data['delmt']['confe164'],
        data['delmt']['mtaccount'],
        data['delmt']['deltime']
    )
    if r:
        mysql_write_thread.push(
            (nms_mysql.add_terminal_info_for_dcs, r)
        )


def ev_dcs_res_info(data):
    '''
    数据会议资源统计消息
    {
        "eventid":"EV_DCS_RES_INFO",
        "devid":"1111"
        "devtype":"dcs",
        "rpttime":"2014/06/16:09:57:50",
        "resinfo":
        {
            "maxconfnum":32, //最大支持的协作会议召开数，默认32个
            "maxmtnum":64, //协作终端总数，根据license授权数
            "confnum":8, //当前协作会议召开数
            "mtnum":32 //当前协作终端数
        }
    }
    '''
    # 消息删除, 不做处理
    pass


def ev_dcs_mode_switch(data):
    '''
    模式切换消息
    {
        "eventid":"EV_DCS_MODE_SWITCH",
        "devid":"1111"
        "devtype":"dcs",
        "rpttime":"2014/06/16:09:57:50",
        "dcsmode":
        {
            "conftype":1, //会议类型(1-多点会议，0-点对点会议)
            "dcsmode":0, //DCS模式, 0-自由模式/1-管理方模式
            "confe164":"1230209" //终端所属会议的E164号
        }
    }
    '''
    r = nms_redis.ev_dcs_mode_switch(
        data['dcsmode']['confe164'],
        data['dcsmode']['dcsmode']
    )
    if r:
        mysql_write_thread.push(
            (nms_mysql.add_dcs_mode_change_recode, r)
        )


def ev_dcs_destroy_conf_info(data):
    '''
    数据会议结束消息
    {
        "eventid":"EV_DCS_DESTROY_CONF_INFO",
        "devid":"1111"
        "devtype":"dcs",
        "rpttime":"2014/06/16:09:57:50",
        "delconf":
        {
            "confe164":"1230209", //会议E164号码
            "conftype":1, //会议类型(1-多点会议，0-点对点会议)
            "endtime":"2018/2/8 09:20:00" //会议结束时间
        }
    }
    '''
    r = nms_redis.ev_dcs_destroy_conf_info(
        data['delconf']['confe164'],
        data['delconf']['endtime']
    )
    if r:
        for terminal_info in r['terminals']:
            mysql_write_thread.push(
                (nms_mysql.add_terminal_info_for_dcs, terminal_info)
            )
        mysql_write_thread.push(
            (nms_mysql.add_meeting_dcs_info, r['dcs_info'])
        )
        mysql_write_thread.push(
            (nms_mysql.add_dcs_mode_change_recode, r['mode_recode'])
        )


def ev_rms_mp_info(data):
    '''
    媒体端口资源，定时上报
    {
        "eventid":"EV_RMS_MP_INFO",
        "devid":"1111"
        "devtype":"rms",
        "rpttime":"2014/06/16:09:57:50",
        "mp_info":
        {
            "moid":”xxxx”, //用户域或机房moid
            "total_h264":2003,
            "used_h264":7,
            "total_h265":2003,
            "used_h265":7,
            "server_type": 0 // 0 --非国密  1--国密s
        }
    }
    '''
    nms_redis.ev_rms_mp_info(
        data['mp_info']['server_type'],
        data['mp_info']['moid'],
        data['mp_info']['total_h264'],
        data['mp_info']['used_h264'],
        data['mp_info']['total_h265'],
        data['mp_info']['used_h265']
    )


def ev_ds_data_throughput_report(data):
    '''
    上报转发流量
    {
        "eventid":"EV_DS_DATA_THROUGHPUT_REPORT",
        "devid":"1111"
        "devtype":"dss-worker",
        "rpttime":"2014/06/16:09:57:50",
        "data_throughput":
        {
            "rate_of_flow":7
        }
    }
    '''
    r = nms_redis.ev_ds_data_throughput_report(
        data['devid'],
        data['data_throughput']['rate_of_flow']
    )
    warning_handler(r['p_server_moid'], r['warning_trigger_flag'],
                    2046, data['rpttime'], 'p_server', **r)


def ev_ds_packet_loss_rate_report(data):
    '''
    上报丢包率
    {
        "eventid": "EV_DS_PACEV_DS_PACKET_LOSS_RATE_REPORTKET_LOSS_RATE_REPORT",
        "devid": "1111"
        "devtype": "dss-worker",
        "rpttime": "2014/06/16:09:57:50",
        "packet_loss_rate_info":
        {
            "send_loss_rate": 7,
            "recv_loss_rate": 7
        }
    }
    '''
    nms_redis.ev_ds_packet_loss_rate_report(
        data['devid'],
        data['packet_loss_rate_info']['send_loss_rate'],
        data['packet_loss_rate_info']['recv_loss_rate']
    )


def ev_logical_server_info(data):
    '''
    {
        "eventid": "EV_LOGICAL_SERVER_INFO",
        "devid": "1111"
        "devtype": "pas", // 所有业务都会上报版本信息
        "rpttime": "2014/06/16:09:57:50",
        "serverinfo":
        {
            "version": "5.0.1 20181212"
        }
    }
    '''
    nms_redis.ev_logical_server_info(
        data['devid'], data['serverinfo']['version'])


def ev_machine_room_res_info(data):
    '''
    机房会议资源统计
    {
        "eventid":"EV_MACHINE_ROOM_RES_INFO",
        "devid":"1111"
        "devtype":"media-master",
        "rpttime":"2014/06/16:09:57:50",
        "room_res_info":
        {
            "machine_room_moid":"111111111111111111", //机房moid
            "total_port":10, //机房总共端口数
            "remainder_port":8, //剩余端口数
            "remainder_tra":5 //机房预计剩余可召开传统会议数
        }
    }
    '''
    nms_redis.ev_machine_room_res_info(
        data['room_res_info']['machine_room_moid'],
        data['room_res_info']['total_port'],
        data['room_res_info']['remainder_port'],
        data['room_res_info']['remainder_tra']
    )


def ev_rms_ap_info(data):
    '''
    接入端口资源
    {
        "eventid": "EV_RMS_AP_INFO",
        "devid": "1111"
        "devtype": "rms",
        "rpttime": "2014/06/16:09:57:50",
        "ap_info":
        {
            "moid": ”yyyyyyyyy”, // 用户域或机房moid
            "total": 100,
            "used": 50,
            "server_type": 0 // 0 - -非国密  1--国密
        }
    }
    '''
    # 国密：domain:{userDomainMoid}:g_ap 和 machine_room:{machineRoomMoid}:g_ap
    # 非国密：domain:{userDomainMoid}:ap 和 machine_room:{machineRoomMoid}:ap
    nms_redis.ev_rms_ap_info(
        data['ap_info']['moid'],
        data['ap_info']['total'],
        data['ap_info']['used'],
        data['ap_info']['server_type']
    )


def ev_rms_vmr_info(data):
    '''
    虚拟会议室信息
    {
        "eventid": "EV_RMS_VMR_INFO",
        "devid": "1111"
        "devtype": "rms",
        "rpttime": "2014/06/16:09:57:50",
        "vmr_info":
        {
            "moid": "xxxxxxxxxxxxxxx", // 机房或用户域moid
            "env_type": 0,  // 用户域或机房环境类型0：JDCloud传统会议模式，1: JD_MCU，2：JDCloud端口会议模式
            "total_192_1080": 64,
            "used_192_1080": 32,
            "total_192_720": 64,
            "used_192_720": 32,
            "total_64_1080": 64,
            "used_64_1080": 32,
            "total_64_720": 64,
            "used_64_720": 32,
            "total_32_1080": 64,
            "used_32_1080”: 32,
            "total_32_720": 64,
            "used_32_720": 32,
            "total_8_1080": 64,
            "used_8_1080": 32,
            "total_8_720": 64,
            "used_8_720": 32
        }
    }
    '''
    nms_redis.ev_rms_vmr_info(
        data['vmr_info']['moid'],
        data['vmr_info']
    )


def ev_conf_res_info(data):
    '''
    会议资源占用情况
    {
        "eventid": "EV_CONF_RES_INFO",
        "devid": "1111"
        "devtype": "media-master",
        "rpttime": "2014/06/16:09:57:50",
        "conf_res_info":
        [
            {
                "conf_e164": "11111111", // 会议e164号码
                "port": 3, // 占用端口数(端口会议占用的端口数或者传统会议挤占的端口数)
                "tra": 1//传统会议占用数(端口数转换成的传统会议数, 如果不是纯转发会议, 该值为1, 纯转发会议不需要发送此消息)
            },
            {
                "conf_e164": "2222222",
                "port": 5,
                "tra": 2
            }
        ]
    }
    '''
    nms_redis.ev_conf_res_info(json.dumps(data['conf_res_info']))


def ev_sfu_conf_res_info(data):
    '''
    sfu会议资源消息
    {
        "eventid":"EV_SFU_CONF_RES_INFO",
        "devid":"1111"
        "devtype":"sfumaster",
        "rpttime":"2014/06/16:09:57:50",
        "sfu_info":
        {
            "moid":"xxxx", //机房moid
            "remainder_count":20  //剩余接入sfu终端数
            "used_count":7  //已接入sfu终端数
        }
    }
    '''
    nms_redis.ev_machine_room_sfu_info(
        data['sfu_info']['moid'],
        data['sfu_info']['remainder_count'],
        data['sfu_info']['used_count']
    )


# # # # # #
# 函数
# # # # # #


def terminal_data_collation(info):
    # 下级级联
    args = {}
    if info['mttype'] == MT_TYPE_SSMMCU or info['mttype'] == MT_TYPE_CSMMCU:
        args = {'mttype': 'meeting',
                'e164': info['mtaccount'], 'type': 'down_meeting'}

    # 普通终端(包含ip和友商)
    elif info['mttype'] == MT_TYPE_MT:
        if info.get('mtaccount'):
            args = {'mttype': 'terminal', 'e164': info['mtaccount'], 'ip': info.get(
                'mtip', ''), 'softversion': info.get('softversion', '')}
        else:
            args = {'mttype': 'e164_ip',
                    'e164': info['mtip'], 'ip': info['mtip'], 'name': info.get('mtname', '')}

    # 上级级联
    elif info['mttype'] == MT_TYPE_MMMCU:
        args = {'mttype': 'meeting',
                'e164': info['mtaccount'], 'type': 'up_meeting'}

    # 电话
    elif info['mttype'] == MT_TYPE_PHONE:
        args = {'mttype': 'telphone', 'e164': info['mtaccount']}

    # ipc
    elif info['mttype'] == MT_TYPE_IPC:
        args = {'mttype': 'ipc', 'e164': info['mtaccount']}

    elif info['mttype'] == MT_TYPE_SATD:
        pass
    elif info['mttype'] == MT_TYPE_VRSREC:
        pass

    if args:
        args['begintime'] = info['begintime']
    return args


def add_terminal_statistic(info, meeting_moid, meeting_moid_map):
    mttype = info['mttype']
    # 下级级联
    if mttype == MT_TYPE_SSMMCU or mttype == MT_TYPE_CSMMCU:
        mysql_write_thread.push((nms_mysql.add_meeting_meeting_statistic, {
            'meeting_moid': meeting_moid,
            'attend_meeting_moid': meeting_moid_map.get(info['mtaccount'], ''),
            'attend_conf_e164': info['mtaccount'],
            'attend_start_time': info['begintime'],
            'attend_conf_name': info.get('mtname', ''),
            'cascade_type': 'down_meeting'
        }))

    # 普通终端
    elif mttype == MT_TYPE_MT:
        mysql_write_thread.push((nms_mysql.add_ip_e164_meeting_statistic, {
            'meeting_moid': meeting_moid,
            'ip_e164': info['mtaccount'],
            'name': info.get('mtname', '')
        }))

    # 上级级联
    elif mttype == MT_TYPE_MMMCU:
        mysql_write_thread.push((nms_mysql.add_meeting_meeting_statistic, {
            'meeting_moid': meeting_moid,
            'attend_conf_e164': info['mtaccount'],
            'attend_start_time': info['begintime'],
            'attend_conf_name': info.get('mtname', ''),
            'cascade_type': 'up_meeting'
        }))

    # 电话
    elif mttype == MT_TYPE_PHONE:
        mysql_write_thread.push((nms_mysql.add_tel_meeting_statistic, {
            'meeting_moid': meeting_moid,
            'tel_number': info['mtaccount']
        }))

    # ipc
    elif mttype == MT_TYPE_IPC:
        mysql_write_thread.push((nms_mysql.add_ipc_meeting_statistic, {
            'meeting_moid': meeting_moid,
            'ipc_e164': info['mtaccount'],
            'ipc_ip': info.get('mtip', '')

        }))
    elif mttype == MT_TYPE_SATD:
        pass
    elif mttype == MT_TYPE_VRSREC:
        pass
