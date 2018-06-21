# -*- coding: utf-8 -*-

import redis
import pymysql

from ..core import config

__all__ = 'get_redis_connection', 'get_mysql_connection'

redis_pool = None
# redis_pool = redis.ConnectionPool(host=config.redis.host,
#                                   port=config.redis.port,
#                                   decode_responses=config.redis.decode_responses)


def get_redis_connection(db=0):
    global redis_pool
    if not redis_pool:
        redis_pool = redis.ConnectionPool(host=config.redis.host,
                                        port=config.redis.port,
                                        decode_responses=config.redis.decode_responses)
    return redis.StrictRedis(connection_pool=redis_pool, db=db)


def get_mysql_connection():
    connection = pymysql.connect(host=config.mysql.host,
                                port=config.mysql.port,
                                user=config.mysql.user,
                                password=config.mysql.password,
                                database=config.mysql.database,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection
