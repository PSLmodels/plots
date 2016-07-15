'''
Tax Brain Widget
'''
import glob
import pickle
import locale
import numpy as np
import os
import pandas as pd

from jinja2 import Environment, FileSystemLoader

from bokeh.models import Plot, Range1d, ImageURL, DataRange1d
from bokeh.embed import components
#from bokeh.layouts import layout
from bokeh.plotting import figure, hplot, vplot, output_file, show
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

from data import get_source_data

PERCENT_CUT_TEXT = ("These reforms could pay for higher spending, "
                    "lower deficits, or a <span>{:.1f}</span> percent tax cut "
                    "for every bracket.")
PERCENT_CUT_EMPTY = "Implement a reform to see the revenue neutralizing rate."

TAXPAYERS_ITEMIZING_TEXT = "<span>{number:.2f}</span> million fewer taxpayers itemizing. (<span>{percent:.1f}%</span> decrease)"
TAXPAYERS_ITEMIZING_EMPTY = "Implement a reform to see how many fewer taxpayers would need to itemize." 

DOLLARS_RAISED_TEXT = "<span>${:.2f}</span> billion raised."
DOLLARS_RAISED_EMPTY = "Implement a reform to see the revenue neutralizing rate."

locale.setlocale(locale.LC_ALL, 'en_US')
def output_page(output_path, **kwargs):
    here = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open(output_path, 'w') as output_file:
        output_file.write(content)

def get_data_sources():
    tax_average_bin_cats = reversed(['(0, 9999]',
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
    line_sources = {}
    bar_sources = {}
    taxcut_sources = {}
    revenue_sources = {}
    filers_sources = {}

    #dataframes = get_source_data()
    #with open("precalculated_data.pkle", "wb") as f:
        #pickle.dump(dataframes, f)

    with open("precalculated_data.pkle", "rb") as f:
        dataframes = pickle.load(f)

    for name, data in dataframes.items():
        if '_data' in name:
            df = data # Process the DataFrame
            df.reset_index(inplace=True)
            annotation_func = lambda r:'$' + locale.format('%d', float(r['mean_income']), grouping=True)
            df['base'] = df['base'] * 100
            df['reform'] = df['reform'] * 100
            df['mean_income'] = df.apply(annotation_func, axis=1)
            line_sources[name] = ColumnDataSource(df)

        elif '_diff' in name:
            df = data # Process the DataFrame
            df.reset_index(inplace=True)
            df.bins = df.bins.astype(str)
            df = df[df.bins != '(-100000000000000, 0]']
            df.bins = df.bins.map(lambda r: tax_average_bin_cats.index(r))
            df['reform_net'] = df['reform'] - df['base']
            df['color'] = np.where(df['reform_net'].values >= 0, GREEN, PURPLE)
            df['width'] = np.abs(df['reform_net'] * 2) # bokeh drawing from center

            annotation_func = lambda r:'$' + locale.format('%d', float(r['reform'] - r['base']), grouping=True)
            df['annotation'] = df.apply(annotation_func, axis=1)
            df['annotation_y'] = df.apply(lambda r:r['bins'] - .38, axis=1)
            df['annotation_x'] = df.apply(lambda r:max(.1, r['width'] / 2), axis=1)
            bar_sources[name] = ColumnDataSource(df)

        elif '_taxcut' in name:
            data_as_per = data * 100.
            txt = PERCENT_CUT_TEXT.format(data_as_per)
            if name.startswith("ds_000"):
                txt = PERCENT_CUT_EMPTY
            df = pd.DataFrame(data={"text":[txt]})
            taxcut_sources[name] = ColumnDataSource(df)

        elif '_revenue' in name:
            data_as_bil = data/(1.0e9)
            txt = DOLLARS_RAISED_TEXT.format(data_as_bil)
            if name.startswith("ds_000"):
                txt = DOLLARS_RAISED_EMPTY
            df = pd.DataFrame(data={"text":[txt]})
            revenue_sources[name] = ColumnDataSource(df)

        elif '_filers' in name:
            num_filers, percent_change = data
            nf_as_mil = num_filers/(-1.0e6)
            percent_change *= -100.0  # Text makes clear value is a decrease
            txt = TAXPAYERS_ITEMIZING_TEXT.format(number=nf_as_mil, percent=percent_change)
            if name.startswith("ds_000"):
                txt = TAXPAYERS_ITEMIZING_EMPTY
            df = pd.DataFrame(data={"text":[txt]})
            filers_sources[name] = ColumnDataSource(df)

    return line_sources, bar_sources, taxcut_sources, revenue_sources, filers_sources


plot_width = 425
plot_height = 250
text_plot_height = 50

line_sources, bar_sources, taxcut_sources, revenue_sources, filers_sources = get_data_sources()

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
                                  '1M+'])

