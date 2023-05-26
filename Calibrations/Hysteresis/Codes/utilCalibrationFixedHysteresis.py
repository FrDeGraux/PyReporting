
import matplotlib.pyplot as plt
from utils.utilData import filterBySymbol
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from utils.utilData import filterBySymbol,getSymbolList,filter_on_entry_datetimes,filter_on_entry_datetimes_cumulative
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from utils.utilConfig import init_config

from os import path
import os
def tot_hours(in_row) :
    return in_row.total_seconds()/3600

def plot_all_results(in_df,in_cfg) :
    symbolsList = getSymbolList(in_df)
    in_threshold = in_cfg.get('FixedHysteresisInput', 'threshold')
    for symbol in symbolsList :
        res = build_all_hyper_cubes(in_df,symbol,in_threshold,in_cfg)

def scatter_data(in_cfg,in_fig,in_df,in_Symbol,min_hyst,max_hyst,z_min,z_max):



    # z_max is the max of the time in the interval

    ax = in_fig.add_subplot(111, projection='3d')
    pnt3d = ax.scatter(in_df['Hysteresis_in'], in_df['Hysteresis_out'], in_df['duration'], c=in_df['duration'])
    cbar = plt.colorbar(pnt3d)
    cbar.set_label("Trade duration")


    short_MA = in_cfg.get('ParametersMA', 'Short_MA')
    Long_MA = in_cfg.get('ParametersMA', 'Long_MA')


    ax.set_xlabel('Hysteresis_in : MA ' + Long_MA + " - MA " + short_MA)
    ax.set_ylabel('Hysteresis_out : MA ' + Long_MA + " - MA " + short_MA)

    plot_edges(ax,min_hyst,max_hyst,z_min,z_max)
    return ax

def make_grid(min_dim1,max_dim1,min_dim2,max_dim2) :
    _step_dim1= (max_dim1-min_dim1)/10
    _step_dim2= (max_dim2-min_dim2)/10
    rng_dim1 = np.arange(min_dim1, max_dim1 + _step_dim1, step=_step_dim1, dtype=float)
    rng_dim2 = np.arange(min_dim2, max_dim2 + _step_dim2, step=_step_dim2, dtype=float)
    grid = np.meshgrid(rng_dim1, rng_dim2)
    return grid
def plot_below_edge(ax,hyst_min,hyst_max,z_min,z_max) :

    xx, yy = make_grid(hyst_min, hyst_max, hyst_min, hyst_max)

    z = np.empty(shape=(xx.shape[0], xx.shape[1]))
    z.fill(z_min)
    ax.plot_surface(xx, yy, z, alpha=0.5,color = 'yellow')
def plot_up_edge(ax, hyst_min,hyst_max,z_min,z_max):
    xx, yy = make_grid(hyst_min, hyst_max, hyst_min, hyst_max)

    z = np.empty(shape=(xx.shape[0], xx.shape[1]))
    z.fill(z_max)
    ax.plot_surface(xx, yy, z, alpha=0.5,color = 'yellow')


def plot_left_edge(ax,hyst_min,hyst_max,z_min,z_max) :
    xx,z = make_grid(hyst_min, hyst_max, z_min, z_max)
    yy = np.empty(shape=(xx.shape[0], xx.shape[1]))
    yy.fill(hyst_min)
    ax.plot_surface(xx, yy, z, alpha=0.5,color = 'yellow')
def plot_right_edge(ax, hyst_min,hyst_max,z_min,z_max):
    xx, z = make_grid(hyst_min, hyst_max, z_min, z_max)
    yy = np.empty(shape=(xx.shape[0], xx.shape[1]))
    yy.fill(hyst_max)
    ax.plot_surface(xx, yy, z, alpha=0.5,color = 'yellow')

def plot_face_edge(ax,hyst_min,hyst_max,z_min,z_max) :
    yy,z = make_grid(hyst_min, hyst_max, z_min, z_max)
    xx = np.empty(shape=(yy.shape[0], yy.shape[1]))
    xx.fill(hyst_min)
    ax.plot_surface(xx, yy, z, alpha=0.5,color = 'yellow')
