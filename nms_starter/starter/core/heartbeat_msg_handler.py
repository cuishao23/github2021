import logging
from retry import retry
from dao import nms_redis, nms_mysql
from config.types import server_type_judgment
from config.common import LOGGING

logger = logging.getLogger(LOGGING['loggername'])


def online_collector(collectorid, devid):
    nms_redis.add_collector(collectorid, devid)


@retry(logger=logger, delay=2, max_delay=30, backoff=2)
def offline_all_collector():
    collectors = nms_redis.get_collectors()
    logger.info('offline %s' % collectors)
    for collectorid in collectors:
        offline_collector(collectorid)


def offline_collector(collectorid):
    devices = nms_redis.get_collector_online_server(collectorid)
    logger.debug('offline %s' % devices)
    for moid, server_type in devices.items():
        logger.debug('offline %s %s %s' % (moid, collectorid, server_type))
        if server_type_judgment.is_physical_type(server_type):
            nms_redis.ev_dev_offline_p(moid, collectorid)
        if server_type_judgment.is_logical_type(server_type):
            offline_logic_device(moid, server_type, collectorid)
        elif '_48' in server_type:
            nms_redis.ev_dev_offline_t48(moid, collectorid)
        else:
            nms_redis.ev_dev_offline_t(moid, server_type, collectorid)
    logger.debug('offline %s' % collectorid)
    nms_redis.offline_collector(collectorid)


def offline_logic_device(moid, server_type, collectorid):
    if server_type == 'pas':
        nms_redis.offline_pas(moid, collectorid)
    elif server_type == 'ejabberd':
        nms_redis.offline_ejabberd(moid, collectorid)
    elif server_type == 'media-worker':
        nms_redis.offline_mediaworker(moid, collectorid)
    # elif server_type == 'mps':
    elif server_type == 'cmu':
        nms_redis.offline_cmu(moid, collectorid)
    elif server_type == 'vrs':
        nms_redis.offline_vrs(moid, collectorid)
    elif server_type == 'dcs':
        nms_redis.offline_dcs(moid, collectorid)
    else:
        nms_redis.ev_dev_offline_l(moid, collectorid)
