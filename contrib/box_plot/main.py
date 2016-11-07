from styles import BLUE, RED, GREEN, PLOT_FORMATS
from bokeh.models import (ColumnDataSource, LogAxis, LinearAxis, Rect, FactorRange, BoxZoomTool, ResetTool,
                          CategoricalAxis, Line, Text, Square, HoverTool, BoxSelectTool)
from bokeh.models import Plot, Range1d, ImageURL, DataRange1d, Select
from bokeh.embed import components
from bokeh.models import CustomJS, Slider, RadioButtonGroup
from bokeh.io import curdoc
from bokeh.plotting import figure, hplot, vplot, output_file, show
from bokeh.layouts import row, widgetbox, column, gridplot
import pandas as pd

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
    plot = figure(plot_height=425, plot_width=425, x_axis_type="datetime",
                  title='Box',
                  tools=[], **PLOT_FORMATS)
    plot.set(y_range=Range1d(0,20))
    plot.vbar(x='year',top='reform',source = source, line_width=20,bottom=0, color=RED, fill_alpha = 0.4)
    plot.title.align = 'center'
    plot.title.text_font_size = '11pt'
    plot.yaxis.axis_label = 'Change in individual income and payroll tax liabilities'
    plot.xaxis.axis_label = 'Year'
    return plot

ref = ColumnDataSource(dict(index = [], reform = [],year=[]))
ref = ColumnDataSource(dict(index = [], reform = [],year=[]))

callback = CustomJS(args=sources, code="""
        var cg = cg_option.active;
        var inc = inc_option.active;
        var i = inc*3 + cg*7;
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
        if (i == 7){
            ref.data = data_1;
        } else if (i == 10){
            ref.data = data_2;
        } else if (i == 13){
            ref.data = data_3;
        } else if (i == 16){
            ref.data = data_4;
        } else if (i == 19){
            ref.data = data_5;
        } else if (i == 0){
            ref.data = data_6;
        } else if (i == 3){
            ref.data = data_7;
        } else if (i == 6){
            ref.data = data_8;
        } else if (i == 9){
            ref.data = data_9;
        } else if (i == 12){
            ref.data = data_10;
        }
        ref.trigger('change');
    """)
select1 = RadioButtonGroup(labels=["0", "0.2","0.4", "0.55", "1.2"], callback=callback,width=350)
select = RadioButtonGroup(labels=["off","on"],callback=callback,width=350)
callback.args['cg_option'] = select
callback.args['inc_option'] = select1
callback.args['ref'] = ref
grid = column(select,select1, fig)
show(grid)
