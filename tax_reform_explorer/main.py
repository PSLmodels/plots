'''
Tax Brain Widget
'''
import os
import pandas as pd
import numpy as np
from numpy.random import randint

from jinja2 import Environment, FileSystemLoader

from bokeh.models import Plot, Range1d, ImageURL
from bokeh.embed import components
from bokeh.models import (ColumnDataSource, LinearAxis, Rect, FactorRange,
                          CategoricalAxis, Line)

from styles import (PLOT_FORMATS,
                    AXIS_FORMATS,
                    RED,
                    BLUE)

plot_width = 400
plot_height = 250

def output_page(output_path, **kwargs):
    here = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open(output_path, 'w') as output_file:
        output_file.write(content)

# ------------------------
def _create_mock_data():

    def _random_source(k):
        df = pd.DataFrame()
        df['average_tax'] = np.random.normal(50000, 10000, 100)
        df['x'] = df.apply(lambda r: randint(0, 100), axis=1)
        df['x1'] = df.apply(lambda r: randint(0, 100), axis=1)
        df['income_percentile'] = pd.Series(list(range(100)))

        # line plot
        baseline_itemized = pd.Series([randint(10, 75) for r in range(100)])
        baseline_itemized.sort()
        df['baseline_itemized'] = baseline_itemized.values

        reform_itemized = pd.Series([randint(10, 75) for r in range(100)])
        reform_itemized.sort()
        df['reform_itemized'] = reform_itemized.values

        # bar plot
        baseline_bars = pd.Series([randint(0, 13) for r in range(100)])
        df['baseline_bars'] = baseline_bars + .125

        reform_bars = pd.Series([randint(0, 13) for r in range(100)])
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

logo_url = 'https://avatars0.githubusercontent.com/u/8301070?v=3&s=200'
logo_source = ColumnDataSource(dict(url=[logo_url], x=[17], y=[.8], w=[100], h=[12]))
logo_image = ImageURL(url="url", x="x", y="y", global_alpha=.05, anchor="bottom_left")

source = ColumnDataSource(data_sources.values()[0].data)

# create line plot --------------------------------------------------
lines = Plot(plot_width=plot_width,
             plot_height=plot_height,
             x_range=Range1d(0, 100),
             y_range=Range1d(0, 100),
             **PLOT_FORMATS)

lines.add_glyph(logo_source, logo_image)

lines.add_glyph(source,
                Line(x='income_percentile',
                     y='baseline_itemized',
                     line_color=BLUE,
                     line_width=2,
                     line_alpha=0.8))

lines.add_glyph(source,
                Line(x='income_percentile',
                     y='reform_itemized',
                     line_color=RED,
                     line_width=2,
                     line_alpha=.8))

lines.add_layout(LinearAxis(axis_label="Percentiles of Income", **AXIS_FORMATS), 'below')
lines.add_layout(LinearAxis(axis_label="% Itemizing", **AXIS_FORMATS), 'left')

# create bar plot -------------------------------------
bars = Plot(plot_width=plot_width,
            plot_height=plot_height,
            title='Average Tax',
            x_range=Range1d(0, 100),
            y_range=FactorRange(*tax_average_bin_names),
            **PLOT_FORMATS)

bars.add_glyph(logo_source, logo_image)

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

# bars.add_layout(LinearAxis(**AXIS_FORMATS), 'below')
bars.add_layout(CategoricalAxis(**AXIS_FORMATS), 'left')

plots = {}
plots['bars_plot'] = bars
plots['line_plot'] = lines

data = {}
for k, v in data_sources.items():
    data[k] = v.data

script, divs = components(plots)
output_page('tax-reform-explorer.html',
            bokeh_script=script,
            plots=divs,
            plot_id=lines._id,
            bokeh_data=data)
