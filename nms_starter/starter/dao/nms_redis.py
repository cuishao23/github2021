# coding=utf-8
from functools import partial
from dao.redis import exec_redis_lua, get_redis_client
from config import common

# domain
add_domain = partial(exec_redis_lua, file_name='add_domain.lua')
update_domain = partial(exec_redis_lua, file_name='update_domain.lua')
del_domain = partial(exec_redis_lua, file_name='del_domain.lua')


# machine_room
add_machine_room = partial(
    exec_redis_lua, file_name='add_machine_room.lua')
update_machine_room = partial(
    exec_redis_lua, file_name='update_machine_room.lua')
del_machine_room = partial(
    exec_redis_lua, file_name='del_machine_room.lua')


# license
add_license = partial(exec_redis_lua, file_name='add_license.lua')
del_license = partial(exec_redis_lua, file_name='del_license.lua')
update_license_warning = partial(
    exec_redis_lua, file_name='update_license_warning.lua')


# p_server
get_p_server = partial(exec_redis_lua, file_name="get_p_server.lua")
add_p_server = partial(exec_redis_lua, file_name='add_p_server.lua')
update_p_server = partial(exec_redis_lua, file_name='update_p_server.lua')
del_p_server = partial(exec_redis_lua, file_name='del_p_server.lua')


# l_server
get_l_server = partial(exec_redis_lua, file_name="get_l_server.lua")
add_l_server = partial(exec_redis_lua, file_name='add_l_server.lua')
update_l_server = partial(exec_redis_lua, file_name='update_l_server.lua')
del_l_server = partial(exec_redis_lua, file_name='del_l_server.lua')


# terminal
get_terminal = partial(exec_redis_lua, file_name="get_terminal.lua")
add_terminal = partial(exec_redis_lua, file_name='add_terminal.lua')
add_old_terminal = partial(exec_redis_lua, file_name='add_old_terminal.lua')
update_terminal = partial(exec_redis_lua, file_name='update_terminal.lua')
del_old_terminal = partial(exec_redis_lua, file_name='del_old_terminal.lua')
del_terminal = partial(exec_redis_lua, file_name='del_terminal.lua')
del_all_terminal = partial(exec_redis_lua, file_name='del_all_terminal.lua')

# init terminal type list
init_terminal_type_list = partial(
    exec_redis_lua, file_name='init_terminal_type_list.lua')


def get_terminal_moid(e164='', ip=''):
    if e164:
        with get_redis_client() as client:
            return client.hget('terminal:%s:baseinfo' % e164, 'moid')
    if ip:
        with get_redis_client() as client:
            return client.hget('terminal:ip2moid', ip)


get_device_moid_by_license = partial(exec_redis_lua, file_name='get_device_moid_by_license.lua')


########################################
#              告警相关                #
########################################
init_warning_global_limit = partial(
    exec_redis_lua, file_name='init_warning_global_limit.lua')
init_warning_server_limit = partial(
    exec_redis_lua, file_name='init_warning_server_limit.lua')
init_warning_notify = partial(
    exec_redis_lua, file_name='init_warning_notify.lua')
init_warning_code = partial(exec_redis_lua, file_name='init_warning_code.lua')
init_warning_stop = partial(exec_redis_lua, file_name='init_warning_stop.lua')
get_warning_notify = partial(
    exec_redis_lua, file_name='get_warning_notify.lua')
add_warning_unrepaired = partial(
    exec_redis_lua, file_name='add_warning_unrepaired.lua')
del_warning_unrepaired = partial(
    exec_redis_lua, file_name='del_warning_unrepaired.lua')
get_all_warning_info = partial(
    exec_redis_lua, file_name='get_all_warning_info.lua')


# 获取全局资源阈值设置
def get_warning_global_limit(resource):
    with get_redis_client() as client:
        return client.hget('warning:limit:global', resource)


# 获取服务器资源阈值设置
def get_warning_server_limit(moid, resource):
    with get_redis_client() as client:
        limit = client.hget('warning:limit:' + moid, resource)
    if limit is None:
        limit = common.SERVER_RESOURCE_LIMIT[resource]
    return limit


# 指定服务域或机房是否暂停告警
def get_stop_warning(moid):
    with get_redis_client() as client:
        return client.sismember('warning:stop', moid)


