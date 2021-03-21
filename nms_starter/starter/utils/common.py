# coding=utf-8
import configparser
import fcntl
import os


def get_conf(section, key, path):
    conf = configparser.ConfigParser()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            conf.read_file(f)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        str_val = conf.get(section, key)
    except Exception:
        str_val = None
    return str_val


def get_account_token(ip, port):
    import requests
    import xml.etree.ElementTree as ET
    try:
        params = {}
        params['oauth_consumer_key'] = 'Nms'
        params['oauth_consumer_secret'] = '12345678'
        url = 'http://{}:{}/apiCore/accountToken'.format(ip, port)
        r = requests.post(url, params=params, timeout=2)
        root = ET.fromstring(r.text)
        token = root.findtext('accountToken')
        return token
    except Exception as e:
        return ''


def get_unix_time_stamp(date_string, time_format):
    '''
    将 %Y/%m/%d %H%M%S格式转换为unix时间
    '''
    from datetime import datetime
    import time
    date_time = datetime.strptime(date_string, time_format)
    return int(time.mktime(date_time.timetuple()))
