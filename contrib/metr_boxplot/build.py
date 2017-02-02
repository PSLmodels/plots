import csv
import numpy as np
import pandas as pd
from os import path
from jinja2 import Environment, FileSystemLoader
from bokeh.plotting import output_file, figure, show
from bokeh.models import (
    NumeralTickFormatter, FixedTicker, FuncTickFormatter, Span, ColumnDataSource,
    HoverTool, BoxAnnotation, CustomJS, PrintfTickFormatter)
from bokeh.models.widgets import Slider, RadioButtonGroup, Paragraph
from bokeh.layouts import column, row, widgetbox
from bokeh.embed import components

from styles import (PLOT_FORMATS,
                    AXIS_FORMATS,
                    FONT_PROPS_SM,
                    DARK_GRAY,
                    GREEN,
                    PURPLE,
                    RED,
                    BLUE)

#create list of lists containing data
tax_rates_file = open('resources/reforms_for_boxplot.csv')
csv_tax_rates = csv.reader(tax_rates_file)
tax_rates = list(csv_tax_rates)
tax_rates_file.close()

# Function to help with format
def  output_page(**kwargs):
    here = path.dirname(path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open('index.html', 'w') as output_file:
        output_file.write(content)

#For a given statistic, finds the max, avg and min values as well as the
#industries/asset type associated with the max and min
def prepare_values(column):

    summary = []
    values = []

    assets = []
    weighted_rates = []
    for index in range(1, len(tax_rates)):
        assets.append(float(tax_rates[index][10]))
    total_assets = sum(assets)


    #read statistic values in from array
    for index in range(1,len(tax_rates)):
        values.append(float(tax_rates[index][column]))

    #add max, avg and min values to summary
    summary.append(max(values))

    summary.append(np.mean(values))
    summary.append(min(values))

    summary.append(tax_rates[values.index(max(values))+1][1])
    summary.append(tax_rates[values.index(min(values))+1][1])

    return summary

#create a column data source for the base policy
def make_base_source():
    standard = prepare_values(40)
    debt = prepare_values(41)
    equity = prepare_values(42)

    lows = [standard[2], debt[2], equity[2]]
    highs = [standard[0], debt[0], equity[0]]
    rates = [standard[0], debt[0], equity[0], standard[1], debt[1], equity[1],
        standard[2], debt[2], equity[2]]
    industries = [standard[3], debt[3], equity[3], "Average", "Average", "Average",
        standard[4], debt[4], equity[4]]

    percents = []
    for rate in rates:
        percents.append(str(round(rate*100,1)) + "%")

    types = ["Typically Financed", "Debt Financed", "Equity Financed"]
    typeNums = [0,1,2]
    typeNums_left = [-0.1, 0.9, 1.9]
    positions = [-0.1, 0.9, 1.9, -0.1, 0.9, 1.9, -0.1, 0.9, 1.9]

    source = ColumnDataSource(
        data=dict(
            positions = positions,
            rates = rates,
            highs = highs+highs+highs,
            lows = lows+lows+lows,
            industries = industries,
            percents = percents
        )
    )

    return source

#create an array of column data sources for the possible reforms
def make_reform_sources():
    sources={}
    for policy in range(0,56):
        standard = prepare_values(policy*3+4)
        debt = prepare_values(policy*3+5)
        equity = prepare_values(policy*3+6)

        lows = [standard[2], debt[2], equity[2]]
        highs = [standard[0], debt[0], equity[0]]
        rates = [standard[0], debt[0], equity[0], standard[1], debt[1], equity[1],
            standard[2], debt[2], equity[2]]
        industries = [standard[3], debt[3], equity[3], "Average", "Average", "Average",
            standard[4], debt[4], equity[4]]

        percents = []
        for rate in rates:
            percents.append(str(round(rate*100,1)) + "%")

        types = ["Typically Financed", "Debt Financed", "Equity Financed"]
        typeNums = [0,1,2]
        typeNums_right = [0.1, 1.1, 2.1]
        positions = [0.1, 1.1, 2.1, 0.1, 1.1, 2.1, 0.1, 1.1, 2.1]

        source = ColumnDataSource(
            data=dict(
                positions = positions,
                rates = rates,
                highs = highs+highs+highs,
                lows = lows+lows+lows,
                industries = industries,
                percents = percents
            )
        )

        sources['_' + str(policy)] = source

    return sources

sources = make_reform_sources()
base_source = make_base_source()
ref_source = ColumnDataSource(sources['_12'].data)

#I have no idea why this step is necessary, but its the only way it can be passed to js
policy_indices = []
for i in range(0,56):
    policy_indices.append(i)
policy_indices_underscore = []
for i in range(0,56):
    policy_indices_underscore.append("_" + str(i))
dict_of_sources = dict(zip(policy_indices, policy_indices_underscore))
js_source_array = str(dict_of_sources).replace("'","")

#output to static html file
output_file("mettr_reform_boxplot.html")

#create figure on which to plot
p = figure(plot_width = 500, plot_height = 500, x_range=(-0.5,2.5), tools=[])

#format graph title
# p.title.text = "The CIT and Investment Incentives"
# p.title.align = 'center'
# p.title.text_font_size = '16pt'
# p.title.text_font = 'Helvetica'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#format axis labels
p.xaxis.axis_label = "Method of Financing"
p.xaxis[0].ticker=FixedTicker(ticks=[0,1,2])
#done as a custom function instead of a categorical axis because
#categorical axes do not work well with other features
p.xaxis.formatter=FuncTickFormatter(code="""
    function (tick) {
        var types = ["Typically Financed", "Debt Financed", "Equity Financed"]
        return types[tick]
    };
""")
p.yaxis.axis_label = "Marginal Effective Tax Rate"
p.yaxis[0].formatter = NumeralTickFormatter(format="0%")
#p.yaxis.bounds = (-90.0, 70.0)
p.y_range.start = -1.0
p.y_range.end = 0.70

#line separating positive and negative rates
zline = Span(location=0, dimension='width', line_alpha=0.2, line_width=2, line_dash='dashed')
p.renderers.extend([zline])

#color different regions
standard_region = BoxAnnotation(right=0.5, fill_alpha=0.2, fill_color='white')
debt_region = BoxAnnotation(left=0.5, right=1.5, fill_alpha=0.1, fill_color='white')
equity_region = BoxAnnotation(left=1.5, fill_alpha=0.2, fill_color='white')

p.add_layout(standard_region)
p.add_layout(debt_region)
p.add_layout(equity_region)

#draw baseline ranges onto graph
p.segment('positions', 'lows', 'positions', 'highs', color=BLUE,
    line_width=2, source=base_source)
p.circle('positions', 'rates', size=12, color = BLUE, source=base_source)

#draw reformed ranges onto graph
p.segment('positions', 'lows', 'positions', 'highs', color=RED,
    line_width=2, source=ref_source)
p.circle('positions', 'rates', size=12, color = RED, source=ref_source)

#display rate and asset type when hovering over a glyph
hover = HoverTool(
        tooltips = [
            ("Rate: ", "@percents"),
            ("Asset Type:",  "@industries"),
        ]
    )
p.add_tools(hover)

#javascript code to change the data source based on slider inputs
source_change_code = """
        var rate_option = rate.active,
            depreciation_option = depreciation.active
            deductibility_option = deductibility.active
            index = deductibility_option + depreciation_option*2 + rate_option*8
            sources = %s,
            new_source_data = sources[index].data;
        ref_source.data = new_source_data;
    """ % js_source_array

callback = CustomJS(args=sources, code=source_change_code)

rate_buttons = RadioButtonGroup(
            labels = ["39.6%", "35%", "30%", "25%", "20%", "15%", "0%"],
            active = 1,
            callback = callback,
            width = 500)
depreciation_buttons = RadioButtonGroup(
            labels = ["Economic", "Current Law, No Bonus", "Current Law", "Full Expensing"],
            active = 2,
            callback = callback,
            width = 500)
deductibility_buttons = RadioButtonGroup(
            labels = ["Fully Deductible", "Non-Deductible"],
            active = 0,
            callback = callback,
            width=500)

rate_label = Paragraph(text="Corporate Tax Rate")
depreciation_label = Paragraph(text="Depreciation System")
deductibility_label = Paragraph(text="Interest Deductibility")

callback.args['rate'] = rate_buttons
callback.args['depreciation'] = depreciation_buttons
callback.args['deductibility'] = deductibility_buttons
callback.args['ref_source'] = ref_source

#display the graph
option_widgets = widgetbox(children = [rate_label, rate_buttons,
                                       depreciation_label, depreciation_buttons,
                                       deductibility_label, deductibility_buttons])

#layout = row(p,option_widgets)
# layout = column(p, option_widgets)
# show(layout)
plots = dict(metr=column(p))
script, divs = components(plots)
output_page(bokeh_script=script,
            plot_id=p._id,
            plots=divs)
