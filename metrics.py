import numpy as np
import json
import pygal

class Metrics:
    def __init__(self, n_points):
        self.metrics = dict()
        self.n = n_points
        self.keys = []
        self.img = None
        self.json_charts = None
    
    def add_metric(self, name, unit, ctype, constant=None):
        self.keys.append(name)
        data = np.zeros(self.n)
        self.metrics[name] = {'unit': unit, 'data': data, 'chart_type':ctype, 'constant': constant}

    def update_metric(self, name, value):
        data = np.roll(self.metrics[name]['data'], -1)
        data[-1] = value
        self.metrics[name]['data'] = data

    def plot_metrics(self):
        charts = dict()
        for i, key in enumerate(self.keys):
            if self.metrics[key]['chart_type'] == 'line':
                chart = pygal.Line(height=500,include_x_axis=False,label_font_size=4,
                    title_font_size=26,x_title='semaines',y_title='taux_debit',legend_at_bottom=True,x_label_rotation=90)
                chart._title = key
                chart._y_title = self.metrics[key]['unit']
                chart.add(key, self.metrics[key]['data'])
                if self.metrics[key]['constant'] is not None:
                    chart.add('constant', self.metrics[key]['constant'])
                chart.render_data_uri()
                charts['c' + i] = chart
            self.json_charts = json.dumps(charts, indent = 4)


