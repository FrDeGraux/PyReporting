# This is a sample Python script.
from utilPlot import plot_scatter,plot_time_graph,plot_scatter_durations
from utilMapping import from_entry_to_category
from utilReader import read_positions
import matplotlib.pyplot as plt
from os import path
from itertools import combinations
from math import floor
from utilConfig import init_config
from utilData import filterBySymbol,getSymbolList,unpackComment_MM
from matplotlib import cm

config = init_config('config_run_2_2_H1.ini')
sRunName = config.get('Run', 'sRunName')
sMotherPath = config.get('FilePth', 'sBasePath')
sMotherPath = sMotherPath.replace("\\\\", "\\")


sBasePath = path.join(sMotherPath,sRunName)
sBasePathFreq = path.join(sBasePath,config.get('Inputs', 'Frequency'))

sReportsPath = path.join(sBasePathFreq,config.get('FilePth', 'sReportsPath'))

sDurationReturnPath = path.join(sReportsPath,config.get('FilePth', 'sDurationPath'))
# Press Shift+F10 to FilePth it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import numpy as np

frequencies = {'H1': config.get('AllInputs', 'Frequencies_1'), 'H4': config.get('AllInputs', 'Frequencies_2'),
               'D1': config.get('AllInputs', 'Frequencies_3'), 'W1': config.get('AllInputs', 'Frequencies_4')}
Frequencies = [value for key,value in frequencies.items()]

sFileName_SMA = {'H1': config.get('AllInputs', 'sFileName_H1_SMA'),
                 'H4': config.get('AllInputs', 'sFileName_H4_SMA'),
                 'D1': config.get('AllInputs', 'sFileName_D1_SMA')}

sFileName_SMA_noHysteresis = {'H1': config.get('Inputs_NoStaticHysteresis', 'sFileName_H1'),
                 'H4': config.get('Inputs_NoStaticHysteresis', 'sFileName_H4'),
                 'D1': config.get('Inputs_NoStaticHysteresis', 'sFileName_D1')}
sFileName_EMA = {'H1': config.get('AllInputs', 'sFileName_H1_EMA'),
                 'H4': config.get('AllInputs', 'sFileName_H4_EMA'),
                 'D1': config.get('AllInputs', 'sFileName_D1_EMA'),
                 'W1': config.get('AllInputs', 'sFileName_W1_EMA')}
sFileNames = {'H1': config.get('AllInputs', 'sFileName_H1'),
                 'H4': config.get('AllInputs', 'sFileName_H4'),
                 'D1': config.get('AllInputs', 'sFileName_D1'),
              'W1': config.get('AllInputs', 'sFileName_W1')}
balance_initial = 10000


#5.•	Graphique Trade durations vs Profit (correlation by symbol?), with marker for the reason (technical or SL/TP)
#•	Number of SL/TP vs full winner (in number and in euro) : full winner
#•	Number of SL lost vs TP win
#•	Return correlations by symbol (with regression line)
# Return 1 is on the H1 dataframe =
#•	Volatility of timeframe returns (H1,D1,etc)#
# Trade Histogram (by biggest to losest trade with dt)
# Plot(time,return)
# Plot(time,nTrades)def print_hi(name):
# knowing the reaons why it was hit (SL,TP,etc)
# Plot(return,régime)    # Use a breakpoint in the code line below to debug your script.
# Plot BySymbol    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def run_all_timeframes(in_config) :

    sFile_SMA = [item.values() for item in sFileName_SMA]
    sFile_EMA = [item.values() for item in sFileName_EMA]


    sListRunNames = [config.get('Run', 'sRunName_SMA'),config.get('Run', 'sRunName_EMA')]
    list_Styles = [config.get('Styles', 'Style_SMA_Returns'),config.get('Styles', 'Style_EMA_Returns')]
    plot_profits_many_runs(Frequencies,sListRunNames,sFile_SMA,sFile_EMA,list_Styles,in_config)

def plot_profits_many_runs(in_frequencies,in_listRunNames,in_sFileName_One,in_sFileName_Two,in_Styles,in_config) :
    sListBasePath = [path.join(sMotherPath,item) for item in in_listRunNames]

    [plot_profits_all_timeframes(item[2],item[0], in_frequencies, item[1],item[3], in_config) for item in zip([in_sFileName_One,in_sFileName_Two],sListBasePath,in_listRunNames,in_Styles)]


    plt.title(in_config.get('Returns', 'Graph_Title') + in_config.get('Run', 'sRunNameSMA') + " VS " + in_config.get('Run', 'sRunNameEMA') + "_" + "_ALL TIMEFRAMES")
    plt.legend(loc="best")
    plt.savefig(path.join(sMotherPath, 'All_returns' + '.png'))



