import json
import time
import math
import base64
from dao import nms_redis, nms_mysql
from threads.msg_threads import mysql_write_thread
from core.warning import warning_handler
from config import enum, common


# 终端会议状态
# 在多点会议中
IN_MULTI_CONF = 1
# 在点对点会议中
IN_P2P_CONF = 2
# 不在会议中
NOT_IN_CONF = 3


def ev_dev_online(data):
    '''
    终端上线消息
    {
        "eventid": "EV_DEV_ONLINE",  # 消息类型(将消息类型定义---必须
        "devid": " 1234567890",   # 终端moid---必须
        "devtype": "Skywalker for Windows",  # 终端类型---必须
        "rpttime": "2018/12/19: 12: 08: 080"  # 上线时间
        "collectorid": "x123123"
    }
    '''
    r = nms_redis.ev_dev_online_t(
        data['devid'], data['devtype'], data['collectorid'])
    if r:
        # nms接入数量阈值告警
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
    终端下线消息
    {
        "eventid": "EV_DEV_OFFLINE"  # 消息类型---必须
        "devid": "1234567890",  # 终端moid---必须
        "devtype": "Skywalker for Windows",  # 终端类型---必须
        "rpttime": "2018/12/19: 12: 08: 080"  # 下线时间
        "collectorid": 'xxx'
    }
    '''
    r = nms_redis.ev_dev_offline_t(
        data['devid'], data['devtype'], data['collectorid'])
    if r is None:
        return
    # nms接入数量阈值告警
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
    终端基本信息
    {
        "eventid": "EV_MT_INFO",
        "devid": "1111",
        "devtype": "HD100_26",
        "rpttime": "2014/06/16:09:57:50",
        "mt_info":
        {
            "cpu_type": "i7", # cpu类型
            "cpu_freq": 5, # cpu主频
            "cpu_num": 4, # cpu核数
            "os": "XP", # 操作系统类型
            "devname": "longweitest", # 终端名称
            "devver": "20141215", # 终端版本号
            "oem": "dddd", # 终端软件版本的oem标志
            "memory": 4000, # 内存总量
            "SN": "adadada@swss", # 产品序列号
            "state_secret": 1,  # 国密状态 0-关闭，1-开启
            "video_format": "UXGA", # 视频制式
            "aps_addr": # aps服务器信息
            {
                "domain": "172.16.72.84", # 域名
                "ip": "218.22.22.23" # ip地址
            },
            "net_config": # 终端网络配置
            {
                "pkt_loss_resend": 0, # 丢包重传 0-关闭，1-开启
                "audio_first": 1, # 音频优先 0-关闭，1-开启
                "fec": 1,  # FEC 0-关闭，1-开启
                "decode_payload_auto": 1, # 强解/载荷自适应  0-关闭，1-开启
            },
            "netinfo": # 网络信息
            {
                "dns": "172.16.0.65", # 终端正在使用的dns
                "nat_ip": "172.16.72.84",
                "ip": "172.16.72.84", # 正在使用的ip
                "sip_link_protocol": "tls" # sip链路类型
            },
            "cameras":
            [{
                "id": "sddff134ffa", # 摄像机唯一标识
                "type": "MOON", # 摄像机类型
                "SN": "adadada@swss", # 摄像机产品序列号
                "version": "5.0.1.0.1", # 摄像机版本号
                "status": 1 # 摄像机状态 0-关闭，1-开启
            }],
            "microphones":
            [{
                "id": "sddff134ffa", # 麦克风唯一标识
                "type": "MOON", # 麦克风类型
                "version": "5.0.1.0.1", # 麦克风版本号
                "status": 1 # 麦克风 0-关闭，1-开启
            }]
        }
    }
    '''
    mt_info = data['mt_info']
    net_config = mt_info.get('net_config', {})
    netinfo = mt_info.get('netinfo', {})
    aps_addr = mt_info.get('aps_addr', {})
    cpu_freq = str(mt_info['cpu_freq']) + \
        'MHz' if mt_info.get('cpu_freq') else ''
    memory = '%.2fGB' % (
        int(mt_info['memory'])/1024) if mt_info.get('memory') else ''
    info = {}
    info['runninginfo'] = {
        'version': mt_info.get('devver', ''),
        'os': mt_info.get('os', ''),
        'cpu_type': mt_info.get('cpu_type', ''),
        'cpu_freq': cpu_freq,
        'cpu_num': mt_info.get('cpu_num', 1),
        'memory': memory,
        'SN': mt_info.get('SN', ''),
        'state_secret': mt_info.get('state_secret', 0),
        'video_format': mt_info.get('video_format', ''),
        'pkt_loss_resend': net_config.get('pkt_loss_resend', 0),
        'audio_first': net_config.get('audio_first', 0),
        'fec': net_config.get('fec', 0),
        'decode_payload_auto': net_config.get('decode_payload_auto', 0),
        'oem': mt_info.get('oem', ''),
    }
    info['netinfo'] = {
        'ip': netinfo.get('ip', ''),
        'nat_ip': netinfo.get('nat_ip', ''),
        'dns': netinfo.get('dns', ''),
        'sip_link_protocol': netinfo.get('sip_link_protocol', ''),
        'aps_domain': aps_addr.get('domain', ''),
        'aps_ip': aps_addr.get('ip', '')
    }
    info['cameras'] = mt_info.get('cameras', False)
    info['microphones'] = mt_info.get('microphones', False)

    nms_redis.ev_mt_info(data['devid'], data['devtype'], json.dumps(info))


