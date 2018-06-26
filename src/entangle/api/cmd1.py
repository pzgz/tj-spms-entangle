""" Implement the cmd1 command.

"""
import logging
import json

import pymysql.cursors
from hashlib import md5

from ..core import config
from .resource import get_mysql_connection, get_oracle_connection,  get_redis_connection

logger = logging.getLogger(__name__)


def main(name="World"):
    """ Execute the command.
    
    """
    logger.info("executing {}".format(name))
    duplicate(name)


def duplicate(table_name):
    
    table_config = config.entangle.get(table_name)
    target_table = table_config.get('target')
    rule_config = table_config.get('rules')

    if not table_config:
        logger.error('{} is not exist.'.format(table_name))
        return
    else:
        logger.debug(table_config)

    # logger.debug('Config -> {}'.format(table_config))

    sql = 'SELECT {} FROM {} ORDER BY {}'.format(
        ','.join(table_config.get('fields').keys()),
        table_name,
        table_config.get('pk')
    )

    logger.info('Executing {}'.format(sql))

    try:
        if table_config.get('source') == 'mysql':
            connection = get_mysql_connection()
        else:
            connection = get_oracle_connection()

        redis_conn = get_redis_connection()

        cursor = connection.cursor()
        cursor.execute(sql)

        # _columns = [(metadata[0], metadata[1]) for metadata in cursor.description]
        # logger.debug(_columns)

        new_set = set()
        results = cursor.fetchall()
        count = 0
        for row in results:
            # logger.debug(row)
            count += 1
            if count % 1000 == 0:
                logger.debug('No.%d', count)

            new_row = dict()
            for _origin, _new in table_config.get('fields').items():
                origin_value = row.get(_origin)   

                # 字段值映射判断                 
                map_rule = rule_config.get(_origin) if rule_config else None
                map_value = map_rule.get(origin_value) if map_rule else None
                new_row[_new] = map_value if map_value else origin_value

                if _origin == table_config.get('pk'):
                    id = row.get(_origin)

            # 计算所有字段值组合的MD5值
            content = ','.join([x if isinstance(x, str) else str(x) for x in new_row.values()])
            new_md5 = md5(content.encode('utf-8')).hexdigest()
            key = '{}:{}'.format(target_table, id)
            new_set.add(key)

            # 和旧记录的MD5值比较
            old_md5 = redis_conn.getset(key, new_md5)

            op = 0
            if not old_md5:
                op = 1  # 新增记录
            elif old_md5 != new_md5:
                op = 2  # 记录发生了变化

            if op:
                v = json.dumps({'id': id, 'op': op,'data': new_row}, ensure_ascii=False)
                logger.info('Hit > %s', v)
                # 将变化数据加入redis队列
                redis_conn.lpush(target_table, v)


        # 判定是否有记录被删除
        old_set = set(redis_conn.keys('{}:*'.format(target_table)))
        del_set = old_set ^ new_set
        for k in del_set:
            v = json.dumps({'id': k.split(':')[1], 'op': 3}, ensure_ascii=False)
            logger.info('Hit > %s', v)
            redis_conn.delete(k)
            redis_conn.lpush(target_table, v)

    except:
        logger.exception('Error: unable to fetch data')
    finally:
        cursor.close()
        connection.close()

    # logger.debug(redis_conn.rpop(target_table))
