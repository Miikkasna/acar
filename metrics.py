import numpy as np
import matplotlib.pyplot as plt
import cv2

class Metrics:
    def __init__(self, n_points):
        self.metrics = dict()
        self.n = n_points
        self.keys = []
        self.interval = 1.0
        self.last_time = 0
        self.img = None
    
    def add_metric(self, name, unit):
        self.keys.append(name)
        data = np.zeros(self.n)
        self.metrics[name] = {'unit': unit, 'data': data}

    def update_metric(self, name, value):
        data = np.roll(self.metrics[name]['data'], -1)
        data[-1] = value
        self.metrics[name]['data'] = data

    def plot_metrics(self, time):
        if time - self.last_time > self.interval:
            n = len(self.keys)
            fig, axs = plt.subplots(2, n, constrained_layout=True)
            for i in range(n):
                if i > 2:
                    r = 1
                else:
                    r = 0
                axs[r, i].plot(self.metrics[self.keys[i]]['data'])
                axs[r, i].set_title(self.keys[i])
                axs[r, i].set_ylabel(self.metrics[self.keys[i]]['unit'])
            plt.savefig('test.png')
            plt.close()
            self.img = cv2.imread('test.png')
            self.last_time = time