def ev_state_secret_info(data):
    '''
    国密状态消息
    {
        "eventid": "EV_STATE_SECRET_INFO",
        "devid": "1.2.2",
        "devtype": "Skywalker for Windows",
        "rpttime": "2014/06/16:09:57:50",
        "state_secret": 1 # 国密状态，0-关闭 1-开启
    }
    '''
    nms_redis.ev_state_secret_info(
        data['devid'], data['devtype'], data.get('state_secret', 0))


def ev_video_format_info(data):
    '''
    视频格式
    {
        "eventid": "EV_VIDEO_FORMAT_INFO",
        "devid": "1.2.2",
        "devtype": "Skywalker for Windows",
        "rpttime": "2014/06/16:09:57:50",
        "video_format": "UXGA"  # 视频格式
    }
    '''
    nms_redis.ev_video_format_info(
        data['devid'], data['devtype'], data.get('video_format', '')
    )


def ev_network_config_info(data):
    '''
    网络配置信息
    {
        "eventid": "EV_NETWORK_CONFIG_INFO",
        "devid": "1.2.2",
        "devtype": "Skywalker for Windows",
        "rpttime": "2014/06/16:09:57:50",
        "network_config":
        {
            "pkt_loss_resend": 0, # 丢包重传  0-关闭，1-开启
            "audio_first": 1, # 音频优先  0-关闭，1-开启
            "fec": 1,  # FEC 0-关闭，1-开启
            "decode_payload_auto": 1 # 强解/载荷自适应  0-关闭，1-开启
        }
    }
    '''
    network_config = data.get('network_config', {})
    nms_redis.ev_network_config_info(
        data['devid'],
        data['devtype'],
        network_config.get('pkt_loss_resend', ''),
        network_config.get('audio_first', ''),
        network_config.get('fec', ''),
        network_config.get('decode_payload_auto', '')
    )


def ev_cameras_add(data):
    '''
    新增摄像机
    {
        "eventid": "EV_CAMERAS_ADD",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "cameras":
        [{
            "id": "sddff134ffa", // 摄像机唯一标识
            "type": "MOON", // 摄像机类型
            "SN": "adadada@swss", // 摄像机产品序列号
            "version": "5.0.1.0.1", // 摄像机版本号
            "status": 1 // 摄像机状态 0-关闭，1-开启
        }]
    }
    '''
    nms_redis.ev_cameras_add_or_update(
        data['devid'], data['devtype'], json.dumps(data.get('cameras', [])))


