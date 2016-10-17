import pandas as pd
import numpy as np
from bokeh.models import (ColumnDataSource, LogAxis, LinearAxis, Rect, FactorRange,
                          CategoricalAxis, Line, Text, Square, HoverTool)
from bokeh.models import Plot, Range1d, ImageURL, DataRange1d, Select
from bokeh.embed import components
from bokeh.models import CustomJS, Slider
from bokeh.io import curdoc
from bokeh.plotting import figure, hplot, vplot, output_file, show
from bokeh.layouts import row, widgetbox
from bokeh.palettes import Blues4, Reds4, Greens4

def get_csv_data(MARS):
    source = pd.read_csv('mtr_data.csv')

    if MARS == 'Single':
        df = source.iloc[:,[0,1,2]]
    elif MARS == 'Joint':
        df = source.iloc[:,[3,4,5]]
    elif MARS == 'Head of Household':
        df = source.iloc[:,[6,7,8]]
    df.columns = ['base','reform','reform_2']
    return ColumnDataSource(df)


def make_a_plot(source):
    plot = figure(plot_height=600, plot_width=800,
                  tools="")
    plot.line('index','reform',source = source, line_color=Greens4[0], line_width=2, line_alpha=.8)
    plot.line('index','reform_2',source = source, line_color=Reds4[0], line_width=2, line_alpha=.8)
    plot.line('index','base',source = source, line_color=Blues4[0], line_width=2, line_alpha=1.2)
    plot.yaxis.axis_label = 'Avg. MTR on Wage Income'
    plot.xaxis.axis_label = 'Percentile of Adjusted Gross Income'
    return plot


def update(attr, old, new):
    src = get_csv_data(MARS_Select.value)
    source.data.update(src.data)

mars = 'Single'
MARS_Select = Select(value=mars, title='MARS', options=['Single', 'Joint', 'Head of Household'])
plot = make_a_plot(get_csv_data(mars))
MARS_Select.on_change('value', update)

layout = row(plot, MARS_Select)
show(layout)
