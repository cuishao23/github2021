"""luban数据库请求"""
from dao.mysql.luban import *
from sqlalchemy.sql import func

# 包含核心域信息, 但信息可能存在未同步情况


def get_machine_room_list(session):
    return session.query(
        MachineRoomInfo.machine_room_moid,
        MachineRoomInfo.machine_room_name,
        MachineRoomInfo.domain_moid
    ).all()


def get_p_server_list(session):
    '''
    获取luban物理服务器列表
    :return:[
        (moid, name, type, machine_room_moid, location, ip, mac_id),
    ]
    '''
    result = []
    # 临时记录machin_room信息
    machine_room_info = {
        machine_room.machine_room_moid: machine_room.machine_room_name for machine_room in session.query(MachineRoomInfo).all()
    }
    # 主机
    machine_list = session.query(MachineInfo).all()
    for machine in machine_list:
        result.append((
            machine.machine_moid,
            machine.machine_name,
            machine.machine_type,
            machine.machine_room_moid,
            machine.machine_room_name,
            machine.ips[0].ip if len(machine.ips) else '',
            machine.mac_id[4:] if machine.mac_id else ''
        ))

    # 机框
    frame_list = session.query(FrameInfo).all()
    for frame in frame_list:
        result.append((
            frame.frame_moid,
            frame.frame_name,
            frame.frame_type,
            frame.machine_room.machine_room_moid,
            frame.machine_room.machine_room_name,
            '',
            ''
        ))
    # 外设
    peripheral_config_list = session.query(PeripheralConfig).filter(
        PeripheralConfig.key == 'device_name'
    ).all()
    for peripheral_config in peripheral_config_list:
        if peripheral_config.peripheral.machine_room_moid:
            machine_room_name = machine_room_info[peripheral_config.peripheral.machine_room_moid]
            result.append((
                peripheral_config.peripheral.per_moid,
                peripheral_config.value,
                peripheral_config.peripheral.per_sub_type,
                peripheral_config.peripheral.machine_room_moid,
                machine_room_name,
                '',
                ''
            ))
    return result


def get_l_server_list(session):
    '''
    获取luban逻辑服务器列表
    :return:[
        (moid, name, type, machine_room_moid, p_server_moid)
    ]
    '''
    return session.query(
        ServerInfo.server_moid,
        ServerInfo.server_name,
        ServerInfo.server_type,
        ServerInfo.machine_room_moid,
        ServerInfo.p_server_moid).filter(ServerInfo.server_type.notilike('ha-%')).all()


def get_machine_info_bak(session):
    return session.query(
        MachineInfoBak.machine_moid,
        MachineInfoBak.machine_name,
        MachineInfoBak.machine_type,
        MachineInfoBak.machine_room_moid,
        MachineInfoBak.machine_room_name,
        MachineInfoBak.ip,
        MachineInfoBak.mac_id,
        MachineInfoBak.operate
    ).all()


def get_machine_info_bak_max_id(session):
    return session.query(func.max(MachineInfoBak.id)).first()[0]


def get_server_info_bak(session):
    return session.query(
        ServerInfoBak.server_moid,
        ServerInfoBak.server_name,
        ServerInfoBak.server_type,
        ServerInfoBak.machine_room_moid,
        ServerInfoBak.p_server_moid,
        ServerInfoBak.operate
    ).filter(ServerInfoBak.server_type.notilike('ha-%')).all()


def get_server_info_bak_max_id(session):
    return session.query(func.max(ServerInfoBak.id)).first()[0]


def del_machine_info_bak(session, max_id):
    session.query(MachineInfoBak).filter(MachineInfoBak.id <= max_id).delete(synchronize_session='fetch')


def del_server_info_bak(session, max_id):
    session.query(ServerInfoBak).filter(ServerInfoBak.id <= max_id).delete(synchronize_session='fetch')
