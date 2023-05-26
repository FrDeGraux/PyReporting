from utils.utilMapping import from_entry_to_category
import pandas as pd
from os import path,makedirs
import numpy as np
def compute_loss_SL (in_df_position) :

    mask_sl = in_df_position['Reason'] == 'DEAL_REASON_SL'
    df_sl = in_df_position[mask_sl]
    df_sl = df_sl[['Profit', 'Swap', 'Commission']]
    df_sl = df_sl.sum(axis=1)
    return df_sl
def get_point_digit(in_symbol):
    sDepositCurr = in_symbol[-3:]
    if(sDepositCurr == 'JPY'):
        return 1
    return 5
def unpackComment_MM_NoPoint(in_df_positions) :
    in_df_positions[['Slow_MM', 'Fast_MM','Other']] = in_df_positions['Comment()'].str.split('_', expand=True)
    in_df_positions.drop(columns = ['Other','Comment()'])
    return in_df_positions

def unpackComment_MM(in_df_positions) :
    try :
      in_df_positions[['Slow_MM', 'Fast_MM','Other','Point']] = in_df_positions['Comment()'].str.split('_', expand=True)
      in_df_positions = in_df_positions['Slow_MM', 'Fast_MM']
      in_df_positions['Swap_corrected'] = 0
    except Exception :
        try :
            in_df_positions[['Slow_MM', 'Fast_MM', 'Other']] = in_df_positions['Comment()'].str.split('_',expand=True)
            in_df_positions.columns = ['Slow_MM', 'Fast_MM', 'Swap_corrected']

        except Exception :
            in_df_positions[['Commission','Point']] = in_df_positions['Comment'].str.split('_',expand=True)

    #in_df_positions.drop(columns = ['Other','Comment()'])
    return in_df_positions

# create a dataframe with in positions matched with out ones (entryIn, entryOut, etc)
def from_in_to_out_mapping(in_df_positions,in_config) :
    mask = in_df_positions['Entry'] == in_config.get('Names', 'Entry_Out')
    df_sell = (in_df_positions[mask])
    df_sell['Reason_number'] = df_sell.apply(lambda row: from_entry_to_category(row), axis=1)
    res = []
    for row in df_sell.iterrows() :
        row = row[1]
        val = row[in_config.get('Names', 'PositionMissedParameters')]
        mask_position = (in_df_positions[in_config.get('Names', 'PositionMissedParameters')] == val)
        df = in_df_positions[mask_position]
        df = df[df['Entry'] == in_config.get('Names', 'Entry_In')]
        if(len(df) > 1) :
            raise Exception('plot_return_durations::more than one purchase')
        entryIn = df['Time'].values[0]
        hysteresis_in = df['Hysteresis'].values[0]
        hysteresis_out = row['Hysteresis']
        entryOut = row['Time']

        res.append((entryIn,entryOut,row['Symbol'],(row['Profit']),hysteresis_in,hysteresis_out,(row['Reason_number'])))
    return(pd.DataFrame(res, columns =['TimeIn', 'TimeOut','Symbol', 'Profit','Hysteresis_in','Hysteresis_out','ReasonNumber']))
def getSymbolList(in_df_positions,in_configcommon) :
    symbolList = in_df_positions['Symbol'].unique()
    symbolList = [item.replace(' ', '') for item in symbolList]
    symbolList = symbolList + [(in_configcommon.get('Names', 'ALL_Symbol'))]

    return symbolList
def get_in_or_out_sign(in_type) :
    if (in_type == 'DEAL_ENTRY_IN'):
        return 1
    if (in_type == 'DEAL_ENTRY_OUT'):
        return -1
    else:
        raise Exception
def get_gross_position(in_type) :
    in_entry = in_type.strip()
    if ( in_entry == 'DEAL_ENTRY_IN') :
        return 1
    if (in_entry == 'DEAL_ENTRY_OUT') :
        return -1
    raise Exception
