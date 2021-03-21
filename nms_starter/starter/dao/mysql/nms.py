"""网管数据库映射"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Enum, SmallInteger, Enum, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class LevelEnum(enum.Enum):
    critical = '1'
    important = '2'
    normal = '3'


class ConfType(enum.Enum):
    traditional = '0'
    port = '1'
    sfu = '2'
    mix = '3'

########### old terminal ##########
# 机房, 核心域下机房为核心域机房


class OldTerminal(Base):
    __tablename__ = 'old_terminal'
    id = Column(Integer, primary_key=True)
    user_domain_moid = Column(String(40))
    moid = Column(String(40))
    type = Column(String(32))
    version = Column(String(64))
    name = Column(String(128))
    e164 = Column(String(32))
    ip = Column(String(128))
    online = Column(Integer)


### 告警配置相关表 ###
# 告警通知规则
class WarningNotify(Base):
    __tablename__ = 'warning_notify'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    domain_moid = Column(String(40))
    user_moid = Column(String(40))
    code_list = Column(String(1024))
    email = Column(String(128))
    phone = Column(String(128))
    wechat = Column(String(128))


# 暂停告警设置表
class StopWarning(Base):
    __tablename__ = 'stop_warning'
    id = Column(Integer, primary_key=True)
    moid = Column(String(40))


# 服务器阈值设置
class ServerResourceLimit(Base):
    __tablename__ = 'server_resource_limit'
    id = Column(Integer, primary_key=True)
    device_moid = Column(String(40))
    cpu = Column(Integer)
    memory = Column(Integer)
    disk = Column(Integer)
    port = Column(Integer)
    diskwritespeed = Column(Integer)
    rateofflow = Column(Integer)


# 终端未修复告警
class TerminalWarningUnrepaired(Base):
    __tablename__ = 'terminal_warning_unrepaired'
    id = Column(Integer, primary_key=True)
    device_moid = Column(String(40))
    device_name = Column(String(128), nullable=True)
    device_type = Column(String(36), nullable=True)
    device_ip = Column(String(128), nullable=True)
    device_e164 = Column(String(32), nullable=True)
    domain_moid = Column(String(40))
    domain_name = Column(String(128), nullable=True)
    code = Column(Integer)
    level = Column(Enum(LevelEnum))
    description = Column(String(128), nullable=True)
    start_time = Column(DateTime)
    resolve_time = Column(DateTime, nullable=True)


# 服务器未修复告警
class ServerWarningUnrepaired(Base):
    __tablename__ = 'server_warning_unrepaired'
    id = Column(Integer, primary_key=True)
    device_moid = Column(String(40))
    device_name = Column(String(128), nullable=True)
    device_type = Column(String(36), nullable=True)
    device_ip = Column(String(128), nullable=True)
    machine_room_moid = Column(String(40))
    machine_room_name = Column(String(128), nullable=True)
    code = Column(Integer)
    level = Column(Enum(LevelEnum))
    description = Column(String(128), nullable=True)
    start_time = Column(DateTime)
    resolve_time = Column(DateTime, nullable=True)
    server_type = Column(SmallInteger)


# 终端已修复告警
class TerminalWarningRepaired(Base):
    __tablename__ = 'terminal_warning_repaired'
    id = Column(Integer, primary_key=True)
    device_moid = Column(String(40))
    device_name = Column(String(128), nullable=True)
    device_type = Column(String(36), nullable=True)
    device_ip = Column(String(128), nullable=True)
    device_e164 = Column(String(32), nullable=True)
    domain_moid = Column(String(40))
    domain_name = Column(String(128), nullable=True)
    code = Column(Integer)
    level = Column(Enum(LevelEnum))
    description = Column(String(128), nullable=True)
    start_time = Column(DateTime)
    resolve_time = Column(DateTime, nullable=True)


# 服务器已修复告警
class ServerWarningRepaired(Base):
    __tablename__ = 'server_warning_repaired'
    id = Column(Integer, primary_key=True)
    device_moid = Column(String(40))
    device_name = Column(String(128), nullable=True)
    device_type = Column(String(36), nullable=True)
    device_ip = Column(String(128), nullable=True)
    machine_room_moid = Column(String(40))
    machine_room_name = Column(String(128), nullable=True)
    code = Column(Integer)
    level = Column(Enum(LevelEnum))
    description = Column(String(128), nullable=True)
    start_time = Column(DateTime)
    resolve_time = Column(DateTime, nullable=True)
    server_type = Column(SmallInteger)


########### terminal ##########
# 终端崩溃
class TerminalCrushReport(Base):
    __tablename__ = 'terminal_crush_report'
    id = Column(Integer, primary_key=True)
    moid = Column(String(40))
    type = Column(String(32))
    version = Column(String(64))
    exception_time = Column(DateTime, nullable=True)
    exception_file = Column(Text)


# 历史会议统计相关
# 多点会议统计
class MultiMeetingStatistic(Base):
    __tablename__ = 'multi_meeting_statistic'
    id = Column(Integer, primary_key=True)
    domain_moid = Column(String(40))
    meeting_moid = Column(String(40))
    conf_e164 = Column(String(32))
    conf_name = Column(String(128))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    info = Column(Text)


# 点对点会议详情
class P2PMeetingStatistic(Base):
    __tablename__ = 'p2p_meeting_statistic'
    id = Column(Integer, primary_key=True)
    domain_moid = Column(String(40))
    meeting_moid = Column(String(40))
    caller_e164 = Column(String(32))
    caller_name = Column(String(128))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    info = Column(Text)


# 点对点会议详情
class EntryMeetingStatistic(Base):
    __tablename__ = 'entry_meeting_statistic'
    id = Column(Integer, primary_key=True)
    domain_moid = Column(String(40))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    info = Column(Text)


# 会议终端详情
class MeetingTerminalDetailStatistic(Base):
    __tablename__ = 'meeting_terminal_detail_statistic'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    moid = Column(String(40))
    info = Column(Text)


# 参会电话信息
class TelMeetingStatistic(Base):
    __tablename__ = 'tel_meeting_statistic'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    info = Column(Text)


# 级联会议信息统计
class MeetingMeetingStatistic(Base):
    __tablename__ = 'meeting_meeting_statistic'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    info = Column(Text)


# 参会IP或友商信息
class IpE164MeetingStatistic(Base):
    __tablename__ = 'ip_e164_meeting_statistic'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    info = Column(Text)


# IPC终端
class IpcMeetingStatistic(Base):
    __tablename__ = 'ipc_meeting_statistic'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    info = Column(Text)


# 终端离会原因统计
class TerminalLeaveMeetingReason(Base):
    __tablename__ = 'terminal_leave_meeting_reason'
    id = Column(Integer, primary_key=True)
    moid = Column(String(40))
    meeting_moid = Column(String(40))
    info = Column(Text)


# 终端离会原因统计
class TerminalMeetingScore(Base):
    __tablename__ = 'terminal_meeting_score'
    id = Column(Integer, primary_key=True)
    moid = Column(String(40))
    meeting_moid = Column(String(40))
    info = Column(Text)


# 入会终端主视频信息
class TerminalMeetingPrivideo(Base):
    __tablename__ = 'terminal_meeting_privideo'
    id = Column(Integer, primary_key=True)
    moid = Column(String(40))
    meeting_moid = Column(String(40))
    channel_id = Column(Integer)
    info = Column(Text)


# 入会终端辅视屏信息
class TerminalMeetingAssvideo(Base):
    __tablename__ = 'terminal_meeting_assvideo'
    id = Column(Integer, primary_key=True)
    moid = Column(String(40))
    meeting_moid = Column(String(40))
    channel_id = Column(Integer)
    info = Column(Text)


# 直播信息
class LiveInfo(Base):
    __tablename__ = 'live_info'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    info = Column(Text)


# 直播用户信息
class UserInfoForLive(Base):
    __tablename__ = 'user_info_for_live'
    id = Column(Integer, primary_key=True)
    live_moid = Column(String(40))
    info = Column(Text)


# 数据协作详情
class MeetingDcsInfo(Base):
    __tablename__ = 'meeting_dcs_info'
    id = Column(Integer, primary_key=True)
    meeting_moid = Column(String(40))
    info = Column(Text)


# 数据协作模式变更记录
class DcsModeChangeRecode(Base):
    __tablename__ = 'dcs_mode_change_recode'
    id = Column(Integer, primary_key=True)
    dcs_moid = Column(String(40))
    info = Column(Text)


# 数据会议里的终端信息
class TerminalInfoForDcs(Base):
    __tablename__ = 'terminal_info_for_dcs'
    id = Column(Integer, primary_key=True)
    dcs_moid = Column(String(40))
    info = Column(Text)


# 终端类型
class TerminalType(Base):
    __tablename__ = "terminal_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    terminal_type = Column(String(2))
    device_tag = Column(String(50))
    product_name = Column(String(128))


# 巡检
class InspectTask(Base):
    __tablename__ = "inspect_task"
    id = Column(Integer, primary_key=True)
    domain_moid = Column(String(40))
    user_moid = Column(String(40))
    start_time = Column(DateTime)
    license = Column(Integer)
    resource = Column(Integer)
    server = Column(Integer)
    terminal = Column(Integer)
    recycle = Column(Integer)
    executed = Column(Integer)
    sub_task = Column(Integer)
    parent_task = Column(Integer)
    task_flag = Column(Integer)


class InspectRange(Base):
    __tablename__ = "inspect_range"
    id = Column(Integer, primary_key=True)
    taskid = Column(Integer)
    inspect_type = Column(String(8))
    service_domain_moid = Column(String(40))
    platform_domain_moid = Column(String(40))
    virtual_machine_room_moid = Column(String(40))
    user_domain_moid = Column(String(40))


class InspectRecycle(Base):
    __tablename__ = "inspect_recycle"
    id = Column(Integer, primary_key=True)
    taskid = Column(Integer)
    end_time = Column(DateTime)
    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