def plot_profits_all_timeframes(in_sRun,in_sFileNameList,in_FrequencyList,in_sBasePath,in_sListLineStyles,in_config) : # for one run

    for sFilePath, freq in zip(in_sFileNameList, in_FrequencyList):
        plot_profit_timeframe(in_sRun,path.join(in_sBasePath,freq,sFilePath),freq,in_sListLineStyles, in_config)
    plt.title(in_config.get('Returns', 'Graph_Title')  + "_" + "_MANY RUNS " + " TIMEFRAMES")
    plt.legend(loc="best")
    plt.show()
    plt.savefig(path.join(in_sBasePath, 'All_returns' + '.png'))





def plot_profit_timeframe(in_sRunName,sFilePath,in_sFreq,style,in_config) :

    sFilePath = path.join(sBasePath,sFilePath)
    df_positions = read_positions(sFilePath)
    in_timeframe = in_config.get('Returns', 'TimeFrame')

    df_positions_filtered = df_positions[['Profit', 'SwapReal', 'Commission']]
    profits = df_positions_filtered.resample(in_timeframe).sum()
    profits_cumulated = profits.cumsum()
    profits_cumulated['Total'] = profits_cumulated[list(profits_cumulated.columns)].sum(axis=1)


    plt.plot(profits_cumulated.index.tolist(), profits_cumulated['Total'].values,label = (in_sFreq + '_' + in_sRunName),linestyle= style)


#1. #Profit TimeSeriees
def plot_profits_all_symbols(in_df_positions,sSymbolList,in_config) :       # plot_balance
    in_timeframe = in_config.get('Returns', 'TimeFrame')
    turbo = cm.get_cmap('turbo', len(sSymbolList))


    for idx,symbol in enumerate(sSymbolList) :
        in_df_positions_filtered = filterBySymbol(in_df_positions,symbol,in_config)

        in_df_positions_filtered = in_df_positions_filtered[['Profit','Swap_corrected','Commission']]
        profits = in_df_positions_filtered.resample(in_timeframe).sum()
        profits_cumulated = profits.cumsum()
        profits_cumulated['Total'] = profits_cumulated[list(profits_cumulated.columns)].sum(axis=1)
        plt.plot(profits_cumulated.index.tolist(), profits_cumulated['Total'].values, label=symbol,color = turbo.colors[idx])
        plt.title(in_config.get('Inputs', 'Frequency')  + '_' + in_config.get('Run', 'sRunName')  + '_' + in_config.get('Returns', 'Graph_Title') + in_timeframe + "_" +symbol)
        plt.legend(loc="best")
        if symbol == 'ALL' :
            plt.savefig(path.join(sReportsPath, sRunName + '_Profits' + symbol) + '.png')



        # filter

    # LEGENDE
#2 Profit vs Time
def plot_returns_durations_compare(in_df_positions,in_symbol,in_config,in_dfPositionToCompareAgainst) :
    plt.figure()
    plot_return_durations(in_df_positions, in_symbol, in_config,'b')
    plot_return_durations(in_dfPositionToCompareAgainst, in_symbol, in_config,'r')
    plt.legend(["With static", "Without static"])
    plt.savefig(path.join(sDurationReturnPath,sRunName + '_durations_vs_returns_' + "_" + in_config.get('Inputs', 'Frequency') + "_" + in_symbol + '.png'))
