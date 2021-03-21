# coding=utf-8
import functools
import redis
import socket

from config.common import REDIS, REDIS_LIMIIT
from utils.lock import synchronized


class RedisPool:
    # redis连接池
    _conn_pool = None

    @classmethod
    @synchronized
    def init_conn_pool(cls):
        if cls._conn_pool is None:
            cls._conn_pool = redis.ConnectionPool(
                **REDIS,
                **REDIS_LIMIIT,
                socket_keepalive=True,
                decode_responses=True,
                socket_keepalive_options={
                    socket.TCP_KEEPIDLE: 30,
                    socket.TCP_KEEPCNT: 3,
                    socket.TCP_KEEPINTVL: 15})

    @staticmethod
    def get_client():
        '''
        初始化redis连接池并返回连接
        连接使用完成后应该close(),回收到连接池
        '''
        # 初始化连接池
        # tcp连接需要设置keepalive
        if RedisPool._conn_pool is None:
            RedisPool.init_conn_pool()
        # 创建redis客户端
        return redis.Redis(connection_pool=RedisPool._conn_pool)
