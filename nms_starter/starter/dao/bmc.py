"""bmc数据库请求"""
from dao.mysql.bmc import *


def get_domain_list(session):
    '''
    获取域信息
    '''
    result = []
    # 服务域
    result += [(
        service_domain.service_domain_moid,
        service_domain.parent_id if service_domain.parent_id else '-1',
        service_domain.service_domain_name,
        'service' if service_domain.parent_id else 'kernel'
    ) for service_domain in session.query(ServiceDomain).all()]

    # 平台域
    platform_domain_query = session.query(PlatformDomain).all()
    result += [(
        platform_domain.platform_domain_moid,
        platform_domain.service_domain_moid,
        platform_domain.platform_domain_name,
        'platform'
    ) for platform_domain in platform_domain_query]

    # 用户域
    user_domain_query = session.query(UserDomain).all()
    result += [(
        user_domain.user_domain_moid,
        user_domain.service_domain_moid,
        user_domain.user_domain_name,
        'user',
        user_domain.machine_rooms[0].machine_room_moid

    ) for user_domain in user_domain_query if user_domain.machine_rooms]
    return result


def get_domain_license_list(session):
    return [(
        license_info.service_domain_moid, license_info.license_id, license_info.mcu_exp_date.strftime(
            '%Y-%m-%d') if license_info.mcu_exp_date is not None else '', license_info.device_id
    ) for license_info in session.query(LicenseInfo).filter(LicenseInfo.type != 1).all()]


# 不包含核心域信息, 其他机房信息完整
def get_machine_room_list(session):
    return session.query(
        MachineRoom.machine_room_moid,
        MachineRoom.machine_room_name,
        MachineRoom.platform_domain_moid
    ).all()


# 获取终端信息
def get_terminal_list(session):
    user_info_query = session.query(UserInfo).filter(
        UserInfo.enable == 1).filter(UserInfo.e164.isnot(None)).filter(UserInfo.user_domain_moid.isnot(None)).filter(UserInfo.account_type != 4).all()
    return [(
        user_info.moid,
        user_info.user_domain_moid,
        user_info.user_profile.name if user_info.user_profile and user_info.user_profile.name else '',
        user_info.e164
    ) for user_info in user_info_query]


# 48终端信息
def get_old_terminal_list(session):
    user_info_query = session.query(UserInfo).filter(
        UserInfo.enable == 1).filter(UserInfo.e164.isnot(None)).filter(UserInfo.user_domain_moid.isnot(None)).filter(UserInfo.account_type == 4).all()
    return [(
        user_info.moid,
        user_info.user_domain_moid,
        user_info.user_profile.name if user_info.user_profile and user_info.user_profile.name else '',
        user_info.e164,
        user_info.account
    ) for user_info in user_info_query]
