import logging
import json
import requests
from config.common import LOGGING

logger = logging.getLogger(LOGGING['loggername'])


def terminal_type_importer():
    '''
    终端型号库导入
    '''
    from dao.mysql import nms_session_scope
    from dao.nms_mysql import del_all_terminal_type, add_terminal_type
    from dao.nms_redis import init_terminal_type_list
    from config.common import TERMINAL_TYPE_XLSX, API_CORE_IP, API_CORE_PORT
    from utils.common import get_account_token

    logger.info('terminal type import ...')
    data = get_terminal_type_list(TERMINAL_TYPE_XLSX)
    post_data = {}
    with nms_session_scope() as session:
        del_all_terminal_type(session)
        for info in data:
            add_terminal_type(session, info)
            if info['name'] not in post_data:
                post_data[info['name']] = []
            post_data[info['name']].append({
                'terminalType': info['terminal_type'],
                'deviceTag': info['device_tag']
            })
    init_terminal_type_list(json.dumps(
        [info['product_name'] for info in data]))
    logger.info('terminal type import ok')
    # 调用bcm接口
    json_data = [{"name": key, 'data': post_data[key]} for key in post_data]
    try:
        token = get_account_token(API_CORE_IP, API_CORE_PORT)
        requests.post(
            'http://{}:{}/apiCore/bmc/device/importData'.format(API_CORE_IP, API_CORE_PORT), 
            params={'account_token': token},
            json=json_data
        )
    except Exception as e:
        logger.warning(e)


def get_terminal_type_list(file):
    import xlrd
    table = xlrd.open_workbook(file).sheets()[0]
    data = []
    for i in range(1, table.nrows):
        content = table.row_values(i)
        name = ' '.join(content[1].strip().split())
        name = name if name else data[i-2]['name']
        product_name = ' '.join(content[2].strip().split())
        product_name = product_name if product_name else data[i-2]['product_name']
        device_tag = ' '.join(content[4].strip().split())
        device_tag = device_tag if device_tag else data[i-2]['device_tag']
        # 终端类型: 0软终端, 1硬终端
        terminal_type = 0 if content[5].strip() == '软件' else 1
        data.append({
            # 主型号
            'name': name,
            # 子型号
            'product_name': product_name,
            # 可登录设备
            'device_tag': device_tag,
            'terminal_type': terminal_type
        })
    return data