def get_net_position(in_type,in_entry) :
    in_type = in_type.strip()
    if (in_type == 'DEAL_TYPE_BUY' and in_entry == 'DEAL_ENTRY_IN') :
        return 1
    if (in_type == 'DEAL_TYPE_BUY' and in_entry == 'DEAL_ENTRY_OUT') :
        return 1
    if (in_type == 'DEAL_TYPE_SELL' and in_entry == 'DEAL_ENTRY_IN') :
        return -1
    if (in_type == 'DEAL_TYPE_SELL' and in_entry == 'DEAL_ENTRY_OUT') :
        return -1
    raise Exception
def filterBySymbol_LastOut_fortest(in_df_position,in_symbol,in_config) :
    if in_symbol == in_config.get('Names', 'ALL_Symbol'):
        return in_df_position
    mask = in_df_position['Symbol'] == in_symbol
    in_df_position = in_df_position[mask]

    in_df_position.drop(in_df_position.tail(1).index, inplace=True)  # drop last row : TEMPORARY

    return in_df_position
def days_hours_minutes(td):
    total_seconds = td.total_seconds()  # Convert timedelta into seconds
    seconds_in_hour = 60 * 60  # Set the number of seconds in an hour
    td_in_hours = total_seconds / seconds_in_hour
    return td_in_hours
def filterBySymbol(in_df_position,in_symbol,in_config = None) :
    if in_config is not None :
        if in_symbol == in_config.get('Names', 'ALL_Symbol'):
            return in_df_position
    mask = in_df_position['Symbol'] == in_symbol
    in_df_position = in_df_position[mask]

    return in_df_position
def remove_none_points(in_df_position):
    mask = in_df_position['Point'] != None
    in_df_position = in_df_position[mask]
    return in_df_position
def filterOnInDeals(in_df_position):
    if not in_df_position['Symbol'].unique() :
        raise Exception
    mask = in_df_position['Entry'] == 'DEAL_ENTRY_IN'
    in_df_position_filtered = in_df_position[mask]
    in_df_position_filtered = pd.concat([in_df_position_filtered,in_df_position.tail(1)],axis = 0) # double last IN entry
    return in_df_position_filtered
def filterOnInDeals_AndLastOut(in_df_position):
    if not in_df_position['Symbol'].unique() :
        raise Exception
    mask = in_df_position['Entry'] == 'DEAL_ENTRY_IN'
    in_df_position_filtered = in_df_position[mask]
    in_df_position_filtered = pd.concat([in_df_position_filtered,in_df_position.tail(1)],axis = 0)
    return in_df_position_filtered
def from_frequency_to_resample_period(in_freq) :
    map = {'H1' : '60min','H4' : '240min','D1':'D','W1' : '7D'}
    return map[in_freq]
def compute_reward_tp(in_df_position) :
    mask_tp = in_df_position['Reason'] == 'DEAL_REASON_TP'
    df_tp = in_df_position[mask_tp]
    df_tp = df_tp[['Profit', 'SwapReal', 'Commission']]
    df_tp = df_tp.sum(axis=1)
    return df_tp
def compute_profit_other(in_df_position) :
    mask_tp = in_df_position['Reason'] == 'DEAL_REASON_TP'
    mask_sl = in_df_position['Reason'] == 'DEAL_REASON_SL'
    df_other = in_df_position[~mask_tp & ~mask_sl]
    df_other = df_other[['Profit', 'SwapReal', 'Commission']]
    df_other = df_other.sum(axis=1)
    return df_other
def filter_on_entry_datetimes(in_df,startTime,in_dt_second) :
    filtered_df = in_df[(in_df['TimeIn_Date'] >= startTime)]
    filtered_df = filtered_df[(in_df['TimeIn_Date'] < (in_dt_second))]

    return(filtered_df)

def filter_on_entry_datetimes_cumulative(in_df,startTime,in_dt_second) :
    filtered_df = in_df[(in_df['TimeIn_Date'] < (in_dt_second))]

    return(filtered_df)
def create_directory_if_not_exists(in_dirName):
    if not path.isdir(in_dirName):
        makedirs(in_dirName)

def filterByDateTimePrevious(in_df_position, in_dt):
      mask = in_df_position['Symbol'] < in_dt
      in_df_position = in_df_position[mask]
      return in_df_position


