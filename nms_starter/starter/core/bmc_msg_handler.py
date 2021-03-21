from dao import nms_redis, nms_mysql
from core.warning import warning_handler
from threads.msg_threads import mysql_write_thread


def add_domain(data):
    '''
    {
        "operation": "add_domain",  // 操作类型说明字符串
        "moid": "1",              // 域的moid
        "parentMoid": "0",         // 域的上级域moid
        "type": "service",          // 域的类型：kernerl, service, platform, user
        "name": "aaa_service",     // 域的名称
        "machineRoomMoid": "1" // 用户域绑定机房的moid
    }
    '''
    nms_redis.add_domain(
        data['moid'],
        data['parentMoid'],
        data['name'],
        data['type'],
        data.get('machineRoomMoid'))


def update_domain(data):
    '''
    {
        "operation": "update_domain",  // 操作类型说明字符串
        "moid": "1",              // 域的moid
        "parentMoid": "0",         // 域的上级域moid
        "type": "service",          // 域的类型：kernerl, service, platform, user
        "name": "aaa_service",      // 域的名称
        "machineRoomMoid": "1" // 用户域绑定机房的moid
    }
    '''
    nms_redis.update_domain(
        data['moid'],
        data['parentMoid'],
        data['name'],
        data['type'],
        data.get('machineRoomMoid'))


def del_domain(data):
    '''
    {
        "operation": "del_domain",  // 操作类型说明字符串
        "moid": "1",              // 域的moid
    }
    '''
    nms_redis.del_domain(data['moid'])


def add_machine_room(data):
    '''
    {
        "operation": "add_machine_room",  // 操作类型说明字符串
        "moid": "1",                    // 机房的moid
        "domainMoid ": "0",             // 机房所属平台域的moid
        "name": "aaa " // 机房的名称
    }
    '''
    nms_redis.add_machine_room(
        data['moid'],
        data['name'],
        data['domainMoid'])


def update_machine_room(data):
    '''
    {
        "operation": "update_machine_room",  // 操作类型说明字符串
        "moid": "1",                       // 机房的moid
        "domainMoid ": "0",                // 机房所属平台域的moid
        "name": "aaa" // 机房的名称
    }
    '''
    nms_redis.update_machine_room(
        data['moid'],
        data['name'],
        data['domainMoid'])


def del_machine_room(data):
    '''
    {
        "operation": "del_ machine_room ",  // 操作类型说明字符串
        "moid": "1",              // 机房的moid
    }
    '''
    nms_redis.del_machine_room(data['moid'])


def add_license(data):
    '''
    {
        "operation": " add_license",  // 操作类型说明字符串
        "moid": "1",              // 服务域的moid
        " licenseId": "0",         // 许可证序号
        " mcuExpDate": "2037-12-31" // 授权到期时间
    }
    '''
    nms_redis.add_license(
        data['moid'],
        data['licenseId'],
        data['mcuExpDate'],
        data['macId'])


def del_license(data):
    '''
    {
        "operation": "del_license",  // 操作类型说明字符串
        "moid": "1",              // 机房的moid
        "licenseId": "0",         // 许可证序号
    }
    '''
    from datetime import datetime

    nms_redis.del_license(
        data['moid'],
        data['licenseId'])
    p_server_moid = nms_redis.get_device_moid_by_license(data['licenseId'])
    if p_server_moid:
        now = datetime.now()
        warning_handler(p_server_moid, False, 2066, now, 'p_server')
        warning_handler(p_server_moid, False, 2065, now, 'p_server')


def add_terminal(data):
    '''
    {
        "operation": "add_terminal",  // 操作类型说明字符串
        "moid": "1.2.1",            // 终端设备的moid
        "domainMoid": "1.2",      // 终端设备所属用户域的moid
        "name": "Terminal1",       // 终端设备的名称
        "e164": "0512111885701" // 终端设备的e164号码
    }
    '''
    nms_redis.add_terminal(
        data['moid'],
        data['domainMoid'],
        data['name'],
        data.get('e164', ''))


def update_terminal(data):
    '''
    {
        "operation": "update_terminal",  // 操作类型说明字符串
        "moid": "1.2.1",            // 终端设备的moid
        "domainMoid": "1.2",      // 终端设备所属用户域的moid
        "name": "Terminal1",       // 终端设备的名称
        "e164": "0512111885701" // 终端设备的e164号码
    }
    '''
    nms_redis.update_terminal(
        data['moid'],
        data['domainMoid'],
        data['name'],
        data.get('e164', ''))


