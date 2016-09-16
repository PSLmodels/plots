'''
This program reads in the btax output dataframes and plots the results.
'''
import pandas as pd
import pickle

from os import path
import os

from jinja2 import Environment, FileSystemLoader
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.embed import components
from bokeh.layouts import column
from styles import (PLOT_FORMATS,
                    RED,
                    BLUE, GREEN, PURPLE)


def output_page(**kwargs):
    here = path.dirname(path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open('index.html', 'w') as output_file:
        output_file.write(content)

def wavg(group, avg_name, weight_name):
    """
    Computes a weighted average
    """
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()

# read data
df_raw = pd.read_csv("resources/by_asset_bonus_phaseout.csv")

# drop intellectual property
df_raw = df_raw[df_raw['asset_category'] != 'Intellectual Property'].copy()

# create weighted average of mettrs, so just one bubble per asset category
# sum assets
df = pd.DataFrame({'mettr_c_2016' : df_raw.groupby(
    ['asset_category','short_category'] ).apply(wavg, "mettr_c_2016", "assets_c")}).reset_index()
df['mettr_c_2016_fmt'] = df.apply(lambda x: "{0:.1f}%".format(x['mettr_c_2016'] * 100), axis=1)
col_list = ['mettr_c_2018', 'mettr_c_2019', 'mettr_c_2020']
for item in col_list:
    df[item] = (pd.DataFrame({item : df_raw.groupby(
        ['asset_category','short_category']).apply(wavg, item, "assets_c")})).reset_index()[item]
    df[item+'_fmt'] = df.apply(lambda x: "{0:.1f}%".format(x[item] * 100), axis=1)
df['assets_c'] = (pd.DataFrame({'assets_c' : df_raw.groupby(
    ['asset_category','short_category'])['assets_c'].sum()})).reset_index()['assets_c']



asset_order = ['Computers and Software',
               'Instruments and Communications Equipment',
               'Office and Residential Equipment',
               'Transportation Equipment',
               'Industrial Machinery',
               'Other Industrial Equipment',
               'Other Equipment']

asset_order2 = ['Residential Buildings',
               'Nonresidential Buildings',
               '                        Mining and Drilling Structures',
               'Other Structures']

SIZES = list(range(6, 22, 3))
df['size'] = pd.qcut(df['assets_c'].values, len(SIZES), labels=SIZES)


# top plot
p = figure(plot_height=230,
           plot_width=990,
           x_range = (.08, .4),
           y_range=list(reversed(asset_order)),
           x_axis_location="above",
           tools='hover',
           **PLOT_FORMATS)
hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset Category', ' @asset_category (@mettr_c_2016_fmt)')]
p.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p.yaxis.axis_label = "Equipment"
p.toolbar_location = None
p.min_border_right = 5
p.outline_line_alpha = 0.2


source1 = ColumnDataSource(df[(~df.asset_category.str.contains('Structures')) & (~df.asset_category.str.contains('Buildings'))])
# source1_2018 = ColumnDataSource(df[(~df.asset_category.str.contains('Structures')) & (~df.asset_category.str.contains('Buildings'))]['mettr_c_2018'])


source2 = ColumnDataSource(df[(df.asset_category.str.contains('Structures')) | (df.asset_category.str.contains('Buildings'))])
# source2_2018 = ColumnDataSource(df[(df.asset_category.str.contains('Structures')) | (df.asset_category.str.contains('Buildings'))]['mettr_c_2018'])

p.circle(x='mettr_c_2016',
         y='asset_category',
         color=RED,
         size='size',
         line_color="white",
         source=source1,
         legend="2016-2017",
         alpha=.4)

p.circle(x='mettr_c_2018',
         y='asset_category',
         color=BLUE,
         size='size',
         line_color="white",
         source=source1,
         legend="2018",
         alpha=.4)

p.circle(x='mettr_c_2019',
         y='asset_category',
         color=GREEN,
         size='size',
         line_color="white",
         source=source1,
         legend="2019",
         alpha=.4)

p.circle(x='mettr_c_2020',
         y='asset_category',
         color=PURPLE,
         size='size',
         line_color="white",
         source=source1,
         legend="2020+",
         alpha=.4)


# bottom plot
p2 = figure(plot_height=160,
            plot_width=990,
            x_range = (.08, .4),
            y_range=list(reversed(asset_order2)),
            tools='hover',
            **PLOT_FORMATS)
hover = p2.select(dict(type=HoverTool))
hover.tooltips = [('Asset Category', ' @asset_category (@mettr_c_2016_fmt)')]
p2.xaxis.axis_label = "Marginal Effective Tax Rate"
p2.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p2.yaxis.axis_label = "Structures"
p2.toolbar_location = None
p2.min_border_right = 5
p2.outline_line_alpha = 0.2


# does this need to be here is above?
hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset Category', ' @asset_category (@mettr_c_2016_fmt)')]

p2.circle(x='mettr_c_2016',
          y='asset_category',
          color=RED,
          size='size',
          line_color="white",
          source=source2,
          alpha=.4)

p2.circle(x='mettr_c_2018',
          y='asset_category',
          color=BLUE,
          size='size',
          line_color="white",
          source=source2,
          alpha=.4)

p2.circle(x='mettr_c_2019',
          y='asset_category',
          color=GREEN,
          size='size',
          line_color="white",
          source=source2,
          alpha=.4)

p2.circle(x='mettr_c_2020',
          y='asset_category',
          color=PURPLE,
          size='size',
          line_color="white",
          source=source2,
          alpha=.4)


plots = dict(metr=column(p, p2))
script, divs = components(plots)
output_page(bokeh_script=script, plots=divs)

os.system("./resources/phantomjs resources/rasterize.js index.html thumbnail.png")
