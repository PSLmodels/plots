from __future__ import print_function
import pandas as pd
import numpy as np
from taxcalc.records import Records
from taxcalc import Policy, Records, Calculator
from taxcalc.utils import *
from taxcalc.records import Records
from taxcalc import Policy, Records, Calculator, Behavior, behavior

EPSILON = 1e-3
CURRENT_YEAR = 2016

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
    return merged

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
    mean_income = df[['c00100', 'bins']].groupby('bins').mean()
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
    merged['mean_income'] = mean_inc_x['c00100'].values
    merged.columns = ['base','reform','mean_income']

    return merged


def diff_in_revenue(reform_on_II, orig_reform):
    policy_func = Policy()
    puf = pd.read_csv("./puf.csv")
    records_func = Records(puf)
    calc_func = Calculator(policy = policy_func, records = records_func)
    policy_bench = Policy()
    records_bench = Records(puf)
    calc_bench = Calculator(policy = policy_bench, records = records_bench)
    reform = {
        CURRENT_YEAR:{
        "_II_rt1":[max(policy_bench._II_rt1[0] *(1 - reform_on_II),0.0)],
        "_II_rt2":[max(policy_bench._II_rt2[0] *(1 - reform_on_II),0.0)],
        "_II_rt3":[max(policy_bench._II_rt3[0] *(1 - reform_on_II),0.0)],
        "_II_rt4":[max(policy_bench._II_rt4[0] *(1 - reform_on_II),0.0)],
        "_II_rt5":[max(policy_bench._II_rt5[0] *(1 - reform_on_II),0.0)],
        "_II_rt6":[max(policy_bench._II_rt6[0] *(1 - reform_on_II),0.0)],
        "_II_rt7":[max(policy_bench._II_rt7[0] *(1 - reform_on_II),0.0)]}
    }
    policy_func.implement_reform(reform)
    policy_func.implement_reform(orig_reform)
    calc_func.advance_to_year(CURRENT_YEAR)
    calc_bench.advance_to_year(CURRENT_YEAR)
    calc_func.calc_all()
    calc_bench.calc_all()
    ans = ((calc_bench.records._combined*calc_bench.records.s006).sum()-(calc_func.records._combined*calc_func.records.s006).sum())
    print("diff in revenue is ", ans)
    return ans


def reform_equiv(orig_reform, epsilon):
    upp = 1
    low = 0
    mid = (upp + low)/2.0
    while (upp - low)/2.0 > epsilon:
        delta = diff_in_revenue(mid,orig_reform)
        if delta == 0:
            return mid
        elif delta < 0:
            low = mid
        else:
            upp = mid
        mid = (upp + low)/2.0
    return mid


def agg_diff(calcX, calcY):
    df_x = results(calcX)
    df_y = results(calcY)
    agg_x = sum(df_x['_combined']*df_x['s006'])
    agg_y = sum(df_y['_combined']*df_y['s006'])
    agg_dif = agg_y - agg_x
    return agg_dif


def agg_num_delta(calcX, calcY):
    df_x = results(calcX)
    df_y = results(calcY)
    id_itemizers_x = ((calcX.records.c04470 > 0) & (calcX.records.c00100 > 0))
    id_itemizers_y = ((calcY.records.c04470 > 0) & (calcY.records.c00100 > 0))
    df_x['pct_itm'] = id_itemizers_x
    df_y['pct_itm'] = id_itemizers_y
    itm_x = sum(df_x['pct_itm'] * df_x['s006'])
    itm_y = sum(df_y['pct_itm'] * df_y['s006'])
    agg_num_d= itm_y - itm_x
    return agg_num_d


RES_COLUMNS = STATS_COLUMNS + ['e00200'] + ['MARS'] + ['n24']
def results(c):
    outputs = []
    for col in RES_COLUMNS:
        if hasattr(c.policy, col):
            outputs.append(getattr(c.policy, col))
        else:
            outputs.append(getattr(c.records, col))
    return DataFrame(data=np.column_stack(outputs), columns=RES_COLUMNS)

def run_reform(name, reform, epsilon):

    puf = pd.read_csv("./puf.csv")
    policy_base = Policy(start_year=2013)
    records_base = Records(puf)
    policy_reform = Policy()
    records_reform = Records(puf)
    calcbase = Calculator(policy = policy_base, records = records_base)
    calcreform = Calculator(policy = policy_reform, records = records_reform)
    policy_reform.implement_reform(reform)
    calcbase.advance_to_year(CURRENT_YEAR)
    calcreform.advance_to_year(CURRENT_YEAR)
    calcbase.calc_all()
    calcreform.calc_all()
    diff_df = get_diff(calcbase, calcreform, name)
    data_df = print_data(calcbase, calcreform, weights = weighted, tab = 'c00100', name=name)
    equiv_tax_cut = reform_equiv(reform, epsilon)
    total_rev_raise = agg_diff(calcbase, calcreform)
    delta_num_filers = agg_num_delta(calcbase, calcreform)

    #diff_df['equiv_rate_cut'] = len(diff_df)*[equiv_tax_cut]
    return diff_df, data_df, equiv_tax_cut, total_rev_raise, delta_num_filers

def get_source_data():
    reform_values = (0,1,)
    groups = {}
    for i in range(2):
        for j in range(2):
            for k in range(2):
                reform = {
                          CURRENT_YEAR:{
                        "_ID_InterestPaid_HC":[reform_values[i]],
                        "_ID_StateLocalTax_HC":[reform_values[j]],
                        "_ID_RealEstate_HC":[reform_values[j]],
                        "_ID_Charity_HC":[reform_values[k]]
                    }
                }
                groups[''.join(['ds_', str(i), str(j), str(k)])] = reform

    dataframes = {}
    eps = 1e-4
    for name, reform in groups.items():
        diff_df, data_df, tax_cut, total_rev, delta_filers = run_reform(name, reform, eps)
        dataframes[name + '_data'] = data_df
        dataframes[name + '_diff'] = diff_df
        dataframes[name + '_taxcut'] = tax_cut if tax_cut > eps else 0.
        dataframes[name + '_revenue'] = total_rev
        dataframes[name + '_filers'] = delta_filers

    return dataframes