# create line plot --------------------------------------------------
lines_source = ColumnDataSource(line_sources['ds_000_data'].data)
lines = Plot(plot_width=plot_width,
             plot_height=plot_height,
             title='Percent Itemizing by Income Percentile',
             x_range=Range1d(0, 100),
             y_range=Range1d(0, 100),
             **PLOT_FORMATS)

lines.add_tools(HoverTool(tooltips=[("mean_income", "@mean_income")]))


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


lines.add_layout(LinearAxis(axis_label="Average Adjusted Gross Income by Percentile", **AXIS_FORMATS), 'below')
lines.add_layout(LinearAxis(axis_label="% Itemizing", **AXIS_FORMATS), 'left')

# create bar plot -------------------------------------
PLOT_FORMATS['min_border_bottom'] = 30
bars_source = ColumnDataSource(bar_sources['ds_000_diff'].data)
bars = Plot(plot_width=500,
            plot_height=plot_height,
            title='Net Change in Average Tax by Annual Income',
            x_range=Range1d(0, 22000),
            y_range=FactorRange(factors=list(tax_average_bin_names)),
            **PLOT_FORMATS)


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


bars.add_glyph(Square(x=14600,
                      y=12,
                      fill_color=GREEN,
                      size=10,
                      line_color=None,
                      fill_alpha=0.65))

bars.add_glyph(Text(x=15000,
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
bars.add_layout(CategoricalAxis(axis_label="Annual Adjusted Gross Income", **AXIS_FORMATS), 'left')

# create text plots -------------------------------------
taxcut_source = ColumnDataSource(taxcut_sources['ds_000_taxcut'].data)
percentcut_text = Plot(plot_width=800,
                       plot_height=text_plot_height,
                       x_range=Range1d(0, 100),
                       y_range=Range1d(0, 100),
                       **PLOT_FORMATS)


textbottom_renderer = percentcut_text.add_glyph(taxcut_source,
                          Text(x=3.15,
                               y=10,
                               text_font_style='normal',
                               text='text',
                               text_font_size='10pt',
                               text_color='#666666'))

filers_source = ColumnDataSource(filers_sources['ds_000_filers'].data)
itemizing_text = Plot(plot_width=500,
                      x_range=Range1d(0, 100),
                      y_range=Range1d(0, 100),
                      plot_height=text_plot_height, **PLOT_FORMATS)

textleft_renderer = itemizing_text.add_glyph(filers_source,
                                             Text(x=5.15,
                                                  y=10,
                                                  text_font_style='normal',
                                                  text="text",
                                                  text_font_size='10pt',
                                                  text_color='#666666'))


revenue_source = ColumnDataSource(revenue_sources['ds_000_revenue'].data)
dollarsraised_text = Plot(plot_width=500,
                          x_range=Range1d(0, 100),
                          y_range=Range1d(0, 100),
                          plot_height=text_plot_height, **PLOT_FORMATS)
textright_renderer = dollarsraised_text.add_glyph(revenue_source,
                             Text(x=5.15,
                                  y=10,
                                  text_font_style='normal',
                                  text="text",
                                  text_font_size='10pt',
                                  text_color='#666666'))


# end create text plots ---------------------------------
plots = {}
plots['bars_plot'] = bars
plots['line_plot'] = lines
#plots['textleft_plot'] = itemizing_text
#plots['textright_plot'] = dollarsraised_text
#plots['textbottom_plot'] = percentcut_text


bars_data = {k: v.data for k, v in bar_sources.items()}
lines_data = {k: v.data for k, v in line_sources.items()}

# Left Text: # Itemizers from filers_source
textleft_data = {k: v.data for k, v in filers_sources.items()}
# Right Text: # Revenue raised from revenue_source
textright_data = {k: v.data for k, v in revenue_sources.items()}
# Bottom Text: # Tax Cut possible from from taxcut_source
textbottom_data = {k: v.data for k, v in taxcut_sources.items()}

script, divs = components(plots)

output_page('index.html',
            bokeh_script=script,
            plots=divs,
            instruction_columns=[PERCENT_CUT_EMPTY,TAXPAYERS_ITEMIZING_EMPTY,DOLLARS_RAISED_EMPTY],

            # Plot Ids
            line_plot_id=lines._id,
            line_renderer_id=line_base_renderer._id,
            bar_plot_id=bars._id,
            bar_renderer_id=bar_base_renderer._id,
            #textleft_plot_id = itemizing_text._id,
            #textleft_renderer_id = textleft_renderer._id,
            #textright_plot_id = dollarsraised_text._id,
            #textright_renderer_id = textright_renderer._id,
            #textbottom_plot_id = percentcut_text._id,
            #textbottom_renderer_id = textbottom_renderer._id,
            bars_data=bars_data,
            textleft_data=textleft_data,
            textright_data=textright_data,
            textbottom_data=textbottom_data,
            lines_data=lines_data)
