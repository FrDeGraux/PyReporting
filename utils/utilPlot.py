
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.utilConfig import build_working_hysteresis_path
from utils.utilData import  days_hours_minutes
from os import path,remove,makedirs
from math import floor
import matplotlib.pyplot as plt

from defined_enums import OptionPlotHysteresis
def plot_ultimate_returns():
    pass
def plot_histo_fixed_hysteresis(in_item_list,in_cfg,in_plot_enum) :
        sFrequency =  in_cfg.get('Inputs', 'Frequency')
        sFileName = in_cfg.get('FilePth', 'sFixedCalibrationFileName')
        threshold = str(100*float(in_cfg.get('FixedHysteresisInput', 'threshold')))
        sFileName = sFileName + '_' + threshold
        if in_plot_enum == OptionPlotHysteresis.CUMULATIVE :
            sFileName = sFrequency + '_cumulative' + sFileName + '.png'
            sTitle = sFrequency + "_cumulative_Fixed_spread"
        else :
            if in_plot_enum == OptionPlotHysteresis.STANDARD:
                sFileName = sFrequency + '_' + sFileName + '.png'
                sTitle = sFrequency + "_Fixed_spread"
            else :
                if in_plot_enum == OptionPlotHysteresis.COMPARATIVE :
                    sFileName = sFrequency + '_' + sFileName + '.png'
                    sTitle = sFrequency + "_Comparisons_Fixed_spread"
                else :
                    raise Exception




        sFileName = path.join(build_working_hysteresis_path(in_cfg),sFileName)


        df = pd.DataFrame(in_item_list, columns=['Symbol', 'Year', 'Fixed_spread'])


        if in_plot_enum != OptionPlotHysteresis.COMPARATIVE :
            sFileNameCSV = in_cfg.get('FilePth', 'sFixedCalibrationFileName')

            sFileNameCSV = path.join(build_working_hysteresis_path(in_cfg), sFileNameCSV)

            if in_plot_enum == OptionPlotHysteresis.CUMULATIVE :
                sFileNameCSV = sFileNameCSV + str(100*float(threshold)) + "_Procent" + "_" + sFrequency + '_cumulative'  + '.csv'
            else :
                if in_plot_enum == OptionPlotHysteresis.STANDARD :
                    sFileNameCSV = sFileNameCSV  + str(100*float(threshold)) + "_Procent" +  "_" + sFrequency + '.csv'
            df.to_csv(sFileNameCSV, sep=';', index=False)




        df = df.pivot("Symbol", "Year", "Fixed_spread")
        df.plot(kind='bar')

        plt.title(sTitle)

        plt.savefig(sFileName)
        pass
def plot_time_graph(in_dt,in_values,in_legendValue) :
    plt.plot(in_dt,in_values,label = in_legendValue)
    pass
def plot_scatter(in_titles,toplot,in_color,in_config) :

    plt.scatter(toplot[0],toplot[1], c=in_color,s= int(in_config.get('Correlations', 'Correlations_Marker_Size')))
    plt.title(in_titles[2],fontsize = 8)
    plt.xlabel(in_titles[0])
    plt.ylabel(in_titles[1])

def plot_scatter_durations(in_Symbol,in_ax,x,y,in_titles,in_color,in_config,xlim,ylim) :

    plt.xlim([0, xlim])
    plt.ylim([-ylim, ylim])
    plt.scatter(x,y, c=in_color,s= float(in_config.get('Correlations', 'Correlations_Marker_Size')))
    m_best, b_best = np.polyfit(x, y, 1)
    plt.plot(x, m_best * (np.array(x)) + b_best)
    correlation = np.corrcoef(x, y)
    title = in_ax.get_title() if in_ax is not None else ''
    if (len(title) > 0) :
        sTitle = in_ax.get_title() + '_' +  str(round(correlation[0,1],2))
    else :
        sTitle = in_Symbol + '_' + str(round(correlation[0, 1], 2))

    plt.title(sTitle ,fontsize = 7)

    plt.xlabel('H')
    plt.ylabel('€')

    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    plt.subplots_adjust(wspace=float(in_config.get('Correlations', 'Correlations_wspace')),
                        hspace=float(in_config.get('Correlations', 'Correlations_hspace')))
def from_plot_to_x_y(toplot) :
    toplot = sorted(toplot, key=lambda x: x[0], reverse=True)
    x = [item[0] for item in toplot]
    y = [item[1] for item in toplot]
    return(x,y)
def plot_scatter_durations_subplot(in_Symbol,toPlot,in_nRowsTotalSubPlot, in_nColsTotalSubPlot, in_plot_count,in_titles,in_color,in_config,xlim,ylim):
    (x,y) = from_plot_to_x_y(toPlot)
    ax1 = plt.subplot(in_nRowsTotalSubPlot, in_nColsTotalSubPlot, in_plot_count)
    plot_scatter_durations(in_Symbol,ax1,x,y,in_titles,in_color,in_config,xlim,ylim)
def plot_scatter_durations_mainplot(in_Symbol,toPlot,in_titles,in_color,in_config,xlim,ylim):
    (x,y) = from_plot_to_x_y(toPlot)
    fig = plt.figure(figsize=(15, 15))

    plot_scatter_durations(in_Symbol,plt.gca(),x,y,in_titles,in_color,in_config,xlim,ylim)
def get_cmap(n, name='hsv'):
      '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
      RGB color; the keyword argument name must be a standard mpl colormap name.'''
      return plt.cm.get_cmap(name, n)

def plt_overwrite_and_save(in_sPath,strFile):
    strFile = path.join(in_sPath,strFile)
    if not path.isdir(in_sPath):
        makedirs(in_sPath)

    if path.isfile(strFile):
        remove(strFile)  # Opt.: os.system("rm "+strFile)
    plt.savefig(strFile)
def get_col_row_correlation_graph(in_toDisplay,in_configcommon) :
    in_nColsTotalSubPlot = in_configcommon.get('Correlations', 'Correlations_NColumns')
    in_nRowsTotalSubPlot = floor(
        (len(in_toDisplay) / int(in_configcommon.get('Correlations', 'Correlations_NColumns')))) + 1
    in_nColsTotalSubPlot = 0
    if len(in_toDisplay) < int(in_configcommon.get('Correlations', 'Correlations_NColumns')):
        in_nColsTotalSubPlot = len(in_toDisplay)
    else :
        in_nColsTotalSubPlot = int(in_configcommon.get('Correlations', 'Correlations_NColumns'))
    return (in_nColsTotalSubPlot,in_nRowsTotalSubPlot)

def plot_scatter(insName,toplot,in_titles,in_config) :

    toplot = list(zip(*toplot))
    x = [item.total_seconds() / 3600 for item in toplot[0]]
    y = toplot[1]
    colormap = np.array(['b','g', 'r'])
    reasonMap = ['Normal','Stop Loss','Take Profit']
    plt.scatter(x,y, c=colormap[list(toplot[2])],label = reasonMap,s= int(in_config.get('Correlations', 'Correlations_Marker_Size')))
    plt.title(in_titles[2])
    plt.xlabel(in_titles[0])
    plt.ylabel(in_titles[1])




    pass

