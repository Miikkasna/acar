import mysql.connector
from dbparams import pi_user, database
from datetime import datetime


class DB_logger():
    
    def __init__(self, batch=False, batch_size=100):
        self.con = mysql.connector.connect(
            host=pi_user.host,
            user=pi_user.user,
            password=pi_user.password,
            database=database
        )
        self.cur = self.con.cursor()
        self.batch_size=batch_size
        self.batch = batch
        self.test_intervals = []

    def create_performance_table(self):
        self.cur.execute('''CREATE TABLE performance (testcase INTEGER, iid int NOT NULL AUTO_INCREMENT PRIMARY KEY, ms INTEGER)''')
        self.con.commit()

    def create_testcases_table(self):
        self.cur.execute('''CREATE TABLE testcases (testcase int NOT NULL AUTO_INCREMENT PRIMARY KEY, test_stamp VARCHAR(300))''')
        self.con.commit()

    def set_new_testcase(self):
        self.cur.execute('''INSERT INTO testcases (test_stamp) VALUES (%s)''', (str(datetime.now()), ))
        self.con.commit()
        self.cur.execute('''SELECT testcase, test_stamp FROM testcases ORDER BY testcase DESC LIMIT 1''')
        self.testcase_id, self.test_stamp = self.cur.fetchone()
        print('testcase: ', self.testcase_id)

    def log_performance(self, interval):
        if self.batch:
            self.test_intervals.append( (self.testcase_id, interval) )
            if len(self.test_intervals)==self.batch_size:
                self.cur.executemany('''INSERT INTO performance (testcase, ms) VALUES (%s, %s)''', self.test_intervals)
                self.test_intervals = []
        else:
            test_interval = (self.testcase_id, interval)
            self.cur.execute('''INSERT INTO performance (testcase, ms) VALUES (%s, %s)''', test_interval)
        self.con.commit()

    def get_performances(self, limit=None):
        if limit is None:
            self.cur.execute('''SELECT ms FROM performance WHERE testcase = {}'''.format(self.testcase_id))
        else:
            self.cur.execute('''SELECT ms FROM performance WHERE testcase = {} ORDER BY  LIMIT {}'''.format(self.testcase_id, limit))
        rows = self.cur.fetchall()
        return rows