def plot_return_durations(in_df_positions,in_symbol,in_config,in_color) :

    in_df_positions = filterBySymbol(in_df_positions,in_symbol,in_config)

    # plot return vs Trade duration (color is the profit)
    mask = in_df_positions['Entry'] == in_config.get('Names', 'Entry_Out')
    df_sell = (in_df_positions[mask])
    df_sell['Reason_number'] = df_sell.apply(lambda row: from_entry_to_category(row), axis=1)
    toplot = []
    for row in df_sell.iterrows() :
        row = row[1]
        val = row[in_config.get('Names', 'PositionMissedParameters')]
        mask_position = (in_df_positions[in_config.get('Names', 'PositionMissedParameters')] == val)
        df = in_df_positions[mask_position]
        df = df[df['Entry'] == in_config.get('Names', 'Entry_In')]
        if(len(df) > 1) :
            raise Exception('plot_return_durations::more than one purchase')
        entryIn = df['Time'].values[0]
        entryOut = row['Time']
       #  entryIn = datetime.strptime(df['Time'].values[0],'%Y.%m.%d %H:%M:%S ')
    #entryOut = datetime.strptime(row['Time'],'%Y.%m.%d %H:%M:%S ')
        toplot.append((entryOut-entryIn,(row['Profit']),(row['Reason_number'])))
    titles = ('Hours','Euro',in_config.get('Run', 'sRunName') + "( " + in_config.get('Inputs', 'Frequency') + " ) " +  'Profit vs durations  ' + in_symbol)
    toplot = sorted(toplot,key=lambda x: x[0],reverse=True)
    plot_scatter_durations(in_symbol,toplot,titles,in_color,in_config)
def plot_returns_duration_bySymbol() :
    pass
#3. # of money (TP) vs # of money (SL)

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
def plot_histogram_SL_TP(in_df_position,in_config) :
    import numpy as np
    import matplotlib.pyplot as plt

    rows = ['TP' 'SL' 'Expert']

    mask_tp = in_df_position['Reason'] == in_config.get('Names', 'Entry_TP')
    mask_sl = in_df_position['Reason'] == in_config.get('Names', 'Entry_SL')
    mask_expert = (in_df_position['Reason'] == in_config.get('Names', 'Entry_Expert')) & (in_df_position['Entry'] == in_config.get('Names', 'Entry_Out'))


    df_tp = in_df_position[mask_tp]
    df_sl = in_df_position[mask_sl]
    df_other = in_df_position[mask_expert]

    dataframes = [df_tp,df_sl,df_other]
    dataframes_processed = []

    for df in dataframes :
        df = df['Profit']
        df = df.reset_index(drop='True')
        df = df.sort_values(ascending=True)
        dataframes_processed.append(df)


    barWidth = 1
    edgeWidth = 0.12
    color_maps = [config.get('SL_TP_Histogram', 'Color_TP'),config.get('SL_TP_Histogram', 'Color_SL'),config.get('SL_TP_Histogram', 'Color_Expert')]
    names = ['TP', 'SL', 'Expert']




    for count_X ,df_plt in enumerate(dataframes_processed) :
        cmap = get_cmap(len(df_plt),color_maps[count_X])
        total = df_plt.sum()
        part_list = []
        mini = df_plt.min()
        maxi = df_plt.max()
        for count,row in enumerate(df_plt):
            part = (row-mini)/(maxi-mini)
            part_list.append(part)
            if count == 0 :
                plt.bar(names[count_X],row,linewidth = edgeWidth,color=cmap(200),alpha = part,edgecolor='blue',width=barWidth,align = 'edge')
            else :
                sum = df_plt.iloc[0:count].sum()
                plt.bar(names[count_X],row,linewidth = edgeWidth,bottom= sum,color=cmap(200),alpha = part,edgecolor='blue', width=barWidth,align = 'edge')
    plt.title(config.get('SL_TP_Histogram', 'Title_SL_TP_Histo'))
    plt.savefig(path.join(sReportsPath,sRunName + '_SL_TP_Histogram.png' ))

def filterByDateTimePrevious(in_df_position,in_dt) :
    mask = in_df_position['Symbol'] < in_dt
    in_df_position = in_df_position[mask]
    return in_df_position


