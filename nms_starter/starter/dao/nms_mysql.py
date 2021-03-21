# coding=utf-8
from dao.mysql.nms import *
import json


# 终端
def add_old_terminal(session, data):
    '''
    添加老终端信息
    '''
    terminal = OldTerminal(
        user_domain_moid=data['user_domain_moid'],
        moid=data['moid'],
        name=data['name'],
        e164=data['e164'],
        ip=data['ip'],
        online=0
    )
    session.add(terminal)


def update_old_terminal(session, data):
    '''
    更新老终端信息
    '''
    treminal = session.query(OldTerminal).filter(
        OldTerminal.moid == data['moid']).first()
    if treminal is not None:
        treminal.user_domain_moid = data['user_domain_moid']
        treminal.name = data['name']
        treminal.ip = data['ip']
    else:
        add_old_terminal(session, data)


def del_old_terminal(session, moid):
    '''
    删除老终端
    '''
    terminal = session.query(OldTerminal).filter(
        OldTerminal.moid == moid).first()
    if terminal is not None:
        session.delete(terminal)


def online_old_terminal(session, ip):
    '''
    48终端上线
    '''
    terminal = session.query(OldTerminal).filter(
        OldTerminal.ip == ip).first()
    if terminal is not None:
        terminal.online = 1


def offline_old_terminal(session, ip):
    '''
    48终端下线
    '''
    terminal = session.query(OldTerminal).filter(
        OldTerminal.ip == ip).first()
    if terminal is not None:
        terminal.online = 0


### 告警 ###
def get_warning_notify(session):
    '''
    获取告警通知信息
    '''
    return [
        {
            'id': notify.id,
            'domain_moid': notify.domain_moid,
            'email': notify.email if notify.email else '',
            'phone': notify.phone if notify.phone else '',
            'wechat': notify.wechat if notify.wechat else '',
            'code_list': notify.code_list.split(',') if notify.code_list else []
        } for notify in session.query(WarningNotify).all()
    ]


def get_warning_stop(session):
    '''
    获取暂停告警设置信息
    '''
    return session.query(StopWarning.moid).all()


def get_resource_limit(session):
    '''
    获取公共阈值设置信息
    '''
    r = session.execute(
        'select s_pas, s_callpair, s_nms, s_media_resource from resource_limit')
    return r.first()


def get_server_resource_limit(session):
    '''
    获取所有服务器阈值设置信息
    '''
    return session.query(
        ServerResourceLimit.device_moid,
        ServerResourceLimit.cpu,
        ServerResourceLimit.memory,
        ServerResourceLimit.disk,
        ServerResourceLimit.port,
        ServerResourceLimit.diskwritespeed,
        ServerResourceLimit.rateofflow
    ).all()


def add_terminal_warning_unrepaired(session, data):
    '''
    添加终端未修复告警信息
    '''
    session.query(TerminalWarningUnrepaired).filter(
        TerminalWarningUnrepaired.device_moid == data.get('device_moid'),
        TerminalWarningUnrepaired.code == data.get('code')
    ).delete()
    info = TerminalWarningUnrepaired(
        device_moid=data.get('device_moid'),
        device_name=data.get('device_name'),
        device_type=data.get('device_type'),
        device_ip=data.get('device_ip'),
        device_e164=data.get('device_e164'),
        domain_moid=data.get('domain_moid'),
        domain_name=data.get('domain_name'),
        code=data.get('code'),
        level=data.get('level'),
        description=data.get('description'),
        start_time=data.get('start_time'),
        resolve_time=data.get('resolve_time')
    )
    session.add(info)


def get_terminal_warning_unrepaired(session):
    from sqlalchemy.sql import func
    return session.query(TerminalWarningUnrepaired.domain_moid, func.count()).group_by('domain_moid').all()


