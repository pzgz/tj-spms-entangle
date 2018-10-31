""" Application commands common to all interfaces.

"""
from .cmd1 import main as cmd1
from .cmd3 import main as cmd3
from .cmd2 import main as cmd2
from .cmd0 import main as cmd0

from .resource import get_mysql_connection
from .resource import get_oracle_connection
from .resource import get_redis_connection

from .glovar import get_exit_flag
from .glovar import set_exit_flag


__all__ = "cmd0", "cmd1", "cmd2", "cmd3", "get_mysql_connection", "get_oracle_connection", "get_redis_connection", "get_exit_flag", "set_exit_flag"
