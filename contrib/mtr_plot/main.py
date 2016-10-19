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
    source_csv = pd.read_csv('mtr_data.csv')

    if MARS == 'Single':
        df = source_csv.iloc[:,[0,1,2]]
    elif MARS == 'Joint':
        df = source_csv.iloc[:,[3,4,5]]
    elif MARS == 'Head of Household':
        df = source_csv.iloc[:,[6,7,8]]
    df.dropna()
    df.index = (df.reset_index()).index
    df.columns = ['base','reform','reform_2']
    df['index'] = df.index
    return df


def make_a_plot(source):
    plot = figure(plot_height=600, plot_width=800,
                  tools="")
    plot.line('index','reform',source = source, line_color=Greens4[0], line_width=2, line_alpha=.8)
    plot.line('index','reform_2',source = source, line_color=Reds4[0], line_width=2, line_alpha=.8)
    plot.line('index','base',source = source, line_color=Blues4[0], line_width=2, line_alpha=1.2)
    plot.yaxis.axis_label = 'Avg. MTR on Wage Income'
    plot.xaxis.axis_label = 'Percentile of Adjusted Gross Income'
    return plot

ref_source = ColumnDataSource(dict(
                    index = [],
                    base = [],
                    reform = [],
                    reform_2 = []
                ))

mars = 'Single'
options = ['Single', 'Joint', 'Head of Household']
scr1 = ColumnDataSource(get_csv_data(options[0]))
scr2 = ColumnDataSource(get_csv_data(options[1]))
scr3 = ColumnDataSource(get_csv_data(options[2]))

plot = make_a_plot(ref_source)
callback = CustomJS(args=dict(sin_ = scr1, jon_ = scr2, sep_ = scr3 ), code="""
        var input = select.value;
        var data_1 = sin_.data;
        var data_2 = jon_.data;
        var data_3 = sep_.data;
        if (input == "Single"){
            ref_source.data = data_1;
        } else if (input == "Joint"){
            ref_source.data = data_2;
        } else{
            ref_source.data = data_3;
        }
        ref_source.trigger('change');
    """)
select = Select(value=mars, title='MARS', options=options,  callback=callback)
callback.args['select'] = select
callback.args['ref_source'] = ref_source

layout = row(plot, select)

show(layout)