def add_server_warning_unrepaired(session, data):
    '''
    添加服务器未修复告警信息
    '''
    session.query(ServerWarningUnrepaired).filter(
        ServerWarningUnrepaired.device_moid == data.get('device_moid'),
        ServerWarningUnrepaired.code == data.get('code')
    ).delete()
    info = ServerWarningUnrepaired(
        device_moid=data.get('device_moid'),
        device_name=data.get('device_name'),
        device_type=data.get('device_type'),
        device_ip=data.get('device_ip'),
        machine_room_moid=data.get('machine_room_moid'),
        machine_room_name=data.get('machine_room_name'),
        code=data.get('code'),
        level=data.get('level'),
        description=data.get('description'),
        start_time=data.get('start_time'),
        resolve_time=data.get('resolve_time'),
        server_type=data.get('server_type', 0)
    )
    session.add(info)


def get_server_warning_unrepaired(session):
    from sqlalchemy.sql import func
    return session.query(ServerWarningUnrepaired.machine_room_moid, func.count()).group_by('machine_room_moid').all()


def add_terminal_warning_repaired(session, data):
    '''
    添加终端修复告警信息
    '''
    warning_unrepaired = session.query(TerminalWarningUnrepaired).filter(
        TerminalWarningUnrepaired.device_moid == data['device_moid'],
        TerminalWarningUnrepaired.code == data['code']
    ).first()
    info = TerminalWarningRepaired(
        device_moid=warning_unrepaired.device_moid,
        device_name=warning_unrepaired.device_name,
        device_type=warning_unrepaired.device_type,
        device_ip=warning_unrepaired.device_ip,
        device_e164=warning_unrepaired.device_e164,
        domain_moid=warning_unrepaired.domain_moid,
        domain_name=warning_unrepaired.domain_name,
        code=warning_unrepaired.code,
        level=warning_unrepaired.level,
        description=warning_unrepaired.description,
        start_time=warning_unrepaired.start_time,
        resolve_time=data['resolve_time']
    )
    session.add(info)
    session.delete(warning_unrepaired)


def add_server_warning_repaired(session, data):
    '''
    添加服务器修复告警信息
    '''
    warning_unrepaired = session.query(ServerWarningUnrepaired).filter(
        ServerWarningUnrepaired.device_moid == data['device_moid'],
        ServerWarningUnrepaired.code == data['code']
    ).first()
    if warning_unrepaired is not None:
        info = ServerWarningRepaired(
            device_moid=warning_unrepaired.device_moid,
            device_name=warning_unrepaired.device_name,
            device_type=warning_unrepaired.device_type,
            device_ip=warning_unrepaired.device_ip,
            machine_room_moid=warning_unrepaired.machine_room_moid,
            machine_room_name=warning_unrepaired.machine_room_name,
            code=warning_unrepaired.code,
            level=warning_unrepaired.level,
            description=warning_unrepaired.description,
            start_time=warning_unrepaired.start_time,
            server_type=warning_unrepaired.server_type,
            resolve_time=data['resolve_time']
        )
        session.add(info)
        session.delete(warning_unrepaired)


def add_terminal_crush_report(session, data):
    dev_type = data['type'].replace('~', ' ')
    info = TerminalCrushReport(
        moid=data['moid'],
        type=dev_type,
        version=data['version'],
        execption_time=data['execption_time'],
        execption_file=data['execption_file']
    )
    session.add(info)


# 会议统计相关接口
# :(