def ev_cameras_update(data):
    '''
    摄像机更新
    {
        "eventid": "EV_CAMERAS_UPDATE",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "cameras":
        [{
            "id": "sddff134ffa", // 摄像机唯一标识
            "type": "MOON", // 摄像机类型
            "SN": "adadada@swss", // 摄像机产品序列号
            "version": "5.0.1.0.1", // 摄像机版本号
            "status": 1 // 摄像机状态 0-关闭，1-开启
        }]
    }
    '''
    nms_redis.ev_cameras_add_or_update(
        data['devid'], data['devtype'], json.dumps(data.get('cameras', [])))


def ev_cameras_del(data):
    '''
    摄像机删除
    {
        "eventid": "EV_CAMERAS_DEL",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "cameras": // 摄像机唯一标识列表
        [
            "sddff134ffa",
            "12345678901"
        ]
    }
    '''
    nms_redis.ev_cameras_del(
        data['devid'], data['devtype'], json.dumps(data.get('cameras', []))
    )


def ev_microphones_add(data):
    '''
    新增麦克风
    {
        "eventid": "EV_MICROPHONES_ADD",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "microphones":
        [{
            "id": "sddff134ffa", // 麦克风唯一标识
            "type": "MOON", // 麦克风类型
            "version": "5.0.1.0.1", // 麦克风版本号
            "status": 1 // 麦克风状态 0-关闭，1-开启
        }]
    }
    '''
    nms_redis.ev_microphones_add_or_update(
        data['devid'], data['devtype'], json.dumps(data.get('microphones', []))
    )


def ev_microphones_update(data):
    '''
    麦克风更新
    {
        "eventid": "EV_MICROPHONES_update",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "microphones":
        [{
            "id": "sddff134ffa", // 麦克风唯一标识
            "type": "MOON", // 麦克风类型
            "version": "5.0.1.0.1", // 麦克风版本号
            "status": 1 // 麦克风状态 0-关闭，1-开启
        }]
    }
    '''
    nms_redis.ev_microphones_add_or_update(
        data['devid'], data['devtype'], json.dumps(data.get('microphones', []))
    )


def ev_microphones_del(data):
    '''
    麦克风删除
    {
        "eventid": "EV_ MICROPHONES _DEL",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "cameras": // 麦克风唯一标识列表
        [
            "sddff134ffa",
            "12345678901"
        ]
    }
    '''
    nms_redis.ev_microphones_del(
        data['devid'], data['devtype'], json.dumps(data.get('microphones', []))
    )


def ev_netinfo_msg(data):
    '''
    网络信息改变
    {
        "eventid": "EV_NETINFO_MSG",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "netinfo":
        {
            "dns": "172.16.0.65", // 终端正在使用的dns
            "nat_ip": "172.16.72.84",
            "ip": "172.16.72.84", // 正在使用的ip
            "sip_link_protocol": "tls" // sip链路类型
        }
    }
    '''
    nms_redis.ev_netinfo_msg(
        data['devid'],
        data['devtype'],
        data['netinfo'].get('ip', ''),
        data['netinfo'].get('nat_ip', ''),
        data['netinfo'].get('dns', ''),
        data['netinfo'].get('sip_link_protocol', ''),
    )


def ev_bandwidth_msg(data):
    '''
    上下行带宽
    {
        "eventid": "EV_BANDWIDTH_MSG",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "recv_bandwidth":
        {
            "bandwidth": 1024, // 接收带宽，单位KB/s
            "drop_rate": 10 // 接收带宽上的丢包率，单位千分之几
        },
        "send_bandwidth":
        {
            "bandwidth": 512, // 发送带宽，单位KB/s
            "drop_rate": 3 // 发送带宽上的丢包率，单位千分之几
        }
    }
    '''
    nms_redis.ev_bandwidth_msg(
        data['devid'],
        data['devtype'],
        data['recv_bandwidth'].get('bandwidth'),
        data['recv_bandwidth'].get('drop_rate', 0)//10,
        data['send_bandwidth'].get('bandwidth'),
        data['send_bandwidth'].get('drop_rate', 0)//10,
        int(time.time())
    )