def compute_profit_durations(df_positions,in_symbol,in_configcommon):
      df_positions = filterBySymbol(df_positions, in_symbol,in_configcommon)

      # plot return vs Trade duration (color is the profit)
      df_sell = (df_positions[df_positions['Entry'] == in_configcommon.get('Names', 'Entry_Out')])
      df_sell.loc[:,'Reason_number'] = df_sell.apply(lambda row: from_entry_to_category(row), axis=1)
      toplot = []
      for row in df_sell.iterrows():
          row = row[1]
          val = row[in_configcommon.get('Names', 'PositionMissedParameters')]
          mask_position = (df_positions[in_configcommon.get('Names', 'PositionMissedParameters')] == val)
          df = df_positions[mask_position]
          df = df[df['Entry'] == in_configcommon.get('Names', 'Entry_In')]
          if (len(df) > 1):
              raise Exception('plot_return_durations::more than one purchase')
          entryIn = df['Time'].values[0]
          entryOut = row['Time']


          toplot.append(((entryOut - entryIn).total_seconds()/3600, (row['Profit']), (row['Reason_number'])))
      return toplot

def compute_MAE_MFE(in_dfPositions, in_configCommon, in_symbolList):
    df_positions_out = in_dfPositions[(in_dfPositions['Entry'] == in_configCommon.get('Names', 'Entry_Out'))]
    df_positions_out = df_positions_out[['Profit', 'Symbol', 'MFE', 'MAE']]
    res = {}
    for item in in_symbolList:
        data = filterBySymbol(df_positions_out, item, in_configCommon)
        gd = data.to_dict()
        profit = pd.to_numeric(data['Profit'], errors='coerce')
        MAE = pd.to_numeric(data['MAE'], errors='coerce')
        MFE = pd.to_numeric(data['MFE'], errors='coerce')

        nan_numbers = MAE.isna().sum()
        if nan_numbers != 0  :
            MAE = -1 * MAE[:-1 * nan_numbers]
            MFE = MFE[:-1 * nan_numbers]
            profit = profit[:-1 * nan_numbers]

        res[item] = (profit, MAE, MFE)
    return res
def compute_return(in_dfPositions,in_cfgcommonn):
      res = []
      for idx,item in in_dfPositions.iterrows():
          if item['Entry'] == in_cfgcommonn.get('Names', 'Entry_Out') :
              posID  = item['PositionID()']
              mask_ticket = (in_dfPositions['Ticket'] ==  int(posID))
              mask_symbol =  (in_dfPositions['Symbol'] == item['Symbol'])
              in_entry = in_dfPositions[(in_dfPositions['Ticket'] ==  int(posID)) & (in_dfPositions['Symbol'] == item['Symbol'])]
              balance = in_entry['Balance'][0]
              res.append((item['Profit_Total'])/balance)
          else :
             res.append(0)
      return res
      # for each entry out

def compute_resampled_return(equities_all_symbol,in_balance_initial):
      equity_resampled_W1_returns = {}

      for item in equities_all_symbol.keys() :

          equity = equities_all_symbol[item]
          equity['EquityChange'] = equity[item + '_Equity'].diff(1)

          equity = equity.drop(columns=[item + '_Equity'])
          equity_resample = pd.DataFrame(equity.resample('W').sum())
          equity_resample['Equity'] = equity_resample['EquityChange'].cumsum()
          equity_resample['Balance'] =in_balance_initial + equity_resample['Equity']

          equity_resample['Balance'] = equity_resample['Balance'].shift(1)
          #equity_resample['EquityChange'] = equity_resample['Equity'].diff()

          equity_resample['Balance'] = equity_resample['Balance'].fillna(in_balance_initial)
          equity_resample['Return'] = equity_resample['EquityChange'] / equity_resample['Balance']
          equity_resample = equity_resample.drop(columns=['EquityChange','Equity', 'Balance'])  # 2
          equity_resampled_W1_returns[item] = equity_resample
      return equity_resampled_W1_returns