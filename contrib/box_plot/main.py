from styles import BLUE, RED, GREEN
from bokeh.models import (ColumnDataSource, LogAxis, LinearAxis, Rect, FactorRange, BoxZoomTool, ResetTool,
                          CategoricalAxis, Line, Text, Square, HoverTool, BoxSelectTool)
from bokeh.models import Plot, Range1d, ImageURL, DataRange1d, Select
from bokeh.embed import components
from bokeh.models import CustomJS, Slider
from bokeh.io import curdoc
from bokeh.plotting import figure, hplot, vplot, output_file, show
from bokeh.layouts import row, widgetbox, column, gridplot
import pandas as pd

def prepare_data():
    source_csv = pd.read_csv('data.csv',index_col=0)
    df = pd.DataFrame(source_csv.ix[:,0])
    df.columns = ['base']
    static = ColumnDataSource(df)
    temp = {}
    for i in range(1,11):
        ddf = pd.DataFrame(source_csv.ix[:,i])
        ddf.columns = ['reform']
        temp[' '.join(str(i))] = ddf
    return static, temp

static, temp  = prepare_data()
def make_box_plot(source):
    plot = figure(plot_height=425, plot_width=425,
                  title='Box',
                  tools=[ResetTool()])
    plot.vbar(x='index',top='base',source = static, width=0.5, bottom=2500, color=BLUE, fill_alpha = 1.8)
    plot.add_tools(HoverTool(tooltips=[("Year", "@index")]))
    plot.vbar(x='index',top='reform',source = source, width=0.48, bottom=2500, color=RED, fill_alpha = 0.4)
    plot.title.align = 'center'
    plot.title.text_font_size = '11pt'
    plot.yaxis.axis_label = 'Combined liability'
    plot.xaxis.axis_label = 'Year'
    return plot

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

ref = ColumnDataSource(dict(index = [], reform = []))
fig = make_box_plot(ref)

callback = CustomJS(args=sources, code="""
        var cg = cg_option.value;
        var inc = inc_option.value;
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
        if ((cg == "off") && (inc == "0")){
            ref.data = data_1;
        } else if ((cg == "off") && (inc == "0.2")){
            ref.data = data_2;
        } else if ((cg == "off") && (inc == "0.4")){
            ref.data = data_3;
        } else if ((cg == "off") && (inc == "0.55")){
            ref.data = data_4;
        } else if ((cg == "off") && (inc == "1.2")){
            ref.data = data_5;
        } else if ((cg == "on") && (inc == "0")){
            ref.data = data_6;
        } else if ((cg == "on") && (inc == "0.2")){
            ref.data = data_7;
        } else if ((cg == "on") && (inc == "0.4")){
            ref.data = data_8;
        } else if ((cg == "on") && (inc == "0.55")){
            ref.data = data_9;
        } else if ((cg == "on") && (inc == "1.2")){
            ref.data = data_10;
        }
        ref.trigger('change');
    """)
select1 = Select(title="Option:", value="0", options=["0", "0.2","0.4", "0.55", "1.2"], callback=callback)
select = Select(title="Option2:", value="off", options=["off", "on"], callback=callback)
callback.args['cg_option'] = select
callback.args['inc_option'] = select1
callback.args['ref'] = ref
grid = column(select,select1, fig)
show(grid)