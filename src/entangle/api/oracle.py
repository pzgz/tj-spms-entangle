# -*- coding: utf-8 -*-

import collections
import cx_Oracle

__all__ = "Connection", "Cursor"

class Connection(cx_Oracle.Connection):

    def cursor(self):
        return Cursor(self)


class Cursor(cx_Oracle.Cursor):

    def execute(self, statement, args=None):
        prepareNeeded = (self.statement != statement)
        result = super(Cursor, self).execute(statement, args or [])
        if prepareNeeded:
            description = self.description
            if description:
                # names = [d[0] for d in description]
                # self.rowfactory = collections.namedtuple("GenericQuery", names)
                self.rowfactory = self.__makedict(self)
        return result

    def __makedict(self, cursor):
        cols = [d[0] for d in cursor.description]

        def createrow(*args):
            return dict(zip(cols, args))
        
        return createrow
