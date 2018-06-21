""" Application commands common to all interfaces.

"""
from .cmd1 import main as cmd1
from .cmd2 import main as cmd2

from .resource import  get_mysql_connection
from .resource import get_redis_connection


__all__ = "cmd1", "cmd2", "get_mysql_connection", "get_redis_connection"