def ev_should_connsrv_msg(data):
    '''
    需要连接的服务器信息
    {
        "eventid": " EV_SHOULD_CONNSRV_MSG",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "conn_srv_type_info'":
            [
                "APS",
                "PAS",
                "SUS"
            ]
    }
    '''
    nms_redis.ev_should_connsrv_msg(
        data['devid'],
        data['devtype'],
        json.dumps(data.get('conn_srv_type_info', []))
    )


def ev_connsrv_conn_msg(data):
    '''
    实际连上的服务器信息
    {
        "eventid": "EV_CONNSRV_CONN_MSG",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "conn_srv_state_info":
        [{
            "ip": "172.16.72.88", // 服务器的ip
            "type": "APS" // 服务器的类型
        }]
    }
    '''
    nms_redis.ev_connsrv_conn_msg(
        data['devid'],
        data['devtype'],
        json.dumps(data.get('conn_srv_state_info', []))
    )


def ev_alarm_msg(data):
    '''
    终端告警信息
    {
        "eventid": "EV_ALARM_MSG”",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "alarm_info":
        {
            "code_id": 1003, // 告警码
            "report_time": "2018/12/19:12:08:080", // 告警产生时间
            "status": 1 // 告警状态，0：告警恢复，1：告警产生
        }
    }
    '''
    warning_handler(
        data['devid'],
        data['alarm_info']['status'],
        data['alarm_info']['code_id'],
        data['rpttime'],
        'terminal',
        device_type=data['devtype']
    )


def ev_exception_file(data):
    '''
    终端崩溃日志
    {
        "eventid": "EV_EXCEPTION_FILE",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "execption_info",
        {
            "devver": "2.6.0.21", // 崩溃的设备版本号
            "execption_file": "moooofly.err", // 崩溃时间，北京时间(GMT标准)
            "execption_time": "2014/05/08:12:08:08" // 崩溃日志
        }
    }
    '''
    mysql_write_thread.push((nms_mysql.add_terminal_crush_report, {
        'moid': data['devid'],
        'type': data['devtype'],
        'version': data['execption_info'].get('devver', ''),
        'execption_time': data['execption_info'].get('execption_time', ''),
        'execption_file': data['execption_info'].get('execption_file', '')
    }))


