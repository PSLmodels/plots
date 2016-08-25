'''
This program reads in the btax output dataframes and plots the results.
'''
import pandas as pd
import pickle

from os import path
from math import pi

from jinja2 import Environment, FileSystemLoader
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.embed import components

def output_page(**kwargs):
    here = path.dirname(path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open('index.html', 'w') as output_file:
        output_file.write(content)

with open("resources/by_asset.pkl", "rb") as pick:
    df = pickle.load(pick)

df = df[df['asset_category'] != 'Intellectual Property'].copy()
df['metr_c_fmt'] = df.apply(lambda x: "{0:.1f}%".format(x['metr_c'] * 100), axis=1)

asset_order = ['Computers and Software',
               'Instruments and Communications Equipment',
               'Office and Residential Equipment',
               'Transportation Equipment',
               'Industrial Machinery',
               'Other Industrial Equipment',
               'Other Equipment',
               'Residential Buildings',
               'Nonresidential Buildings',
               'Mining and Drilling Structures',
               'Other Structures']

# reform and baseline policy as separate colors
# use of pickles long term?
# commiting large files to git...?

p = figure(plot_height=380,
           plot_width=990,
           y_range=list(reversed(asset_order)),
           tools='hover')
p.xaxis.axis_label = "Marginal Effective Tax Rate"
p.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p.yaxis.axis_label = "Asset Category"
p.yaxis.major_label_orientation = pi/4
p.toolbar_location = None
p.min_border_right = 5
p.min_border_bottom = 60

hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset', ' @Asset (@metr_c_fmt)')]

SIZES = list(range(6, 22, 3))
df['size'] = pd.qcut(df['assets'].values, len(SIZES), labels=SIZES)

source = ColumnDataSource(df)
p.circle(x='metr_c',
         y='asset_category',
         color="#73000A",
         size='size',
         line_color="white",
         source=source,
         alpha=.6)

p.line(x=[0,0],
       y=[0,100],
       line_dash=[5,5],
       color='black')

plots = dict(metr=p)
script, divs = components(plots)
output_page(bokeh_script=script, plots=divs)
