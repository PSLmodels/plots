'''
Tax Brain Widget
'''
import glob
import os
import pandas as pd
import numpy as np

from jinja2 import Environment, FileSystemLoader

from bokeh.models import Plot, Range1d, ImageURL
from bokeh.embed import components
from bokeh.models import (ColumnDataSource, LinearAxis, Rect, FactorRange,
                          CategoricalAxis, Line, Text, Square)

from styles import (PLOT_FORMATS,
                    AXIS_FORMATS,
                    FONT_PROPS_SM,
                    GREEN,
                    RED,
                    BLUE)

def output_page(output_path, **kwargs):
    here = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open(output_path, 'w') as output_file:
        output_file.write(content)

def get_data_sources():
    tax_average_bin_cats = reversed(['(-100000000000000, 0]',
                                     '(0, 9999]',
                                     '(9999, 19999]',
                                     '(19999, 29999]',
                                     '(29999, 39999]',
                                     '(39999, 49999]',
                                     '(49999, 74999]',
                                     '(74999, 99999]',
                                     '(99999, 199999]',
                                     '(199999, 499999]',
                                     '(499999, 1000000]',
                                     '(1000000, 100000000000000]'])
    tax_average_bin_cats = list(tax_average_bin_cats)
    files = glob.glob('ds_*_*.csv')
    line_sources = {}
    bar_sources = {}
    for f in files:
        ds_id = os.path.splitext(f)[0]
        df = pd.read_csv(f)

        if '_data' in ds_id:
            df['base'] = df['base'] * 100
            df['reform'] = df['reform'] * 100
            line_sources[ds_id] = ColumnDataSource(df)

        elif '_diff' in ds_id:
            df['bins'] = df['bins'].map(lambda r: tax_average_bin_cats.index(r))
            df['reform_net'] = np.log((df['reform'] - df['base']).values).astype(np.int8)
            bar_sources[ds_id] = ColumnDataSource(df)

    return line_sources, bar_sources

plot_width = 380
plot_height = 250

line_sources, bar_sources = get_data_sources()
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

# create line plot --------------------------------------------------
lines_source = ColumnDataSource(line_sources.values()[0].data)
lines = Plot(plot_width=plot_width,
             plot_height=plot_height,
             x_range=Range1d(0, 100),
             y_range=Range1d(0, 100),
             **PLOT_FORMATS)

lines.add_glyph(logo_source, logo_image)

line_base_renderer = lines.add_glyph(lines_source,
                                     Line(x='index',
                                          y='base',
                                          line_color=BLUE,
                                          line_width=2,
                                          line_alpha=0.8))

lines.add_glyph(lines_source,
                Line(x='index',
                     y='reform',
                     line_color=RED,
                     line_width=2,
                     line_alpha=.8))

lines.add_glyph(Text(x=5.15,
                     y=92.5,
                     text=['baseline'],
                     text_font_size='8pt',
                     text_color='#666666'))

lines.add_glyph(Square(x=3,
                       y=95,
                       fill_color=BLUE,
                       size=10,
                       line_color=None,
                       fill_alpha=0.8))


lines.add_glyph(Text(x=5.15,
                     y=84.75,
                     text=['reform'],
                     text_font_size='8pt',
                     text_color='#666666'))

lines.add_glyph(Square(x=3,
                       y=88,
                       fill_color=RED,
                       size=10,
                       line_color=None,
                       fill_alpha=0.8))


lines.add_layout(LinearAxis(axis_label="Percentiles of Income", **AXIS_FORMATS), 'below')
lines.add_layout(LinearAxis(axis_label="% Itemizing", **AXIS_FORMATS), 'left')

# create bar plot -------------------------------------
PLOT_FORMATS['min_border_bottom'] = 30
bars_source = ColumnDataSource(bar_sources.values()[0].data)
bars = Plot(plot_width=plot_width,
            plot_height=plot_height,
            title='Average Tax',
            x_range=Range1d(0, 10),
            y_range=FactorRange(*tax_average_bin_names),
            **PLOT_FORMATS)

bars.add_glyph(logo_source, logo_image)

bar_base_renderer = bars.add_glyph(bars_source,
                                   Rect(x=0,
                                        y='bins',
                                        height=0.2,
                                        width='reform_net',
                                        fill_color=GREEN,
                                        fill_alpha=0.65,
                                        line_color=None))

# bars.add_layout(LinearAxis(**AXIS_FORMATS), 'below')
bars.add_layout(CategoricalAxis(**AXIS_FORMATS), 'left')

plots = {}
plots['bars_plot'] = bars
plots['line_plot'] = lines

bars_data = {k: v.data for k, v in bar_sources.items()}
lines_data = {k: v.data for k, v in line_sources.items()}

script, divs = components(plots)
output_page('tax-reform-explorer.html',
            bokeh_script=script,
            plots=divs,
            line_plot_id=lines._id,
            line_renderer_id=line_base_renderer._id,
            bar_plot_id=bars._id,
            bar_renderer_id=bar_base_renderer._id,
            bars_data=bars_data,
            lines_data=lines_data)
