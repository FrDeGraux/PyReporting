import numpy as np
import pandas as pd
from utils.utilReader import read_positions
from utils.utilData import filterBySymbol
from scipy.optimize import minimize
import matplotlib.pyplot as plt
range_step = 50
def euros_to_pips(in_euro,in_point,in_volume) :

    if pd.isna(in_euro) :
        return np.nan
    res = (in_euro/in_point)
    res = in_volume*res
    return res*0.1
def add_points_level(positions) :
    positions['MAE_point'] = positions.apply(lambda x: euros_to_pips(x.MAE, x.Point,x.Volume), axis=1)
    positions['MFE_point'] = positions.apply(lambda x: euros_to_pips(x.MFE, x.Point,x.Volume), axis=1)
    positions['profit_point'] = positions.apply(lambda x: euros_to_pips(x.MFE, x.Point,x.Volume), axis=1)

    positions = positions[~positions['MAE'].isna()]
    positions.loc[positions['MAE_point'] < 0,'MAE_point'] = 0
    positions.loc[positions['MFE_point'] < 0,'MFE_point'] = 0

    positions['MFE_bins'] = positions.apply(lambda x: to_range_idx(range_step, x.MFE_point), axis=1)
    positions['MAE_bins'] = positions.apply(lambda x: to_range_idx(range_step, x.MAE_point), axis=1)

    return positions

def to_range_idx(range_step,val) :
    return int(val/range_step)
def compute_conditional_returns_per_bin(positions) :
    positions = positions[['profit_point','MFE_bins','MAE_bins']]
    MFE_bin = positions.groupby('MFE_bins')['profit_point'].mean()
    MFE_bin_counts = positions.groupby('MFE_bins')['profit_point'].count()
    MFE_bin_counts = MFE_bin_counts/MFE_bin_counts.sum()


    MAE_bin = positions.groupby('MAE_bins')['profit_point'].mean()
    MAE_bin_counts = positions.groupby('MAE_bins')['profit_point'].count()
    MAE_bin_counts = MAE_bin_counts/MAE_bin_counts.sum()
    return(pd.DataFrame([MAE_bin,MAE_bin_counts,MFE_bin,MFE_bin_counts]).T.fillna(0).sort_index(ascending=False))
sFilePath = 'C:\\Users\\franc\\Documents\\MetaTrader_tests\\Strategy_1_MM_crossover_Hysteresis\\12_11_Run1_No_SL_No_TP_SMA\\Run_1.1_8_21\\H1\\12_11_Run1_No_SL_No_TP_SMA-Run_1.1_8_21-H1.csv'

positions =read_positions(sFilePath)
positions = add_points_level(positions)
bins = compute_conditional_returns_per_bin(positions)
bins.columns = ['MFE_bins','MFE_bins_count','MAE_bins','MAE_bins_count']
bins = bins.reindex(list(range(bins.index.min(),bins.index.max()+1)),fill_value=0)
pass

