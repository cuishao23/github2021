import json
import time
from dao import nms_redis
from core.warning import warning_handler
from config.common import SERVER_RESOURCE_LIMIT
from config.warning import *


def ev_server_info(data):
    '''
    服务器信息
    {
        "eventid":"EV_SERVER_INFO",
        "devid":"1111",
        "devtype":"x86_server",
        "rpttime":"2014/06/16:09:57:50",
        "serverinfo":[
            {"ip":"172.16.100.1"},
            {"ip":"172.16.110.1"}]
    }
    '''
    ip_list = [ip_info['ip'] for ip_info in data['serverinfo']]
    nms_redis.ev_server_info(data['devid'], ';'.join(ip_list))


def ev_dev_online(data):
    '''
    物理服务器上线
    {
        "eventid": "EV_DEV_ONLINE",
        "devid": "111",
        "devtype": "SERVICE_SRV_PHY",
        "collectorid": "60a44c502a60"
    }
    '''
    r = nms_redis.ev_dev_online_p(
        data['devid'], data['devtype'], data['collectorid'])

    # nms接入数量阈值告警
    warning_handler(r['collector_p_server_moid'], r['warning_trigger_flag'],
                    2016, data['rpttime'], 'p_server', **r)

    # 下线告警修复
    code = 2015 if data['devtype'] == 'x86_server' else 3010
    warning_handler(data['devid'], False, code, data['rpttime'], 'p_server')


def ev_dev_offline(data):
    '''
    物理服务器下线
    {
        "eventid": "EV_DEV_OFFLINE",
        "devid": "111",
        "devtype": "SERVICE_SRV_PHY",
        "collectorid": "60a44c502a60"
    }
    '''
    r = nms_redis.ev_dev_offline_p(
        data['devid'], data['collectorid'])

    # nms接入数量阈值告警
    warning_handler(r['collector_p_server_moid'], r['warning_trigger_flag'],
                    2016, data['rpttime'], 'p_server', **r)

    # 下线告警
    code = 2015 if data['devtype'] == 'x86_server' else 3010
    warning_handler(data['devid'], True, code, data['rpttime'], 'p_server')


def ev_systime_sync(data):
    '''
    时间同步
    {
        "eventid": "EV_SYSTIME_SYNC",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/16:09:57:50",
        "syncstate": 0  //时间同步状态，0：未同步，1：同步
    }
    '''
    warning_handler(data['devid'], int(data['syncstate']) == 0,
                    2004, data['rpttime'], 'p_server')


def ev_pfminfo_cpu(data):
    from dao.graphite_statistic import add_cpu_resource_statistic
    '''
    cpu状态
    {
        "eventid": "EV_PFMINFO_CPU",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/16:09:57:50",
        "cpuinfo": {
            "cpuusage": 80, // 总的cpu使用率
            "cpucorecount": 8, // cpu个数
            "coreinfo": [
                {"cpucore1": 100},
                {"cpucore2": 10},
                {"cpucore3": 20},
                {"cpucore4": 30},
                {"cpucore5": 40},
                {"cpucore6": 50},
                {"cpucore7": 60},
                {"cpucore8": 70}
            ]
        }
    }
    '''
    coreinfo = {}
    for info in data['cpuinfo']['coreinfo']:
        coreinfo.update(info)
    r = nms_redis.ev_pfminfo_cpu(
        data['devid'], data['cpuinfo']['cpuusage'], data['cpuinfo']['cpucorecount'], json.dumps(coreinfo))
    for key, value in coreinfo.items():
        add_cpu_resource_statistic(
            r['machine_room_moid'], data['devid'], key, value, int(time.time()))
    add_cpu_resource_statistic(
        r['machine_room_moid'], data['devid'], 'cpuusage', data['cpuinfo']['cpuusage'], int(
            time.time())
    )
    code = 2002 if data['devtype'] == 'x86_server' else 3007
    warning_handler(data['devid'], r['warning'], code,
                    data['rpttime'], 'p_server', **r)


def ev_pfminfo_mem(data):
    from dao.graphite_statistic import add_mem_resource_statistic
    '''
    内存状态
    {
        "eventid":"EV_PFMINFO_MEM",
        "devid":"1111",
        "devtype":"x86_server",
        "rpttime":"2014/06/16:09:57:50",
        "meminfo":{
            "total":2048, //总的mem大小
            "used":1024, //已使用的mem大小
            "userate":50 ////mem使用率(单位:万分之几)
        }
    }
    '''
    r = nms_redis.ev_pfminfo_mem(
        data['devid'], data['meminfo']['total'], data['meminfo']['used'], data['meminfo']['userate']
    )
    add_mem_resource_statistic(
        r['machine_room_moid'], data['devid'], data['meminfo']['userate'], int(time.time()))
    code = 2003 if data['devtype'] == 'x86_server' else 3008
    warning_handler(data['devid'], r['waring'], code,
                    data['rpttime'], 'p_server', **r)


