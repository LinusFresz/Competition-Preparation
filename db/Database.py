#!/usr/bin/python

import pymysql, sys
from pymysql.cursors import Cursor


class Database:
    def __init__(self, db: str, host: str, user: str, passwd: str, port: int = 3306, socket: str = None):
        if socket is None:
            try: 
                self.cnx = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, autocommit=True)
            except pymysql.Error as error:
                print('An error occured while connecting to the WCA database:')
                print(error)
                print('\n Script aborted.')
                sys.exit()
        else:
            try:
                self.cnx = pymysql.connect(host=host, unix_socket=socket, user=user, passwd=passwd, db=db, autocommit=True)
            except pymysql.Error as error:
                print('An error occured while connecting to the WCA database:')
                print(error)
                print('\n Script aborted.')
                sys.exit()

    def begin_transaction(self):
        self.cnx.autocommit(False)

    def commit(self):
        self.cnx.commit()
        self.cnx.autocommit(True)

    def query(self, query: str, args=None) -> Cursor:
        cursor = self.cnx.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, args)

        return cursor