def ev_conf_info(data):
    '''
    终端会议信息
    {
        "eventid": "EV_CONF_INFO",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "mt_state": 2, // 终端状态, 1.在多点会议, 2.在点对点会议, 3.不在会议中
        "conf_info":
        {
            "mt_e164": "0512111886042", // 终端e164号
            "conf_e164": "0512111886042", // 会议E164号(如果是点对点会议，使用主叫方e164号)
            "bitrate": 328, // 会议码率
            "mute": 1, // 静音状态 1: 是 0: 否
            "dumbness": 1, // 哑音状态 1: 是 0: 否
            "encryption": 2, // 终端加密类型
            "privideo_recv":
            [{
                "id": 1, // 主视频接收第几路视频码流(计数从0开始)
                "framerate": 25, // 主视频接收帧率
                "video_pkts_lose": 555, // 主视频下行丢包总数
                "video_pkts_loserate": 5, // 主视频下行丢包率
                "video_down_bitrate": 256, // 主视频下行码率
                "format": 0, // 主视频接收格式
                "res": 3 // 主视频分辨率格式
            }],
            "privideo_send":
            [{
                "id": 1, // 主视频发送第几路视频码流(计数从0开始)
                "video_resource_exist": 1, // 有无主视频源 1: 有 0: 没有
                "framerate": 25, // 主视频发送帧率
                "video_pkts_lose": 123, // 主视频上行丢包总数
                "video_pkts_loserate": 12, // 主视频上行丢包率
                "video_up_bitrate": 56, // 主视频上行码率
                "format": 0, // 主视频发送格式
                "res": 3 // 主视频分辨率格式
            }],
            "assvideo_recv":
            [{
                "id": 1, // 辅视频接收第几路视频码流(计数从0开始)
                "framerate": 5, // 辅视频接收帧率
                "video_pkts_lose": 500, // 辅视频下行丢包总数
                "video_pkts_loserate": 5, // 辅视频下行丢包率
                "video_down_bitrate": 256, // 辅视频下行码率
                "format": 0, // 辅视频接收格式
                "res": 3 // 辅视频分辨率格式
            }],
            "assvideo_send":
            [{
                "id": 1, // 辅视频发送第几路视频码流(计数从0开始)
                "video_resource_exist": 1, // 有无主视频源 1: 有 0: 没有
                "framerate": 25, // 辅视频发送帧率
                "video_pkts_lose": 123, // 辅视频上行丢包总数
                "video_pkts_loserate": 12, // 辅视频上行丢包率
                "video_up_bitrate": 256, // 辅视频上行码率
                "format": 0, // 辅视频发送格式
                "res": 3 // 辅视频分辨率格式
            }],
            "audio_recv":
            [{
                "id": 1, // 第几路音频接收码流(计数从0开始)
                "format": 0, // 音频接收格式
                "audio_pkts_lose": 64, // 音频下行丢包总数
                "audio_pkts_loserate": 2, // 音频下行丢包率
                "audio_down_bitrate": 64 // 音频下行码率(KB/s)
            }]
            "audio_send":
            [{
                "id": 1, // 第几路音频发送码流(计数从0开始)
                "format": 0, // 音频发送格式
                "audio_pkts_lose: 123, // 音频上行丢包总数
                "audio_pkts_loserate: 12, // 音频上行丢包率
                "audio_up_bitrate": 64 // 音频上行码率(KB/s)
            }]
        }
    }
    '''
    state = "online" if data.get('mt_state', 3) == 3 else "conference"
    if state == 'conference':
        json_data = {
            'conf_e164': data['conf_info']['conf_e164'],
            'bitrate': data['conf_info']['bitrate'],
            'mute': data['conf_info']['mute'],
            'dumbness': data['conf_info']['dumbness'],
            'encryption': enum.TERMINAL_ENCRYPTION.get(data['conf_info'].get('encryption'), 'unkown')
        }
        privideo_chan = {}
        assvideo_chan = {}
        max_lossrate = 0
        # 主视频接收
        for info in data['conf_info'].get('privideo_recv', []):
            channel_id = info['id']
            if channel_id not in privideo_chan:
                privideo_chan[channel_id] = {
                    'channel_id': channel_id
                }
            privideo_chan[channel_id]['recv_video_format'] = enum.TERMINAL_VIDEO_FORMAT.get(
                info['format'], 'unkown')
            privideo_chan[channel_id]['recv_video_framerate'] = info['framerate']
            privideo_chan[channel_id]['recv_video_pkts_lose'] = info.get(
                'video_pkts_lose', 0)
            privideo_chan[channel_id]['recv_video_pkts_loserate'] = info.get(
                'video_pkts_loserate', 0)
            privideo_chan[channel_id]['recv_video_bitrate'] = info.get(
                'video_down_bitrate', 0)
            privideo_chan[channel_id]['recv_video_res'] = enum.TERMINAL_RES.get(
                info.get('res'), 'unknown')
            max_lossrate = max(max_lossrate, info.get(
                'video_pkts_loserate', 0))

        # 主视频发送
        for info in data['conf_info'].get('privideo_send', []):
            channel_id = info['id']
            if channel_id not in privideo_chan:
                privideo_chan[channel_id] = {
                    'channel_id': channel_id
                }
            privideo_chan[channel_id]['send_video_format'] = enum.TERMINAL_VIDEO_FORMAT.get(
                info['format'], 'unkown')
            privideo_chan[channel_id]['send_video_framerate'] = info['framerate']
            privideo_chan[channel_id]['send_video_pkts_lose'] = info.get(
                'video_pkts_lose', 0)
            privideo_chan[channel_id]['send_video_pkts_loserate'] = info.get(
                'video_pkts_loserate', 0)
            privideo_chan[channel_id]['send_video_bitrate'] = info.get(
                'video_down_bitrate', 0)
            privideo_chan[channel_id]['send_video_res'] = enum.TERMINAL_RES.get(
                info.get('res'), 'unknown')
            privideo_chan[channel_id]['send_video_resource_exist'] = info['video_resource_exist']
            max_lossrate = max(max_lossrate, info.get(
                'video_pkts_loserate', 0))

        # 音频接收
        for info in data['conf_info'].get('audio_recv', []):
            channel_id = info['id']
            if channel_id not in privideo_chan:
                privideo_chan[channel_id] = {
                    'channel_id': channel_id
                }
            privideo_chan[channel_id]['recv_audio_format'] = enum.TERMINAL_AUDIO_FORMAT.get(
                info['format'], 'unkown')
            privideo_chan[channel_id]['recv_audio_pkts_lose'] = info.get(
                'audio_pkts_lose', 0)
            privideo_chan[channel_id]['recv_audio_pkts_loserate'] = info.get(
                'audio_pkts_loserate', 0)
            privideo_chan[channel_id]['recv_audio_bitrate'] = info.get(
                'video_down_bitrate', 0)
        # 音频发送
        for info in data['conf_info'].get('audio_send', []):
            channel_id = info['id']
            if channel_id not in privideo_chan:
                privideo_chan[channel_id] = {
                    'channel_id': channel_id
                }
            privideo_chan[channel_id]['send_audio_format'] = enum.TERMINAL_AUDIO_FORMAT.get(
                info['format'], 'unkown')
            privideo_chan[channel_id]['send_audio_pkts_lose'] = info.get(
                'audio_pkts_lose', 0)
            privideo_chan[channel_id]['send_audio_pkts_loserate'] = info.get(
                'audio_pkts_loserate', 0)
            privideo_chan[channel_id]['send_audio_bitrate'] = info['audio_up_bitrate']

        # 辅视频接收
        for info in data['conf_info'].get('assvideo_recv', []):
            channel_id = info['id']
            if channel_id not in assvideo_chan:
                assvideo_chan[channel_id] = {
                    'channel_id': channel_id
                }
            assvideo_chan[channel_id]['recv_video_format'] = enum.TERMINAL_VIDEO_FORMAT.get(
                info['format'], 'unkown')
            assvideo_chan[channel_id]['recv_video_framerate'] = info['framerate']
            assvideo_chan[channel_id]['recv_video_pkts_lose'] = info.get(
                'video_pkts_lose', 0)
            assvideo_chan[channel_id]['recv_video_pkts_loserate'] = info.get(
                'video_pkts_loserate', 0)
            assvideo_chan[channel_id]['recv_video_bitrate'] = info.get(
                'video_down_bitrate', 0)
            assvideo_chan[channel_id]['recv_video_res'] = enum.TERMINAL_RES.get(
                info.get('res'), 'unknown')
            max_lossrate = max(max_lossrate, info.get(
                'video_pkts_loserate', 0))
        # 辅视频发送
        for info in data['conf_info'].get('assvideo_send', []):
            channel_id = info['id']
            if channel_id not in assvideo_chan:
                assvideo_chan[channel_id] = {
                    'channel_id': channel_id
                }
            assvideo_chan[channel_id]['send_video_format'] = enum.TERMINAL_VIDEO_FORMAT.get(
                info['format'], 'unkown')
            assvideo_chan[channel_id]['send_video_framerate'] = info['framerate']
            assvideo_chan[channel_id]['send_video_pkts_lose'] = info.get(
                'video_pkts_lose', 0)
            assvideo_chan[channel_id]['send_video_pkts_loserate'] = info.get(
                'video_pkts_loserate', 0)
            assvideo_chan[channel_id]['send_video_bitrate'] = info.get(
                'video_down_bitrate', 0)
            assvideo_chan[channel_id]['send_video_res'] = enum.TERMINAL_RES.get(
                info.get('res'), 'unknown')
            assvideo_chan[channel_id]['send_video_resource_exist'] = info['video_resource_exist']
            max_lossrate = max(max_lossrate, info.get(
                'video_pkts_loserate', 0))

        json_data['privideo_chan'] = privideo_chan
        json_data['assvideo_chan'] = assvideo_chan

        # 丢包评分 向上取整
        score = math.ceil(
            max_lossrate/common.SCORE['lossrate']['step']) * common.SCORE['lossrate']['score']
        json_data['score'] = score
        json_data['lossrate'] = max_lossrate
        json_data['time'] = data['rpttime']
    else:
        json_data = {}
    nms_redis.ev_conf_info(
        data['devid'],
        data['devtype'],
        state,
        json.dumps(json_data)
    )


