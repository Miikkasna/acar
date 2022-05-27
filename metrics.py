import numpy as np
import json

class Metrics:
    def __init__(self):
        self.metrics = dict()
        self.keys = []
        self.n_points = {}
        self.json_charts = None


    def add_metric(self, title, n_points=10, xaxis={'range':[0, 10], 'title':''}, yaxis={'range':[0, 10], 'title':''}, stack=False):
        self.keys.append(title)
        self.n_points[title] = n_points
        if stack:
            layout = {'xaxis':xaxis, 'yaxis':yaxis, 'title':title, 'barmode':'stack'}
        else:
            layout = {'xaxis':xaxis, 'yaxis':yaxis, 'title':title}
        self.metrics[title] = {'series':[], 'layout':layout}

    def add_series(self, title, name, ctype, constant=0):
        n = self.metrics[title]['layout']
        datay = list(np.zeros(self.n_points[title]) + constant)
        datax = list(range(1, self.n_points[title]+1))
        self.metrics[title]['series'].append({'y': datay, 'x':datax, 'type':ctype, 'name':name})

    def update_metric(self, title, value, series_number=0):
        data = np.roll(self.metrics[title]['series'][series_number]['y'], -1)
        data[-1] = value
        self.metrics[title]['series'][series_number]['y'] = list(data)

    def update_chart_data(self):
        data = dict()
        for i, key in enumerate(self.keys):
            data['c' + str(i+1)] = self.metrics[key]
        charts = json.dumps(data, indent = 4)
        self.json_charts = charts


