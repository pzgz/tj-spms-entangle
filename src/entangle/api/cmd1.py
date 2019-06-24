# -*- coding: utf-8 -*-

""" Implement the cmd1 command.
    增量模式：将外部系统数据同步到科研系统
"""
import logging
import json

import pymysql.cursors
from hashlib import md5
from datetime import date, datetime

from ..core import config
from .resource import get_mysql_connection, get_oracle_connection,  get_redis_connection

logger = logging.getLogger(__name__)

table_key_set = dict()

def main(name="World"):
    """ Execute the command.
    
    """
    logger.info("executing %s", name)
    duplicate(name)


def duplicate(table_name):
    
    table_config = config.entangle.get(table_name)
    target_table = table_config.get('target')
    rule_config = table_config.get('rules')

    if not table_config:
        logger.error('%s is not exist.', table_name)
        return
    else:
        logger.debug(table_config)

    # logger.debug('Config -> {}'.format(table_config))

    sql = 'SELECT {} FROM {} WHERE {}'.format(
        ','.join(table_config.get('fields').keys()),
        table_name,
        table_config.get('condition') if table_config.get('condition') else '1=1'
    )
    if table_config.get('order_by'):
        sql = '{} ORDER BY {}'.format(
            sql,
            table_config.get('order_by')
        )

    logger.info('Executing %s', sql)

    try:
        if table_config.get('source') == 'mysql':
            connection = get_mysql_connection()
        else:
            connection = get_oracle_connection()

        redis_conn = get_redis_connection()

        # redis：某个表的每条记录的md5记录在redisk的key(${exchange:*:target}:*)中
        # 将表的所有记录的key初始化存入old_set中，如果后续有新纪录产生，添加到old_set中
        # 表中实际有的记录的key存入new_set中
        # 判断是否有数据删除时，计算old_set和new_set的差
        old_set = table_key_set.get(table_name)
        if old_set:
            logger.debug('Table <%s> has %d records.', table_name, len(old_set))
        else:
            logger.info('Initializing key set...')
            old_set = set(redis_conn.keys('{}:*'.format(target_table)))
            table_key_set[table_name] = old_set

        cursor = connection.cursor()
        cursor.execute(sql)

        # rows = cursor.fetchall()
        new_set = set()
        count = 0
        while True:
            rows = cursor.fetchmany(config.core.get('batch'))
            if rows:
                count += len(rows)
                logger.debug('No.%d', count)
            else:
                break

            for row in rows:
                id = dict()
                new_row = dict()
                for _origin, _new in table_config.get('fields').items():
                    origin_value = row.get(_origin)
                    if isinstance(origin_value, str):
                        origin_value = origin_value.strip()

                    # 字段值映射判断                 
                    map_rule = rule_config.get(_origin) if rule_config else None
                    map_value = map_rule.get(origin_value) if map_rule else None
                    new_row[_new] = map_value if map_value else origin_value

                    if _origin in table_config.get('pk'):
                        id[_new] = new_row[_new]
                        # id = row.get(_origin)

                # 计算所有字段值组合的MD5值
                content = ','.join([x if isinstance(x, str) else str(x) for x in new_row.values()])
                new_md5 = md5(content.encode('utf-8')).hexdigest()
                key = '{}:{}'.format(target_table, ':'.join(
                    [x if isinstance(x, str) else str(x) for x in id.values()]))
                new_set.add(key)

                # 和旧记录的MD5值比较
                old_md5 = redis_conn.getset(key, new_md5)

                op = 0
                if not old_md5:
                    op = 1  # 新增记录
                    old_set.add(key)
                elif old_md5 != new_md5:
                    op = 2  # 记录发生了变化

                if op:
                    v = json.dumps({'pk': id, 'op': op, 'data': new_row}, ensure_ascii=False, cls=ComplexEncoder)
                    logger.info('Hit %s > %s', target_table, v)
                    # 将变化数据加入redis队列
                    redis_conn.lpush(target_table, v)

        # 判定是否有记录被删除
        pk_cols = list()
        for _origin, _new in table_config.get('fields').items():
            if _origin in table_config.get('pk'):
                pk_cols.append(_new)

        # old_set = set(redis_conn.keys('{}:*'.format(target_table)))
        del_set = old_set ^ new_set
        for k in del_set:
            v = json.dumps(
                {'pk': dict(zip(pk_cols, k.split(':')[-len(pk_cols):])), 'op': 3}, ensure_ascii = False, cls = ComplexEncoder)
            logger.info('Hit %s > %s', target_table, v)
            redis_conn.delete(k)
            redis_conn.lpush(target_table, v)
            old_set.remove(k)

    except:
        logger.exception('Error: unable to fetch data')
    finally:
        cursor.close()
        connection.close()

    # logger.debug(redis_conn.rpop(target_table))

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
