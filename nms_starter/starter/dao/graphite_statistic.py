import logging
from threads.msg_threads import graphite_statistic_thread
from time import time
from config.common import LOGGING

# 定时统计
# 服务器告警
SERVER_WARNING = "nms.warning.{machine_room_moid}.server"
# 终端告警
TERMINAL_WARNING = "nms.warning.{domain_moid}.terminal"
# 预约会议
APPOINTMENT_MEETING_COUNT = "nms.meeting.{domain_moid}.appointment_count"
# 点对点会议
P2P_MEETING_COUNT = "nms.meeting.{domain_moid}.p2p_count"
# 点对点会议终端数量
P2P_MEETING_TERMINAL_COUNT = 'nms.meeting.{domain_moid}.p2p_terminal_count'
# 多点会议
MULTI_MEETING_COUNT = "nms.meeting.{domain_moid}.multi_count"
# 多点会议终端数量
MULTI_MEETING_TERMINAL_COUNT = 'nms.meeting.{domain_moid}.multi_terminal_count'
# SIP在线数
SIP_ONLINE_COUNT = 'nms.device.{domain_moid}.sip_online_count'
# H323在线数
H323_ONLINE_COUNT = 'nms.device.{domain_moid}.h323_online_count'
# RTC在线数
RTC_ONLINE_COUNT = 'nms.device.{domain_moid}.rtc_online_count'
# 在线服务器
ONLINE_SERVER_COUNT = "nms.device.{machine_room_moid}.physical.online_count"
# 离线服务器
OFFLINE_SERVER_COUNT = "nms.device.{machine_room_moid}.physical.offline_count"
# 在线终端数量
ONLINE_TERMINAL_COUNT = "nms.device.{domain_moid}.terminal.online_count"
# 离线终端数量
OFFLINE_TERMINAL_COUNT = "nms.device.{domain_moid}.terminal.offline_count"

# 消息
# cpu使用率
CPU_RESOURCE = "nms.resource.{machine_room_moid}.{p_server_moid}.cpu.{cpu}"
# 内存使用率
MEM_RESOURCE = "nms.resource.{machine_room_moid}.{p_server_moid}.mem"
# 上行流量
NETCARD_UP_RESOURCE = "nms.resource.{machine_room_moid}.{p_server_moid}.netcard.{netcard_name}.up"
# 下行流量
NETCARD_DOWN_RESOURCE = "nms.resource.{machine_room_moid}.{p_server_moid}.netcard.{netcard_name}.down"
# 总上行流量
NETCARD_TOTAL_UP_RESOURCE = "nms.resource.{machine_room_moid}.{p_server_moid}.netcard.up"
# 总下行流量
NETCARD_TOTAL_DOWN_RESOURCE = "nms.resource.{machine_room_moid}.{p_server_moid}.netcard.down"

logger = logging.getLogger(LOGGING['loggername'])


def add_statistic(path, value, timestamp):
    msg = "{path} {value} {timestamp}\n".format(
        path=path, value=value, timestamp=timestamp)
    graphite_statistic_thread.push(msg)


def add_server_warning_statistic(machine_room_moid, value, timestamp):
    path = SERVER_WARNING.format(machine_room_moid=machine_room_moid)
    add_statistic(path, value, timestamp)


def add_terminal_warning_statistic(domain_moid, value, timestamp):
    path = TERMINAL_WARNING.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_appointment_meeting_statistic(domain_moid, value, timestamp):
    path = APPOINTMENT_MEETING_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_p2p_meeting_statistic(domain_moid, value, timestamp):
    path = P2P_MEETING_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_multi_meeting_statistic(domain_moid, value, timestamp):
    path = MULTI_MEETING_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_p2p_meeting_terminal_statistic(domain_moid, value, timestamp):
    path = P2P_MEETING_TERMINAL_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_multi_meeting_terminal_statistic(domain_moid, value, timestamp):
    path = MULTI_MEETING_TERMINAL_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_sip_count_statistic(domain_moid, value, timestamp):
    path = SIP_ONLINE_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_h323_count_statistic(domain_moid, value, timestamp):
    path = H323_ONLINE_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_rtc_count_statistic(domain_moid, value, timestamp):
    path = RTC_ONLINE_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_online_server_statistic(machine_room_moid, value, timestamp):
    path = ONLINE_SERVER_COUNT.format(machine_room_moid=machine_room_moid)
    add_statistic(path, value, timestamp)


def add_offline_server_statistic(machine_room_moid, value, timestamp):
    path = OFFLINE_SERVER_COUNT.format(machine_room_moid=machine_room_moid)
    add_statistic(path, value, timestamp)


def add_online_terminal_statistic(domain_moid, value, timestamp):
    path = ONLINE_TERMINAL_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_offline_terminal_statistic(domain_moid, value, timestamp):
    path = OFFLINE_TERMINAL_COUNT.format(domain_moid=domain_moid)
    add_statistic(path, value, timestamp)


def add_cpu_resource_statistic(machine_room_moid, p_server_moid, cpu, value, timestamp):
    path = CPU_RESOURCE.format(
        machine_room_moid=machine_room_moid, p_server_moid=p_server_moid, cpu=cpu)
    add_statistic(path, value, timestamp)


def add_mem_resource_statistic(machine_room_moid, p_server_moid, value, timestamp):
    path = MEM_RESOURCE.format(
        machine_room_moid=machine_room_moid, p_server_moid=p_server_moid)
    add_statistic(path, value, timestamp)


def add_netcard_up_statistic(machine_room_moid, p_server_moid, netcard_name, value, timestamp):
    path = NETCARD_UP_RESOURCE.format(
        machine_room_moid=machine_room_moid, p_server_moid=p_server_moid, netcard_name=netcard_name)
    add_statistic(path, value, timestamp)


def add_netcard_down_statistic(machine_room_moid, p_server_moid, netcard_name, value, timestamp):
    path = NETCARD_DOWN_RESOURCE.format(
        machine_room_moid=machine_room_moid, p_server_moid=p_server_moid, netcard_name=netcard_name)
    add_statistic(path, value, timestamp)


def add_total_up_statistic(machine_room_moid, p_server_moid, value, timestamp):
    path = NETCARD_TOTAL_UP_RESOURCE.format(
        machine_room_moid=machine_room_moid, p_server_moid=p_server_moid)
    add_statistic(path, value, timestamp)


def add_total_down_statistic(machine_room_moid, p_server_moid, value, timestamp):
    path = NETCARD_TOTAL_DOWN_RESOURCE.format(
        machine_room_moid=machine_room_moid, p_server_moid=p_server_moid)
    add_statistic(path, value, timestamp)