def ev_pfminfo_msg(data):
    '''
    性能消息
    {
        "eventid": "EV_PFMINFO_MSG ",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "collectorid": "12331",
        "pfm_info":
        {
            "cpu_userate": 12, // cpu使用百分比
            "mem_userate": 12, // 内存使用百分比
            "sip_addr": "192.168.1.1", // sip服务器信息
            "gk_addr": "", // GK服务器信息
            "master_chip_status": 0, // 主芯片状态，0-正常，1-异常
            "temperature_status": 0, // 温度状态，0-正常，1-异常
            "netcardinfo":
            {
                "sendkbps": 123,
                "recvkbps": 123,
                "netcardcount: 123, // 网卡个数
                "netcards":
                [{
                    "name": "eth0", // 网卡名称（比如eth0）
                    "netcardtype": 1, // 网卡类型
                    "sendkbps": 123, // 网卡出口量
                    "recvkbps": 123 // 网卡入口量
                }]
            },
            "video_resource_name":
            [{
                "video_index": "HDMI0", // 视频源名称
                "type": 1 // 视频源类型 0：主流 1：双流
            }],
            "loudspeakers":
            [{
                "name": "001", // 扬声器名称
                "status": 1 // 扬声器状态，0-正常，1-异常
            }],
            "microphones":
            [{
                "name": "xxxxx", // 麦克风名称
                "status": 1 // 麦克风状态，0-正常，1-异常
            }]
        }
    }
    '''
    info = {}
    netcardinfo = data['pfm_info'].get('netcardinfo', {})
    info['netcards'] = netcardinfo.get('netcards', [])
    info['video_resource_name'] = data['pfm_info'].get(
        'video_resource_name', [])
    info['loudspeakers'] = data['pfm_info'].get('loudspeakers', [])
    info['microphones'] = data['pfm_info'].get('microphones', [])

    info['pfm_info'] = {
        "cpu_userate": data['pfm_info'].get('cpu_userate', ''),
        "mem_userate": data['pfm_info'].get('mem_userate', ''),
        "sip_addr": data['pfm_info'].get('sip_addr', ''),
        "gk_addr": data['pfm_info'].get('gk_addr', ''),
        "master_chip_status": data['pfm_info'].get('master_chip_status', ''),
        "temperature_status": data['pfm_info'].get('temperature_status', '')
    }
    if netcardinfo:
        info['pfm_info']['netcardcount'] = netcardinfo.get('netcardcount', 0)

    nms_redis.ev_pfminfo_msg(
        data['devid'],
        data['devtype'],
        json.dumps(info)
    )


