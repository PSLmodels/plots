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


# Read in and format data for better handling
df = pd.DataFrame.from_csv('resources/reforms_for_boxplot.csv')

corp_rates = [{'btax_betr_corp': .396},{'btax_betr_corp': .35},{'btax_betr_corp': .30},
              {'btax_betr_corp': .25},{'btax_betr_corp': .20},
              {'btax_betr_corp': .15},{'btax_betr_corp': 0.}]
depr  = [{'btax_depr_3yr_tax_Switch': True, 'btax_depr_5yr_tax_Switch': True,
         'btax_depr_7yr_tax_Switch': True, 'btax_depr_10yr_tax_Switch': True,
         'btax_depr_15yr_tax_Switch': True, 'btax_depr_20yr_tax_Switch': True,
         'btax_depr_25yr_tax_Switch': True, 'btax_depr_27_5yr_tax_Switch': True,
         'btax_depr_39yr_tax_Switch': True, 'btax_depr_3yr_exp': 0.,
         'btax_depr_5yr_exp': 0.,'btax_depr_7yr_exp': 0.,'btax_depr_10yr_exp': 0.,
         'btax_depr_15yr_exp': 0.,'btax_depr_20yr_exp': 0., 'btax_depr_25yr_exp': 0.,
         'btax_depr_27_5yr_exp': 0.,'btax_depr_39yr_exp': 0.},{'btax_depr_3yr_exp': 0.,
         'btax_depr_5yr_exp': 0.,'btax_depr_7yr_exp': 0.,'btax_depr_10yr_exp': 0.,
         'btax_depr_15yr_exp': 0.,'btax_depr_20yr_exp': 0.,},{},
        {'btax_depr_3yr_exp': 100.,'btax_depr_5yr_exp': 100.,'btax_depr_7yr_exp': 100.,
        'btax_depr_10yr_exp': 100.,'btax_depr_15yr_exp': 100.,'btax_depr_20yr_exp': 100.,
        'btax_depr_25yr_exp': 100., 'btax_depr_27_5yr_exp': 100., 'btax_depr_39yr_exp': 100.,
        'btax_depr_expense_inventory':True,'btax_depr_expense_land':True}]
interest_hair = [{'btax_other_hair': 0.},{'btax_other_hair': 1.}]

plot_df = pd.DataFrame([['this','that','other', 0.0]], columns=['asset_name', 'rate_type', 'statistic', 'value'])
for tax in ('mettr_c_', 'metr_c_'):
    for fin in ('','d_','e_'):
        i_num = 0
        for i in range(len(corp_rates)):
            j_num = 0
            for j in range(len(depr)):
                m_num = 0
                for m in range(len(interest_hair)):
                    val1= df.loc[df[tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)].idxmax()][tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)]
                    rate_type1 = tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)
                    asset1 = df.loc[df[tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)].idxmax()]['Asset']

                    val2= df.loc[df[tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)].idxmin()][tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)]
                    rate_type2 = tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)
                    asset2 = df.loc[df[tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)].idxmin()]['Asset']

                    val3 = df.mean()[tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)]
                    rate_type3 = tax+fin+str(i_num)+'_'+str(j_num)+'_'+str(m_num)

                    # put values in dictionary and then append to df
                    out_dict  = {'value':(val1, val2, val3), 'rate_type':(rate_type1, rate_type2, rate_type3), 'statistic':('max','min','avg'),'asset_name':(asset1, asset2, 'Average')}
                    out_df = pd.DataFrame.from_dict(out_dict)
                    plot_df = (plot_df.append([out_df],ignore_index=True))#.copy().reset_index()

                    m_num+=1
                j_num+=1
            i_num+=1



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
def make_base_sources(plot_df):
    sources={}
    for tax in ('mettr', 'metr'):
        standard = plot_df[plot_df['rate_type']==tax+'_c_1_2_1']
        debt = plot_df[plot_df['rate_type']==tax+'_c_d_1_2_1']
        equity = plot_df[plot_df['rate_type']==tax+'_c_e_1_2_1']

        low_rates = [float(standard[standard['statistic']=='min']['value']), float(debt[debt['statistic']=='min']['value']), float(equity[equity['statistic']=='min']['value'])]
        high_rates = [float(standard[standard['statistic']=='max']['value']), float(debt[debt['statistic']=='max']['value']), float(equity[equity['statistic']=='max']['value'])]
        avg_rates = [float(standard[standard['statistic']=='avg']['value']), float(debt[debt['statistic']=='avg']['value']), float(equity[equity['statistic']=='avg']['value'])]
        rates = high_rates + avg_rates + low_rates
        low_assets = [(standard[standard['statistic']=='min']['asset_name']).values[0], (debt[debt['statistic']=='min']['asset_name']).values[0], (equity[equity['statistic']=='min']['asset_name']).values[0]]
        high_assets = [(standard[standard['statistic']=='max']['asset_name']).values[0], (debt[debt['statistic']=='max']['asset_name']).values[0], (equity[equity['statistic']=='max']['asset_name']).values[0]]
        avg_assets = [(standard[standard['statistic']=='avg']['asset_name']).values[0], (debt[debt['statistic']=='avg']['asset_name']).values[0], (equity[equity['statistic']=='avg']['asset_name']).values[0]]
        assets = high_assets + avg_assets + low_assets

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
                highs = high_rates+high_rates+high_rates,
                lows = low_rates+low_rates+low_rates,
                assets = assets,
                percents = percents
            )
        )

        sources[tax] = source

    return sources