def del_terminal(data):
    '''
    {
        "operation": "del_terminal",  // 操作类型说明字符串
        "moid": "1.2.1",            // 终端设备的moid
    }
    '''
    nms_redis.del_terminal(data['moid'])


def del_all_terminal(data):
    '''
    {
        "operation": "del_all_terminal",  // 操作类型说明字符串
        "domainMoid ": "1.2.1",            // 用户域moid
    }
    '''
    nms_redis.del_all_terminal(data['domainMoid '])


# TODO 用户相关的操作移除
def add_user(data):
    '''
    {
        "operation": "add_user",       // 操作类型说明字符串
        "moid": "1.2.1",              // 用户的moid
        "domainMoid": "1.2",         // 用户所属域的moid
        "role": "1",               // 用户的角色1: 服务域管理员，0：服务域操作员，2：用户域管理员
        "name": "张三",              // 用户的名称
        "email": "zhangsan@kedacom",  // 用户的邮箱
        "phone": "13621652385",       // 用户的电话
        "officeLocation": "17L" // 用户的办公室地址
    }
    '''
    pass


def update_user(data):
    '''
    {
        "operation": "update_user",      // 操作类型说明字符串
        "moid": "1.2.1",          // 用户的moid
        "domainMoid": "1.2",     // 用户所属域的moid
        "role": "1",              // 用户的角色1: 服务域管理员，0：服务域操作员，2：用户域管理员
        "name": "张三",               // 用户的名称
        "email": "zhangsan@kedacom",  // 用户的邮箱
        "phone": "13621652385",       // 用户的电话
        "officeLocation": "17L" // 用户的办公室地址
    }
    '''
    pass


def del_user(data):
    '''
    {
        "operation": "del_user",       // 操作类型说明字符串
        "moid": "1.2.1",              // 用户的moid
    }
    '''
    pass


def del_all_user(data):
    '''
    {
        "operation": "del_all_user",       // 操作类型说明字符串
        "domainMoid": "1.2.1",              // 用户域moid
    }
    '''
    pass


def add_old_terminal(data):
    '''
    {
        "operation": "add_old_terminal",       // 操作类型说明字符串
        "moid": "1.2.1",              		// 老终端的moid
        "domainMoid": "1.2",         		// 老终端所属用户域的moid
        "name": "张三",              		// 老终端的名称
        "e164": "1230456044",  // 老终端的E164号
        "ip": "172.16.80.236",  // 老终端的IP地址
    }
    '''
    nms_redis.add_old_terminal(
        data['moid'], data['domainMoid'], data.get(
            'name', ''), data('e164', ''), data.get('ip', '')
    )
    mysql_write_thread.push((nms_mysql.add_old_terminal, {
        'moid': data['moid'],
        'user_domain_moid': data['domainMoid'],
        'name': data.get('name'),
        'e164': data.get('e164'),
        'ip': data.get('ip')
    }))


def update_old_terminal(data):
    '''
    {
        "operation": "update_old_terminal",    // 操作类型说明字符串
        "moid": "1.2.1",              		// 老终端的moid
        "domainMoid": "1.2",         		// 老终端所属用户域的moid
        "name": "张三",              		// 老终端的名称
        "e164": "1230456044",  // 老终端的E164号
        "ip": "172.16.80.236",  // 老终端的IP地址
    }
    '''
    nms_redis.add_old_terminal(
        data['moid'], data['domainMoid'], data.get(
            'name', ''), data.get('e164', ''), data.get('ip', '')
    )
    nms_redis.add_old_terminal()
    mysql_write_thread.push((nms_mysql.update_old_terminal, {
        'moid': data['moid'],
        'user_domain_moid': data['domainMoid'],
        'name': data.get('name'),
        'e164': data.get('e164'),
        'ip': data.get('ip')
    }))


def del_old_terminal(data):
    '''
    {
        "operation": "del_old_terminal",       // 操作类型说明字符串
        "moid": "1.2.1",              		// 老终端的moid
    }
    '''
    nms_redis.del_old_terminal(data['moid'])
    mysql_write_thread.push((nms_mysql.del_old_terminal, data['moid']))
