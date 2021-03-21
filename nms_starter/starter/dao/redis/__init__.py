import os
import json
import logging
from dao.redis.base import RedisPool
from config.common import SCRIPT_DIR, LOGGING

logger = logging.getLogger(LOGGING['loggername'])


def get_redis_client():
    return RedisPool.get_client()


def exec_redis_lua(*args, file_name=''):
    '''
    执行lua脚本, 读/写redis信息
    '''
    logger.info('[run_script %s] arg=%s' % (file_name, args))
    new_args = [arg if arg is not None else '' for arg in args]
    with get_redis_client() as client:
        with open(os.path.join(SCRIPT_DIR, file_name), encoding='utf-8') as f:
            script = f.read()
            r = client.eval(script, 0, *new_args)
            logger.info('[run_script %s]: return=%s'%(file_name, r))
            if r:
                try:
                    return json.loads(r, encoding='utf-8')
                except:
                    pass
            return r