def plot_return_correlation_ByPair(in_df_positions,symbol_one,symbol_two,in_count,in_nRowsTotalSubPlot,in_nColsTotalSubPlot,config) :

    mask = in_df_positions['Entry'] == config.get('Names', 'Entry_Out')
    in_df_positions = (in_df_positions[mask])
    df_to_process = [filterBySymbol(in_df_positions,item,config) for item in [symbol_two,symbol_one]]
    df_processed = []
    for item in df_to_process :
        try :
            item = item['Profit'] + item['Commission'] + item['Swap_corrected']
        except :
            pass
        item = pd.DataFrame(item.resample('W').sum())
        item['Balance'] = item.cumsum()
        item['Balance'] = item['Balance'].shift(periods=1)

        item['Balance'] = balance_initial + item['Balance']
        item.iat[0,1] = balance_initial
        item.columns = ['Profit', 'Balance']
        item['Return'] = item['Profit']/item['Balance']
        item = item.drop(['Profit', 'Balance'], axis=1)
        df_processed.append(item)

    res = pd.concat(df_processed,axis=1)
    res = res.dropna()
    res.columns = ['Return_' + symbol_one, 'Return_' + symbol_two]
    ax1 = plt.subplot(in_nRowsTotalSubPlot, in_nColsTotalSubPlot, in_count)
    plt.scatter(res.iloc[:,0], res.iloc[:,1],s = int(config.get('Correlations', 'Correlations_Marker_Size')), label=('correlations' + symbol_one + '_' + symbol_two))

    ax1.set_xlim([-0.05, 0.05])
    if((symbol_one == ('ALL') or symbol_two == 'ALL')):
        ax1.set_xlim([float(config.get('Correlations', 'Correlations_xlim_all_min')), float(config.get('Correlations', 'Correlations_xlim_all_max'))])
    else :
        ax1.set_xlim([float(config.get('Correlations', 'Correlations_xlim_symbol_min')), float(config.get('Correlations', 'Correlations_xlim_symbol_max'))])


     # plt.xlabel(symbol_one,fontsize =  config.get('Correlations', 'Correlations_Font_Size'))
    #plt.ylabel(symbol_two,fontsize = config.get('Correlations', 'Correlations_Font_Size'))
    m, b = np.polyfit(res.iloc[:,0], res.iloc[:,1], 1)

    plt.plot(res.iloc[:,0], m * (res.iloc[:,0]) + b)
    plt.title(( symbol_one + '_' + symbol_two + '(' + str(round(m,4)) + ')'),fontsize= config.get('Correlations', 'Correlations_Font_Size'))

    plt.subplots_adjust(wspace =float(config.get('Correlations', 'Correlations_wspace')),hspace = float(config.get('Correlations', 'Correlations_hspace')))
def plot_return_correlation_All(symbolList) :
    list_combinations = list(combinations(symbolList, 2))
    in_nRowsTotalSubPlot = floor((len(list_combinations)/ int(config.get('Correlations', 'Correlations_NColumns'))))+1
    in_nColsTotalSubPlot = 0
    if len(list_combinations) <  int(config.get('Correlations', 'Correlations_NColumns')):
        in_nColsTotalSubPlot = len(list_combinations)
    else :
        in_nColsTotalSubPlot = int(config.get('Correlations', 'Correlations_NColumns'))

    for count,item in enumerate(list_combinations):
        plot_return_correlation_ByPair(df_positions,item[0], item[1],count+1,in_nRowsTotalSubPlot,in_nColsTotalSubPlot,config)

    plt.suptitle( config.get('Correlations', 'SupTilteName') + " (" + config.get('Run', 'sRunName') + ")" + " (" + config.get('Inputs', 'Frequency') + ")",fontsize= int(config.get('Correlations', 'Correlations_SupTitleSize')))
    plt.show()
    plt.savefig(path.join(sReportsPath,config.get('Inputs', 'Frequency') + '_' + sRunName +'_Correlations.png'))



if __name__ == '__main__':
    #run_all_timeframes(config)

    string_val = config.get('Names', 'Entry_Out')
    df_positions = read_positions(path.join(sBasePathFreq, sFileNames[config.get('Inputs','Frequency')]))


  #  df_positions_to_compare_against = read_positions(path.join(sMotherPath,config.get('Run_NoHysteresis','sRunName_SMA'),config.get('Inputs','Frequency'), sFileName_SMA_noHysteresis[config.get('Inputs','Frequency')]))
    symbolList= getSymbolList(df_positions)
    symbolList.append('ALL')
   # plt.figure(3)
  #  [plot_returns_durations_compare(df_positions, symbol, config,df_positions_to_compare_against) for symbol in symbolList]

    plt.figure(4)
  #  plot_return_correlation_All(symbolList)

    df_positions[ config.get('Names', 'PositionMissedParameters')]  = (df_positions[ config.get('Names', 'PositionMissedParameters')]).astype(str) + df_positions['Symbol']
    plt.figure(1)
    plot_histogram_SL_TP(df_positions,config)

    plt.figure(2)
    plot_profits_all_symbols(df_positions,symbolList,config)

    # 2. Duration vs Profit

    # 3. # of money (TP) vs # of money (SL)
    pass

    #4 For each out, plot Hysteresis_entry and Hysteresis_Out : intensity is the profit

