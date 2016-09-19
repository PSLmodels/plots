import pandas as pd

from os import path

from jinja2 import Environment, FileSystemLoader
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import Legend
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import Plot, Text, Circle, Range1d
from bokeh.plotting import Figure

from styles import (PLOT_FORMATS, RED, BLUE)


def  output_page(**kwargs):
    here = path.dirname(path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(here), trim_blocks=True)
    content = j2_env.get_template('template.j2').render(**kwargs)
    with open('index.html', 'w') as output_file:
        output_file.write(content)


# load data
df = pd.read_csv("resources/by_asset_bonus_phaseout.csv")
df = df[~df['asset_category'].isin(['Intellectual Property','Land','Inventories'])].copy()
df = df.where((pd.notnull(df)), 'null')

SIZES = list(range(12, 30, 8))
df['size'] = pd.qcut(df['assets_c'].values, len(SIZES), labels=SIZES)
#df = df.where((pd.notnull(df)), 'null')

# divide up equipment vs. structures
equipment_df = df[(~df.asset_category.str.contains('Structures')) & (~df.asset_category.str.contains('Buildings'))]
structure_df = df[(df.asset_category.str.contains('Structures')) | (df.asset_category.str.contains('Buildings'))]

data_sources = {}
format_fields = ['mettr_c_2016', 'mettr_c_2018', 'mettr_c_2019', 'mettr_c_2020']
for f in format_fields:
    equipment_copy = equipment_df.copy()
    equipment_copy['reform'] = equipment_copy[f]
    equipment_copy['baseline'] = equipment_copy['mettr_c_2016']
    equipment_copy['hover'] = equipment_copy.apply(lambda x: "{0:.1f}%".format(x[f] * 100), axis=1)
    equipment_copy['hover2016'] = equipment_copy.apply(lambda x: "{0:.1f}%".format(x['mettr_c_2016'] * 100), axis=1)

    data_sources['equipment_' + f] = ColumnDataSource(equipment_copy)

fudge_factor = '                          ' # this a spacer for the y-axis label
for f in format_fields:
    structure_copy = structure_df.copy()
    structure_copy['reform'] = structure_copy[f]
    structure_copy['baseline'] = structure_copy['mettr_c_2016']
    structure_copy['hover'] = structure_copy.apply(lambda x: "{0:.1f}%".format(x[f] * 100), axis=1)
    structure_copy['short_category'].str.replace('Residential Bldgs', fudge_factor + 'Residential Bldgs')
    data_sources['structure_' + f] = ColumnDataSource(structure_copy)

equipment_assets = ['Computers and Software',
                    'Instruments and Communications',
                    'Office and Residential',
                    'Transportation',
                    'Industrial Machinery',
                    'Other Industrial',
                    'Other']

structure_assets = [fudge_factor + 'Residential Bldgs',
                    'Nonresidential Bldgs',
                    'Mining and Drilling',
                    'Other']


# top plot
p = figure(plot_height=230,
           plot_width=990,
           x_range = (-.05, .5),
           y_range=list(reversed(equipment_assets)),
           x_axis_location="above",
           tools='hover',
           **PLOT_FORMATS)

hover = p.select(dict(type=HoverTool))
hover.tooltips = [('Asset', ' @Asset (@hover)')]
p.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p.yaxis.axis_label = "Equipment"
p.toolbar_location = None
p.min_border_right = 5


p.circle(x='baseline',
         y='short_category',
         color="#AAAAAA",
         size='size',
         line_color="#333333",
         line_alpha=.1,
         fill_alpha=0,
         source=ColumnDataSource(data_sources['equipment_mettr_c_2016'].data),
         alpha=.4)

equipment_renderer = p.circle(x='reform',
                              y='short_category',
                              color=BLUE,
                              size='size',
                              line_color="white",
                              source=data_sources['equipment_mettr_c_2016'],
                              alpha=.4)


# bottom plot
p2 = figure(plot_height=160,
            plot_width=990,
            x_range = (-.05, .5),
            y_range=list(reversed(structure_assets)),
            tools='hover',
            **PLOT_FORMATS)


hover = p2.select(dict(type=HoverTool))
hover.tooltips = [('Asset', ' @Asset (@hover)')]
p2.xaxis.axis_label = "Marginal Effective Tax Rate"
p2.xaxis[0].formatter = NumeralTickFormatter(format="0.1%")
p2.yaxis.axis_label = "Structures"
p2.toolbar_location = None
p2.min_border_right = 5
p2.outline_line_alpha = 0.2


p2.circle(x='baseline',
          y='short_category',
          color=RED,
          size='size',
          line_color="#333333",
          line_alpha=.1,
          fill_alpha=0,
          source=ColumnDataSource(data_sources['structure_mettr_c_2016'].data),
          alpha=.4)


structure_renderer = p2.circle(x='reform',
                               y='short_category',
                               color=BLUE,
                               size='size',
                               line_color="white",
                               source=data_sources['structure_mettr_c_2016'],
                               alpha=.4)


plots = dict(metr=column(p, p2))
script, divs = components(plots)
output_page(bokeh_script=script,
            equipment_plot_id=p._id,
            equipment_renderer_id=equipment_renderer._id,
            structure_plot_id=p2._id,
            structure_renderer_id=structure_renderer._id,
            data_sources={k:v.data for k, v in data_sources.items()},
            plots=divs)