########################################
#              消息处理                #
########################################
# 物理服务器消息
ev_server_info = partial(exec_redis_lua, file_name='ev_server_info.lua')
ev_dev_online_p = partial(exec_redis_lua, file_name='ev_dev_online_p.lua')
ev_dev_offline_p = partial(exec_redis_lua, file_name='ev_dev_offline_p.lua')
ev_pfminfo_cpu = partial(exec_redis_lua, file_name='ev_pfminfo_cpu.lua')
ev_pfminfo_mem = partial(exec_redis_lua, file_name='ev_pfminfo_mem.lua')
ev_pfminfo_disk = partial(exec_redis_lua, file_name='ev_pfminfo_disk.lua')
ev_pfminfo_disk_age = partial(
    exec_redis_lua, file_name='ev_pfminfo_disk_age.lua')
ev_pfminfo_netcard = partial(
    exec_redis_lua, file_name='ev_pfminfo_netcard.lua')
ev_hdu_info = partial(exec_redis_lua, file_name='ev_hdu_info.lua')
ev_smu_cards_info = partial(exec_redis_lua, file_name='ev_smu_cards_info.lua')


def ev_srv_system_uptime(moid, uptime):
    with get_redis_client() as client:
        client.hset('p_server:'+moid+':info',
                    'uptime', uptime)


# 终端消息
ev_dev_online_t = partial(exec_redis_lua, file_name='ev_dev_online_t.lua')
ev_dev_offline_t = partial(exec_redis_lua, file_name='ev_dev_offline_t.lua')
ev_mt_info = partial(exec_redis_lua, file_name='ev_mt_info.lua')
ev_state_secret_info = partial(
    exec_redis_lua, file_name='ev_state_secret_info.lua')
ev_video_format_info = partial(
    exec_redis_lua, file_name='ev_video_format_info.lua')
ev_network_config_info = partial(
    exec_redis_lua, file_name='ev_network_config_info.lua')
ev_cameras_add_or_update = partial(
    exec_redis_lua, file_name='ev_cameras_add_or_update.lua')
ev_cameras_del = partial(exec_redis_lua, file_name='ev_cameras_del.lua')
ev_microphones_add_or_update = partial(
    exec_redis_lua, file_name='ev_microphones_add_or_update.lua')
ev_microphones_del = partial(
    exec_redis_lua, file_name='ev_microphones_del.lua')
ev_netinfo_msg = partial(exec_redis_lua, file_name='ev_netinfo_msg.lua')
ev_bandwidth_msg = partial(exec_redis_lua, file_name='ev_bandwidth_msg.lua')
ev_should_connsrv_msg = partial(
    exec_redis_lua, file_name='ev_should_connsrv_msg.lua')
ev_connsrv_conn_msg = partial(
    exec_redis_lua, file_name='ev_connsrv_conn_msg.lua')
ev_alarm_msg = partial(exec_redis_lua, file_name='ev_alarm_msg.lua')
ev_conf_info = partial(exec_redis_lua, file_name='ev_conf_info.lua')
ev_pfminfo_msg = partial(exec_redis_lua, file_name='ev_pfminfo_msg.lua')
ev_audio_video_status_ack = partial(
    exec_redis_lua, file_name='ev_audio_video_status_ack.lua')
ev_blunt_info = partial(exec_redis_lua, file_name='ev_blunt_info.lua')
ev_volume_ack = partial(exec_redis_lua, file_name='ev_volume_ack.lua')
ev_config_1st_video_format_ntf = partial(
    exec_redis_lua, file_name='ev_config_1st_video_format_ntf.lua')
ev_config_reg_addr_ntf = partial(
    exec_redis_lua, file_name='ev_config_reg_addr_ntf.lua')
ev_config_network_ntf = partial(
    exec_redis_lua, file_name='ev_config_network_ntf.lua')
ev_imix_info = partial(exec_redis_lua, file_name='ev_imix_info.lua')


# 48终端
ev_dev_online_t48 = partial(exec_redis_lua, file_name='ev_dev_online_t48.lua')
ev_dev_offline_t48 = partial(
    exec_redis_lua, file_name='ev_dev_offline_t48.lua')
ev_alarm_msg_t48 = partial(exec_redis_lua, file_name='ev_alarm_msg_t48.lua')