def ev_pfminfo_disk(data):
    '''
    磁盘状态
    {
        "eventid":"EV_PFMINFO_DISK",
        "devid":"1111",
        "devtype":"x86_server",
        "rpttime":"2014/06/16:09:57:50",
        "disknum": 2,
        "diskinfo":[
            # old
            {
                "totalsize" : 128, //磁盘总空间(G)
                "used":28479932, //已使用空间大小
                "userate":3,  //磁盘空间使用率
                "diskname": "sda1"
            },
            # new
            {
                "totalsize" : 128, //磁盘总空间
                "usesize":1024, //已使用空间大小(M)
                "userate":3  //磁盘空间使用率
                "diskname": "sda2"
            }
        ]
    }
    '''
    if isinstance(data['diskinfo'], list):
        diskinfo = [
            {
                "totalsize": info["totalsize"],
                "usesize": round(info["usesize"]/1024),
                "userate": info["userate"],
                "diskname": info["diskname"],
            } for info in data['diskinfo']
        ]
    else:
        diskinfo = [{
            "totalsize": round(data['diskinfo']["total"]/1024/1024),
            "usesize": round(data['diskinfo']["used"]/1024/1024),
            "userate": data['diskinfo']["userate"],
            "diskname": 'disk'
        }]
    totalsize = sum((info['totalsize'] for info in diskinfo))
    usesize = sum((info['usesize'] for info in diskinfo))
    total_usereate = int(usesize/totalsize*100)
    r = nms_redis.ev_pfminfo_disk(
        data['devid'], total_usereate, json.dumps(diskinfo)
    )
    code = 2018 if data['devtype'] == 'x86_server' else 3009
    warning_handler(data['devid'], r['waring'], code,
                    data['rpttime'], 'p_server', **r)


def ev_pfminfo_disk_age(data):
    '''
    磁盘寿命
    {
        "eventid":"EV_PFMINFO_DISK_AGE",
        "devid":"1111",
        "devtype":"x86_server",
        "rpttime":"2014/06/16:09:57:50",
        "diskage": [
            {"dev": "sda1", "age": 20},
            {"dev": "sda2", "age": 20}
        ]
    }
    '''
    diskage = {info['dev']: info['age'] for info in data['diskage'] if info}
    if diskage:
        nms_redis.ev_pfminfo_disk_age(data['devid'], json.dumps(diskage))
        max_age = max(diskage.values())
        warning_handler(data['devid'], max_age >= SERVER_RESOURCE_LIMIT['diskage'], 2045,
                        data['rpttime'], 'p_server', threshold_value=SERVER_RESOURCE_LIMIT['diskage'], current_value=max_age)


def ev_pfminfo_disk_speed(data):
    '''
    磁盘速率
    仅检测最后4/3次, 判定告警或修复
    {
        "eventid": "EV_PFMINFO_DISK_SPEED",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/16:09:57:50",
        "speedlist": [123, 234, 112, 115, 238, 245, 100, 444, 356, 290]
    }
    '''
    disk_speed_threshold = int(nms_redis.get_warning_server_limit(
        data['devid'], 'diskwritespeed')) * 1024
    if all([speed >= disk_speed_threshold for speed in data['speedlist'][-4:]]):
        warning_handler(data['devid'], True, 2047, data['rpttime'], 'p_server')
    elif all([speed < disk_speed_threshold for speed in data['speedlist'][-3:]]):
        warning_handler(data['devid'], False, 2047,
                        data['rpttime'], 'p_server')