def add_multi_meeting_statistic(session, data):
    '''
    添加多点会议
    '''
    info = MultiMeetingStatistic(
        domain_moid=data['domain_moid'],
        meeting_moid=data['meeting_moid'],
        conf_e164=data['e164'],
        conf_name=data['name'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        info=json.dumps(data)
    )
    session.add(info)


def add_p2p_meeting_statistic(session, data):
    '''
    添加点对点会议
    '''
    info = P2PMeetingStatistic(
        domain_moid=data['caller_domain_moid'],
        meeting_moid=data['meeting_moid'],
        caller_e164=data['caller_e164'],
        caller_name=data['caller_name'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        info=json.dumps(data)
    )
    session.add(info)


def add_entry_meeting_statistic(session, data):
    '''
    添加实体会议
    '''
    info = EntryMeetingStatistic(
        domain_moid=data['domain_moid'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        info=json.dumps(data['info'])
    )
    session.add(info)


def add_meeting_terminal_detail_statistic(session, data):
    '''
    添加会议软硬终端
    '''
    session.query(MeetingTerminalDetailStatistic).filter(
        MeetingTerminalDetailStatistic.moid == data['moid'],
        MeetingTerminalDetailStatistic.meeting_moid == data['meeting_moid']
    ).delete()
    info = MeetingTerminalDetailStatistic(
        meeting_moid=data['meeting_moid'],
        moid=data['moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_tel_meeting_statistic(session, data):
    '''
    添加电话终端
    '''
    info = TelMeetingStatistic(
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_meeting_meeting_statistic(session, data):
    '''
    添加级联会议
    '''
    info = MeetingMeetingStatistic(
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_ip_e164_meeting_statistic(session, data):
    '''
    添加ip和友商终端
    '''
    info = IpE164MeetingStatistic(
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_ipc_meeting_statistic(session, data):
    '''
    添加ipc
    '''
    info = IpcMeetingStatistic(
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_terminal_leave_meeting_reason(session, data):
    '''
    添加终端离会原因
    '''
    info = TerminalLeaveMeetingReason(
        moid=data['moid'],
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data['info'])
    )
    session.add(info)


def add_terminal_meeting_socre(session, data):
    '''
    添加终端离会原因
    '''
    info = TerminalMeetingScore(
        moid=data['moid'],
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data['info'])
    )
    session.add(info)


def add_terminal_meeting_privideo(session, data):
    '''
    添加终端主视屏信息
    '''
    session.query(TerminalMeetingPrivideo).filter(
        TerminalMeetingPrivideo.moid == data['moid'],
        TerminalMeetingPrivideo.meeting_moid == data['meeting_moid'],
        TerminalMeetingPrivideo.channel_id == data['channel_id'],
    ).delete()
    info = TerminalMeetingPrivideo(
        moid=data['moid'],
        meeting_moid=data['meeting_moid'],
        channel_id=data['channel_id'],
        info=json.dumps(data)
    )
    session.add(info)


def add_terminal_meeting_assvideo(session, data):
    '''
    添加终端辅视屏信息
    '''
    session.query(TerminalMeetingAssvideo).filter(
        TerminalMeetingAssvideo.moid == data['moid'],
        TerminalMeetingAssvideo.meeting_moid == data['meeting_moid'],
        TerminalMeetingAssvideo.channel_id == data['channel_id']
    ).delete()
    info = TerminalMeetingAssvideo(
        moid=data['moid'],
        meeting_moid=data['meeting_moid'],
        channel_id=data['channel_id'],
        info=json.dumps(data)
    )
    session.add(info)


def add_live_info(session, data):
    '''
    添加直播信息
    '''
    info = LiveInfo(
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_live_user_info(session, data):
    '''
    添加直播用户信息
    '''
    info = UserInfoForLive(
        live_moid=data['live_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_meeting_dcs_info(session, data):
    '''
    添加数据协作信息
    '''
    info = MeetingDcsInfo(
        meeting_moid=data['meeting_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_dcs_mode_change_recode(session, data):
    '''
    添加数据协作模式变更信息
    '''
    info = DcsModeChangeRecode(
        dcs_moid=data['dcs_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_terminal_info_for_dcs(session, data):
    '''
    添加数据协作终端信息
    '''
    info = TerminalInfoForDcs(
        dcs_moid=data['dcs_moid'],
        info=json.dumps(data)
    )
    session.add(info)


def add_terminal_type(session, data):
    '''
    添加终端型号
    '''
    info = TerminalType(
        name=data['name'],
        terminal_type=data['terminal_type'],
        device_tag=data['device_tag'],
        product_name=data['product_name']
    )
    session.add(info)


def del_all_terminal_type(session):
    session.query(TerminalType).delete()


def get_inspect_recycle(session, taskid):
    return session.query(InspectRecycle).filter(InspectRecycle.taskid == taskid).first()


def get_inspect_task(session, taskid):
    return session.query(InspectTask).filter(InspectTask.id == taskid).first()


def get_inspect_tasks(session):
    return session.query(InspectTask.id).filter(InspectTask.sub_task == 0, InspectTask.task_flag == 1).all()


def set_inspect_task_executed(session, taskid, executed):
    task = session.query(InspectTask).filter(InspectTask.id == taskid).first()
    if task:
        task.executed = executed
