import logging
import json
from config.common import LOGGING, MAIL
from config.warning import WARNING_MQ_CONFIG

P_MAIL_MSG = '''\
设备类型：物理服务器({type})<br>\
设备moid：{moid}<br>\
设备名称：{name}<br>\
设备位置：{location}<br>\
设 备 IP：{ip}<br>\
告 警 码：{code}<br>\
告警名称：{warning_name}<br>\
告警描述：{description}<br>\
{threshold_string}\
解决建议：{suggestion}<br>\
{warning_status}\
'''

L_MAIL_MSG = '''\
设备类型：逻辑服务器({type})<br>\
设备moid：{moid}<br>\
设备名称：{name}<br>\
所属物理服务器moid：：{p_server_moid}<br>\
告 警 码：{code}<br>\
告警名称：{warning_name}<br>\
告警描述：{description}<br>\
{threshold_string}\
解决建议：{suggestion}<br>\
{warning_status}\
'''

T_MAIL_MSG = '''\
设备类型：终端设备<br>\
设备moid：{moid}<br>\
设备名称：{name}<br>\
设备E164：{e164}<br>\
告 警 码：{code}<br>\
告警名称：{warning_name}<br>\
告警描述：{description}<br>\
{threshold_string}\
解决建议：{suggestion}<br>\
{warning_status}\
'''

logger = logging.getLogger(LOGGING['loggername'])


def send_warning_mail(mail_list, server_type, warning_trigger_flag, info, warning_info, threshold_value=None, current_value=None):
    from threads.mq_threads import rmq_produce_thread
    subject = get_subject(warning_trigger_flag, info, warning_info)
    if server_type == 'p_server':
        get_msg = get_physical_server_msg
    elif server_type == 'l_server':
        get_msg = get_logic_server_msg
    else:
        get_msg = get_terminal_msg
    msg = get_msg(warning_trigger_flag, info, warning_info,
                  threshold_value=threshold_value, current_value=current_value)
    logger.info('send mail:%s, %s' % (subject, msg))
    for mail in mail_list:
        json_data = {
            'type': 'EMAIL_SEND_INSTANT',
            'syskey': 'nms_warning_mail',
            'from': MAIL,
            'subject': subject,
            'text': msg,
            'to': mail}
        rmq_produce_thread.push(
            (*WARNING_MQ_CONFIG['mail'], json.dumps(json_data)))


def get_subject(warning_trigger_flag, info, warning_info):
    warning_status = '' if warning_trigger_flag else '[已修复]'
    if warning_info['level'] == 'critical':
        level = '[严重告警]'
    elif warning_info['level'] == 'important':
        level = '[重要告警]'
    else:
        level = '[普通告警]'
    tpye_str = '[{}]'.format(info['type']) if 'type' in info else ''
    return warning_status + level + tpye_str + info['name'] + '--' + warning_info['name']


def get_physical_server_msg(warning_trigger_flag, p_info, warning_info, threshold_value=None, current_value=None):
    warning_status = '' if warning_trigger_flag else '告警状态：已修复<br>'
    if threshold_value and current_value:
        threshold_string = '阈 值 为：{threshold_value}{unit}<br>当前值为：{current_value}{unit}<br>'.format(
            threshold_value=threshold_value,
            current_value=current_value,
            unit=warning_info.get('unit', '')
        )
    else:
        threshold_string = ''
    return P_MAIL_MSG.format(
        type=p_info.get('type', ''),
        moid=p_info.get('moid', ''),
        name=p_info.get('name', ''),
        location=p_info.get('location', ''),
        ip=p_info.get('ip', ''),
        code=warning_info.get('code', ''),
        warning_name=warning_info.get('name', ''),
        description=warning_info.get('description', ''),
        threshold_string=threshold_string,
        suggestion=warning_info.get('suggestion', ''),
        warning_status=warning_status
    )


def get_logic_server_msg(warning_trigger_flag, l_info, warning_info, threshold_value=None, current_value=None):
    warning_status = '' if warning_trigger_flag else '告警状态：已修复<br>'
    if threshold_value == '' or current_value == '':
        threshold_string = ''
    else:
        threshold_string = '阈 值 为：{threshold_value}{unit}<br>当前值为：{current_value}{unit}<br>'.format(
            threshold_value=threshold_value,
            current_value=current_value,
            unit=warning_info.get('unit', '')
        )
    return L_MAIL_MSG.format(
        type=l_info.get('type', ''),
        moid=l_info.get('moid', ''),
        name=l_info.get('name', ''),
        p_server_moid=l_info.get('p_server_moid', ''),
        code=warning_info.get('code', ''),
        warning_name=warning_info.get('name', ''),
        description=warning_info.get('description', ''),
        threshold_string=threshold_string,
        suggestion=warning_info.get('suggestion', ''),
        warning_status=warning_status
    )


def get_terminal_msg(warning_trigger_flag, t_info, warning_info, threshold_value=None, current_value=None):
    warning_status = '' if warning_trigger_flag else '告警状态：已修复<br>'
    if threshold_value == '' or current_value == '':
        threshold_string = ''
    else:
        threshold_string = '阈 值 为：{threshold_value}{unit}<br>当前值为：{current_value}{unit}<br>'.format(
            threshold_value=threshold_value,
            current_value=current_value,
            unit=warning_info.get('unit', '')
        )
    return T_MAIL_MSG.format(
        moid=t_info.get('moid', ''),
        name=t_info.get('name', ''),
        e164=t_info.get('e164', ''),
        code=warning_info.get('code', ''),
        warning_name=warning_info.get('name', ''),
        description=warning_info.get('description', ''),
        threshold_string=threshold_string,
        suggestion=warning_info.get('suggestion', ''),
        warning_status=warning_status
    )