def ev_pfminfo_netcard(data):
    from dao.graphite_statistic import add_netcard_down_statistic, add_netcard_up_statistic, add_total_up_statistic, add_total_down_statistic
    '''
    网卡状态消息
    单位: 阈值Mbps, 消息KBps, 告警和redis:Kbps
    {
        "eventid": "EV_PFMINFO_NETCARD",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/16:09:57:50",
        "netcardinfo":
        {
            "netcardcount": 2, # 网卡个数
            "recvpktloserate": 0, # 总的网卡接受丢包率
            "recvkbps": 0,  # 总的网卡接收速率 KBps
            "sendkbps": 0,  # 总的网卡发送速率 KBps
            "netcards":[
                    {
                        "recvpktloserate": 0, # 单个网卡的接受丢包率
                        "recvkbps": 0, # 单个网卡的接收速率
                        "sendkbps": 0, # 单个网卡的发送速率
                        "ifname": "eth0" # 单个网卡的名称
                    },
                    {
                        "recvpktloserate": 0,
                        "sendkbps": 0,
                        "recvkbps": 0,
                        "ifname": "eth1" # 单个网卡的名称
                    }
            ]
        }
    }

    old
    {
        'netcardinfo': {
            'recvpktloserate': 0,
            'netcards': [
                {
                    'netcard1': {
                        'recvpktloserate': 0,
                        'recvkbps': 0,
                        'sendkbps': 0,
                        'ifname': 'eth0'
                    }
                },
                {
                    'netcard2': {
                        'recvpktloserate': 0,
                        'recvkbps': 7,
                        'sendkbps': 0,
                        'ifname': 'eth1'
                    }
                },
                {
                    'netcard3': {
                        'recvpktloserate': 0,
                        'recvkbps': 0,
                        'sendkbps': 0,
                        'ifname': 'eth2'
                    }
                }
            ]
        }
    }
    '''
    netcard_info = []
    netcards = data['netcardinfo']['netcards']
    if not netcards:
        return
    if 'ifname' not in netcards[0]:
        tmp = []
        for element in netcards:
            tmp += list(element.values())
        netcards = tmp
    for info in netcards:
        netcard_info.append(info['ifname'])
        netcard_info.append(info['recvkbps'] * 8)
        netcard_info.append(info['sendkbps'] * 8)
        netcard_info.append(info['recvpktloserate'])

    r = nms_redis.ev_pfminfo_netcard(
        data['devid'],
        data['netcardinfo']['recvkbps'] * 8,
        data['netcardinfo']['sendkbps'] * 8,
        data['netcardinfo']['recvpktloserate'],
        data['netcardinfo']['netcardcount'],
        *netcard_info
    )
    timestamp = int(time.time())
    for info in netcards:
        add_netcard_up_statistic(
            r['machine_room_moid'], data['devid'], info['ifname'], info['sendkbps'], timestamp)
        add_netcard_down_statistic(
            r['machine_room_moid'], data['devid'], info['ifname'], info['recvkbps'], timestamp)
    add_total_up_statistic(r['machine_room_moid'], data['devid'],
                           data['netcardinfo']['sendkbps'], timestamp)
    add_total_down_statistic(
        r['machine_room_moid'], data['devid'], data['netcardinfo']['recvkbps'], timestamp)
    warning_handler(data['devid'], r['warning'], 2019,
                    data['rpttime'], 'p_server', **r)

    # 丢包率告警
    # 5% 和 10% 分别对应告警码 2013 和 2014
    lost_list = [info['recvpktloserate']
                 for info in netcards]
    lost_10 = any(map(lambda x: x >= 10, lost_list))
    lost_5 = any(map(lambda x: x >= 5, lost_list))
    warning_handler(data['devid'], lost_10, 2014, data['rpttime'], 'p_server')
    warning_handler(data['devid'], lost_5, 2013, data['rpttime'], 'p_server')


def ev_usb_storage_state(data):
    '''
    USB状态
    {
        "eventid": "EV_USB_STORAGE_STATE",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/16:09:57:50",
        "usb_storage_exists": 0
    }
    '''
    warning_handler(data['devid'], data['usb_storage_exists']
                    == 0, 2044, data['rpttime'], 'p_server')


def ev_smu_warning_info(data):
    '''
    smu告警消息
    {
        "eventid": "EV_SMU_WARNING_INFO",
        "devid": "1111",
        "devtype": "smu",
        "rpttime": "2014/06/16:09:57:50",
        "smu_warning_info":
        {
            "card_guid": "yyyyyyyy", # 板卡guid
            "code": 5001, # 告警码
            "level": 1, # 告警等级，0：普通告警，1：重要告警，2：严重告警
            "status": 1 #告警状态，0: 解除告警，1: 产生告警
        }
    }
    '''
    smu_code = data['smu_warning_info']['code']
    nms_code = smu_warning_code_2_nms(
        smu_code, data['smu_warning_info']['level'])
    repair_code_list = [
        smu_warning_code_2_nms(smu_code, level) for level in (0, 1, 2)
    ]
    if smu_code in (SMU_ALAM_CODE_TVS4000_TEMPERATURE, SMU_ALAM_CODE_CHIP_FAULT, SMU_ALAM_CODE_FANSPEED):
        warning_handler(
            data['devid'],
            data['smu_warning_info']['status'],
            nms_code,
            data['rpttime'],
            'p_server'
        )
    else:
        for code in repair_code_list:
            warning_handler(
                data['devid'],
                False,
                code,
                data['rpttime'],
                'p_server'
            )
        if data['smu_warning_info']['status']:
            warning_handler(
                data['devid'],
                True,
                nms_code,
                data['rpttime'],
                'p_server'
            )


