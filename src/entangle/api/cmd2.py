""" Implement the cmd2 command.

"""
import logging
import time
import sched

from . import cmd1
from ..core import config

logger = logging.getLogger(__name__)

scheduler = sched.scheduler(time.time, time.sleep)

def main(name="World"):
    """ Execute the command.
    
    """
    logger.debug("executing cmd2 command with %s", name)
    mymain(name, 60)


#enter四个参数分别为：间隔时间、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给他的参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
def perform(name, inc):
    scheduler.enter(inc, 0, perform, (name, inc,))
    doit('Starting...')
    for table in config.entangle.keys():
        cmd1(table)
    doit('Ended.')


def mymain(name, inc=10):
    scheduler.enter(0, 0, perform, (name, inc,))
    scheduler.run()


def doit(action):
    logger.info('%s -> %s', time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime()), action)

