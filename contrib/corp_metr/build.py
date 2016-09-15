'''
This program reads in the btax output dataframes and plots the results.
'''
import pandas as pd
import pickle

from os import path

from jinja2 import Environment, FileSystemLoader
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.embed import components
from bokeh.layouts import column
from styles import (PLOT_FORMATS,
                    RED,
                    BLUE)


def output_page(**kwargs):
    here = path.dirname(path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open('index.html', 'w') as output_file:
        output_file.write(content)


with open("resources/by_asset.pkl", "rb") as pick:
    df = pickle.load(pick)

reform_df = pd.read_csv("resources/reform_byasset.csv")

df = df[df['asset_category'] != 'Intellectual Property'].copy()
reform_df = reform_df[reform_df['asset_category'] != 'Intellectual Property'].copy()


df['mettr_c_fmt'] = df.apply(lambda x: "{0:.1f}%".format(x['mettr_c'] * 100), axis=1)
reform_df['mettr_c_fmt'] = reform_df.apply(lambda x: "{0:.1f}%".format(x['mettr_c'] * 100), axis=1)

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
df['size'] = pd.qcut(df['assets'].values, len(SIZES), labels=SIZES)
reform_df['size'] = pd.qcut(reform_df['assets_c'].values, len(SIZES), labels=SIZES)


# top plot
p = figure(plot_height=230,
           plot_width=990,
           x_range = (-.05, .28),
           y_range=list(reversed(asset_order)),
           x_axis_location="above",
           tools='hover',
           **PLOT_FORMATS)
hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset', ' @Asset (@mettr_c_fmt)')]
p.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p.yaxis.axis_label = "Equipment"
p.toolbar_location = None
p.min_border_right = 5
p.outline_line_alpha = 0.2


source1 = ColumnDataSource(df[(~df.asset_category.str.contains('Structures')) & (~df.asset_category.str.contains('Buildings'))])
reform_source1 = ColumnDataSource(reform_df[(~reform_df.asset_category.str.contains('Structures')) & (~reform_df.asset_category.str.contains('Buildings'))])

source2 = ColumnDataSource(df[(df.asset_category.str.contains('Structures')) | (df.asset_category.str.contains('Buildings'))])
reform_source2 = ColumnDataSource(reform_df[(reform_df.asset_category.str.contains('Structures')) | (reform_df.asset_category.str.contains('Buildings'))])

p.circle(x='mettr_c',
         y='asset_category',
         color=RED,
         size='size',
         line_color="white",
         source=source1,
         legend="baseline",
         alpha=.4)

p.circle(x='mettr_c',
         y='asset_category',
         color=BLUE,
         size='size',
         line_color="white",
         source=reform_source1,
         legend="reform",
         alpha=.4)


# bottom plot
p2 = figure(plot_height=160,
            plot_width=990,
            x_range = (-.05, .28),
            y_range=list(reversed(asset_order2)),
            tools='hover',
            **PLOT_FORMATS)
hover = p2.select(dict(type=HoverTool))
hover.tooltips = [('Asset', ' @Asset (@mettr_c_fmt)')]
p2.xaxis.axis_label = "Marginal Effective Tax Rate"
p2.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p2.yaxis.axis_label = "Structures"
p2.toolbar_location = None
p2.min_border_right = 5
p2.outline_line_alpha = 0.2


hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset', ' @Asset (@mettr_c_fmt)')]

p2.circle(x='mettr_c',
          y='asset_category',
          color=RED,
          size='size',
          line_color="white",
          source=source2,
          alpha=.4)

p2.circle(x='mettr_c',
          y='asset_category',
          color=BLUE,
          size='size',
          line_color="white",
          source=reform_source2,
          alpha=.4)


plots = dict(metr=column(p, p2))
script, divs = components(plots)
output_page(bokeh_script=script, plots=divs)
