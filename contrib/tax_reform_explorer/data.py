import pandas as pd
import numpy as np
from taxcalc.records import Records
from taxcalc import Policy, Records, Calculator
from taxcalc.utils import *
from taxcalc.records import Records
from taxcalc import Policy, Records, Calculator, Behavior, behavior

from pdb import set_trace

EPSILON = 1e-3

def get_diff(calcX, calcY, name):
    df_x = results(calcX)
    df_y = results(calcY)

    df_x = add_income_bins(df_x, compare_with = 'webapp', income_measure='c00100')
    df_y = add_income_bins(df_y, compare_with = 'webapp', income_measure='c00100')

    gp_x = df_x.groupby('bins', as_index=True)
    gp_y = df_y.groupby('bins', as_index=True)

    wgtm_x = gp_x.apply(weighted_mean, '_combined')
    wgtm_y = gp_y.apply(weighted_mean, '_combined')

    w_x = DataFrame( data=wgtm_x, columns=['w_mean'])
    w_y = DataFrame( data=wgtm_y, columns=['w_mean'])
    index = w_x.index.values

    w_x['bins'] = np.arange(1, len(WEBAPP_INCOME_BINS))
    w_y['bins'] = np.arange(1, len(WEBAPP_INCOME_BINS))

    merged = pd.concat( [w_x, w_y], axis=1, ignore_index=True)
    merged.drop(merged.columns[[1,3]], axis=1, inplace=True)

    merged.columns = ['base','reform']
    indexed = merged.reset_index([index])

    indexed.to_csv('{}_diff.csv'.format(name),float_format = '%1.3f',sep=',',header = True, index =False)

def weighted(agg, col_name):
    return (float((agg[col_name] * agg['s006']).sum())/
            ((agg['s006']).sum() + EPSILON))

def add_income_bins2(df, num_bins, tab):
    df.sort(tab, inplace=True)
    df['cumsum_weights'] = np.cumsum(df['s006'].values)
    max_ = df['cumsum_weights'].values[-1]
    bin_edges = [0] + list(np.arange(1, (num_bins+1)) * (max_ / float(num_bins)))
    labels = range(1, (num_bins+1))
    df['bins'] = pd.cut(df['cumsum_weights'], bins=bin_edges, labels=labels)
    mean_income = df[['_expanded_income', 'bins']].groupby('bins').mean()
    return df, mean_income

def print_data(calcX, calcY, weights, tab, name):
    df_x = results(calcX)
    df_y = results(calcY)

    id_itemizers_x = ((calcX.records.c04470 > 0) & (calcX.records.c00100 > 0))
    id_itemizers_y = ((calcY.records.c04470 > 0) & (calcY.records.c00100 > 0))
    df_x['pct_itm'] = id_itemizers_x
    df_y['pct_itm'] = id_itemizers_y


    df_y[tab] = df_x[tab]

    df_x, mean_inc_x = add_income_bins2(df_x, 100, tab)
    df_y, mean_inc_y = add_income_bins2(df_y, 100, tab)

    df_filtered_x = df_x.copy()
    df_filtered_y = df_y.copy()

    gp_x = df_filtered_x.groupby('bins', as_index=False)
    gp_y = df_filtered_y.groupby('bins', as_index=False)

    wgtpct_x = gp_x.apply(weights, 'pct_itm')
    wgtpct_y = gp_y.apply(weights, 'pct_itm')

    wpct_x = DataFrame( data=wgtpct_x, columns=['w_pct'])
    wpct_y = DataFrame( data=wgtpct_y, columns=['w_pct'])

    wpct_x['bins'] = np.arange(1, 101)
    wpct_y['bins'] = np.arange(1, 101)

    rsltx = pd.merge(df_filtered_x[['bins']], wpct_x, how='left')
    rslty = pd.merge(df_filtered_y[['bins']], wpct_y, how='left')

    df_filtered_x['w_pct'] = rsltx['w_pct'].values
    df_filtered_y['w_pct'] = rslty['w_pct'].values

    df_filtered_x.drop_duplicates(subset = 'bins', inplace = True)
    df_filtered_y.drop_duplicates(subset = 'bins', inplace = True)

    df_filtered_x = df_filtered_x['w_pct']
    df_filtered_y = df_filtered_y['w_pct']

    merged = pd.concat([df_filtered_x, df_filtered_y], axis=1, ignore_index=True)
    merged['mean_income'] = mean_inc_x['_expanded_income'].values
    merged.columns = ['base','reform','mean_income']

    merged.to_csv('{}_data.csv'.format(name),float_format = '%1.3f',sep=',',header = True, index =False)

RES_COLUMNS = STATS_COLUMNS + ['e00200'] + ['MARS'] + ['n24']
def results(c):
    outputs = []
    for col in RES_COLUMNS:
        if hasattr(c.policy, col):
            outputs.append(getattr(c.policy, col))
        else:
            outputs.append(getattr(c.records, col))
    return DataFrame(data=np.column_stack(outputs), columns=RES_COLUMNS)

def main(name, reform):

    puf = pd.read_csv("./puf.csv")
    policy_base = Policy(start_year=2013)
    records_base = Records(puf)
    policy_reform = Policy()
    records_reform = Records(puf)
    calcbase = Calculator(policy = policy_base, records = records_base)
    calcreform = Calculator(policy = policy_reform, records = records_reform)
    policy_reform.implement_reform(reform)
    calcbase.advance_to_year(2016)
    calcreform.advance_to_year(2016)
    calcbase.calc_all()
    calcreform.calc_all()
    get_diff(calcbase, calcreform, name)
    print_data(calcbase, calcreform, weights = weighted, tab = 'c00100', name=name)

if __name__ == '__main__':
    reform_values = (0,1,)
    groups = {}
    for i in range(2):
        for j in range(2):
            for k in range(2):
                reform = {
                          2016:{
                        "_ID_InterestPaid_HC":[reform_values[i]],
                        "_ID_StateLocalTax_HC":[reform_values[j]],
                        "_ID_RealEstate_HC":[reform_values[j]],
                        "_ID_Charity_HC":[reform_values[k]]
                    }
                }
                groups[''.join(['ds_', str(i), str(j), str(k)])] = reform

    for name, reform in groups.items():
        main(name, reform)
