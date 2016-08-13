'''
------------------------------------------------------------------------
Last updated 8/5/2016

This program reads in the btax output dataframes and plots the results.

This py-file calls the following other file(s):

This py-file creates the following other file(s):

------------------------------------------------------------------------
'''

# Packages
import numpy as np
import pandas as pd
import pickle
import os
from bokeh.layouts import row, widgetbox
from bokeh.models import Select
from bokeh.palettes import Spectral5, Reds9
from bokeh.plotting import curdoc, figure
from bokeh.client import push_session
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource
from bokeh.charts.attributes import ColorAttr, CatAttr


# Constants for look of figure
SIZES = list(range(6, 22, 3))
COLORS = Reds9


def asset_bubble(output_by_assets):
    """Creates a bokeh bubble plot of results by asset

        :output_by_assets: Contains output by asset
        :type output_by_assets: dataframe
        :returns:
        :rtype:
    """
    df_all = output_by_assets.copy()

    # set up to sort differently than alphabetical
    asset_category_order = {'Computers and Software':1,
        'Instruments and Communications Equipment':2,
        'Office and Residential Equipment':3,
        'Transportation Equipment':4,
        'Industrial Machinery':5,
        'Other Industrial Equipment':6,
        'Other Equipment':7,
        'Residential Buildings':8,
        'Nonresidential Buildings':9,
        'Mining and Drilling Structures':10,
        'Other Structures':11,
        'Intellectual Property':12}

    # drop Intellectual Property
    df = df_all[df_all['asset_category']!='Intellectual Property'].copy()


    # sort categories
    df['sort_order'] = df['asset_category']
    df['sort_order'].replace(asset_category_order,inplace=True)
    df.sort_values(by="sort_order",axis=0,ascending=False,inplace=True)
    df.reset_index(inplace=True)

    xs = df['metr_c'].values
    ys = df['asset_category'].values

    x_title = "Marginal Effective Tax Rate"
    y_title = "Asset Category"

    source = ColumnDataSource(ColumnDataSource.from_df(df))

    kw = dict()
    kw['y_range'] = sorted(set(ys))
    kw['title'] = "Marginal Effective Tax Rates on Corporate Investments, 2016 Law"

    p = figure(plot_height=420, plot_width=700, tools='pan,box_zoom,reset,hover', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [('Asset', '@Asset')]

    sz = 9
    groups = pd.qcut(df['assets'].values, len(SIZES))
    sz = [SIZES[xx] for xx in groups.codes]

    c = "#73000A"
    p.circle(x=xs, y=ys, source=source, color=c, size=sz, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)


    layout = row(p)
    curdoc().add_root(layout)
    curdoc().title = "Corporate METRs"

    # save plot to html
    plot = curdoc()
    #plot.circle([1,2], [3,4])
    html = file_html(plot, CDN, "Corporate METRs")
    file = open("index.html","wb") #open file in binary mode
    file.writelines(html)
    file.close()

    os.system("./resources/phantomjs resources/rasterize.js index.html thumbnail.png")


'''
------------------------------------------
Plot results
------------------------------------------
'''

# Load data
output_by_asset = pickle.load( open( "resources/by_asset.pkl", "rb" ) )

# Call function to create figure
asset_bubble(output_by_asset)
