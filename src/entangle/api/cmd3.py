
# -*- coding: utf-8 -*-

""" Implement the cmd2 command.

"""
import logging
import time
import threading
import redis

from pprint import pprint

from ..core import config
from .resource import get_redis_connection, get_mysql_connection, get_oracle_connection
from .glovar import get_exit_flag

logger = logging.getLogger(__name__)

queue = "spms:out"
backup_queue = '{}:backup'.format(queue)
redis_conn = None

def main(name="World"):
    """ Execute the command.
    
    """
    global queue
    global backup_queue
    global redis_conn

    if config.core.get('out_queue'):
        queue = config.core.get('out_queue')
        backup_queue = '{}:backup'.format(queue)

    redis_conn = get_redis_connection()

    logger.debug("executing cmd3 command with %s", name)
    _handleBackupQueue()
    _handleQueue()


def _handleQueue():
    logger.info('Starting listener %s...', queue)
    while not get_exit_flag():
        try:
            message = redis_conn.brpoplpush(queue, backup_queue, 10)
        except Exception as err:
            logger.error(err)
            time.sleep(5)
        else:
            _process_message(message)
        finally:
            pass

    logger.info('Exit listener %s.', queue)

count = 0

def _process_message(message=None):
    global count
    try:
        count = count + 1
        if message == 'error' and count % 3 == 0:
            raise Exception('failure to write db.')
        else:
            logger.debug('No.%d = [%s]', count, message)
    except Exception as err:
        logger.error(err)
        # 消息处理出错了，消息仍然留在backup队列中，backup队列监听器会将消息扔回queue中，重新处理
        # redis_connection.lpush(self.name, message)
    else:
        # 消息处理成功，将其从backup queue中删除
        redis_conn.lrem(backup_queue, 1, message)
        # 但是，如果业务处理时间过长（超过timeout时间），可能导致这条消息在backup队列存在较长时间，
        # backup队列监听器会将消息扔回queu中，但实际上消息已经被处理，结果是消息被重复处理


def _handleBackupQueue():
    handler = BackupQueueHandler(1, queue)
    handler.start()
    # handler.join()


class BackupQueueHandler(threading.Thread):
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.queu = queue
        self.backup_queue = '{}:backup'.format(queue)

    def run(self):
        logger.info('Starting listener %s...', self.backup_queue)
        conn = get_redis_connection()
        while not get_exit_flag():
            try:
                rows = conn.lrange(self.backup_queue, -1, -1)
                message = rows[0] if rows else None
                if message:
                    # 先判定backup队列中这条最老的message是否超时,
                    # 超时表示在正常处理中遇到问题，将其扔回queue中重新处理
                    logger.warn('retry %s...', message)
                    pipe = conn.pipeline(transaction=True)
                    pipe.watch(queue, backup_queue)
                    pipe.multi()
                    pipe.lrem(backup_queue, 1, message)
                    pipe.lpush(queue, message)
                    pipe.execute()
                else:
                    logger.debug('empty.')
            except redis.exceptions.WatchError as ex:
                logger.error(ex)
                pipe.unwatch()
            except redis.exceptions.RedisError as err:
                logger.error(err)
                pipe.unwatch()
            finally:
                time.sleep(5)           

        logger.info('Exit listener %s.', self.backup_queue)
