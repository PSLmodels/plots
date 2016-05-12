'''
Tax Brain Widget
'''
import glob
import locale
import numpy as np
import os
import pandas as pd

from jinja2 import Environment, FileSystemLoader

from bokeh.models import Plot, Range1d, ImageURL, DataRange1d
from bokeh.embed import components
from bokeh.models import (ColumnDataSource, LogAxis, LinearAxis, Rect, FactorRange,
                          CategoricalAxis, Line, Text, Square, HoverTool)

from styles import (PLOT_FORMATS,
                    AXIS_FORMATS,
                    FONT_PROPS_SM,
                    DARK_GRAY,
                    GREEN,
                    PURPLE,
                    RED,
                    BLUE)

locale.setlocale(locale.LC_ALL, 'en_US')

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
            net = np.maximum(df['reform'] - df['base'], 1)
            df['reform_net'] = np.nan_to_num(np.sign(net) * np.log(np.abs(net)))
            df['color'] = np.where(df['reform_net'].values >= 0, GREEN, PURPLE)
            df['width'] = np.abs(df['reform_net'] * 2) # bokeh drawing from center

            annotation_func = lambda r:'$' + locale.format('%d', float(r['reform'] - r['base']), grouping=True)
            df['annotation'] = df.apply(annotation_func, axis=1)
            df['annotation_y'] = df.apply(lambda r:r['bins'] - .38, axis=1)
            df['annotation_x'] = df.apply(lambda r:max(.1, r['width'] / 2), axis=1)
            bar_sources[ds_id] = ColumnDataSource(df)

    return line_sources, bar_sources


plot_width = 425
plot_height = 250

line_sources, bar_sources = get_data_sources()
tax_average_bin_names = reversed(['Less than 10k',
                                  '10k - 20k',
                                  '20k - 30k',
                                  '30k - 40k',
                                  '40k - 50k',
                                  '50k - 75k',
                                  '75k - 100k',
                                  '100k - 200k',
                                  '200k - 500k',
                                  '500k - 1M',
                                  '1M+',
                                  'All'])

logo_url = 'https://avatars0.githubusercontent.com/u/8301070?v=3&s=200'
logo_source = ColumnDataSource(dict(url=[logo_url], x=[17], y=[.8], w=[100], h=[12]))
logo_image = ImageURL(url="url", x="x", y="y", global_alpha=.05, anchor="bottom_left")

# create line plot --------------------------------------------------
lines_source = ColumnDataSource(line_sources['ds_000_data'].data)
lines = Plot(plot_width=plot_width,
             plot_height=plot_height,
             title='Percent Itemizing by Income Percentile',
             x_range=Range1d(0, 100),
             y_range=Range1d(0, 100),
             **PLOT_FORMATS)

lines.add_glyph(logo_source, logo_image)

lines.add_glyph(lines_source,
                Line(x='index',
                     y='reform',
                     line_color=RED,
                     line_width=2,
                     line_alpha=.8))

line_base_renderer = lines.add_glyph(lines_source,
                                     Line(x='index',
                                          y='base',
                                          line_color=BLUE,
                                          line_width=2,
                                          line_alpha=1))


lines.add_glyph(Text(x=5.15,
                     y=92,
                     text_font_style='italic',
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
                     text_font_style='italic',
                     text=['reform'],
                     text_font_size='8pt',
                     text_color='#666666'))

lines.add_glyph(Square(x=3,
                       y=88,
                       fill_color=RED,
                       size=10,
                       line_color=None,
                       fill_alpha=0.8))


lines.add_layout(LinearAxis(axis_label="Percentile of Income", **AXIS_FORMATS), 'below')
lines.add_layout(LinearAxis(axis_label="% Itemizing", **AXIS_FORMATS), 'left')

# create bar plot -------------------------------------
PLOT_FORMATS['min_border_bottom'] = 30
bars_source = ColumnDataSource(bar_sources['ds_000_diff'].data)
bars = Plot(plot_width=500,
            plot_height=plot_height,
            title='Net Change in Average Tax by Annual Income',
            x_range=Range1d(0, 11),
            y_range=FactorRange(factors=list(tax_average_bin_names)),
            **PLOT_FORMATS)

bars.add_tools(HoverTool(tooltips=[("width", "@width"),
                                   ("reform_net", "@reform_net"),
                                   ("bins", "@bins"),
                                   ]))

bars.add_glyph(logo_source, logo_image)

bar_base_renderer = bars.add_glyph(bars_source,
                                   Rect(x=0,
                                        y='bins',
                                        height=0.7,
                                        width='width',
                                        fill_color='color',
                                        fill_alpha=0.65,
                                        line_color=None))

bars.add_glyph(Text(x=4.6,
                    y=11.6,
                    text_font_style='italic',
                    text=[''],
                    text_font_size='8pt',
                    text_color='#666666'))


bars.add_glyph(Square(x=7.5,
                      y=12,
                      fill_color=GREEN,
                      size=10,
                      line_color=None,
                      fill_alpha=0.65))

bars.add_glyph(Text(x=7.7,
                    y=11.6,
                    text_font_style='italic',
                    text=['net tax increase'],
                    text_font_size='8pt',
                    text_color='#666666'))

bars.add_glyph(bars_source,
               Text(x='annotation_x',
                    y='annotation_y',
                    text='annotation',
                    text_font_style='italic',
                    text_font_size='8pt',
                    text_color=DARK_GRAY))

#bars.add_layout(LinearAxis(**AXIS_FORMATS), 'below')
#bars.add_layout(LinearAxis(**AXIS_FORMATS), 'left')
bars.add_layout(CategoricalAxis(axis_label="Annual Income (USD)", **AXIS_FORMATS), 'left')

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
