import mysql.connector
from dbparams import win_user, database
import time
import random
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


def connect():
	con = mysql.connector.connect(
        host=win_user.host,
        user=win_user.user,
        password=win_user.password,
        database=database
    )
	return con

<<<<<<< HEAD
with con:
	while True:
		try:
			cur = con.cursor()
			cur.execute('''SELECT iid, ms FROM performance WHERE testcase = {} ORDER BY iid DESC LIMIT 100'''.format(520))
			rows = np.array(cur.fetchall())
			ids = np.flip(rows[:, 0])
			ms = np.flip(rows[:, 1])
			plt.cla()
			plt.plot(ids, ms)
			plt.ylim([0, 200])
			plt.pause(1.5)
		except:
			time.sleep(1.0)
			pass



#print(ms.mean(), ms.std(), ms.max(), ms.min())