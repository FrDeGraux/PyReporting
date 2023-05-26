import numpy as np
import pandas as pd
from utils.utilReader import read_positions
from utils.utilData import filterBySymbol
from scipy.optimize import minimize
sFilePath = 'C:\\Users\\franc\\Documents\\MetaTrader_tests\\Strategy_1_MM_crossover_Hysteresis\\12_11_Run1_No_SL_No_TP_SMA\\Run_1.1_8_21\\H1\\12_11_Run1_No_SL_No_TP_SMA-Run_1.1_8_21-H1.csv'
def get_score(in_lambda,dfPosition):

    dfPosition_out = dfPosition.loc[(dfPosition['Entry'] == 'DEAL_ENTRY_OUT')]

    dfPosition_out = dfPosition_out[['Ticket', 'PositionID()', 'Entry', 'Profit', 'Price', 'MAE', 'MFE','Type','Point']]
    dfPosition_out = pd.merge(dfPosition_out, dfPosition, how='left', left_on='PositionID()', right_on='Ticket')

    dfPosition_out = dfPosition_out[['PositionID()_x', 'Entry_x', 'Price_x', 'Profit_x', 'MAE_x', 'MFE_x', 'Price_y','Type_x','Point_x','ATR']]
    columns_titles = ['PositionID()_x', 'Entry_x','Type_x', 'Price_x', 'Price_y', 'Profit_x', 'MAE_x', 'MFE_x','ATR','Point_x']
    dfPosition_out = dfPosition_out.reindex(columns=columns_titles)
    dfPosition_out.columns = ['PositionID', 'Entry','Type', 'Price_out', 'Price_in', 'Profit', 'MAE', 'MFE','ATR','Point']
    dfPosition_out['MAE_n'] = 0.001*dfPosition_out['MAE'] / (dfPosition_out['Point']/0.00001)
    dfPosition_out['MFE_n'] = 0.001*dfPosition_out['MFE'] /(dfPosition_out['Point']/0.00001)
    dfPosition_out['Profit_n'] =  dfPosition_out['Profit'] / (dfPosition_out['Point']/0.00001)
    dfPosition_out['sign'] = dfPosition_out['Type'].apply(lambda x: 1 if x == 'DEAL_TYPE_SELL' else -1)
    dfPosition_out['ProfitBis'] = dfPosition_out['sign']*(dfPosition_out['Price_out'] - dfPosition_out['Price_in'])


    dfPosition_out['lambda_SL'] =-dfPosition_out['sign']*in_lambda*dfPosition_out['ATR']
    dfPosition_out['lambda_TP'] =dfPosition_out['sign']*in_lambda*dfPosition_out['ATR']


    dfPosition_out.loc[dfPosition_out['lambda_SL'].abs() > dfPosition_out['MAE_n'], 'hit_SL'] = 0
    dfPosition_out.loc[dfPosition_out['lambda_SL'].abs() <= dfPosition_out['MAE_n'], 'hit_SL'] = 1

    dfPosition_out.loc[dfPosition_out['lambda_TP'].abs() > dfPosition_out['MFE_n'], 'hit_TP'] = 0
    dfPosition_out.loc[dfPosition_out['lambda_TP'].abs() <= dfPosition_out['MFE_n'], 'hit_TP'] = 1
    dfPosition_out['Odds'] = 0
    mask = (dfPosition_out['hit_TP'] == 1) & (dfPosition_out['hit_SL'] == 1)
    dfPosition_out['P_out_final'] = dfPosition_out['Price_out']
    dfPosition_out.loc[mask,'Odds'] = dfPosition_out['MAE_n']/(dfPosition_out['MAE_n'] + dfPosition_out['MFE_n'])
    dfPosition_out.loc[~mask & dfPosition_out['hit_SL']== 1,'Odds'] =0
    dfPosition_out.loc[~mask & dfPosition_out['hit_SL']== 1,'P_out_final'] = 1

    dfPosition_out.loc[~mask & dfPosition_out['hit_SL']== 1,'P_out_final'] = dfPosition_out.loc[~mask & dfPosition_out['hit_SL']== 1,'Price_in']-dfPosition_out.loc[~mask & dfPosition_out['hit_SL']== 1,'lambda_SL']

    dfPosition_out.loc[~mask & dfPosition_out['hit_TP']== 1,'Odds'] =0
    dfPosition_out.loc[~mask & dfPosition_out['hit_TP']== 1,'P_out_final'] = dfPosition_out.loc[~mask & dfPosition_out['hit_TP']== 1,'Price_in']+dfPosition_out.loc[~mask & dfPosition_out['hit_TP']== 1,'lambda_TP']
    dfPosition_out.loc[mask,'P_out_final'] = dfPosition_out.loc[mask,'Odds']*(dfPosition_out.loc[mask,'Price_in']-dfPosition_out.loc[mask,'lambda_SL']) + (1-dfPosition_out.loc[mask,'Odds'])*(dfPosition_out.loc[mask,'Price_in']-dfPosition_out.loc[mask,'lambda_SL'])
    dfPosition_out['Profit'] = dfPosition_out['P_out_final'] - dfPosition_out['Price_in']

    profit_local =  dfPosition_out['Profit'].sum()*1000 # profit in base currency (i.e GBP)
    profit_currency = dfPosition_out['Profit']*(dfPosition_out['Point']/0.00001)
    return (profit_local,profit_currency)

'''

obj = lambda x : -1*get_score(x)
bound = ([(0,5)])
x0 =  (0)
sol = minimize(obj,x0,bounds = bound)
pass
'''
rng = range(0,4,1)
rng = [item/4 for item in rng]
score = []
positions =read_positions(sFilePath)
profits = positions['Profit'].sum()
symbols = positions['Symbol'].unique()
df_position_by_symbol = [filterBySymbol(positions,item) for item in symbols]

res = []
for idx,item in enumerate(df_position_by_symbol) :
    for x in rng :
        res.append(get_score(x,df_position_by_symbol[idx]))