def plot_dark_edge(ax,hyst_min,hyst_max,z_min,z_max) :
    yy,z = make_grid(hyst_min, hyst_max, z_min, z_max)
    xx = np.empty(shape=(yy.shape[0], yy.shape[1]))
    xx.fill(hyst_max)
    ax.plot_surface(xx, yy, z, alpha=0.5,color = 'yellow')
def plot_edges(in_ax,in_hist_min,in_hist_max,z_min,z_max) :
    _step = (in_hist_max-in_hist_min)/10
    rng = np.arange(in_hist_min, in_hist_max, step=_step, dtype=float)
    grid = np.meshgrid(rng, rng)


    plot_below_edge(in_ax,in_hist_min,in_hist_max,z_min,z_max)
    plot_left_edge(in_ax, in_hist_min,in_hist_max,z_min,z_max)
    plot_right_edge(in_ax,in_hist_min,in_hist_max,z_min,z_max)
    plot_up_edge(in_ax, in_hist_min,in_hist_max,z_min,z_max)
    plot_face_edge(in_ax,in_hist_min,in_hist_max,z_min,z_max)
    plot_dark_edge(in_ax,in_hist_min,in_hist_max,z_min,z_max)



def compute_hyper_cube(in_df,in_theshold,min_step,max_step,nSteps = 100) :
    cumulative_duration = []
    maximum_time  = []
    minimum_time = []
    duration_total = in_df['duration'].sum()
    item_max = 0

    sample = np.linspace(min_step, max_step, num=nSteps)

    for item in sample :
        filtered_data  = in_df[in_df['Hysteresis_in'] <= item]
        filtered_data = filtered_data[filtered_data['Hysteresis_out'] <= item]
        filtered_data_index_list = filtered_data.index.values
        unfiltered_data = in_df[~in_df.index.isin(filtered_data_index_list)]

        if(filtered_data.empty) :
            continue

        duration_item = filtered_data['duration'].sum()/duration_total
        if not (maximum_time) :
            maximum_time.append(max(filtered_data['duration']))
            minimum_time.append(min(filtered_data['duration']))
        else  :
         maximum_time.append(max(maximum_time[-1],max(filtered_data['duration'])))
         minimum_time.append(min(maximum_time[-1], min(filtered_data['duration'])))

        cumulative_duration.append((item,duration_item))
        if( duration_item > float(in_theshold)) :
            return (unfiltered_data,item,minimum_time[-1],maximum_time[-1])
            # return max of

    return (unfiltered_data,sample[-1],minimum_time[-1],maximum_time[-1])
def build_all_hyper_cubes(in_df,in_symbol,in_threshold,in_cfg) :
    in_df = filterBySymbol(in_df,in_symbol, in_cfg)
    in_df['TimeIn_Date'] = in_df['TimeIn'].dt.date
    in_df['TimeOut_Date'] = in_df['TimeOut'].dt.date
    dt_min = in_df['TimeIn_Date'].min()
    dt_max = in_df['TimeOut_Date'].max()

    dtStart = datetime.date(dt_min.year,1,1)
    dtEnd = datetime.date(dt_max.year+1,1,1)
    pass
    diff = relativedelta(dtEnd, dtStart)
    res = []
    for i in range(diff.years):
        startTime = dtStart +  relativedelta(years=i)
        filtered_df = filter_on_entry_datetimes(in_df,startTime,startTime+ relativedelta(years=1))
        res.append(((dtStart + relativedelta(years=i)).strftime("%m/%d/%Y") ,in_symbol,build_hyper_cube(filtered_df,startTime,startTime+ relativedelta(years=1),in_symbol,in_threshold,in_cfg,isCumulative = False)))

    res.insert(0,(((dtStart-relativedelta(years=1)).strftime("%m/%d/%Y") ,in_symbol,build_hyper_cube(filter_on_entry_datetimes(in_df,dtStart,dtStart+ relativedelta(years=1)),dtStart,dtStart+ relativedelta(years=1),in_symbol,in_threshold,in_cfg,isCumulative = False))))

    return res

