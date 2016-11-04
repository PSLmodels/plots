import pandas as pd
import numpy as np
import sys
from taxcalc.records import Records
from taxcalc import *
from taxcalc.utils import *

puf = pd.read_csv("puf.csv")
policy_base = Policy()
records_base = Records(puf)
consump = Consumption()

policy_T = Policy()
records_reform = Records(puf)
consump_T = Consumption()

policy_H = Policy()
records_org = Records(puf)
consump_H = Consumption()

calcbase = Calculator(policy = policy_base, records = records_base,consumption=consump)
calc_T = Calculator(policy = policy_T, records = records_reform,consumption=consump_T)
calc_H = Calculator(policy = policy_H, records = records_org,consumption=consump_H)

reform_H= {
    2017: {'_AGI_surtax_thd': [[5000000, 5000000, 5000000, 5000000, 5000000, 5000000]],
           '_AGI_surtax_trt': [0.04],
           '_FST_AGI_trt':[0.3],
           '_ID_BenefitCap_rt': [0.28],
           '_ACTC_Income_thd': [0],
           '_CTC_c': [2000]
        }}

reform_T = {
    2017: {'_II_rt1': [0.12],
           '_II_brk1': [[37500, 75000, 37500, 37500, 75000, 37500]],
           '_II_rt2': [0.25],
           '_II_brk2': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_II_rt3': [0.25],
           '_II_brk3': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_II_rt4': [0.25],
           '_II_brk4': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_II_rt5': [0.25],
           '_II_brk5': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_II_rt6': [0.25],
           '_II_brk6': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_II_rt7': [0.33],
           '_PT_rt1': [0.12],
           '_PT_brk1': [[37500, 75000, 37500, 37500, 75000, 37500]],
           '_PT_rt2': [0.25],
           '_PT_brk2': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_PT_rt3': [0.25],
           '_PT_brk3': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_PT_rt4': [0.25],
           '_PT_brk4': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_PT_rt5': [0.25],
           '_PT_brk5': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_PT_rt6': [0.25],
           '_PT_brk6': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_PT_rt7': [0.33],
           '_CG_thd1': [[37500, 75000, 37500, 37500, 75000, 37500]],
           '_CG_thd2': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_AMT_CG_thd1': [[37500, 75000, 37500, 37500, 75000, 37500]],
           '_AMT_CG_thd2': [[112500, 225000, 112500, 112500, 225000, 112500]],
           '_AMT_trt1':[0],
           '_AMT_trt2':[0],
           '_NIIT_trt':[0],
           '_STD': [[15000,30000,15000,15000,12600, 6300, 1050]],
           '_II_em': [0],
           '_ID_BenefitSurtax_crt': [0.0],
           '_ID_BenefitSurtax_trt': [1.0],
           '_ID_BenefitSurtax_em': [[100000, 200000, 100000, 100000, 200000, 100000]]
        }}

policy_T.implement_reform(reform_T)
policy_H.implement_reform(reform_H)
calcbase.advance_to_year(2017)
calc_T.advance_to_year(2017)
calc_H.advance_to_year(2017)

calcbase.calc_all()
calc_T.calc_all()
calc_H.calc_all()

def source_data(data_1, data_2):
    data_1.index = (data_1.reset_index()).index
    data_2.index = (data_2.reset_index()).index
    df = data_1
    df['reform_2'] = data_2['reform']
    return df


source1 =mtr_graph_data(calcbase,calc_T,mars = 1,income_measure = 'wages', dollar_weighting = True)
source2 =mtr_graph_data(calcbase,calc_H,mars = 1,income_measure = 'wages', dollar_weighting = True)
source_sin = source_data(source1,source2)
source1 =mtr_graph_data(calcbase,calc_T,mars = 2,income_measure = 'wages', dollar_weighting = True)
source2 =mtr_graph_data(calcbase,calc_H,mars = 2,income_measure = 'wages', dollar_weighting = True)
source_ma = source_data(source1,source2)
source1 =mtr_graph_data(calcbase,calc_T,mars = 4,income_measure = 'wages', dollar_weighting = True)
source2 =mtr_graph_data(calcbase,calc_H,mars = 4,income_measure = 'wages', dollar_weighting = True)
source_HH = source_data(source1,source2)
source_sin.index = range(0,100)
source_ma.index = range(100,200)
source_HH.index = range(200,300)
result = pd.concat([source_sin, source_ma, source_HH], axis=1)
result.to_csv('mtr_data_2.csv', index= False)
