# -*- coding: utf-8 -*-

""" Implement the cmd2 command.
    COPY模式：将外部系统数据同步到科研系统
"""

import logging
import json

from hashlib import md5
from datetime import date, datetime

from ..core import config
from .resource import get_redis_connection, get_mysql_connection, get_oracle_connection

logger = logging.getLogger(__name__)


def main(name="World", year=None, history=False):
    """ Execute the command.    
    """
    logger.debug("executing cmd2 command with %s", name)
    table_config = config.entangle.get(name)
    if not table_config:
        logger.error('%s is not exist.', name)
        return
    else:
        logger.debug(table_config)

    current_year = datetime.now().year
    if history:
        start_year = table_config.get('history')
        if start_year:
            for year in range(start_year, current_year):
                _duplicate(name+str(year), table_config, year)
    else:
        _name = name.split('.')
        if _name[-1] == 'forward':
            _forward(_name[0], table_config)
        else:
            _duplicate(_name[0], table_config)
    # app.debug = True
    # app.run(host='0.0.0.0', port=5000)


def _duplicate(table_name, table_config, year=None):
    if year:
        target = table_config.get('target').format(year=year)
    else:
        target = table_config.get('target')

    rule_config = table_config.get('rules')

    sql = 'SELECT {} FROM {} WHERE {}'.format(
        ','.join(table_config.get('fields').keys()),
        table_name,
        table_config.get('condition') if table_config.get('condition') else '1=1'
    )
    logger.info('Executing %s', sql)

    temp_target = '{}:tmp'.format(target)
    redis_conn = get_redis_connection()
    try:
        if table_config.get('source') == 'mysql':
            connection = get_mysql_connection()
        else:
            connection = get_oracle_connection()

        redis_conn.delete(temp_target)

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            new_row = dict()
            new_key = target
            for _origin, _new in table_config.get('fields').items():
                origin_value = row.get(_origin)
                if isinstance(origin_value, str):
                    origin_value = origin_value.strip()

                # 字段值映射判断
                map_rule = rule_config.get(_origin) if rule_config else None
                map_value = map_rule.get(origin_value) if map_rule else None
                new_row[_new] = map_value if map_value else origin_value

                if _origin in table_config.get('pk'):
                    new_key = '{}:{}'.format(new_key, new_row.get(_new))

            redis_conn.hmset(new_key, new_row)

            v = json.dumps(new_row, ensure_ascii=False)
            redis_conn.sadd(temp_target, v)

        redis_conn.rename(temp_target, target)
    except:
        logger.exception('Error: unable to fetch data')
    finally:
        cursor.close()
        connection.close()


def _forward(table_name, table_config):
    target = table_config.get('target')
    rule_config = table_config.get('rules')

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

    hash_target = '{}:md5'.format(target)
    redis_conn = get_redis_connection()
    try:
        if table_config.get('source') == 'mysql':
            connection = get_mysql_connection()
        else:
            connection = get_oracle_connection()

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        new_rows = list()
        for row in rows:
            new_row = dict()
            for _origin, _new in table_config.get('fields').items():
                origin_value = row.get(_origin)
                if isinstance(origin_value, str):
                    origin_value = origin_value.strip()
                # 字段值映射判断
                map_rule = rule_config.get(_origin) if rule_config else None
                map_value = map_rule.get(origin_value) if map_rule else None
                new_row[_new] = map_value if map_value else origin_value

            new_rows.append(new_row)

        v = json.dumps(new_rows, ensure_ascii=False)
        new_md5 = md5(v.encode('utf-8')).hexdigest()
        old_md5 = redis_conn.getset(hash_target, new_md5)
        if new_md5 != old_md5:
            _content = {'updated_at':int(datetime.now().timestamp()),
                'entity':table_name.lower(),
                'data':new_rows}

            redis_conn.set(target, json.dumps(_content, ensure_ascii=False))

    except:
        logger.exception('Error: unable to fetch data')
    finally:
        cursor.close()
        connection.close()
