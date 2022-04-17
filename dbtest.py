import mysql.connector
import time
import random
from datetime import datetime

con = mysql.connector.connect(
  host="localhost",
  user="pi",
  password="pi",
  database="acar"
)

cur = con.cursor()
cur.execute('''CREATE TABLE performance (testcase INTEGER, iid int NOT NULL AUTO_INCREMENT PRIMARY KEY, ms INTEGER)''')
cur.execute('''CREATE TABLE testcases (testcase int NOT NULL AUTO_INCREMENT PRIMARY KEY, test_stamp VARCHAR(300))''')
con.commit()

stamp = str(datetime.now())
cur.execute('''INSERT INTO testcases (test_stamp) VALUES (%s)''', (stamp, ))
con.commit()
cur.execute('''SELECT testcase, test_stamp FROM testcases ORDER BY testcase DESC LIMIT 1''')
iid, _ = cur.fetchone()
print('testcase: ', iid)
last_time = time.time()
intervals = []
for i in range(50):
    time.sleep(0.1 + random.random()/10.0)
    
    interval = time.time() - last_time
    last_time = time.time()
    intervals.append((iid, int(interval*1000)))
    
    if len(intervals) ==10:
        cur.executemany('''INSERT INTO performance (testcase, ms) VALUES (%s, %s)''', intervals)
        con.commit()
        intervals = []

cur.execute('''SELECT ms FROM performance WHERE testcase = {}'''.format(iid))
rows = cur.fetchall()
print(rows)
print('done')