import requests
import logging
from datetime import datetime
from config.common import BRAND, LOGGING, SERVICE_IP, SERVICE_PORT


logger = logging.getLogger(LOGGING['loggername'])


def send_warning_shortmsg(mobile_num_list, server_type, warning_trigger_flag, info, warning_info, threshold_value=None, current_value=None):
    data = {
        'key_id': 'nms',
        'key_secret': '12345678',
        'template_param': get_template_param(info, warning_info, threshold_value, current_value),
        'type': 'application/json',
        'brand': BRAND
    }
    if threshold_value and current_value:
        if warning_trigger_flag:
            # 阈值告警
            data['msg_type'] = 'NMS_UNREPAIRED_THRESHOLD_WARNING'
        else:
            # 阈值告警修复
            data['msg_type'] = 'NMS_REPAIRED_THRESHOLD_WARNING'
    else:
        if warning_trigger_flag:
            # 非阈值告警
            data['msg_type'] = 'NMS_UNREPAIRED_COMMON_WARNING'
        else:
            # 非阈值告警修复
            data['msg_type'] = 'NMS_REPAIRED_COMMON_WARNING'

    url = 'http://%s:%s/serviceCore/cxf/sms/sendSMSMEssageInCore' % (
        SERVICE_IP, SERVICE_PORT)
    for mobile_num in mobile_num_list:
        data['mobile'] = mobile_num
        try:
            requests.post(url, json=data)
        except Exception as e:
            logger.error(e)


def get_template_param(info, warning_info, threshold_value=None, current_value=None):
    template_param = {
        "device_name": info['name'],
        "warning_name": warning_info['name']
    }
    if warning_info['level'] == 'critical':
        template_param['warning_level'] = '[严重告警]'
    elif warning_info['level'] == 'important':
        template_param['warning_level'] = '[重要告警]'
    else:
        template_param['warning_level'] = '[普通告警]'
    template_param['warning_time'] = datetime.now().strftime(
        '%Y/%m/%d %H:%M:%S')

    if threshold_value and current_value:
        unit = warning_info.get('unit')
        template_param["warning_threshold"] = '%s%s' % (threshold_value, unit)
        template_param["current_value"] = '%s%s' % (current_value, unit)
    return template_param