def ev_audio_video_status_ack(data):
    '''
    终端音视频状态
    {
        "eventid": "EV_AUDIO_VIDEO_STATUS_ACK",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "audio_input_sign":
        [
            {
                "type": "DVI",
                "status": 1 // 1: 正常 0: 异常
            },
            {
                "type": "RCA",
                "status": 0
            }
        ],
        "audio_output_sign":
        [
            {
                "type": "HDMI",
                "status": 1
            },
            {
                "type": "SDI",
                "status": 0
            }
        ],
        "video_input_sign":
        [
            {
                "type": "VGA",
                "status": 1
            },
            {
                "type": "HDMI",
                "status": 0
            }
        ],
        "video_output_sign":
        [
            {
                "type": "HDMI",
                "status": 1
            },
            {
                "type": "SDI",
                "status": 0
            }
        ]
    }
    '''
    nms_redis.ev_audio_video_status_ack(
        data['devid'],
        json.dumps(data)
    )


def ev_blunt_info(data):
    '''
    终端卡顿次数上报
    {
        "eventid": "EV_BLUNT_INFO",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "blunt_info":
        {
            "count": 15
        }
    }
    '''
    count = data['blunt_info'].get('count', 0)
    score = (count // common.SCORE['blunt']['step']
             ) * common.SCORE['blunt']['score']
    if count is not None:
        nms_redis.ev_blunt_info(data['devid'], count, score, data['rpttime'])


