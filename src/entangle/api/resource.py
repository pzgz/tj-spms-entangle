# -*- coding: utf-8 -*-

import os
import decimal
import redis
import pymysql
import logging
import oracledb as cx_Oracle

from ..core import config
from .oracle import Connection

__all__ = 'get_redis_connection', 'get_mysql_connection', 'get_oracle_connection'

redis_pool = None
# redis_pool = redis.ConnectionPool(host=config.redis.host,
#                                   port=config.redis.port,
#                                   decode_responses=config.redis.decode_responses)

logger = logging.getLogger(__name__)

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


def outputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.NUMBER:
        return cursor.var(decimal.Decimal, arraysize = cursor.arraysize)

def get_oracle_connection():
    try:
        connection = Connection(user=config.oracle.user,
        password=config.oracle.password,
        dsn='{}:{}/{}'.format(config.oracle.host, config.oracle.port, config.oracle.database))
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        if error.code == 1017:
            logger.error('Please check your credentials.')
        else:
            logger.error('Database connection error: {}'.format(e))

        raise    

    # connection.outputtypehandler = outputTypeHandler
    return connection
