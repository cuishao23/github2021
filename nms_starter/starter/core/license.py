from dao import nms_redis
from core.warning import warning_handler
from datetime import datetime


def update_license_warning():
    now = datetime.now()
    licenses = nms_redis.update_license_warning()
    for info in licenses:
        exp_date = datetime.strptime(info['date'], '%Y-%m-%d')
        d = exp_date-now
        if d.days <= 7:
            warning_handler(info['p_server_moid'], True, 2066, now, 'p_server')
        elif d.days <= 30:
            warning_handler(info['p_server_moid'], True, 2065, now, 'p_server')
