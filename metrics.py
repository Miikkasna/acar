import numpy as np
import json

class Metrics:
    def __init__(self, n_points, apx_loop_time=0.1):
        self.metrics = dict()
        self.n = n_points
        self.keys = []
        self.json_charts = None
        time_span = round(apx_loop_time*n_points, 1)
        self.x_title = 'last {} seconds'.format(time_span)

    def add_metric(self, title, xaxis={'range':[0, 10], 'title':''}, yaxis={'range':[0, 10], 'title':''}, stack=False):
        self.keys.append(title)
        if stack:
            layout = {'xaxis':xaxis, 'yaxis':yaxis, 'title':title, 'barmode':'stack'}
        else:
            layout = {'xaxis':xaxis, 'yaxis':yaxis, 'title':title}
        self.metrics[title] = {'series':[], 'layout':layout}

    def add_series(self, title, name, ctype, constant=0):
        datay = list(np.zeros(self.n) + constant)
        datax = list(range(1, self.n+1))
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


