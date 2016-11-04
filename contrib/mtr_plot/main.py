import pandas as pd
import numpy as np
from styles import BLUE, RED, GREEN, PLOT_FORMATS
from bokeh.models import (ColumnDataSource, LogAxis, LinearAxis, Rect, FactorRange, BoxZoomTool, ResetTool,
                          CategoricalAxis, Line, Text, Square, HoverTool, BoxSelectTool)
from bokeh.models import Plot, Range1d, ImageURL, DataRange1d, Select
from bokeh.embed import components
from bokeh.models import CustomJS, Slider
from bokeh.io import curdoc
from bokeh.plotting import figure, hplot, vplot, output_file, show
from bokeh.layouts import row, widgetbox, column, gridplot

hover = HoverTool(
        tooltips=[
            ("Marginal Tax Rate", "$y")
        ]
    )

plot_width = 425


def get_csv_data(MARS):
    source_csv = pd.read_csv('mtr_data.csv')

    if MARS == 'Single':
        df = source_csv.iloc[:,[0,1,2]]
    elif MARS == 'Joint':
        df = source_csv.iloc[:,[3,4,5]]
    elif MARS == 'Head of Household':
        df = source_csv.iloc[:,[6,7,8]]
    df = df.dropna()
    df.index = (df.reset_index()).index
    df.columns = ['base','reform','reform_2']
    return df


def make_a_plot(source):
    plot = figure(plot_height=450, plot_width=450,
                  title='Marginal Tax Rates under Clinton and Trump Tax Plans',
                  tools=[hover], **PLOT_FORMATS)

    plot.title.align = 'center'
    plot.title.text_font_size = '11pt'
    plot.line('index','reform',source = source, line_color=GREEN, line_width=2, line_alpha=0.8, legend="Trump")
    plot.line('index','base',source = source, line_color=BLUE, line_width=5, line_alpha=0.8, legend="Current Law")
    plot.line('index','reform_2',source = source, line_color=RED, line_width=2, legend="Clinton")
    plot.yaxis.axis_label = 'Average Marginal Tax Rate'
    plot.xaxis.axis_label = 'Percentile of Adjusted Gross Income'
    plot.legend.location = "bottom_right"
    plot.legend.label_text_font = "times"
    plot.legend.label_text_font_style = "italic"
    plot.legend.label_width = 5
    plot.legend.label_height = 5
    plot.legend.label_standoff = 5
    plot.legend.glyph_width = 20
    plot.legend.glyph_height = 20
    plot.legend.legend_spacing = 5
    plot.legend.legend_padding = 5
    return plot


options = ['Single', 'Joint', 'Head of Household']
scr1 = ColumnDataSource(get_csv_data(options[0]))
scr2 = ColumnDataSource(get_csv_data(options[1]))
scr3 = ColumnDataSource(get_csv_data(options[2]))
ref_source = ColumnDataSource(get_csv_data(options[0]))
sources = dict(Single=scr1, Joint=scr2, Head=scr3)
plot = make_a_plot(ref_source)
callback = CustomJS(args=sources, code="""
        var input = select.value;
        var data_1 = Single.data;
        var data_2 = Joint.data;
        var data_3 = Head.data;
        if (input == "Joint"){
            ref_source.data = data_2;
        } else if (input == "Head of Household"){
            ref_source.data = data_3;
        }
        ref_source.trigger('change');
        if (input == "Single") {
            ref_source.data = data_1;
        }
        ref_source.trigger('change');
    """)
select = Select(title='Filing Status', value='Single',  options=options,  callback=callback)
callback.args['select'] = select
callback.args['ref_source'] = ref_source
grid = column(select, plot)
output_file("index_landscape.html")
show(grid)