#create an array of column data sources for the possible reforms
def make_reform_sources(plot_df):
    sources={}
    for tax in ('mettr', 'metr'):
        i_num = 0
        for i in range(len(corp_rates)):
            j_num = 0
            for j in range(len(depr)):
                m_num = 0
                for m in range(len(interest_hair)):
                    standard = plot_df[plot_df['rate_type']==tax+'_c_'+str(i_num)+'_'+str(j_num)+'_'+str(m_num)]
                    debt = plot_df[plot_df['rate_type']==tax+'_c_d_'+str(i_num)+'_'+str(j_num)+'_'+str(m_num)]
                    equity = plot_df[plot_df['rate_type']==tax+'_c_e_'+str(i_num)+'_'+str(j_num)+'_'+str(m_num)]

                    low_rates = [float(standard[standard['statistic']=='min']['value']), float(debt[debt['statistic']=='min']['value']), float(equity[equity['statistic']=='min']['value'])]
                    high_rates = [float(standard[standard['statistic']=='max']['value']), float(debt[debt['statistic']=='max']['value']), float(equity[equity['statistic']=='max']['value'])]
                    avg_rates = [float(standard[standard['statistic']=='avg']['value']), float(debt[debt['statistic']=='avg']['value']), float(equity[equity['statistic']=='avg']['value'])]
                    rates = high_rates + avg_rates + low_rates
                    low_assets = [(standard[standard['statistic']=='min']['asset_name']).values[0], (debt[debt['statistic']=='min']['asset_name']).values[0], (equity[equity['statistic']=='min']['asset_name']).values[0]]
                    high_assets = [(standard[standard['statistic']=='max']['asset_name']).values[0], (debt[debt['statistic']=='max']['asset_name']).values[0], (equity[equity['statistic']=='max']['asset_name']).values[0]]
                    avg_assets = [(standard[standard['statistic']=='avg']['asset_name']).values[0], (debt[debt['statistic']=='avg']['asset_name']).values[0], (equity[equity['statistic']=='avg']['asset_name']).values[0]]
                    assets = high_assets + avg_assets + low_assets

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
                            highs = high_rates+high_rates+high_rates,
                            lows = low_rates+low_rates+low_rates,
                            assets = assets,
                            percents = percents
                        )
                    )

                    sources[tax+'_'+str(i_num)+'_'+str(j_num)+'_'+str(m_num)] = source
                    m_num+=1
                j_num+=1
            i_num+=1

    return sources

