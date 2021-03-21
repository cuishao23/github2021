
def send_warning_wechat(wechat_list, server_type, warning_trigger_flag, info, warning_info, threshold_value=None, current_value=None):
    import json
    from threads.mq_threads import rmq_produce_thread
    from config.warning import WARNING_MQ_CONFIG
    if warning_info['level'] == 'critical':
        level = '严重'
    elif warning_info['level'] == 'important':
        level = '重要'
    else:
        level = '一般'
    json_data = {
        'event': 'alarm_notify',
        'to_user': wechat_list,
        'name': warning_info['name'],
        'number': warning_info['code'],
        'type': '产生告警' if warning_trigger_flag else '修复告警',
        'level': level,
        'description': warning_info['description'],
        'advice': warning_info['suggestion']
    }
    rmq_produce_thread.push(
        (*WARNING_MQ_CONFIG['wechat'], json.dumps(json_data)))