def ev_volume_ack(data):
    '''
    终端音量能量值请求回复
    {
        "eventid": "EV_VOLUME_ACK",
        "devid": "1111",
        "devtype": "TrueLink",
        "rpttime": "2014/06/16:09:57:50",
        "volume_info": // 音量信息
        {
            "input": 12, // 输入音量能量值大小---必须
            "output": 12//输出音量能量值大小---必须
        }
    }
    '''
    if data.get('volume_info') is not None:
        nms_redis.ev_volume_ack(
            data['devid'],
            data['volume_info']['input'],
            data['volume_info']['output']
        )


def ev_config_1st_video_format_ntf(data):
    '''
    终端视频制式配置结果
    {
        "eventid": "EV_CONFIG_1ST_VIDEO_FORMAT_NTF",
        "devid": "0de645a5-36a2-47c2-8979-2b344a78868a",
        "devtype": "SKY Windows",
        "rpttime": "2019/03/14 13:35:40",
        "result": 1 // 1是成功，0是失败
    }
    '''
    nms_redis.ev_config_1st_video_format_ntf(
        data['devid'], data['devtype'], data['result'])


def ev_config_reg_addr_ntf(data):
    '''
    终端注册地址配置结果通知
    {
        "eventid": "EV_CONFIG_REG_ADDR_NTF",
        "devid": "0de645a5-36a2-47c2-8979-2b344a78868a",
        "devtype": "SKY Windows",
        "rpttime": "2019/03/14 13:35:40",
        "result": 1 // 1是成功，0是失败
    }
    '''
    nms_redis.ev_config_reg_addr_ntf(
        data['devid'],
        data['devtype'],
        data['result']
    )


def ev_config_network_ntf(data):
    '''
    终端网络配置结果通知
    {
        "eventid": "EV_CONFIG_NETWORK_NTF",
        "devid": "0de645a5-36a2-47c2-8979-2b344a78868a",
        "devtype": "SKY Windows",
        "rpttime": "2019/03/14 13:35:40",
        "result": 1 // 1是成功，0是失败
    }
    '''
    nms_redis.ev_config_network_ntf(
        data['devid'],
        data['devtype'],
        data['result']
    )


def ev_imix_info(data):
    '''
    Sky终端上报网呈IMIX设备信息
    {
        "eventid": "EV_IMIX_INFO",
        "devid": "0de645a5-36a2-47c2-8979-2b344a78868a",
        "devtype": "SKY Windows",
        "rpttime": "2019/03/14 13:35:40",
        "imix_info": {
            "devtype": "IMIX", // 终端类型
            "softver": "5.1.2.3", // 软件版本
            "sn": "fe:12:dd:ddddd", // 序列号
            "mac": "50:9a:4c:25:fe:b0", // mac地址
            "ip": "192.168.1.5" // ip地址
        }
    }
    '''
    nms_redis.ev_imix_info(
        data['devid'],
        data['devtype'],
        data['imix_info']['devtype'],
        data['imix_info']['sn'],
        data['imix_info']['mac'],
        data['imix_info']['ip'],
        data['imix_info']['softver'],
        base64.b64encode(data['imix_info']['sn'].encode(
            'utf-8')).decode('utf-8')
    )