def build_all_hyper_cubes_cumulated(in_df,in_symbol,in_threshold,in_cfg) :
    in_df = filterBySymbol(in_df,in_symbol, in_cfg)
    in_df['TimeIn_Date'] = in_df['TimeIn'].dt.date
    in_df['TimeOut_Date'] = in_df['TimeOut'].dt.date
    dt_min = in_df['TimeIn_Date'].min()
    dt_max = in_df['TimeOut_Date'].max()

    dtStart = datetime.date(dt_min.year,1,1)
    dtEnd = datetime.date(dt_max.year+1,1,1)
    pass
    diff = relativedelta(dtEnd, dtStart)
    res = []
    for i in range(diff.years):

        filtered_df = filter_on_entry_datetimes_cumulative(in_df,dtStart,dtStart+ relativedelta(years=i+1))

        # from start to year
        res.append(((dtStart + relativedelta(years=i)).strftime("%m/%d/%Y"), in_symbol,build_hyper_cube(filtered_df, dtStart, dtStart + relativedelta(years=i+1), in_symbol,in_threshold, in_cfg, isCumulative=True)))

    res.insert(0,(((dtStart - relativedelta(years=1)).strftime("%m/%d/%Y"), in_symbol,build_hyper_cube(filter_on_entry_datetimes_cumulative(in_df,dtStart,dtStart+ relativedelta(years =1)), dtStart, dtStart + relativedelta(years=1), in_symbol,in_threshold, in_cfg, isCumulative=True))))

    return res

def build_hyper_cube(in_df,dtStart,dtEnd,in_symbol,in_threshold,in_cfg,isCumulative) :
    if (in_df.empty) :
        return 0
    threshold = in_cfg.get("FixedHysteresisInput","threshold")
    sBasePath = in_cfg.get('FilePth', 'sBasePath')
    sBasePath = path.join( sBasePath,in_cfg.get('Run', 'sRunNameHysteresis'))
    sFrequency = in_cfg.get('Inputs', 'Frequency')
    sCalibrationBasePath = in_cfg.get('FilePth', 'sFixedHysteresisPath')
    sYear = str(dtStart.year)

    sFileName= sFrequency + "_" + in_symbol + '_'  + in_cfg.get('FilePth', 'sFixedCalibrationFileName') + '.png'
    if isCumulative :
        sFileName = 'Cumulated_' + sFileName

    sFolderPath = path.join(sBasePath,sFrequency,sCalibrationBasePath,str(100*float(threshold)) + "_Procent",sYear)
    sFilePath =  path.join(sFolderPath,sFileName)
    if not os.path.exists(sFolderPath):
        os.makedirs(sFolderPath)

    in_df = filterBySymbol(in_df, in_symbol, in_cfg)

    if(float(in_threshold)> 1 or float(in_threshold) < 0) :
        raise Exception("build_hyper_cube Threshold must be between 0 and 1")


    in_df = in_df.drop(columns=['TimeIn', 'TimeOut','Profit','ReasonNumber'])



    in_df['Hysteresis_in'] = pd.to_numeric(in_df['Hysteresis_in'])
    in_df['Hysteresis_out'] = pd.to_numeric(in_df['Hysteresis_out'])


    min_hyst = min(min(in_df['Hysteresis_in'].values),min(in_df['Hysteresis_out'].values))
    max_hyst = max(max(in_df['Hysteresis_in'].values),max(in_df['Hysteresis_out'].values))

    fig = plt.figure()
    plt.ion()
    df_unfiltered,fixed_hyst_res,z_min,z_max = compute_hyper_cube(in_df,in_threshold,min_hyst,max_hyst)
    sTitle = ""
    if isCumulative :
        sTilte = in_symbol + "_Cumulative Fixed hysteresis calibration " + str(100*float(threshold)) + "_Procent" + "(" + dtStart.strftime("%Y") + ";" + dtEnd.strftime("%Y")
    else :
        sTitle = in_symbol + "_Fixed hysteresis calibration " + threshold + "_Procent"  + "( "  + dtStart.strftime("%Y") + ";" + dtEnd.strftime("%Y") + ")"
    ax = scatter_data(in_cfg,fig,in_df, in_symbol, 0, fixed_hyst_res, 0, z_max)
    ax.set_title(sTitle)

    print(" Figure saved @ " + sFilePath)
    plt.ioff()
    plt.savefig(sFilePath + '.png')

    return(round(fixed_hyst_res))










