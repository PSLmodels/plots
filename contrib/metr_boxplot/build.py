import csv
import numpy as np
from bokeh.plotting import output_file, figure, show
from bokeh.models import (
	NumeralTickFormatter, FixedTicker, FuncTickFormatter, Span, ColumnDataSource, 
	HoverTool, BoxAnnotation, CustomJS)
from bokeh.models.widgets import Slider, Toggle
from bokeh.layouts import column

#create list of lists containing data
tax_rates_file = open('resources/btax_dot_plot_data_by_asset.csv')
csv_tax_rates = csv.reader(tax_rates_file)
tax_rates = list(csv_tax_rates)
tax_rates_file.close()

#For a given statistic, finds the max, avg and min values as well as the
#industries associated with the max and min
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
	
	summary.append(tax_rates[values.index(max(values))+1][0])
	summary.append(tax_rates[values.index(min(values))+1][0])
	
	return summary

#create a column data source for the base policy
def make_base_source():
	standard = prepare_values(1)
	debt = prepare_values(3)
	equity = prepare_values(2)
	
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
	for policy in range(1,3):
		standard = prepare_values(policy*3+1)
		debt = prepare_values(policy*3+3)
		equity = prepare_values(policy*3+2)
		
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

base_source = make_base_source()
sources = make_reform_sources()
ref_source = sources['_1']

#I have no idea why this step is necessary, but its the only way it can be passed to js
dictionary_of_sources = {1 : '_1', 2: '_2'}
js_source_array = str(dictionary_of_sources).replace("'","")

#output to static html file
output_file("mettr_reform_boxplot.html")

#create figure on which to plot
p = figure(plot_width = 500, plot_height = 500, x_range=(-0.5,2.5), tools=[])

#format graph title
p.title.text = "Marginal Effective Tax Rates"
p.title.align = 'center'
p.title.text_font_size = '16pt'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#format axis labels
p.xaxis.axis_label = "Entity Type"
p.xaxis[0].ticker=FixedTicker(ticks=[0,1,2])
#done as a custom function instead of a categorical axis because 
#categorical axes do not work well with other features
p.xaxis.formatter=FuncTickFormatter(code="""
	function (tick) {
		var types = ["Typically Financed", "Debt Financed", "Equity Financed"]
		return types[tick]
	};
""")
p.yaxis[0].formatter = NumeralTickFormatter(format="0%")

#line separating positive and negative rates
zline = Span(location=0, dimension='width', line_color='gray', line_width=2)
p.renderers.extend([zline])

#color different regions
standard_region = BoxAnnotation(right=0.5, fill_alpha=0.2, fill_color='lightblue')
debt_region = BoxAnnotation(left=0.5, right=1.5, fill_alpha=0.1, fill_color='gray')
equity_region = BoxAnnotation(left=1.5, fill_alpha=0.2, fill_color='lightblue')

p.add_layout(standard_region)
p.add_layout(debt_region)
p.add_layout(equity_region)

#draw baseline ranges onto graph	
p.segment('positions', 'lows', 'positions', 'highs', color="black", 
	line_width=2, source=base_source)
p.circle('positions', 'rates', size=12, color = "green", source=base_source)

#draw reformed ranges onto graph	
p.segment('positions', 'lows', 'positions', 'highs', color="blue", 
	line_width=2, source=ref_source)
p.circle('positions', 'rates', size=12, color = "green", source=ref_source)

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
		var input = slider.value,
			sources = %s,
			new_source_data = sources[input].data;
		ref_source.data = new_source_data;
	""" % js_source_array
	
test_code = """
		window.alert(slider.value);
	"""

callback = CustomJS(args=sources, code=source_change_code)
slider = Slider(start=1, end=2, value=1, step=1, title="reform", callback=callback) 
callback.args['slider'] = slider
callback.args['ref_source'] = ref_source

#display the graph
layout = column(p, slider)
show(layout)