# 逻辑服务器消息
ev_dev_online_l = partial(exec_redis_lua, file_name='ev_dev_online_l.lua')
ev_dev_offline_l = partial(exec_redis_lua, file_name='ev_dev_offline_l.lua')
ev_xmpp_info = partial(exec_redis_lua, file_name='ev_xmpp_info.lua')
offline_pas = partial(exec_redis_lua, file_name='offline_pas.lua')
offline_ejabberd = partial(exec_redis_lua, file_name='offline_ejabberd.lua')
offline_mediaworker = partial(
    exec_redis_lua, file_name='offline_mediaworker.lua')
offline_vrs = partial(exec_redis_lua, file_name='offline_vrs.lua')
offline_cmu = partial(exec_redis_lua, file_name='offline_cmu.lua')
offline_dcs = partial(exec_redis_lua, file_name='offline_dcs.lua')
ev_mediaresource_info = partial(
    exec_redis_lua, file_name='ev_mediaresource_info.lua')
ev_mps_info = partial(exec_redis_lua, file_name='ev_mps_info.lua')
ev_pas_info = partial(exec_redis_lua, file_name='ev_pas_info.lua')
ev_mcu_conf_create = partial(
    exec_redis_lua, file_name='ev_mcu_conf_create.lua')
add_meeting_terminal = partial(
    exec_redis_lua, file_name='add_meeting_terminal.lua')
del_meeting_terminal = partial(
    exec_redis_lua, file_name='del_meeting_terminal.lua')
ev_mcu_conf_destroy = partial(
    exec_redis_lua, file_name='ev_mcu_conf_destroy.lua')
ev_mcu_conf_update = partial(
    exec_redis_lua, file_name='ev_mcu_conf_update.lua')
ev_mcu_conf_time_change = partial(
    exec_redis_lua, file_name='ev_mcu_conf_time_change.lua')
ev_pas_p2pconf_create = partial(
    exec_redis_lua, file_name='ev_pas_p2pconf_create.lua')
ev_pas_all_online_stat = partial(
    exec_redis_lua, file_name='ev_pas_all_online_stat.lua')
ev_aps_all_mt_info = partial(
    exec_redis_lua, file_name='ev_aps_all_mt_info.lua')
ev_vrs_create_live_info = partial(
    exec_redis_lua, file_name='ev_vrs_create_live_info.lua')
ev_vrs_update_user_info = partial(
    exec_redis_lua, file_name='ev_vrs_update_user_info.lua')
ev_vrs_create_aplive_info = partial(
    exec_redis_lua, file_name='ev_vrs_create_aplive_info.lua')
ev_vrs_destroy_aplive_info = partial(
    exec_redis_lua, file_name='ev_vrs_destroy_aplive_info.lua')
ev_dcs_create_conf_info = partial(
    exec_redis_lua, file_name='ev_dcs_create_conf_info.lua')
ev_dcs_online_state_change_info = partial(
    exec_redis_lua, file_name='ev_dcs_online_state_change_info.lua')
ev_alarm_report = partial(
    exec_redis_lua, file_name='ev_alarm_report.lua')
ev_dcs_coop_state_change_info = partial(
    exec_redis_lua, file_name='ev_dcs_coop_state_change_info.lua')
ev_dcs_conf_mt_del_info = partial(
    exec_redis_lua, file_name='ev_dcs_conf_mt_del_info.lua')
ev_dcs_destroy_conf_info = partial(
    exec_redis_lua, file_name='ev_dcs_destroy_conf_info.lua')
ev_ds_data_throughput_report = partial(
    exec_redis_lua, file_name='ev_ds_data_throughput_report.lua')
ev_vrs_destroy_live_info = partial(
    exec_redis_lua, file_name='ev_vrs_destroy_live_info.lua')
ev_pas_p2pconf_destroy = partial(
    exec_redis_lua, file_name='ev_pas_p2pconf_destroy.lua')
ev_pas_mt_encryption = partial(
    exec_redis_lua, file_name='ev_pas_mt_encryption.lua')
ev_dcs_mode_switch = partial(
    exec_redis_lua, file_name='ev_dcs_mode_switch.lua')
ev_modb_warning_info = partial(
    exec_redis_lua, file_name='ev_modb_warning_info.lua')
