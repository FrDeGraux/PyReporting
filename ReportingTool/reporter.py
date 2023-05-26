from utils.utilReader import read_positions
import matplotlib.pyplot as plt
from os import path
from scipy.stats import norm

from utils.utilData import compute_resampled_return,compute_profit_durations,compute_MAE_MFE,compute_return,remove_none_points,get_gross_position,get_point_digit,get_in_or_out_sign,filterBySymbol, filterOnInDeals,filterOnInDeals_AndLastOut,getSymbolList, get_net_position,unpackComment_MM,from_frequency_to_resample_period,create_directory_if_not_exists
from utils.utilPlot import plot_scatter_durations,plot_scatter,get_col_row_correlation_graph,get_cmap
from itertools import combinations
from math import floor
import matplotlib.dates as mdates
from utils.utilPlot import go_overwrite_and_save,plt_overwrite_and_save,from_plot_to_x_y,plot_scatter_durations_subplot,plot_scatter_durations_mainplot

from utils.utilMapping import from_entry_to_category
bAdjustSwapCorrectedFactor = 10000
import pandas as pd
import numpy as np
from matplotlib import cm

from utils.utilConfig import init_config

class Reporter:
  def __init__(self,in_config_specific,in_config_subrun,in_config_common):
      self.config = init_config(in_config_specific)
      self.configcommon = in_config_common
      self.configsubrun = init_config(in_config_subrun)  # config_run_1.2

      self.sRunName = self.configsubrun.get('Run', 'sRunName')
      self.sSubRunName =  self.configsubrun.get('Run', 'sSubRunName')
      self.sTitlePrefix = self.sRunName + '_' + self.sSubRunName

      self.freq = self.config.get('Inputs','Frequency')
      self.sMotherPath = self.configcommon.get('FilePth', 'sBasePath')
      self.sMotherPath = self.sMotherPath.replace("\\\\", "\\")

      self.sBasePathRun = path.join(self.sMotherPath, self.sRunName)
      self.sBasePath = path.join(self.sBasePathRun,self.sSubRunName)
      self.sBasePathFreq = path.join(self.sBasePath, self.config.get('Inputs', 'Frequency'))

      self.sReportsPath = path.join(self.sBasePathFreq, self.configcommon.get('FilePth', 'sReportsPath'))
      self.sDurationReturnPath = path.join(self.sReportsPath, self.configcommon.get('FilePth', 'sDurationPath'))
      self.sFileName =  self.config.get('Inputs', 'sFileName')

      self.lastDayEquity =  pd.Timestamp('20000101 11:59:59.999999999')
      sFileOutput = self.sFileName.split('.')
      self.sFileOutput  = ''.join(sFileOutput[:-1])
      create_directory_if_not_exists(self.sDurationReturnPath)


      self.balance_initial = 10000
      self.style = self.configsubrun.get('Styles','Style')

      self.df_positions =  read_positions(path.join(self.sBasePathFreq, self.sFileName))
      self.df_positions[self.configcommon.get('Names', 'PositionMissedParameters')] = (self.df_positions[self.configcommon.get('Names', 'PositionMissedParameters')]).astype(str)
      self.symbolList= getSymbolList(self.df_positions,self.configcommon)
      self.symbolListNoALL = self.symbolList[:-1]
      self.turbo = cm.get_cmap('turbo', len(self.symbolList))

      self.previous_row_average_entry_price = None
      self.equity_resampled_W1_returns = []
      self.df_equities_percent = {}
      self.df_equities_ultimate_percent = {}

      self.process_data()
      self.profits_duration = {}
      self.durations_color = self.configsubrun.get('ColorDuration','color')
  def toYearlyPercentEquity(self):
      for in_symbol in self.symbolList :
          df_equities = self.equities_all_symbol[in_symbol]
          df_equities = df_equities.resample('Y').last()
          df_equities = self.balance_initial + df_equities
          self.df_equities_percent[in_symbol] = df_equities[in_symbol + '_Equity'].pct_change(fill_method='ffill')
          last = df_equities[in_symbol + '_Equity'].iat[-1]
          first = df_equities[in_symbol + '_Equity'].iat[0]
          val = (last- first)/first
          self.df_equities_ultimate_percent[in_symbol] = val
          pass
  def plot_bar_returns(self,in_symbol,count,ax1 = None,ylim = None):
      ax = plt.subplot(len(self.symbolList), 1, count+1,sharex = ax1)
      if ylim is not None :
        ax.set_ylim([-ylim, ylim])
      df_equities = self.equities_all_symbol[in_symbol]
      df_equities = df_equities.resample('Y').last()
      df_equities = self.balance_initial + df_equities
      df_equities_percent = df_equities[in_symbol + '_Equity'].pct_change(fill_method='ffill')
      plt.bar(df_equities_percent.index.year, df_equities_percent, color='maroon',width =0.5)
      plt.title(in_symbol + '_Returns',fontsize = 8,loc = 'center')
      return(ax)
  def plot_profit_from_multi_reporter(self,in_sSymbol,in_plotStyle,in_ylimsNotAll,in_ylimsALL,in_title = None,in_plotCommissionFree = True):
     color_idx = self.symbolList.index(in_sSymbol)
     df_equity_symbol = self.equities_all_symbol[in_sSymbol]
     self.plot_profit_by_symbol(df_equity_symbol, in_sSymbol, self.turbo.colors[color_idx],in_title,in_ylimsNotAll,in_ylimsALL,in_plotStyle,in_plotCommissionFree)
     # Plot one equity for a specific symbolin

  def plot_commissions(self,in_symbol):
      in_df = filterBySymbol(self.df_positions,in_symbol,self.configcommon)
      plt.hist(in_df['Commissions'], bins=100,density = True, alpha=0.5, label= in_symbol)
      # Plot the PDF.
      xmin, xmax = plt.xlim()
      ymin, ymax = plt.ylim()

      x = np.linspace(xmin, xmax, 100)
      mu, std = norm.fit(in_df['Spread'].dropna(how='all'))

    #  p = norm.pdf(x, mu, std)

      #plt.plot(x, p, 'k', linewidth=2)
      plt.xlim([xmin, xmax])
      plt.ylim([ymin, ymax])
      sFilePath = path.join(self.sReportsPath, self.configcommon.get('FilePth', 'sCommissionsPath'),in_symbol + '_commissions.png')

      plt.legend(loc="upper right")
      #plt.show()

      plt_overwrite_and_save(sFilePath)
      plt.close()

      return {in_symbol : (mu,std)}
  def plot_profit_by_symbol(self,in_df,in_symbol,in_color,in_title = None,ylims_NotALL = None,ylims_ALL = None, in_plotStyle = 'solid',in_plotCommissionFree = True) :

        if in_symbol == 'ALL' :
            if in_plotCommissionFree is True :
                plt.plot(in_df.index.tolist(), in_df[in_symbol + '_Equity'] + in_df[in_symbol + '_Commission'], label='commissions',linestyle = in_plotStyle)
                plt.plot(in_df.index.tolist(), in_df[in_symbol + '_Equity'] + in_df[in_symbol + '_Commission']-in_df[in_symbol +'_Swap_corrected'], label='swaps',linestyle =in_plotStyle)
            ylims = ylims_ALL
        else :
            ylims = ylims_NotALL
        #plt.plot(in_df.index.tolist(), in_df[in_symbol + '_Equity'].values, label=self.sTitlePrefix + '_' + in_symbol + '_' + self.sSubRunName + '_' + self.freq,color=in_color,linestyle = in_plotStyle)

        plt.plot(in_df.index.tolist(), in_df[in_symbol + '_Equity'].values, label=in_symbol + '_' + self.sSubRunName + '_' + self.freq,color=in_color,linestyle = in_plotStyle)
        if in_title is None :
            in_title = self.config.get('Inputs', 'Frequency') + '_' + self.configsubrun.get('Run','sRunName') + '_' + self.configcommon.get('Returns', 'Graph_Title') + self.freq + "_" + in_symbol
        plt.title(in_title)

        if ylims is not None :
            ax = plt.gca()
            ax.set_ylim([ylims[0], ylims[1]])

        plt.legend(loc="lower left")


        monthFmt = mdates.DateFormatter('%Y')
        plt.gca().xaxis.set_major_formatter(monthFmt)
  def compute_balance(self):
      self.df_positions['Profit_Total'] = self.df_positions['Profit'] + self.df_positions['Commission'] + self.df_positions['Swap_corrected']
      self.df_positions['Balance'] =self.balance_initial + self.df_positions['Profit_Total'].cumsum()
  def process_data(self):

      self.compute_balance()
      #self.df_positions['returns'] = compute_return(self.df_positions,self.configcommon)
      self.compute_equity_all_symbol()
      self.toYearlyPercentEquity()
      #elf.plotBaRReturns()
      #plt.show()
      pass
  def plotBaRReturns(self):
      ax1 =self.plot_bar_returns('ALL', 0)
      ylim = max([self.df_equities_percent[item].max()  for item in self.symbolListNoALL])

      [self.plot_bar_returns(item, count+1,ax1,ylim) for count,item in enumerate(self.symbolListNoALL)]
      pass
  def compute_equity_all_symbol(self):
      # compute the dataframe list with all equities
      self.equities_all_symbol = {}
      sFilePath = path.join(self.sBasePathFreq,self.sFileOutput  + '_equities.csv')

      bRecomputeData = (path.exists(sFilePath) is not True)
      [self.equities_all_symbol.update({item:self.compute_equity(item)}) for item in self.symbolListNoALL]
      res = pd.DataFrame()

      for count,item in enumerate(list(self.equities_all_symbol.values()) ):
          res = pd.merge(res,item, left_index=True, right_index=True, how='outer')
      equities_headers = [item for item in res.columns if 'Equity' in item]
      commissions_headers = [item for item in res.columns if 'Commission' in item]
      swap_headers = [item for item in res.columns if 'Swap' in item]

      res_equities = res[equities_headers]
      res_commissions = res[commissions_headers]
      res_swaps = res[swap_headers]
      equities_all = pd.DataFrame()
      equities_all['ALL_Equity'] = res_equities.sum(axis=1)
      equities_all['ALL_Commission'] = res_commissions.sum(axis=1)
      equities_all['ALL_Swap_corrected'] = res_swaps.sum(axis=1)

      self.equities_all_symbol.update({'ALL' : equities_all})

      sFilePath = path.join(self.sBasePathFreq,self.sFileOutput  + '_equities.csv')
      if bRecomputeData is True  :
          df = pd.DataFrame()
          for key in self.equities_all_symbol :
            df = pd.merge(df,self.equities_all_symbol[key], left_index=True,right_index=True, how='outer')
          df.to_csv(sFilePath)

      pass
  def plot_profits_all_symbols(self):  # plot_balance
      in_timeframe  = from_frequency_to_resample_period(self.freq)
      turbo = cm.get_cmap('turbo', len(self.symbolList))
      df_all_equity = None

      for idx, symbol in enumerate(self.symbolList):
          if symbol == 'ALL' :
              plt_overwrite_and_save(self.sReportsPath, self.sRunName + '_ProfitsSymbols'+ '.png')

          df_equity_symbol = self.equities_all_symbol[symbol]
          self.plot_profit_by_symbol(df_equity_symbol,symbol,turbo.colors[idx])
      plt_overwrite_and_save(self.sReportsPath, self.sRunName + '_Profits' + '.png')
      plt.close()

  def get_avg_entry_price(self,in_ID,price,in_symbol,in_previous_positioning,in_type,in_entry,in_quantity = 1):

      if in_entry == 'DEAL_ENTRY_OUT' :
        entry_row = self.df_positions[(self.df_positions['PositionID()'] == in_ID) & (self.df_positions['Symbol'] == in_symbol) & (self.df_positions['Entry'] == 'DEAL_ENTRY_IN')]
        price = entry_row['Price']
          # find corresponding prrice

      if self.previous_row_average_entry_price is None : # first buy/sell
            average_entry_price = price
      else :
          new_positioning = in_previous_positioning + get_in_or_out_sign(in_entry) * abs(in_quantity)

          if new_positioning == 0 : # portfolio is sold out, avg price = 0
            average_entry_price = 0
          else :
            average_entry_price =  ((1/new_positioning)*(in_previous_positioning*(self.previous_row_average_entry_price) + get_in_or_out_sign(in_entry)*price))
      if in_entry == 'DEAL_ENTRY_IN' :
        self.previous_row_average_entry_price = average_entry_price
      return average_entry_price


  def plot_MAE_MFE_bySymbol(self,item,data,count,in_nRowsTotalSubPlot_MAE_MFE,in_nColsTotalSubPlot_MAE_MFE,xlim):
          in_titles = item + '_MAE/MFE'
          ax1 = plt.subplot(in_nRowsTotalSubPlot_MAE_MFE, in_nColsTotalSubPlot_MAE_MFE, count+1)

          ax1.set_xlim([-xlim, xlim])
          ax1.set_ylim([-xlim, xlim])
          (profit,MAE,MFE) = data[item]
          plt.scatter(profit, MAE, s=float(self.configcommon.get('Correlations', 'Correlations_Marker_Size')),label=('MAE' + item + '_'))
          plt.scatter(profit,MFE, s=float(self.configcommon.get('Correlations', 'Correlations_Marker_Size')),label=('MFE' + item + '_'))
          correlation_MAE = np.corrcoef(profit, MAE)
          correlation_MFE = np.corrcoef(profit, MFE)
          try :
            m_best, b_best = np.polyfit(profit, MFE, 1)
          except :
            m_best, b_best = np.polyfit(profit, MFE, 1)

          plt.plot(profit, m_best * (profit) + b_best,'orange')

          m_worst, b_worst = np.polyfit(profit,MAE, 1)
          plt.plot(profit, m_worst * (profit) + b_worst,color = 'blue')
          plt.title(item + "(" + str(round(correlation_MAE[0,1],2)) + ")" ,fontsize=self.configcommon.get('Correlations', 'Correlations_Font_Size'))

  def plot_MAE_MFE(self):
      data = compute_MAE_MFE(self.df_positions,self.configcommon,self.symbolList)

      xmax_not_all = max([x.max() for b in list(data.values())  for x in b])
      xmin_not_all = min([x.min() for b in list(data.values()) for x in b])
      xlim_not_all = 1.2*max(abs(xmax_not_all),abs((xmin_not_all)))

      xmax_all = max([x.max() for b in list(data.values())  for x in b])
      xmin_all = min([x.min() for b in list(data.values()) for x in b])
      xlim_all = 1.2*max(abs(xmax_all),abs((xmin_all)))
      in_nRowsTotalSubPlot_MAE_MFE,in_nColsTotalSubPlot_MAE_MFE = get_col_row_correlation_graph(self.symbolListNoALL,self.configcommon)
      [self.plot_MAE_MFE_bySymbol(item, data, count, in_nRowsTotalSubPlot_MAE_MFE, in_nColsTotalSubPlot_MAE_MFE, xlim_not_all) for count,item in enumerate(self.symbolListNoALL)]
      plt_overwrite_and_save(path.join(self.sReportsPath, self.configcommon.get('FilePth', 'sMAE_MFEPath')), self.config.get('Inputs',
                                                                    'Frequency') + '_' + self.sRunName + '_MAEMFE.png')
      plt.close()
      in_nRowsTotalSubPlot_MAE_MFE,in_nColsTotalSubPlot_MAE_MFE = get_col_row_correlation_graph(['ALL'],self.configcommon)

      [self.plot_MAE_MFE_bySymbol('ALL', data, count , in_nRowsTotalSubPlot_MAE_MFE, in_nColsTotalSubPlot_MAE_MFE, xlim_all) for count,item in enumerate(['ALL'])]
      plt_overwrite_and_save(path.join(self.sReportsPath, self.configcommon.get('FilePth', 'sMAE_MFEPath')), 'ALL_' + self.config.get('Inputs',
                                                                    'Frequency') + '_' + self.sRunName + '_MAEMFE.png')
      plt.close()
  def compute_equity(self,in_symbol) :

      sFilePath = path.join(self.sBasePathFreq,self.sFileOutput  + '_equities.csv')
      bToRecompute = not(path.exists(sFilePath))
      bToRecompute = True
      if bToRecompute is False :
            res = pd.read_csv(sFilePath)
            res = res.set_index('idx')
            res.index = pd.to_datetime(res.index)
            return res[[in_symbol + '_' +  item for item in ['Equity','Commission','Swap_corrected']]]
      positions =  self.df_positions[['Symbol','Type','Entry','Price','Commissions','Swap_corrected','Profit','PositionID()','Point']]
      positions.columns = ['Symbol','Type','Entry','Price','Commission','Swap_corrected','Profit','PositionID','Point']
      positions = filterBySymbol(positions, in_symbol,self.configcommon)



      positions['positioning_net'] = positions.apply(lambda x: get_net_position(x.Type,x.Entry),axis=1)
      positions['positioning_gross'] = positions.apply(lambda x: get_gross_position(x.Entry),axis=1)
      positions['Commission'] = pd.to_numeric( positions['Commission'], errors='coerce')
      positions['Swap_corrected'] = pd.to_numeric( positions['Swap_corrected'], errors='coerce')
      positions['Swap_corrected'] = positions['Swap_corrected'].fillna(0)

      positions['Swap_corrected'] = positions['Swap_corrected']/bAdjustSwapCorrectedFactor


      positions['Profit'] = pd.to_numeric( positions['Profit'], errors='coerce')
      positions['Commission'] = positions['Commission'].fillna(0)


      positions['Profit_cumulative'] = positions[['Profit']].cumsum()
      positions['Commission'] = positions[['Commission']].cumsum()
      positions['Swap_corrected'] = positions[['Swap_corrected']].cumsum()
      positions['Total_PL'] = positions['Swap_corrected'] + positions['Profit_cumulative']

      positions['positioning_net']  = positions['positioning_net'].cumsum()
      positions['positioning_gross']  = positions['positioning_gross'].cumsum()

      positions['positioning_gross_shifted'] = positions['positioning_gross'].shift(1)
      positions['avgEntryPrice'] = positions['Price']
      #positions['avgEntryPrice'] = positions.apply(lambda x: self.get_avg_entry_price(x.PositionID,x.Price,x.Symbol,x.positioning_gross_shifted,x.Type,x.Entry,1), axis=1)
      self.previous_row_average_entry_price = None
      positions[['Symbol','avgEntryPrice','Entry','positioning_net','Point','positioning_gross','Commission','Swap_corrected']] = positions[['Symbol','avgEntryPrice','Entry','positioning_net','Point','positioning_gross','Commission','Swap_corrected']]
      positions_cumulative = filterOnInDeals(positions)
      prices_list_D1 = pd.read_csv(path.join(self.configcommon.get('FilePth', 'sBaseDevelopmentPath'),'Data',in_symbol,in_symbol + '_' + 'D1' + '.csv'),delim_whitespace=True)
      prices_list_D1 = prices_list_D1[['<DATE>','<CLOSE>']]
      prices_list_D1['<DateTime>'] = prices_list_D1['<DATE>']
      prices_list_D1 = prices_list_D1[['<DateTime>', '<CLOSE>']]
      prices_list_D1 = prices_list_D1.set_index('<DateTime>')
      lastDay = pd.Timestamp(pd.to_datetime(positions_cumulative.index[-1])).ceil(freq='D')
      if (lastDay > self.lastDayEquity) :
          self.lastDayEquity = lastDay
      positions_cumulative_com_swap = positions_cumulative[['Commission','Swap_corrected']].reindex(prices_list_D1.index,method='ffill')
      positions_cumulative_com_swap =positions_cumulative_com_swap.fillna(method='ffill')
      positions_cumulative = positions_cumulative.reindex(prices_list_D1.index, method='ffill')
      positions_cumulative = positions_cumulative.drop(['Commission','Swap_corrected'],axis=1)
      positions_cumulative = pd.merge(positions_cumulative,positions_cumulative_com_swap,left_index=True, right_index=True, how='outer')
      positions_cumulative['PriceFromFile'] =positions_cumulative['Price']

      positions_cumulative['Price'] = prices_list_D1['<CLOSE>'].shift(1)
      positions_cumulative['PriceFromEquity'] =positions_cumulative['Price']

      positions_cumulative['delta_price'] =positions_cumulative['PriceFromFile']-positions_cumulative['Price']




      positions_cumulative['idx'] = positions_cumulative.index
      positions_cumulative['idx'] = positions_cumulative['idx'].shift(1)
      positions_cumulative.index = pd.to_datetime(positions_cumulative['idx'])


      positions_cumulative = positions_cumulative.dropna(how='all')
      positions_cumulative = positions_cumulative.dropna(subset=['Point'])

      mask = (positions_cumulative.index) < lastDay
      positions_cumulative = (positions_cumulative[mask])

      positions_cumulative[positions_cumulative['Point'] == ""] = np.NaN

      positions_cumulative['Point'] = positions_cumulative['Point'].fillna(method='ffill')
    # if in_symbol[-3:] == 'JPY' :
       #   positions_cumulative['Point'] = 100*positions_cumulative['Point']
      positions_cumulative['PL_Points'] =(pow(10,get_point_digit( in_symbol)))*(positions_cumulative['Price'] - positions_cumulative['avgEntryPrice'])
      positions_cumulative['Point'] = pd.to_numeric(positions_cumulative['Point'])

      positions_cumulative['PL_Points_Euro'] = positions_cumulative['PL_Points']*positions_cumulative['Point']
      positions_cumulative['PL_final']  = 100000*0.01*positions_cumulative['positioning_net']*positions_cumulative['PL_Points_Euro']
      positions_cumulative['Equity'] = positions_cumulative['PL_final'] + positions_cumulative['Total_PL']

      positions_cumulative = positions_cumulative.drop(columns=['PL_Points','PL_Points_Euro', 'Point','Symbol'])    #2

      mask = pd.to_datetime(prices_list_D1.index) > positions_cumulative.index[0]

      positions_cumulative['Equity'] = positions_cumulative['Equity'].fillna(positions_cumulative['Total_PL'])

      res = positions_cumulative[['Equity','Commission','Swap_corrected']] # Equity will include swap_corrected + com
      res.columns = [in_symbol + '_' + item for item in res.columns]
      return res

  def compute_duration_bounds(self):
      xmin = []
      xmax = []
      ymin = []
      ymax = []
      self.compute_profit_durations()
      for item in list(self.profits_duration.values()) : # list of tuple
          xmin.append(min([iter[0] for iter in item ]))
          xmax.append(max([iter[0] for iter in item ]))
          ymin.append(max([iter[1] for iter in item ]))
          ymax.append(min([iter[1] for iter in item ]))
      pass

      xmax_all = xmax[-1]
      xmin_all = xmin[-1]

      ymax_all = ymax[-1]
      ymin_all = ymin[-1]

      xmax_symbols = max((xmax[:-1]))
      xmin_symbols =  min((xmax[:-1]))
      xlim_all = 1.2*max((abs(xmax_all),abs(xmin_all)))
      xlim_symbols = 1.2*max((abs(xmax_symbols),abs(xmin_symbols)))

      ymax_symbols = max((ymax[:-1]))
      ymin_symbols =  min((ymax[:-1]))
      ylim_all = 1.2*max((abs(ymax_all),abs(ymin_all)))
      ylim_symbols = 1.2*max((abs(ymax_symbols),abs(ymin_symbols)))
      return[(xlim_symbols,ylim_symbols),(xlim_all,ylim_all)]
  def compute_profit_durations(self):
      if bool(self.profits_duration):
          return
      [self.profits_duration.update({item : compute_profit_durations(self.df_positions,item,self.configcommon)}) for item in self.symbolList]

  def plot_return_durations_all_symbols(self):
      self.compute_profit_durations()
      bounds = self.compute_duration_bounds()
      xlim_symbols = bounds[0][0]
      ylim_symbols = bounds[0][1]
      xlim_all = bounds[1][0]
      ylim_all = bounds[1][1]

      titles = ('Hours', 'Euro', self.sRunName + "( " + self.freq + " ) " + 'Profit vs durations ')


      (in_nColsTotalSubPlot,in_nRowsTotalSubPlot) = get_col_row_correlation_graph(self.symbolListNoALL,self.configcommon)
      plt.figure(figsize=(15, 15))

      [plot_scatter_durations_subplot(item,self.profits_duration[item],in_nColsTotalSubPlot,in_nRowsTotalSubPlot,count+1,titles,'b',self.configcommon,xlim_symbols,ylim_symbols) for count,item in enumerate(self.symbolListNoALL)]
      plt.suptitle(self.configcommon.get('Correlations', 'SupTilteName') + " (" + self.configsubrun.get('Run', 'sRunName') + ":" + self.configsubrun.get('Run', 'sSubRunName') + ")" +  " (" + self.freq + ")", fontsize=int(self.configcommon.get('Correlations', 'Correlations_SupTitleSize')))
      plt_overwrite_and_save(path.join(self.sReportsPath,self.configcommon.get('FilePth','sDurationPath')), self.config.get('Inputs', 'Frequency') + '_' + self.sRunName + '_durations.png')
      plt.close()

      plt.figure(figsize=(15, 15))

      plot_scatter_durations_mainplot('ALL',self.profits_duration['ALL'],titles,'b',self.configcommon,xlim_all,ylim_all)
      plt_overwrite_and_save( path.join(self.sReportsPath,self.configcommon.get('FilePth','sDurationPath')), self.config.get('Inputs', 'Frequency') + '_' + self.sRunName + '_ALL_durations.png')
      plt.close()
  def plot_return_durations(self, in_symbol,toplot,in_nColsTotalSubPlot,in_nRowsTotalSubPlot,in_plot_count,xlim,ylim):



      plot_scatter_durations(in_symbol, x,y, in_nRowsTotalSubPlot, in_nColsTotalSubPlot, in_plot_count,titles, 'b', self.configcommon,xlim,ylim)



  def plot_histogram_SL_TP(self):
      rows = ['TP' 'SL' 'Expert']

      mask_tp = self.df_positions['Reason'] == self.configcommon.get('Names', 'Entry_TP')
      mask_sl = self.df_positions['Reason'] == self.configcommon.get('Names', 'Entry_SL')
      mask_expert = (self.df_positions['Reason'] == self.configcommon.get('Names', 'Entry_Expert')) & (
                  self.df_positions['Entry'] == self.configcommon.get('Names', 'Entry_Out'))

      df_tp = self.df_positions[mask_tp]
      df_sl = self.df_positions[mask_sl]
      df_other = self.df_positions[mask_expert]

      dataframes = [df_tp, df_sl, df_other]
      dataframes_processed = []

      for df in dataframes:
          df = df['Profit']
          df = df.reset_index(drop='True')
          df = df.sort_values(ascending=True)
          dataframes_processed.append(df)

      barWidth = 1
      edgeWidth = 0.12
      color_maps = [self.configcommon.get('SL_TP_Histogram', 'Color_TP'), self.configcommon.get('SL_TP_Histogram', 'Color_SL'),
                    self.configcommon.get('SL_TP_Histogram', 'Color_Expert')]


      names = ['TP', 'SL', 'Expert']

      for count_X, df_plt in enumerate(dataframes_processed):
          cmap = get_cmap(len(df_plt), color_maps[count_X])
          total = df_plt.sum()
          part_list = []
          mini = df_plt.min()
          maxi = df_plt.max()
          for count, row in enumerate(df_plt):
              part = (row - mini) / (maxi - mini)
              part_list.append(part)
              if count == 0:
                  plt.bar(names[count_X], row, linewidth=edgeWidth, color=cmap(200), alpha=part, edgecolor='blue',
                          width=barWidth, align='edge')
              else:
                  sum = df_plt.iloc[0:count].sum()
                  plt.bar(names[count_X], row, linewidth=edgeWidth, bottom=sum, color=cmap(200), alpha=part,
                          edgecolor='blue', width=barWidth, align='edge')
      plt.title(self.configcommon.get('SL_TP_Histogram', 'Title_SL_TP_Histo'))
      plt_overwrite_and_save(path.join(self.sReportsPath, self.sRunName + '_SL_TP_Histogram.png'))
      plt.close()


  def plot_return_correlation_BySymbol(self,in_nRowsTotalSubPlot,in_nColsTotalSubPlot,in_plot_count,dict_return,xlim):
      symbols = list(dict_return.keys())
      returns = list(dict_return.values())
      returns = [item['Return'] for item in returns]
      df_equities_to_scatter = pd.concat(returns, axis=1)
      df_equities_to_scatter = df_equities_to_scatter.dropna()
      df_equities_to_scatter.columns = ['Return_' + symbols[0], 'Return_' + symbols[1]]
      ax1 = plt.subplot(in_nRowsTotalSubPlot, in_nColsTotalSubPlot, in_plot_count)
      plt.scatter(df_equities_to_scatter.iloc[:, 0], df_equities_to_scatter.iloc[:, 1], s=int(self.configcommon.get('Correlations', 'Correlations_Marker_Size')),
                  label=('correlations' + symbols[0] + '_' +  symbols[1]))

      ax1.set_xlim([-xlim, xlim])
      ax1.set_ylim([-xlim, xlim])

      m, b = np.polyfit(df_equities_to_scatter.iloc[:, 0], df_equities_to_scatter.iloc[:, 1], 1)

      plt.plot(df_equities_to_scatter.iloc[:, 0], m * (df_equities_to_scatter.iloc[:, 0]) + b)
      plt.title((symbols[0] + '_' + symbols[1] + '(' + str(round(m, 4)) + ')'),
                fontsize=self.configcommon.get('Correlations', 'Correlations_Font_Size'))
      plt.xlabel(symbols[0])
      plt.ylabel(symbols[1])

      plt.subplots_adjust(wspace=float(self.configcommon.get('Correlations', 'Correlations_wspace')),
                          hspace=float(self.configcommon.get('Correlations', 'Correlations_hspace')))
      pass
  def plot_return_correlation_ByPair(self,in_nRowsTotalSubPlot,in_nColsTotalSubPlot,in_plot_count,symbol_one, symbol_two,xlim):

      df_positions =  read_positions(path.join(self.sBasePathFreq, self.sFileName))

      mask = df_positions['Entry'] ==  self.configcommon.get('Names', 'Entry_Out')
      in_df_positions = (df_positions[mask])
      df_to_process = [filterBySymbol(in_df_positions, item, self.configcommon) for item in [symbol_two, symbol_one]]
      df_processed = []
      for item in df_to_process:
          try:
              item = item['Profit'] + item['Commission'] + item['Swap_corrected']
          except:
              pass
          item = pd.DataFrame(item.resample('W').sum())
          item['Balance'] = item.cumsum()
          item['Balance'] = item['Balance'].shift(periods=1)

          item['Balance'] = self.balance_initial + item['Balance']
          item.iat[0, 1] = self.balance_initial
          item.columns = ['Profit', 'Balance']
          item['Return'] = item['Profit'] / item['Balance']
          item = item.drop(['Profit', 'Balance'], axis=1)
          df_processed.append(item)

      res = pd.concat(df_processed, axis=1)
      res = res.dropna()
      res.columns = ['Return_' + symbol_one, 'Return_' + symbol_two]
      ax1 = plt.subplot(in_nRowsTotalSubPlot, in_nColsTotalSubPlot, in_plot_count)
      plt.scatter(res.iloc[:, 0], res.iloc[:, 1], s=0.5,
                  label=('correlations' + symbol_one + '_' + symbol_two))

      ax1.set_xlim([-xlim,xlim])
      ax1.set_ylim([-xlim,xlim])


      m, b = np.polyfit(res.iloc[:, 0], res.iloc[:, 1], 1)

      plt.plot(res.iloc[:, 0], m * (res.iloc[:, 0]) + b,linewidth = 0.25)
      plt.title((symbol_one + '_' + symbol_two + '(' + str(round(m, 2)) + ')'),
                fontsize=self.configcommon.get('Correlations', 'Correlations_Font_Size'))
      plt.xticks(fontsize=5)
      plt.yticks(fontsize=5)


      plt.subplots_adjust(wspace=float(self.configcommon.get('Correlations', 'Correlations_wspace')),
                          hspace=float(self.configcommon.get('Correlations', 'Correlations_hspace')))

  def plot_return_correlation_AllCombinations(self):
      equity_resampled_W1_returns = compute_resampled_return(self.equities_all_symbol,self.balance_initial)

      xmax = np.array(([item['Return'].max() for item in list(equity_resampled_W1_returns.values())]))
      xmin = np.array(([item['Return'].min() for item in list(equity_resampled_W1_returns.values())]))

      xmax_all = xmax[-1]
      xmin_all = xmin[-1]

      xmax_symbols = max((xmax[:-1]))
      xmin_symbols =  min((xmax[:-1]))
      xlim_all = 1.2*max((abs(xmax_all),abs(xmin_all)))
      xlim_symbols = 1.2*max((abs(xmax_symbols),abs(xmin_symbols)))
      list_combinations = list(combinations(self.symbolList, 2))
      (in_nColsTotalSubPlot,in_nRowsTotalSubPlot) = get_col_row_correlation_graph(list_combinations,self.configcommon)

      list_combinations_not_all = [item for item in list_combinations if 'ALL' not in item]
      list_combinations_only_all = [item for item in list_combinations if 'ALL' in item]
      plt.figure(figsize=(15, 15))

      for count, item in enumerate(list_combinations_not_all):
          self.plot_return_correlation_ByPair(in_nRowsTotalSubPlot, in_nColsTotalSubPlot,count + 1, item[0], item[1],xlim_symbols)
      plt.suptitle(self.configcommon.get('Correlations', 'SupTilteName') + " (" + self.configsubrun.get('Run', 'sRunName') + ":" + self.configsubrun.get('Run', 'sSubRunName') + ")" +  " (" + self.freq + ")", fontsize=int(self.configcommon.get('Correlations', 'Correlations_SupTitleSize')))
      plt_overwrite_and_save(path.join(self.sReportsPath,self.configcommon.get('FilePth','sCorrelationPath')), self.config.get('Inputs', 'Frequency') + '_' + self.sRunName + '_Correlations.png')
      plt.close()


      (in_nColsTotalSubPlot,in_nRowsTotalSubPlot) = get_col_row_correlation_graph(list_combinations_only_all,self.configcommon)
      plt.figure(figsize=(15, 15))

      for count, item in enumerate(list_combinations_only_all):
          self.plot_return_correlation_ByPair(in_nRowsTotalSubPlot, in_nColsTotalSubPlot,count + 1, item[0], item[1],xlim_all)
      plt.suptitle(
          self.configcommon.get('Correlations', 'SupTilteName') + " (" + self.configsubrun.get('Run', 'sRunName') + ":" + self.configsubrun.get('Run', 'sSubRunName') + ")" +  " (" + self.freq + ")", fontsize=int(self.configcommon.get('Correlations', 'Correlations_SupTitleSize')))
      plt_overwrite_and_save(path.join(self.sReportsPath, self.configcommon.get('FilePth','sCorrelationPath')),self.config.get('Inputs', 'Frequency') + '_' + self.sRunName + '_ALLCorrelations.png')
      plt.close()



  def plot_return_correlation_symbols(self):
      df_positions = self.df_positions
      equity_resampled_W1_returns = compute_resampled_return(self.equities_all_symbol)
      max_profit = df_positions['Profit'].max()
      xmax = np.array(([item['Return'].max() for item in list(equity_resampled_W1_returns.values())]))
      xmin = np.array(([item['Return'].min() for item in list(equity_resampled_W1_returns.values())]))

      xmax_all = xmax[-1]
      xmin_all = xmin[-1]

      xmax_symbols = max((xmax[:-1]))
      xmin_symbols =  min((xmax[:-1]))
      xlim_all = 1.2*max((abs(xmax_all),abs(xmin_all)))
      xlim_symbols = 1.2*max((abs(xmax_symbols),abs(xmin_symbols)))

      list_combinations = self.symbolListNoALL
      in_nColsTotalSubPlot = self.configcommon.get('Correlations','Correlations_NColumns')
      in_nRowsTotalSubPlot = floor(
          (len(list_combinations) / int(self.configcommon.get('Correlations', 'Correlations_NColumns')))) + 1

      if len(list_combinations) < int(self.configcommon.get('Correlations', 'Correlations_NColumns')):
          in_nColsTotalSubPlot = len(list_combinations)
      else:
          in_nColsTotalSubPlot = int(self.configcommon.get('Correlations', 'Correlations_NColumns'))

      for symbol_count,symbol in enumerate(self.symbolListNoALL) :
        plt.figure()
        [self.plot_return_correlation_BySymbol(in_nRowsTotalSubPlot, in_nColsTotalSubPlot,count + 1, {symbol: equity_resampled_W1_returns[symbol], item:  equity_resampled_W1_returns[item]},xlim_symbols) for count,item in enumerate(self.symbolListNoALL) if symbol not in item]
        plt.suptitle(self.configcommon.get('Correlations', 'SupTilteName') + " (" + self.configsubrun.get('Run', 'sRunName') + ":" + self.configsubrun.get('Run', 'sSubRunName') + ")" +  " (" + self.freq + ")", fontsize=int(self.configcommon.get('Correlations', 'Correlations_SupTitleSize')))
        plt_overwrite_and_save(path.join(self.sReportsPath, self.configcommon.get('FilePth','sCorrelationPath'),symbol + '_' + self.config.get('Inputs', 'Frequency') + '_' + self.sRunName + '_Correlations.png'))
        plt.close()
      plt.figure()
      for count, item in enumerate(self.symbolListNoALL):
          self.plot_return_correlation_BySymbol(in_nRowsTotalSubPlot, in_nColsTotalSubPlot,count + 1, {'ALL' : equity_resampled_W1_returns['ALL'], item:  equity_resampled_W1_returns[item]},xlim_all)
      plt.suptitle(self.configcommon.get('Correlations', 'SupTilteName') + " (" + self.configsubrun.get('Run', 'sRunName') + ":" + self.configsubrun.get('Run', 'sSubRunName') + ")" +  " (" + self.freq + ")", fontsize=int(self.configcommon.get('Correlations', 'Correlations_SupTitleSize')))
      plt_overwrite_and_save(path.join(self.sReportsPath, self.configcommon.get('FilePth','sCorrelationPath'),'ALL_' + self.config.get('Inputs', 'Frequency') + '_' + self.sRunName + '_Correlations.png'))
      plt.close()
     # plt.show()
      pass
  def calibrate_commissions(self):
      calibs = self.plot_commissions_all()
      sFilePath = path.join(self.sReportsPath, self.configcommon.get('FilePth', 'sCommissionsPath'),  'Calibrations.csv')
      values = [list(item.values()) for item in calibs]
      values = [item[0] for item in values]
      keys = [list(item.keys()) for item in calibs]
      keys = [item[0] for item in keys]

      df_calibs = pd.DataFrame(values,index = keys )
      df_calibs.columns = ['mu','sigma']
      df_calibs.to_csv(sFilePath,sep = ";")
      pass
  def plot_commissions_all(self):

      plt.figure(figsize=(15, 15))
      plt.xlabel('Commissions(€)')
      plt.ylabel('Number')
      xmax = (self.df_positions['Commissions'].max())
      xmin = 0
      xmax = 1

      plt.xlim([xmin, xmax])
      calibrations =[self.plot_commissions(item) for item in self.symbolListNoALL]

      return(calibrations)
  def make_waterfall_return_figure(self):
      import plotly.graph_objects as go
      df_equities_ultimate_percent_no_all = {k: self.df_equities_ultimate_percent[k] for k in self.df_equities_ultimate_percent.keys() - {'ALL'}}

      df_equities_ultimate_percent_no_all = dict(sorted(df_equities_ultimate_percent_no_all.items(), key=lambda x: x[0].lower()))
      df_equities_ultimate_percent_no_all.update({'ALL' : self.df_equities_ultimate_percent['ALL']})
      df_equities_ultimate_percent = df_equities_ultimate_percent_no_all.copy()

      measures = ["relative" for item in list(df_equities_ultimate_percent_no_all)]
      measures.append("total")
      symbols = [item for item in df_equities_ultimate_percent.keys()]
      yvalues = [round(100*item,2) for item in df_equities_ultimate_percent.values()]
      text = [str(item) + '%' for item in yvalues]
      fig = go.Figure(go.Waterfall(
          name="20", orientation="v",
          measure=measures,
          x=symbols,
          textposition="outside",
          text=text,
          y=yvalues,
          connector={"line": {"color": "rgb(63, 63, 63)"}},
      ))

      fig.update_layout(
          title=self.freq + '_' + +self.sTitlePrefix ,
          showlegend=True
      )
      go_overwrite_and_save(self.sReportsPath, self.sRunName + '_Waterfall' + '.png',fig)

      pass
  def run(self):

    # self.plot_return_correlation_symbols()
     #self.calibrate_commissions()

     #self.plot_histogram_SL_TP()
     plt.figure(figsize=(15, 15))
     self.plot_profits_all_symbols()


     self.plot_return_durations_all_symbols()
     self.plot_return_correlation_AllCombinations()
     plt.figure(figsize=(15, 15))

     self.plot_MAE_MFE()
     pass
