import pandas as pd
import os
from utils.utilData import unpackComment_MM

def read_positions(sBaseTickPath) :
    try :
        df_positions = pd.read_csv(os.path.join(sBaseTickPath), sep=";", encoding='utf-16',dtype=str)
    except :
        pass
    list_first_trial = [' Ticket               ','Entry               ','Time                ','Reason              ','Position ID        (missed string parameter)','Volume              ','Price               ','Commission          ','Swap                ','Swap_corrected','Profit              ','Symbol              ','Comment            ','sl                  ','tp                  ']
    list_second_trial = [' Ticket               ','Entry               ','Type                ','Time                ','Reason              ','Position ID        (missed string parameter)','Volume              ','Price               ','Commission          ','Swap                ','Swap_corrected','Profit ','Symbol              ','Comment             (missed string parameter)','sl                  ','tp                  ','Comment                                  ','ATR                 ','MFE                 ','MAE                 ','Commissions         ','Point               ','Spread              ']

   # list_second_trial = [' Ticket               ','Entry               ','Type                ','Time                ','Reason              ','Position ID        (missed string parameter)','Volume              ','Price               ','Commission          ','Swap                ','Swap_corrected','Profit ','Symbol              ','Comment             (missed string parameter)','sl                  ','tp                  ','Comment                                  ','ATR                 ','MFE                 ','MAE                 ','Commissions         ','Point              ']
    list_second_trial = [' Ticket               ','Entry               ','Type                ','Time                ','Reason              ','Position ID        (missed string parameter)','Volume              ','Price               ','Commission          ','Swap                ','Swap_corrected','Profit ','Symbol              ','Comment             (missed string parameter)','sl                  ','tp                  ','Comment                                  ','ATR                 ','MFE                 ','MAE                 ','Commissions         ','Point               ']

    df_positions = df_positions[list_second_trial]

    df_positions.columns = df_positions.columns.str.replace(' ', '',regex = True)
    df_positions.columns = df_positions.columns.str.replace('(missedstringparameter)','',regex = True)
    df_positions = pd.concat([df_positions,],axis=1)



    df_positions['Symbol'] = df_positions['Symbol'].str.replace(' ', '')

    df_positions['Entry'] = df_positions['Entry'].str.replace(' ', '')
    df_positions['Reason'] = df_positions['Reason'].str.replace(' ', '')
    df_positions['Type'] = df_positions['Type'].str.replace(' ', '')
    df_positions['PositionID()'] = df_positions['PositionID()'].astype('int')

    df_positions['Time'] = pd.to_datetime(df_positions['Time'])
    #  df_positions = df_positions[mask]
    df_positions = df_positions.set_index(pd.DatetimeIndex(df_positions['Time']))
    cols = df_positions.columns.drop(['Comment()','Comment','PositionID()','Reason','Time','Entry','Type'])
    symbols = df_positions['Symbol'].values
    df_positions[cols] = df_positions[cols].apply(pd.to_numeric, errors='coerce')
    df_positions['Symbol']  = symbols

    df_positions['Stateright'] = df_positions['Symbol'].str[-3:]
    mask =  (df_positions['Symbol'].str[-3:] == 'JPY')

    df_positions.loc[mask,'Swap_corrected']  = 0.01*df_positions.loc[mask,'Swap_corrected']
    df_positions.loc[mask,'Commissions']  = 0.01*df_positions.loc[mask,'Commissions']

    return df_positions