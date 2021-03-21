import time
import json
from utils.common import get_unix_time_stamp
from dao import nms_redis, nms_mysql
from threads.msg_threads import mysql_write_thread


def ev_conf_appointment(data):
    '''
    预约会议
    {
        "eventid": "EV_CONF_APPOINTMENT",
        "userDomainMoid": "8o65ossdose061anmahaoilp",  # 用户域moid
        "operation": "add",
        "conf": {
            "id": 811,  # 会议id
            "confe164": "05551234567",  # 会议e164号
            "subject": "预约视频会议测试",  # 会议主题
            "organizerMoid": "urhvs6xfnrngawq07o3v9vto",  # 会议组织者moid
            "startTime": "2018-10-25 12:18:03",  # 会议开始时间
            "endTime": "2018-10-26 22:18:03",  # 会议结束时间
            "regularId": 123,  # 所属例会
            "isVideoMeeting": 1,  # 是否是视频会议，1-是，0-否
            "isConflict": 0,  # 会议是否冲突，1-是，0-否
            "creator": "李四",  # 创会人
            "mobile": "0551234567",  # 座机
            "telephone": "1555555553",  # 手机
            "meetingType": 0,  # 是否例会，0-单次例会，1-例会
            "lastModifyTime": "2018/06/01 09:18:03",  # 最后更新时间
            "meetingResourceVO": {
                "id": 123,  # 会议室规模或类型id
                "name": "Hello",  # 名称
                "key": "xxxx",  # 映射key
                "multi": 8,  # 方数
                "resolution": "1080P",  # 分辨率
                        "format": "H264",  # 格式
                        "frameRate": 30,  # 帧率
                        "bitRate": 1024,  # 码率
                        "encryption": "aes",  # 加密方式，取值none, aes等
                        "guest": 1,  # 来宾会议室 1 - 开启，0 - 关闭
                        "callType": 0,  # 呼叫方式 0 - 自动呼叫，1 - 手动呼叫
                        "meetingType": 0,  # 视频会议类型，0 - 传统会议， 1 - 端口会议
                "totalCount": 10,  # 总数
                "usedCount": 3  # 已使用
            },
            "rooms": [
                {
                    "id": 1,  # 会议室id
                    "name": "苏州会议室1"  # 会议室名称
                },
                {
                    "id": 2,  # 会议室id
                    "name": "上海会议室1"  # 会议室名称
                }
            ]
        }
    }
    '''
    # redis: appointment_meeting:confE164:info
    if data['conf'].get('isVideoMeeting', False):
        start_time = data['conf'].get('startTime', 0)
        if start_time:
            expired_time = int(get_unix_time_stamp(
                start_time, "%Y-%m-%d %H:%M:%S") - time.time())
        else:
            expired_time = 0
        info = json.dumps(data['conf'])
        nms_redis.ev_conf_appointment(data['conf']['confe164'], data['operation'], data['conf'].get(
            'startTime', ''), data['conf'].get('endTime', ''), expired_time, data['userDomainMoid'], info)


def ev_conf_entity(data):
    '''
    实体会议
    {
        "eventid": "EV_CONF_ENTITY",
        "userDomainMoid": "xxxxxxxxxx", //用户域moid
        "operation": "delete", //取值delete/add/update,
        "conf": {
            "id": 111, //会议id
            // "confe164": "05551234567", //会议e164号
            "subject": 5, //会议主题
            "organizerMoid": "xxxxxxxxx", //会议组织者moid
            "startTime": "2018/06/02 09:18:03", //会议开始时间
            "endTime": "2018/06/02 10:18:03", //会议结束时间
            "regularId": 123, //所属例会
            "isVideoMeeting": 0, //是否是视频会议，1-是，0-否
            "creator": "李四", //创会人
            "mobile": "0551234567", //座机
            "telephone": "1555555553", //手机
            "meetingType": 0, //是否例会，0-单次例会，1-例会
            "lastModifyTime": "2018/06/01 09:18:03", //最后更新时间
            // "meetingResourceVO": {
            //     "id": 123, //会议室规模或类型id
            //     "name": "Hello", //名称
            //     "key": "xxxx", //映射key
            //     "multi": 8, //方数
            //     "resolution": "1080P", //分辨率
            //     "totalCount": 10, //总数
            //     "usedCount": 3 //已使用
            // },
            "rooms": [
                {
                    "id": 111, //会议室id
                    "name": "DDD" //会议室名称
                }
            ]
        }
    }
    '''
    r = nms_redis.ev_conf_entity(
        data.get('userDomainMoid', ''),
        data['conf'], ['id'],
        data['operation'],
        data['conf'].get('startTime', ''),
        data['conf'].get('endTime', ''),
        json.dumps(data['conf'])
    )
    if r and data['operation'] == 'delete':
        r['domain_moid'] = data['userDomainMoid']
        mysql_write_thread.push(
            (nms_mysql.add_multi_meeting_statistic, r))
