# -*- coding: utf-8 -*-

""" Implementation of the command line interface.

"""
import os
import sys
import signal
import logging

from argparse import ArgumentParser
from inspect import getfullargspec

from . import __version__
from .api import cmd0, cmd1, cmd2, cmd3
from .api import set_exit_flag
from .core import config
from .core import logger, setupLogging

__all__ = "main",


def main(argv=None):
    """ Execute the application CLI.

    Arguments are taken from sys.argv by default.

    """
    signal.signal(signal.SIGINT, signal_handling)
    signal.signal(signal.SIGTERM, signal_handling)

    args = _args(argv)
    logger.start(args.warn)
    logger.debug("starting execution")
    config.load(args.config)

    os.environ['NLS_LANG'] = config.oracle.nls_lang

    # logger.info('{}'.format(config.entangle))
    
    logger.info('logging config: {}'.format(config.logging.config))
    setupLogging(config.logging.config)


    config.core.logging = args.warn
    command = args.command
    args = vars(args)
    spec = getfullargspec(command)
    if not spec.varkw:
        # No kwargs, remove unexpected arguments.
        args = {key: args[key] for key in args if key in spec.args}
    try:
        command(**args)
    except RuntimeError as err:
        raise
        logger.critical(err)
        return 1
    logger.debug("successful completion")
    return 0
 

def _args(argv=None):
    """ Parse command line arguments.

    """
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", action="append",
            help="config file [etc/config.yml]")
    parser.add_argument("-v", "--version", action="version",
            version="entangle {:s}".format(__version__),
            help="print version and exit")
    parser.add_argument("-w", "--warn", default="DEBUG",
            help="logger warning level [WARN]")
    parser.add_argument("-s", "--history", action="store_true",
                        help="duplicate history data")
    common = ArgumentParser(add_help=False)  # common subcommand arguments
    common.add_argument("--name", "-n", default="World", help="greeting name")
    subparsers = parser.add_subparsers(title="subcommands")
    _cmd0(subparsers, common)
    _cmd3(subparsers, common)
    _cmd1(subparsers, common)
    common.add_argument("--year", "-d", default="None", help="Year of data")
    _cmd2(subparsers, common)
    args = parser.parse_args(argv)
    if not args.config:
        # Don't specify this as an argument default or else it will always be
        # included in the list.
        args.config = "etc/config.yml"
    return args
 

def _cmd0(subparsers, common):
    """ CLI adaptor for the api.cmd0 command.

    """
    parser = subparsers.add_parser("cmd0", parents=[common])
    parser.set_defaults(command=cmd0)
    return


def _cmd1(subparsers, common):
    """ CLI adaptor for the api.cmd1 command.

    """
    parser = subparsers.add_parser("cmd1", parents=[common])
    parser.set_defaults(command=cmd1)
    return


def _cmd2(subparsers, common):
    """ CLI adaptor for the api.cmd2 command.

    """
    parser = subparsers.add_parser("cmd2", parents=[common])
    parser.set_defaults(command=cmd2)
    return


def _cmd3(subparsers, common):
    """ CLI adaptor for the api.cmd3 command.

    """
    parser = subparsers.add_parser("cmd3", parents=[common])
    parser.set_defaults(command=cmd3)
    return


def signal_handling(signum, frame):
    logger.warn('You pressed Ctrl_c to stop me.')
    set_exit_flag(True)
    

# Make the module executable.

if __name__ == "__main__":
    try:
        status = main()
    except:
        logger.critical("shutting down due to fatal error")
        raise  # print stack trace
    else:
        raise SystemExit(status)
