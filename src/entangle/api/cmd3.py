
# -*- coding: utf-8 -*-

""" Implement the cmd3 command.

"""
import logging
import json
import time
import arrow
import threading
import redis

import cx_Oracle

from pprint import pprint
from enum import Enum

from ..core import config
from .resource import get_redis_connection, get_mysql_connection, get_oracle_connection
from .glovar import get_exit_flag

logger = logging.getLogger(__name__)

spms_to_finance_entities_config = None
queue = "exchange:s2f"
backup_queue = '{}:backup'.format(queue)
redis_conn = None

SQL = Enum('SQL', ('UPSERT','MSGID'))
SYNCMODE = Enum('SYNMODE', ('INCREMENT','COPY'))

sync_point = dict()

def main(name="World"):
    """ Execute the command.
    
    """
    global queue
    global backup_queue
    global redis_conn
    global spms_to_finance_entities_config
    
    spms_to_finance_entities_config = config.spms_to_finance.get('entities')
    if config.spms_to_finance.get('real_time_queue'):
        queue = config.spms_to_finance.get('real_time_queue')
        backup_queue = '{}:backup'.format(queue)

    redis_conn = get_redis_connection()

    logger.debug("executing cmd3 command with %s", name)
    _handleBackupQueue()
    _handleQueue()


def _handleQueue():
    logger.info('Starting listener %s...', queue)
    t0 = arrow.now().timestamp - 290
    while not get_exit_flag():
        try:
            message = redis_conn.brpoplpush(queue, backup_queue, 10)
        except redis.RedisError as err:
            logger.error(err)
            time.sleep(10)
        else:
            if message:
                _process_message(message)
            else:
                t1 = arrow.now().timestamp
                if t1 - t0 >= 300: # 5分钟检查全量同步队列
                    _copy_message()
                    t0 = t1
                else:
                    logger.debug('nothing.')

    logger.info('Exit listener %s.', queue)


def _copy_message():
    try:
        for queue in config.spms_to_finance.get('fixed_time_queues'):
            message = redis_conn.get(queue)
            if message:
                _process_message(message, SYNCMODE.COPY)
    except redis.RedisError as err:
        logger.error(err)


def _process_message(message, mode=SYNCMODE.INCREMENT):
    switcher = {
        'project': _on_project,
        'budgets': _on_budgets,
        'fund_item': _on_fund_item,
        'category': _on_category,
        't_zzgl_xzjg': _on_t_zzgl_xzjg,
    }
    try:        
        msg = json.loads(message)
        entity = msg.get('entity')

        hit_flag = True
        if mode == SYNCMODE.COPY:
            updated_at = msg.get('updated_at')
            last_updated_at = sync_point.get(entity, -1)
            if updated_at > last_updated_at:
                sync_point[entity] = updated_at
            else:
                hit_flag = False            

        if hit_flag:
            logger.info('Hit %s', message)
            handler = switcher.get(entity, _on_miss)
            handler(msg)
    except ValueError as err:
        # 消息格式（JSON）错误
        logger.error('无效的消息: %s', message)
        redis_conn.lrem(backup_queue, 1, message) if mode == SYNCMODE.INCREMENT else None
    except Exception as err:
        logger.exception(err)
        # 消息处理出错了，消息仍然留在backup队列中，backup队列监听器会将消息扔回queue中，重新处理
    else:
        # 消息处理成功，将其从backup queue中删除
        redis_conn.lrem(backup_queue, 1, message) if mode == SYNCMODE.INCREMENT else None
        # 但是，如果业务处理时间过长（超过timeout时间），可能导致这条消息在backup队列存在较长时间，
        # backup队列监听器会将消息扔回queu中，但实际上消息已经被处理，结果是消息被重复处理

def _map_message(entity, data):
    _config = spms_to_finance_entities_config.get(entity)
    new_row = {'m_id':data.get('m_id'), 'last_ver':data.get('last_ver')}

    for _new, _origin  in _config.get('fields').items():
        origin_value = data.get(_origin)
        new_row[_new] = origin_value
    
    return new_row

    
def _on_project(message):
    data = message.get('data')
    data['m_id'] = message.get('id')
    data['last_ver'] = _to_date(message.get('created_at'))

    data['_start_year'] = data.get('setup_date')[0:4]    
    data['_end_year'] = data.get('end_date')[0:4]    
    # data['start_date'] = _to_date(data.get('start_date'))
    # data['end_date'] = _to_date(data.get('end_date'))
    # data['setup_date'] = _to_date(data.get('setup_date'))
    # data['updated_at'] = _to_date(data.get('updated_at'))
    # data['is_local_card'] = 'Y' if data.get('is_local_card') else 'N'   
    entity = message.get('entity')
    rows = [_map_message(entity, data)] 

    _save_message(entity, rows)


def _on_fund_item(message):
    data = message.get('data')
    data['fund_no'] = str(data.get('fund_no'))
    data['card_close_at'] = _to_date(data.get('card_close_at'))

    data['m_id'] = message.get('id')
    data['last_ver'] = _to_date(message.get('created_at'))

    entity = message.get('entity')
    rows = [_map_message(entity, data)] 
    _save_message(entity, rows)


def _on_budgets(message):
    entity = message.get('entity')
    m_id = message.get('id')
    m_created_at = _to_date(message.get('created_at'))    
    data = message.get('data')
    budgets = data.get('budgets')
    rows = []
    for budget in budgets:
        budget['m_id'] = m_id
        budget['last_ver'] = m_created_at
        budget['project_no'] = data.get('project_no')
        budget['card_no'] = data.get('card_no')
        _budget = _map_message(entity, budget)

        # josn数据中，属性plan_amt偶尔会有string类型的值,例如“3.1”
        amount = _budget.get('plan_amt')
        _budget['plan_amt'] = amount if isinstance(amount, (int, float)) else float(amount)
        
        rows.append(_budget)

    _save_message(entity, rows)


