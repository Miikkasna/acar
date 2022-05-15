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
        self.data = []

    def create_data_table(self):
        self.cur.execute('''CREATE TABLE data (testcase INTEGER, iid int NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            loop_time INTEGER, speed REAL, distance REAL, battery_voltage REAL, angle_offset REAL, steering REAL, throttle REAL)''')
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

    def log_data(self, loop_time=None, speed=None, distance=None, battery_voltage=None, angle_offset=None, steering=None, throttle=None):
        if self.batch:
            self.data.append( (self.testcase_id, loop_time, speed, distance, battery_voltage, angle_offset, steering, throttle) )
            if len(self.data)==self.batch_size:
                self.cur.executemany('''INSERT INTO data (testcase, loop_time, speed, distance, battery_voltage, angle_offset, steering, throttle) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', self.data)
                self.data = []
        else:
            data = (self.testcase_id, loop_time, speed, distance, battery_voltage, angle_offset, steering, throttle)
            self.cur.execute('''INSERT INTO data (testcase, loop_time, speed, distance, battery_voltage, angle_offset, steering, throttle) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', data)
        self.con.commit()

