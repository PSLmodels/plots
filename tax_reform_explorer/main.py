'''
Tax Brain Widget
'''
import pandas as pd
import numpy as np
from numpy.random import normal, randint

from pdb import set_trace


from bokeh.models import Plot, ColumnDataSource, Range1d, Rect, Line
from bokeh.io import output_file
from bokeh.plotting import show
from bokeh.models import (ColumnDataSource, CustomJS, HoverTool,
                          Range1d, Plot, LinearAxis, Rect, FactorRange,
                          CategoricalAxis, DatetimeAxis, Line, DataRange1d,
                          MultiLine, Text, Circle, VBox, Slider)

from models import IonRangeSlider

from styles import (DATETIME_FORMAT,
                    PLOT_FORMATS,
                    AXIS_FORMATS,
                    LINE_FORMATS,
                    FONT_PROPS_SM,
                    RED,
                    BLUE)

plot_width = 400
plot_height = 250

# ------------------------
def _create_mock_data():

    def _random_source(k):
        df = pd.DataFrame()
        df['average_tax'] = np.random.normal(50000, 10000, 100)
        df['x'] = df.apply(lambda r: randint(0, 100), axis=1)
        df['x1'] = df.apply(lambda r: randint(0, 100), axis=1)
        df['income_percentile'] = pd.Series(list(range(100)))
    
        # line plot
        baseline_itemized = pd.Series([randint(10,75) for r in range(100)])
        baseline_itemized.sort(inplace=True)
        df['baseline_itemized'] = baseline_itemized

        reform_itemized = pd.Series([randint(10,75) for r in range(100)])
        reform_itemized.sort(inplace=True)
        df['reform_itemized'] = reform_itemized

        # bar plot ---------------------
        baseline_bars = pd.Series([randint(0,13) for r in range(100)])
        baseline_bars.sort(inplace=True)
        df['baseline_bars'] = baseline_bars + .125

        reform_bars = pd.Series([randint(0,13) for r in range(100)])
        reform_bars.sort(inplace=True)
        df['reform_bars'] = reform_bars - .125

        return ColumnDataSource(df)

    groups = []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                groups.append((str(i), str(j), str(k)))

    groups = ['ds_' + ''.join(g) for g in groups]
    column_data_sources = map(_random_source, list(range(len(groups))))
    return dict(zip(groups, column_data_sources))

# ------------------------

def get_data_sources():
    # TODO: replace with actual data...
    return _create_mock_data()

data_sources = get_data_sources()

tax_average_bin_names = reversed(['Less than 10',
                         '10 - 20',
                         '20 - 30',
                         '30 - 40',
                         '40 - 50',
                         '50 - 75',
                         '75 - 100',
                         '100 - 200',
                         '200 - 500',
                         '500 - 1000',
                         '1000+',
                         'All'])

slider1 = Slider(title="Mortage & Other Interest Paid Deduction",
                  value=0, start=0, end=2, step=1)

slider2 = Slider(title="State & Local Tax Deduction",
                  value=0, start=0, end=2, step=1)

slider3 = Slider(title="Charitable Contribution",
                  value=0, start=0, end=2, step=1)

source = ColumnDataSource(data_sources.values()[0].data)

# create line plot --------------------------------------------------
lines = Plot(plot_width=plot_width,
            plot_height=plot_height,
            x_range=Range1d(0, 100),
            y_range=Range1d(0, 100),
            **PLOT_FORMATS)

lines.add_glyph(source,
               Line(x='income_percentile',
                    y='baseline_itemized',
                    line_color=BLUE,
                    line_alpha=0.8))

lines.add_glyph(source,
               Line(x='income_percentile',
                    y='reform_itemized',
                    line_color=RED,
                    line_alpha=.5))

lines.add_layout(LinearAxis(axis_label="Percentiles of Income", **AXIS_FORMATS), 'below')
lines.add_layout(LinearAxis(axis_label="% Itemizing", **AXIS_FORMATS), 'left')

# create bar plot -------------------------------------
bars = Plot(plot_width=plot_width,
            plot_height=plot_height,
            title='Average Tax',
            x_range=Range1d(0, 100),
            y_range=FactorRange(*tax_average_bin_names),
            **PLOT_FORMATS)

bars.add_glyph(source,
               Rect(x='x',
                    y='baseline_bars',
                    height=0.2,
                    width=100,
                    fill_color=BLUE,
                    fill_alpha=0.8,
                    line_color=None))

bars.add_glyph(source,
               Rect(x='x1',
                    y='reform_bars',
                    height=0.2,
                    width=100,
                    fill_color=RED,
                    fill_alpha=1,
                    line_color=None))

#bars.add_layout(LinearAxis(**AXIS_FORMATS), 'below')
bars.add_layout(CategoricalAxis(**AXIS_FORMATS), 'left')

# wire up for interactivity ------------------------
layout = VBox(width=plot_width, children=[slider1, slider2, slider3, lines, bars])

data_sources['slider1'] = slider1
data_sources['slider2'] = slider2
data_sources['slider3'] = slider3
data_sources['source'] = source

jscode="""
source_id = 'ds_';
source_id += slider1.get('value').toString();
source_id += slider2.get('value').toString();
source_id += slider3.get('value').toString();

var new_data = eval(source_id).get('data')
source.set('data', new_data)

"""

slider1.callback = CustomJS(args=data_sources, code=jscode)
slider2.callback = CustomJS(args=data_sources, code=jscode)
slider3.callback = CustomJS(args=data_sources, code=jscode)

output_file('tax-reform-explorer.html')
show(layout)
