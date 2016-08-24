'''
This program reads in the btax output dataframes and plots the results.
'''
import pandas as pd
import pickle
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource
from bokeh.io import output_file, show

with open("resources/by_asset.pkl", "rb") as pick:
    df = pickle.load(pick)

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

p = figure(plot_height=420,
           plot_width=620,
           title="Marginal Effective Tax Rates on Corporate Investments, 2016 Law",
           y_range=list(reversed(asset_order)),
           x_range=[-.15, .3],
           tools='pan,box_zoom,reset,hover')
p.xaxis.axis_label = "Marginal Effective Tax Rate"
p.yaxis.axis_label = "Asset Category"

hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset', '@Asset')]

SIZES = list(range(6, 22, 3))
df['size'] = pd.qcut(df['assets'].values, len(SIZES), labels=SIZES)

source = ColumnDataSource(df)
p.circle(x='metr_c',
         y='asset_category',
         source=source,
         color="#73000A",
         size='size',
         line_color="white",
         alpha=.6,
         hover_color='white',
         hover_alpha=0.5)
layout = row(p)
output_file('index.html')
show(layout)