def ev_smu_cards_info(data):
    '''
    {
        "eventid": "EV_SMU_CARDS_INFO",
        "devid": "1111",
        "devtype": "jd10000",
        "rpttime": "2014/06/16:09:57:50",
        "smu_guid": "xxxxxxxxxxxx", // 机框的moid
        "cards_num": 2, // 板卡数量
        "collectorid": "xxx"
        "cards_info": [
            {
                "card_guid": "yyyyyyyyy", // 板卡的moid
                "card_pos": 5, // 板卡插槽位置
                "card_ip": "172.16.81.101", // 板卡ip地址
                "card_state": 1 // 板子状态(0: 拔掉，1: 插上)
            },
            {
                "card_guid": "zzzzzzzzzz", // 板卡的GUID
                "card_pos": 7, // 板卡插槽位置
                "card_ip": "172.16.81.102", // 板卡ip地址
                "card_state": 1 // 板子状态(0: 拔掉，1: 插上)
            }
        ]
    }
    '''
    for info in data['cards_info']:
        if info['card_guid']:
            nms_redis.ev_smu_cards_info(
                data['smu_guid'],
                info['card_guid'],
                info['card_ip'],
                info['card_state'],
                data['collectorid']
            )
            warning_handler(
                info['card_guid'],
                info['card_state'] == 0,
                3010,
                data['rpttime'],
                'p_server'
            )


def ev_smu_card_state_rpt_info(data):
    '''
    {
        "eventid": "EV_SMU_CARD_STATE_RPT_INFO",
        "devid": "1111",
        "devtype": "jd10000",
        "rpttime": "2014/06/16:09:57:50",
        "collectorid": "xxx",
        "smu_state":
        {
            "card_guid": "yyyyyyyyy", // 板卡的moid
            "card_pos": 5, // 板卡插槽位置
            "card_ip": ”172.16.81.101”, // 板卡ip地址
            "card_state": 0 // 板子状态(0: 拔掉，1: 插上)
            "smu_guid": ”xxxxxxxxxxxx”, // 机框的moid
        }
    }
    '''
    if data['smu_state']['card_guid']:
        nms_redis.ev_smu_cards_info(
            data['smu_statue']['smu_guid'],
            data['smu_statue']['card_guid'],
            data['smu_statue']['card_ip'],
            data['smu_statue']['card_state'],
            data['collectorid']
        )
        warning_handler(
            data['devid'],
            data['smu_state']['card_state'] == 0,
            3010,
            data['rpttime'],
            'p_server'
        )


def ev_x86frame_warning_info(data):
    '''
    {
        "eventid": "EV_X86FRAME_WARNING_INFO",
        "devid": "1111",
        "devtype": "jd2000",
        "rpttime": "2014/06/16:09:57:50",
        "warning_info":
        {
            "warning_code": 5001, // 告警码
            "warning_status": 0 // 告警状态, 0: 解除告警，1: 产生告警
            # 告警等级默认严重 2
        }
    }
    '''
    frame_code = data['warning_info']['warning_code']
    nms_code = smu_warning_code_2_nms(frame_code, 2)
    warning_handler(
        data['devid'],
        data['warning_info']['warning_status'],
        nms_code,
        data['rpttime'],
        'p_server'
    )


def ev_srv_system_uptime(data):
    '''
    运行时长消息
    {
        "eventid": "EV_SRV_SYSTEM_UPTIME",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/13 16:09:57",
        "uptime": "1天5时0分"
    }
    '''
    nms_redis.ev_srv_system_uptime(data['devid'], data['uptime'])


def ev_srv_warning_info(data):
    '''
    告警消息
    {
        "eventid": "EV_SRV_WARNING_INFO",
        "devid": "1111",
        "devtype": "x86_server",
        "rpttime": "2014/06/16:09:57:50",
        "warning_info":
        {
            "code": 2015, // 告警码
            "status": 0, // 告警状态 0：告警解除 1：告警产生
            "time": "2014/06/16:09:57:50", // 告警产生时间
            "guid": "123456789" // 产生告警的服务器moid
        }
    }
    '''
    code = data['warning_info']['code']
    status = data['warning_info']['status']
    if code == 2023 or code == 2027:
        # 物理服务器告警
        warning_handler(data['warning_info']['guid'],
                        status, code, data['warning_info']['time'], 'p_server')
    else:
        # 逻辑服务器告警
        warning_handler(data['warning_info']['guid'],
                        status, code, data['warning_info']['time'], 'l_server')
    if code == 2021 or code == 2022:
        # 主备告警, 无修复消息, 立刻清除
        warning_handler(data['warning_info']['guid'], False,
                        code, data['warning_info']['time'], 'l_server')
