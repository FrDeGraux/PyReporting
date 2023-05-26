import matplotlib.pyplot as plt
from os import path
from utils.utilPlot import plot_scatter_durations,plot_scatter,get_col_row_correlation_graph,get_cmap
from utils.utilPlot import plt_overwrite_and_save,from_plot_to_x_y,plot_scatter_durations_subplot,plot_scatter_durations_mainplot

import pandas as pd
import math
import numpy as np
class MultiTFReporter :
    def __init__(self,in_list_reporter,in_sComparaison,in_sRunName,in_config_common,in_sBasePath):
        self.config_common =in_config_common
        self.frequencies = {'H1': self.config_common.get('AllInputs', 'Frequencies_1'),
                            'H4': self.config_common.get('AllInputs', 'Frequencies_2'),
                            'D1': self.config_common.get('AllInputs', 'Frequencies_3'),
                            'W1': self.config_common.get('AllInputs', 'Frequencies_4')}
        self.Frequencies = [value for key, value in self.frequencies.items()]

        self.sFileNames = [item.sFileName for item in in_list_reporter]
        self.lst_reporters = in_list_reporter
        self.sBasePath = in_sBasePath
        self.sSymbolList = in_list_reporter[0].symbolList
        self.sSymbolListNoALL = in_list_reporter[0].symbolListNoALL
        self.comparisons = in_sComparaison
        self.sRunName = in_sRunName
        self.sTitlePrefix = ''
        self.stylesPlot = ['solid','dotted','dashed']
        self.ylims = self.compute_y_lims()
        self.symbolList = self.lst_reporters[0].symbolList
        self.percents = [item.df_equities_percent for item in self.lst_reporters]
        self.df_equities_ultimate_percent = [item.df_equities_ultimate_percent for item in self.lst_reporters]

        self.symbolListNoALL = self.lst_reporters[0].symbolListNoALL
        self.names = [item.sSubRunName for item in self.lst_reporters]

    def compute_y_lims(self):
        minimums_all_tf = []
        maximums_all_tf = []
        minimums_all_tf_ALL = []
        maximums_all_tf_ALL = []
        for reporter in self.lst_reporters :
            dict_equities = reporter.equities_all_symbol
            minimums = [dict_equities[item][item + '_Equity'].min() for item in self.sSymbolListNoALL]

            maximums = [dict_equities[item][item + '_Equity'].max() for item in self.sSymbolListNoALL]
            minimums_ALL = dict_equities['ALL']['ALL' + '_Equity'].min()
            maximums_ALL = dict_equities['ALL']['ALL' + '_Equity'].max()
            minimums_all_tf.append(minimums)
            maximums_all_tf.append(maximums)
            minimums_all_tf_ALL.append(minimums_ALL)
            maximums_all_tf_ALL.append(maximums_ALL)
        minimums_all_tf = [item for sublist in minimums_all_tf for item in sublist]
        maximums_all_tf = [item for sublist in maximums_all_tf for item in sublist]
        return([(min(minimums_all_tf),max(maximums_all_tf)),(min(minimums_all_tf_ALL),max(maximums_all_tf_ALL))])
        pass

    def bar_symbol_profit(self, in_symbol,count, ax1=None, ylim=None):
        ax = plt.subplot(len(self.symbolList), 1, count + 1, sharex=ax1)
        data = [item[in_symbol] for item in self.percents]
        data_ultimate = [item[in_symbol] for item in self.df_equities_ultimate_percent]
        data = pd.concat(data, axis=1)

        data.columns = [col + '_' + name for (col,name) in zip(data.columns,self.names)]
        #  data['year'] = data.index.year
        iBarStep = 0.3
        nMethods = len(data.columns)
        dts= data.index[-1] +  pd.offsets.DateOffset(years=1)
        data_ultimate = pd.DataFrame(data_ultimate).T
        data_ultimate = data_ultimate.set_index(pd.Index([dts]))
        data_ultimate.columns = list(data.columns)
        data = pd.concat([data, data_ultimate],axis =0 )
        step_values = 2*iBarStep/(math.ceil(nMethods / 2.) * 2)
        if (nMethods % 2) == 0:
            step_lim = iBarStep-step_values
        else :
            step_lim = iBarStep
        xindexes = np.arange(-iBarStep, step_lim + step_values,step_values)
        for idx,_ in enumerate(data.columns) :
            plt.bar(data.index.year -1  + xindexes[idx], data.iloc[:,idx], step_values, label=self.names[idx])
        if ylim is not None:
            ax.set_ylim([-ylim, ylim])
        plt.legend(bbox_to_anchor=(1, 1.0), loc='upper left',fontsize = 5)

        #ax.legend(fontsize = 5)

        plt.title(in_symbol + '_Returns', fontsize=5, loc='center')

        return (ax)
    def bar_all_profits(self):
        percents = [item.df_equities_percent for item in self.lst_reporters]
        symbols = self.symbolListNoALL
        df_concat = [pd.concat(item, axis=1) for item in self.percents]
        df_ultimate = [pd.DataFrame.from_records(item,index = ['A']) for item in self.df_equities_ultimate_percent]
        df_concat = [df_periodic_item.append(df_ultimate_item, ignore_index=True) for df_periodic_item,df_ultimate_item in zip (df_concat,df_ultimate)]
        df_concat = [item.dropna() for item in df_concat]

        df_concat_all= [item['ALL'] for item in df_concat]
        df_concat_noall= [item.drop(columns = ['ALL']) for item in df_concat]



        dmax_noall = max([item.max().max() for item in df_concat_noall])
        dmin_noall = min([item.min().min() for item in df_concat_noall])

        dmmax_all = max([item.min()for item in df_concat_all])
        dmin_all = min([item.min() for item in df_concat_all])

        ylims_noall = max(abs(dmax_noall),abs(dmin_noall))
        ylims_all = max(abs(dmmax_all),abs(dmin_all))
        ax = self.bar_symbol_profit('ALL', 0,None,ylims_all)
        self.bar_symbol_profit('ALL', 0,ax,ylims_all)

        for idx,symbol in enumerate(symbols ):
            self.bar_symbol_profit(symbol,1+idx,ax,ylims_noall)
        plt.title('Bars_' + self.freq + '_' + self.sRunName)
        plt.savefig(path.join(self.sBasePath, self.comparisons, self.lst_reporters[0].freq, 'Reports','Bars_' + self.sRunName + '_' + symbol + '.png'), dpi=800)

        pass
        # df _H1 , H_4, H_
        # for the symbol

    def plot_durations_comparisons(self):

        bounds_all_reporters = [item.compute_duration_bounds() for item in self.lst_reporters]

        bounds_not_all = [item[0] for item in bounds_all_reporters]
        bounds_all = [item[1] for item in bounds_all_reporters]


        x_bounds = max(bounds_not_all,key=lambda item:item[0])[0]
        y_bounds = max(bounds_not_all,key=lambda item:item[1])[1]

        x_bounds_all = max(bounds_all,key=lambda item:item[0])[0]
        y_bounds_all = max(bounds_all,key=lambda item:item[1])[1]

        (in_nColsTotalSubPlot,in_nRowsTotalSubPlot) = get_col_row_correlation_graph(self.symbolListNoALL,self.config_common)
        fig = plt.figure(figsize=(15, 15))
        for reporter in (self.lst_reporters) :
            [plot_scatter_durations_subplot(item,reporter.profits_duration[item],in_nColsTotalSubPlot,in_nRowsTotalSubPlot,count+1,'tests',reporter.durations_color,self.config_common,x_bounds,y_bounds) for count,item in enumerate(self.symbolListNoALL)]



        sTitle = [item.sFileOutput for item in self.lst_reporters]
        sTitle = ",".join(sTitle)
        sTitle = 'Correlations : ' + sTitle + " (" + self.lst_reporters[0].freq + ")"
        plt.suptitle(sTitle, fontsize=int(self.config_common.get('Correlations', 'Correlations_SupTitleSize')))

        sFileName_NotALL = self.lst_reporters[0].freq + '_' + self.sRunName + '_durations.png'
        sFileName_ALL = self.lst_reporters[0].freq + '_' + self.sRunName + '_ALL_durations.png'
        sSavePath = path.join(self.sBasePath, self.comparisons, self.lst_reporters[0].freq, 'Reports', 'Durations_Returns')

        plt_overwrite_and_save(sSavePath, sFileName_NotALL)

        plt.close()

        fig = plt.figure(figsize=(15, 15))
        ax = plt.gca()

        for reporter in self.lst_reporters:
            plot_scatter_durations_mainplot('ALL', reporter.profits_duration['ALL'], ax, 'te', reporter.durations_color,
                                            self.config_common, x_bounds_all, y_bounds_all)
        plt.suptitle(sTitle)
        plt.suptitle(sTitle)

        plt_overwrite_and_save(sSavePath, sFileName_ALL)
        plt.close()

    def plot_profits_all_timeframes(self): # for one run
        # By Symbol,plot inside the reporter function
        for symbol in self.sSymbolList :
            plt.figure(figsize=(15, 15))
            sTitle = symbol + '_' + 'Multiple_Methods'
            [item.plot_profit_from_multi_reporter(symbol,self.stylesPlot[idx],self.ylims[0],self.ylims[1],in_title=sTitle,in_plotCommissionFree = False) for idx,item in enumerate(self.lst_reporters)]
            plt.title(symbol + '_' + self.lst_reporters[0].freq + '_' +  self.sRunName )
            plt.savefig(path.join( self.sBasePath,self.comparisons,self.lst_reporters[0].freq,'Reports',self.sRunName + '_' + symbol + '.png'),dpi = 800)
            pass