from styles import BLUE, RED, GREEN, PLOT_FORMATS, DARK_GRAY
from bokeh.models import (ColumnDataSource, LogAxis, LinearAxis, Rect, FactorRange, BoxZoomTool, ResetTool,
                          CategoricalAxis, Line, Text, Square, HoverTool, BoxSelectTool)
from bokeh.models import Plot, Range1d, ImageURL, DataRange1d, Select
from bokeh.embed import components
from bokeh.models import CustomJS, Slider,RadioButtonGroup, Paragraph
from bokeh.io import curdoc
from bokeh.plotting import figure, hplot, vplot, output_file, show
from bokeh.layouts import row, widgetbox, column, gridplot
from bokeh.models.widgets import Div
import pandas as pd
from math import pi

def prepare_data():
    source_csv = pd.read_csv('data.csv', parse_dates=[0])
    source_csv=source_csv.rename(columns = {'Unnamed: 0':'year'})
    temp = {}
    source_csv.index = source_csv['year']
    for i in range(1,11):
        ddf = pd.DataFrame(source_csv.ix[:,i])
        ddf.columns = ['reform']
        temp[' '.join(str(i))] = ddf
    sources = dict(re00=ColumnDataSource(temp['1']), 
                       re01=ColumnDataSource(temp['2']), 
                      re02=ColumnDataSource(temp['3']), 
                      re03=ColumnDataSource(temp['4']), 
                      re04=ColumnDataSource(temp['5']), 
                      re10=ColumnDataSource(temp['6']), 
                      re11=ColumnDataSource(temp['7']), 
                      re12=ColumnDataSource(temp['8']), 
                      re13=ColumnDataSource(temp['9']),
                      re14=ColumnDataSource(temp['1 0']))
    return sources

sources  = prepare_data()

def make_box_plot(source):
    plot = figure(plot_height=600, plot_width=550, x_axis_type="datetime",
                  tools=[],**PLOT_FORMATS)
    plot.set(y_range=Range1d(-9.5,18.5))
    plot.vbar(x='year',top='reform',source = source, line_width=20,bottom=0, color=RED, fill_alpha = 0.4)
    plot.title.align = 'center'
    plot.title.text_font_size = '10pt'
    plot.yaxis.axis_label = 'Change in individual income and payroll tax liabilities (Billions)'
    plot.xaxis.axis_label = 'Year'
    return plot

ref = ColumnDataSource(sources['re00'].data)
static = ColumnDataSource(sources['re00'].data)
empty = ColumnDataSource(dict(index = [], reform = [],year=[]))
sources["re14"].data = empty.data

fig = make_box_plot(ref)
fig.rect(x='year',y='reform',source = static, angle=pi/2,width=5, height=1, color=DARK_GRAY)
callback = CustomJS(args=sources, code="""
        var i = option.active;
        var data_1 = re00.data;
        var data_2 = re01.data;
        var data_3 = re02.data;
        var data_4 = re03.data;
        var data_5 = re04.data;
        var data_6 = re10.data;
        var data_7 = re11.data;
        var data_8 = re12.data;
        var data_9 = re13.data;
        var data_10 = re14.data;
        if (i == 0){
            ref.data = data_1;
        } else if (i == 1){
            ref.data = data_2;
        } else if (i == 2){
            ref.data = data_3;
        } else if (i == 3){
            ref.data = data_4;
        } else if (i == 4){
            ref.data = data_5;
        } else if (i == 8){
            ref.data = data_6;
        } else if (i == 9){
            ref.data = data_7;
        } else if (i == 10){
            ref.data = data_8;
        } else if (i == 11){
            ref.data = data_9;
        } else{
            ref.data = data_10;
        }
        ref.trigger('change');
    """)

option = RadioButtonGroup(labels=["0.0", "0.25","0.4", "0.55", "1.09","\a","\a","\a","0.0", "0.25","0.4", "0.55"], callback=callback,width=600, active=0)
Par1 = Div(text="""Elasticity of taxable income <b>without</b> additional capital gains behavior.""",
width=280, height=18)
Par2 = Div(text="""Elasticity of taxable income <b>with</b> additional capital gains behavior.""",
width=280, height=18)
option.active
TIT = Div(text='Revenue Impact of a 4% Surtax on Taxpayers with Adjusted Gross Income over $5 Million',
width=550, height=30)
callback.args['option'] = option
callback.args['ref'] = ref


grid = column(column(row(children = [widgetbox(Par1), widgetbox(Par2)]),option), column(TIT,fig))
output_file("index_landscape.html")
show(grid)
