# -*- coding: utf-8 -*-

""" Implement the cmd0 command.
    调度模块
"""
import logging
import time
import sched

from pprint import pprint

from . import cmd1, cmd2
from ..core import config
from .glovar import get_exit_flag

logger = logging.getLogger(__name__)

scheduler = sched.scheduler(time.time, time.sleep)


def main(name="Scheduler"):
    """ Execute the command.
    
    """
    logger.debug("executing cmd0 command with %s", name)

    inc = config.core.get('period')
    scheduler.enter(0, 0, perform, (name, inc,))
    scheduler.run()

#enter四个参数分别为：间隔时间、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给他的参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
def perform(name, inc):
    if not get_exit_flag():
        scheduler.enter(inc, 0, perform, (name, inc,))
    else:
        return
    
    logger.info('%s -> %s', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'Starting...')

    for table in config.entangle.keys():
        table_config = config.entangle.get(table)
        mode = table_config.get('mode')
        if mode == 'copy':
            cmd2(table)
        else:
            cmd1(table)

    logger.info('Ended.')