reform_sources = make_reform_sources(plot_df)
base_sources = make_base_sources(plot_df)
base_source = ColumnDataSource(base_sources['mettr'].data)
ref_source = ColumnDataSource(reform_sources['mettr_1_2_1'].data)

#I have no idea why this step is necessary, but its the only way it can be passed to js
policy_indices = []
for tax in ('mettr', 'metr'):
    i_num = 0
    for i in range(len(corp_rates)):
        j_num = 0
        for j in range(len(depr)):
            m_num = 0
            for m in range(len(interest_hair)):
                policy_indices.append(tax+'_'+str(i_num)+'_'+str(j_num)+'_'+str(m_num))
                m_num+=1
            j_num+=1
        i_num+=1
dict_of_sources = dict(zip(policy_indices, policy_indices))
js_source_array = str(dict_of_sources).replace("'","")

# print 'js_source_array: ', js_source_array
# # quit()

#output to static html file
output_file("mettr_reform_boxplot.html")

#create figure on which to plot
p = figure(plot_width = 500, plot_height = 500, x_range=(-0.5,2.5), tools=[])

#format graph title
p.title.text = "Taxes and Investment Incentives"
p.title.align = 'center'
p.title.text_font_size = '16pt'
p.title.text_font = 'Helvetica'
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
p.circle('positions', 'rates', size=12, color = BLUE, source=base_source, legend="Baseline")

#draw reformed ranges onto graph
p.segment('positions', 'lows', 'positions', 'highs', color=RED,
    line_width=2, source=ref_source)
p.circle('positions', 'rates', size=12, color = RED, source=ref_source, legend="Reform")

p.legend.location = "bottom_right"

#display rate and asset type when hovering over a glyph
hover = HoverTool(
        tooltips = [
            ("Rate", "@percents"),
            ("Asset Type",  "@assets"),
        ]
    )
p.add_tools(hover)

#javascript code to change the data source based on slider inputs
reform_source_change_code = """
        var rate_option = rate.active,
            depreciation_option = depreciation.active
            deductibility_option = deductibility.active
            individual_option = individual.active
            tax = 'mettr_'
        if (individual.active == 1) {
            tax == 'metr_';
        } else {
            tax == 'mettr_';
        }
        var index = tax + String(rate_option) + '_' + String(depreciation_option) + '_' + String(deductibility_option)
            reform_sources = %s,
            new_source_data = reform_sources[index].data;
        ref_source.data = new_source_data;
    """ % js_source_array

callback = CustomJS(args=reform_sources, code=reform_source_change_code)
# base_source_change_code = """
#         var individual_option = individual.active
#             index = 'mettr'
#         if (individual_option == 1) {
#             index == 'metr';
#         }
#         var base_sources = %s,
#             new_source_data = base_sources[index].data;
#         base_source.data = new_source_data;
#     """
# callback = CustomJS(args=base_sources, code=base_source_change_code)

# Create buttons
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
individual_buttons = RadioButtonGroup(
            labels = ["Yes", "No"],
            active = 0,
            callback = callback,
            width=500)

rate_label = Paragraph(text="Corporate Tax Rate")
depreciation_label = Paragraph(text="Depreciation System")
deductibility_label = Paragraph(text="Interest Deductibility")
individual_label = Paragraph(text="Include Individual Income Taxes")

callback.args['rate'] = rate_buttons
callback.args['depreciation'] = depreciation_buttons
callback.args['deductibility'] = deductibility_buttons
callback.args['individual'] = individual_buttons
callback.args['ref_source'] = ref_source

#display the graph
option_widgets = widgetbox(children = [rate_label, rate_buttons,
                                       depreciation_label, depreciation_buttons,
                                       deductibility_label, deductibility_buttons,
                                       individual_label, individual_buttons])


layout = column(p, option_widgets)
show(layout)
