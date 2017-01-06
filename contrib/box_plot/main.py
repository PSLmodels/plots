
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models import CustomJS, RadioButtonGroup
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models.widgets import Div, RadioGroup
from bokeh.embed import components

import pandas as pd
from math import pi

from taxplots.utils import render_template

from styles import RED, PLOT_FORMATS, DARK_GRAY

# create data sources -----------------
source_csv = pd.read_csv('data.csv', parse_dates=[0])
source_csv = source_csv.rename(columns={'Unnamed: 0': 'year'})
temp = {}
source_csv.index = source_csv['year']
for i in range(1, 11):
    ddf = pd.DataFrame(source_csv.ix[:, i])
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

sources['static'] = ColumnDataSource(sources['re00'].data)
sources['empty'] = ColumnDataSource(dict(index=[], reform=[], year=[]))
sources['ref'] = ColumnDataSource(sources['re00'].data)
sources["re14"].data = sources['empty'].data

sources['capital_gains_no'] = ColumnDataSource(dict(labels=["0.0", "0.25", "0.4", "0.55", "1.09"],
                                                    source_ids=["re00", "re01", "re02", "re03", "re04"]))

sources['capital_gains_yes'] = ColumnDataSource(dict(labels=["0.0", "0.25", "0.4", "0.55"],
                                                     source_ids=["re10", "re11", "re12", "re13"]))


# create figure ------------------
fig = figure(x_axis_type="datetime",
             tools=[],
             plot_width=400,
             plot_height=400,
             **PLOT_FORMATS)
fig.set(y_range=Range1d(-9.5, 18.5))
fig.vbar(x='year',
         top='reform',
         source=sources['ref'],
         line_width=20,
         bottom=0,
         color=RED,
         fill_alpha=0.4)

fig.title.align = 'center'
fig.title.text_font_size = '10pt'
fig.yaxis.axis_label = 'Change in individual income and payroll tax liabilities (Billions)'
fig.xaxis.axis_label = 'Year'

fig.rect(x='year',
         y='reform',
         source=sources['static'],
         angle=pi/2,
         width=5,
         height=1,
         color=DARK_GRAY)


# create components --------------
title_div = Div(text='Revenue Impact of a 4% Surtax on Taxpayers with Adjusted Gross Income over $5 Million', height=30)

radio_group_text = Div(text="Include Additional Capital Gains Behavior.")
radio_group = RadioGroup(labels=["Without", "With"], active=0)
sources['radio_group'] = radio_group

elasticity_text = Div(text="Elasticity of Taxable Income")
elasticity_option = RadioButtonGroup(labels=sources['capital_gains_no'].data['labels'], active=0)
sources['elasticity_option'] = elasticity_option


# create callbacks ---------------
radio_group.callback = CustomJS(args=sources, code="""
  var capitalGainsType = radio_group.active === 0 ? capital_gains_no : capital_gains_yes;
  elasticity_option.set('labels', capitalGainsType.data.labels);

  while (elasticity_option.active > capitalGainsType.data.source_ids.length - 1) {
    elasticity_option.active = elasticity_option.active - 1;
  }

  ref.data = eval(capitalGainsType.data.source_ids[elasticity_option.active]).data;
  ref.trigger('change');
""")

elasticity_option.callback = CustomJS(args=sources, code="""
  var capitalGainsType = radio_group.active === 0 ? capital_gains_no : capital_gains_yes;
  ref.data = eval(capitalGainsType.data.source_ids[elasticity_option.active]).data;
  ref.trigger('change');
""")


# create layout -----------------
controls = column(radio_group_text,
                  radio_group,
                  elasticity_text,
                  elasticity_option)

plots = dict(header=title_div, left=controls, center=fig)
script, divs = components(plots)

template_args = dict()
template_args['bokeh_script'] = script
template_args['plots'] = divs
template_args['page_title'] = 'Box Plot'
render_template('responsive', template_args, 'index.html')
