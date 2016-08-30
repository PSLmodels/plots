from bokeh.io import vform
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show
from bokeh.charts import Bar
import numpy as np

output_file("callback.html")
x_years = range(2010,2020,2)

y_rev = [x_rev*0.005 for x_rev in range(0, 10)]
y_tax = [x_tax*0.009 for x_tax in range(0, 10)]

source_rev = ColumnDataSource(data=dict(x=x_years, y=y_rev))
source_tax = ColumnDataSource(data=dict(x=x_years, y=y_tax))

plot = figure(plot_width=1000, plot_height=500)

plot.line('x', 'y', source=source_rev, line_width=3, line_alpha=0.6, color="red")
plot.line('x', 'y', source=source_tax, line_width=3, line_alpha=0.6, color="lime")
#p = Bar({x,y}, title="Average MPG by YR",  label='yr')
powder = CustomJS(args=dict(source=source_rev), code="""
        var data = source.get('data');
        var f = cb_obj.get('value')
        x = data['x']
        y = data['y']
        for (i = 0; i < x.length; i++) {
            y[i] = Math.pow(x[i], f)
        }
        source.trigger('change');
    """)
lowder = CustomJS(args=dict(source=source_tax), code="""
        var data = source.get('data');
        var f = cb_obj.get('value')
        x = data['x']
        y = data['y']
        for (i = 0; i < x.length; i++) {
            y[i] = Math.pow(x[i], 1/f)
        }
        source.trigger('change');
    """)

slider = Slider(start=2, end=12, value=6, step=2, title="Rate hike", callback=powder)
slider2 = Slider(start=0, end=1.2, value=0.6, step=.1, title="Elasticity of taxable income", callback=lowder)

layout = vform(slider, slider2, plot)

show(layout)