ev_ds_packet_loss_rate_report = partial(
    exec_redis_lua, file_name='ev_ds_packet_loss_rate_report.lua')
ev_rms_ap_info = partial(
    exec_redis_lua, file_name='ev_rms_ap_info.lua')
ev_conf_res_info = partial(
    exec_redis_lua, file_name='ev_conf_res_info.lua')


def ev_aps_add_mt_info(moid, operator_type):
    with get_redis_client() as client:
        client.hset('terminal:'+moid+':baseinfo',
                    'operator_type', operator_type)


def ev_rms_mp_info(service_type, moid, total_h264, used_h264, total_h265, used_h265):
    suffix = 'mg' if service_type == 0 else 'g_mg'
    key = 'domain:' + moid + ':' + suffix
    with get_redis_client() as client:
        client.hmset(
            key,
            {
                'total_h264': total_h264,
                'used_h264': used_h264,
                'total_h265': total_h265,
                'used_h265': used_h265
            })


def ev_logical_server_info(moid, version):
    with get_redis_client() as client:
        client.hset('l_server:'+moid+':info', 'version', version)


def ev_machine_room_res_info(machine_room_moid, total_port, remainder_port, remainder_tra):
    key = 'machine_room:' + machine_room_moid + ':info'
    with get_redis_client() as client:
        client.hmset(
            key,
            {
                'total_port': total_port,
                'remainder_port': remainder_port,
                'remainder_tra': remainder_tra
            })


def ev_machine_room_sfu_info(machine_room_moid, used_sfu, remainder_sfu):
    key = 'machine_room:' + machine_room_moid + ':info'
    with get_redis_client() as client:
        client.hmset(
            key,
            {
                'used_sfu': used_sfu,
                'remainder_sfu': remainder_sfu
            })


def ev_rms_vmr_info(moid, mapping):
    key = 'domain:'+moid+':vmr'
    with get_redis_client() as client:
        client.hmset(key, mapping)


# 预约会议
ev_conf_appointment = partial(
    exec_redis_lua, file_name='ev_conf_appointment.lua')
ev_conf_entity = partial(
    exec_redis_lua, file_name='ev_conf_entity.lua')


########################################
#              其他                    #
########################################

# collector
def get_collector_p_server_moid(collectorid):
    with get_redis_client() as client:
        key = 'collector:%s:info' % collectorid
        return client.hget(key, 'p_server_moid')


# 获取导入标志
# 可用于跨版本升级
def nms_is_first_import():
    with get_redis_client() as client:
        r = client.get('nms_first_import')
        return r != common.IMPORT_FLAG


# 设置导入标志
def set_nms_first_import():
    with get_redis_client() as client:
        client.set('nms_first_import', common.IMPORT_FLAG)


# 获取所有collector
def get_collectors():
    with get_redis_client() as client:
        return client.smembers('collector')


def add_collector(collectorid, devid):
    with get_redis_client() as client:
        client.sadd('collector', collectorid)
        client.hset('collector:%s:info' % collectorid, 'p_server_moid', devid)


# 获取所有collecotor在线设备
def get_collector_online_server(collectorid):
    with get_redis_client() as client:
        return client.hgetall('collector:%s:online' % collectorid)


offline_collector = partial(exec_redis_lua, file_name='offline_collector.lua')


# 清除所有redis信息
def flush_redis_db():
    with get_redis_client() as client:
        client.flushall()


# 获取类型信息
def get_types():
    with get_redis_client() as client:
        return client.smembers('p_server:type'), client.smembers('l_server:type')


def clean_up_tmp_db():
    pass


# 统计
meeting_statistic = partial(exec_redis_lua, file_name='meeting_statistic.lua')
meeting_terminal_statistic = partial(
    exec_redis_lua, file_name='meeting_terminal_statistic.lua')
pas_statistic = partial(exec_redis_lua, file_name='pas_statistic.lua')
server_online_statistic = partial(
    exec_redis_lua, file_name='server_online_statistic.lua')
terminal_online_statistic = partial(
    exec_redis_lua, file_name='terminal_online_statistic.lua')

# def test():
#     with get_redis_client() as client:
#         return client.hgetall('collector:a4bf01306d06:online')

test = partial(exec_redis_lua, file_name='test.lua')