def _on_category(message):
    entity = message.get('entity')    
    m_id = message.get('updated_at')
    m_created_at = _to_date(m_id)
    _type = dict()
    rows = []
    for category in message.get('categories'):
        category['m_id'] = m_id
        category['last_ver'] = m_created_at
        category['parent_code'] = '*'
        category['project_type'] = str(category.get('project_type'))
        _type[category.get('code')] = category.get('project_type')
        rows.append(_map_message(entity, category))
    for category in message.get('sub_categories'):
        category['m_id'] = m_id
        category['last_ver'] = m_created_at
        category['project_type'] = _type.get(category.get('parent_code'))
        rows.append(_map_message(entity, category))

    _save_message(entity, rows)

def _on_t_zzgl_xzjg(message):
    entity = message.get('entity')    
    m_id = message.get('updated_at')
    m_created_at = _to_date(m_id)
    rows = []
    for row in message.get('data'):
        row['m_id'] = m_id
        row['last_ver'] = m_created_at
        rows.append(_map_message(entity, row))

    _save_message(entity, rows)


def _on_miss(message):
    logger.warn('No implement for entity: %s.', message.get('entity'))


def _save_message(entity, rows):
    if rows:
        mid = _get_message_id(entity, rows[0])
        if mid < rows[0].get('m_id'):
            sql = _get_statement(entity)
            db = get_oracle_connection()
            db.autocommit = False
            cursor = db.cursor()
            db.begin()
            try:
                if len(rows) > 1:
                    cursor.executemany(sql[0], rows)
                else:
                    cursor.execute(sql[0], rows[0])
            except cx_Oracle.DatabaseError as err:
                db.rollback()
                raise
            else:
                db.commit()
            finally:
                cursor.close()
        else:
            logger.warn('Discard message: %s', rows)


def _get_message_id(entity, data):
    sql = _get_statement(entity, SQL.MSGID)
    pk = sql[1]
    args = { k:v for (k,v) in data.items() if k in pk}
    conn = get_oracle_connection()
    cursor = conn.cursor()
    cursor.execute(sql[0], args)
    row = cursor.fetchone()
    cursor.close()
    conn.commit()
    return row.get('M_ID') if row else -1


def _get_statement(entity, sql=SQL.UPSERT):
    _config = spms_to_finance_entities_config.get(entity)
    fields = list(map(lambda x: x.lower(), _config.get('fields').keys())) + ['m_id', 'last_ver']
    pk = list(map(lambda x: x.lower(), _config.get('pk')))
    update_sql = _config.get('update_sql')
    get_message_id_sql = _config.get('get_message_id_sql')
    if not update_sql:
        non_pk_fields = list(set(fields).difference(set(pk)))

        get_message_id_sql = 'select m_id from {} where {}'.format(
            _config.get('target'),
            ' AND '.join(list(map(lambda x: '{}=:{}'.format(x, x), pk)))
        )

        update_sql = '''
            merge into {} t using dual on ({})  
                when not matched then insert ({}) values ({})  
                when matched then update set {}  
        '''.format(
            _config.get('target'),
            ' AND '.join(list(map(lambda x: 't.{}=:{}'.format(x, x), pk))),
            ','.join(fields),
            ','.join(list(map(lambda x: ':{}'.format(x), fields))),
            ','.join(list(map(lambda x: '{}=:{}'.format(x, x), non_pk_fields)))
        )
        _config['update_sql'] = update_sql
        _config['get_message_id_sql'] = get_message_id_sql
        logger.debug('%s - sql1 = %s', entity, get_message_id_sql)
        logger.debug('%s - sql2 = %s', entity, update_sql)

    return (update_sql,fields) if sql == SQL.UPSERT else (get_message_id_sql, pk)


def _to_date(src_date):
    if src_date:
        try:
            target_date = arrow.get(src_date).to('local').datetime
        except arrow.parser.ParserError:
            return None
        else:
            return target_date
    else:
        return None

def _handleBackupQueue():
    handler = BackupQueueHandler(1, queue)
    handler.start()
    # handler.join()

class BackupQueueHandler(threading.Thread):
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.__queue = queue
        self.__backup_queue = '{}:backup'.format(queue)
        self.__redis = get_redis_connection()

    def run(self):
        logger.info('Starting listener %s...', self.__backup_queue)
        while not get_exit_flag():
            try:
                rows = self.__redis.lrange(self.__backup_queue, -1, -1)
                message = rows[0] if rows else None
                if message:
                    # 先判定backup队列中这条最老的message是否超时,
                    # 超时表示在正常处理中遇到问题，将其扔回queue中重新处理
                    logger.warn('retry %s...', message)
                    pipe = self.__redis.pipeline(transaction=True)
                    pipe.watch(self.__queue, self.__backup_queue)
                    pipe.multi()
                    pipe.lrem(self.__backup_queue, 1, message)
                    pipe.lpush(self.__queue, message)
                    pipe.execute()
                else:
                    pass
                    # logger.debug('empty.')
            except redis.WatchError as err:
                logger.error(err)
                pipe.unwatch()
            except redis.RedisError as err:
                logger.error(err)
                pipe.unwatch()
            finally:
                time.sleep(5)           

        logger.info('Exit listener %s.', self.__backup_queue)
