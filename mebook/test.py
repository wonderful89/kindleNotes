#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import re

arr = ["aaa", "bbb", 333]
import sqlite3


class dbOperation(object):
    def __init__(self, dbFile="moehui.db"):
        self.__tableName = ""
        if not dbFile:
            print("Database Not Found.Exiting...")
        self.dbConn = sqlite3.connect(dbFile)
        if not self.dbConn:
            print("Can not connect to databse,Exiting...")
        self.dbCursor = self.dbConn.cursor()
        if not self.dbCursor:
            print("Can not get databse cursor,Exiting...")
        print("Databse Initilized.")

    def createTable(self, tableName="ImageRepo"):
        self.__tableName = tableName
        sql = """CREATE TABLE IF NOT EXISTS`%s` (
            `Name`	TEXT NOT NULL, \
            `PanLink`	TEXT,
            `PanPwd`	TEXT,
            `isTransfered`	INTEGER
        );"""
        sql2 = sql % tableName
        self.dbCursor.execute(sql2)
        self.dbConn.commit()

    def insert(self, name, link, pwd, isTransfered=0):
        sql = """INSERT INTO %s (Name,PanLink,PanPwd,isTransfered) VALUES ('%s', '%s', 
        '%s', %d)"""
        sql2 = sql % (self.__tableName, name, link, pwd, isTransfered)
        print("sql2 = {}".format(sql2))
        self.dbCursor.execute(sql2)
        self.dbConn.commit()


def test():
    print("in test")
    db = dbOperation()
    db.createTable()
    db.insert("xxx1", "http://baidu.com", "123")
    db.insert("xxx122", "http://baidu.com", "456", 1)


test()
