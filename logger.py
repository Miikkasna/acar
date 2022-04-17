import mysql.connector
import time
import random
from datetime import datetime
from dbparams import pi_user, database


class DB_logger():
    def __init__(self):
        self.con = mysql.connector.connect(
            host=pi_user.host,
            user=pi_user.user,
            password=pi_user.password,
            database=database
        )
        self.cur = con.cursor()
    def create_performance_table(self):
        cur.execute('''CREATE TABLE performance (testcase INTEGER, iid int NOT NULL AUTO_INCREMENT PRIMARY KEY, ms INTEGER)''')
        self.con.commit()
    def create_testcases_table(self):
        cur.execute('''CREATE TABLE testcases (testcase int NOT NULL AUTO_INCREMENT PRIMARY KEY, test_stamp VARCHAR(300))''')
        self.con.commit()
    def set_new_testcase(self, stamp)
        cur.execute('''INSERT INTO testcases (test_stamp) VALUES (%s)''', (stamp, ))
        con.commit()
        cur.execute('''SELECT testcase, test_stamp FROM testcases ORDER BY testcase DESC LIMIT 1''')
        testcase_id, _ = cur.fetchone()
        print('testcase: ', testcase_id)
        self.testcase_id = testcase_id
    def log_performance(self, test_interval, batch=False):
        if batch:
            cur.executemany('''INSERT INTO performance (testcase, ms) VALUES (%s, %s)''', test_interval)
        else:
            cur.execute('''INSERT INTO performance (testcase, ms) VALUES (%s, %s)''', test_interval)
        con.commit()
    def get_performances(self, limit=None)
        if limit is None:
            cur.execute('''SELECT ms FROM performance WHERE testcase = {}'''.format(self.testcase_id))
        else:
            cur.execute('''SELECT ms FROM performance WHERE testcase = {} ORDER BY  LIMIT {}'''.format(self.testcase_id, limit))
        rows = cur.fetchall()
        return rows
