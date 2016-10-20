import csv
import numpy as np
from bokeh.plotting import output_file, figure, show
from bokeh.models import Label, LabelSet, NumeralTickFormatter, FixedTicker, FuncTickFormatter, BoxAnnotation, Span, ColumnDataSource

#create list of lists containing data
tax_rates_file = open('baseline_byindustry_no_bonus.csv')
csv_tax_rates = csv.reader(tax_rates_file)
tax_rates = list(csv_tax_rates)
tax_rates_file.close()

#calculate values for traditionally financed c-corp
metr_c_std = []
for index in range(1,len(tax_rates)):
	metr_c_std.append(float(tax_rates[index][9]))
metr_c_std_high = max(metr_c_std)
metr_c_std_avg = np.mean(metr_c_std)
metr_c_std_low = min(metr_c_std)

#calculate values for debt financed c-corp
metr_c_debt = []
for index in range(1,len(tax_rates)):
	metr_c_debt.append(float(tax_rates[index][10]))
metr_c_debt_high = max(metr_c_debt)
metr_c_debt_avg = np.mean(metr_c_debt)
metr_c_debt_low = min(metr_c_debt)

#calculate values for equity financed c-corp
metr_c_equity = []
for index in range(1,len(tax_rates)):
	metr_c_equity.append(float(tax_rates[index][11]))
metr_c_equity_high = max(metr_c_equity)
metr_c_equity_avg = np.mean(metr_c_equity)
metr_c_equity_low = min(metr_c_equity)

#calculate values for traditionally financed pass through entity
metr_nc_std = []
for index in range(1,len(tax_rates)):
	metr_nc_std.append(float(tax_rates[index][23]))
metr_nc_std_high = max(metr_nc_std)
metr_nc_std_avg = np.mean(metr_nc_std)
metr_nc_std_low = min(metr_nc_std)

#calculate values for debt financed pass through entity
metr_nc_debt = []
for index in range(1,len(tax_rates)):
	metr_nc_debt.append(float(tax_rates[index][24]))
metr_nc_debt_high = max(metr_nc_debt)
metr_nc_debt_avg = np.mean(metr_nc_debt)
metr_nc_debt_low = min(metr_nc_debt)

#calculate values for equity financed c-corp
metr_nc_equity = []
for index in range(1,len(tax_rates)):
	metr_nc_equity.append(float(tax_rates[index][25]))
metr_nc_equity_high = max(metr_nc_equity)
metr_nc_equity_avg = np.mean(metr_nc_equity)
metr_nc_equity_low = min(metr_nc_equity)


#output to static html file
output_file("metr_boxplot.html")

#create data arrays to be plotted
types = ["Typically Financed", "Debt Financed", "Equity Financed", "Typically Financed", "Debt Financed", "Equity Financed"] 
typeNums = [0,1,2,3,4,5]
highs = [metr_c_std_high, metr_c_debt_high, metr_c_equity_high, metr_nc_std_high, metr_nc_debt_high, metr_nc_equity_high]
avgs = [metr_c_std_avg, metr_c_debt_avg, metr_c_equity_avg, metr_nc_std_avg, metr_nc_debt_avg, metr_nc_equity_avg]
lows = [metr_c_std_low, metr_c_debt_low, metr_c_equity_low, metr_nc_std_low, metr_nc_debt_low, metr_nc_equity_low]

source = ColumnDataSource(data=dict(highs=highs,avgs=avgs,lows=lows,
									types=types,typeNums=typeNums,
									letters=["A","B","C","D","E","F"]))

#create figure on which to plot
p = figure(plot_width = 800, plot_height = 500,x_range=(-1,6), y_range = (-0.8,0.5))

#format graph title
p.title.text = "Marginal Effective Tax Rates"
p.title.align = 'center'
p.title.text_font_size = '16pt'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#line separating positive and negative rates
zline = Span(location=0, dimension='width', line_color='gray', line_width=2)
p.renderers.extend([zline])

#format labels
p.xaxis.axis_label = "Entity type"
p.xaxis[0].ticker=FixedTicker(ticks=typeNums)
#done as a custom function instead of a categorical axis because 
#categorical axes do not work well with other features
p.xaxis.formatter=FuncTickFormatter(code="""
	function (tick) {
		var types = ["Typically Financed", "Debt Financed", "Equity Financed", "Typically Financed", "Debt Financed", "Equity Financed"]
		return types[tick]
	};
""")
p.yaxis[0].formatter = NumeralTickFormatter(format="0%")

#draw ranges onto graph	
p.segment(typeNums, lows, typeNums, highs, color="black", line_width=2)
p.circle(typeNums, highs, size=10, color = "red")
p.circle(typeNums, avgs, size=10, color = "blue")
p.circle(typeNums, lows, size=10, color = "green")

#add coloring for corp vs pass-through regions
pass_through_box = BoxAnnotation(left=2.5, fill_alpha=0.1, fill_color='olive')
p.add_layout(pass_through_box) 
ccorp_box = BoxAnnotation(right=2.5, fill_alpha=0.1, fill_color='gray')
p.add_layout(ccorp_box) 

labels = LabelSet(x='types', y='highs', text='letters', level='glyph',
              x_offset=0, y_offset=0, source=source, render_mode='canvas')
p.add_layout(labels)


show(p)


