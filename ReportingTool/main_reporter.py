from reporter import Reporter
from utils.utilConfig import init_config
from multiTFReporter import MultiTFReporter
from os import path
import numpy as np
sMetaMethod= 'SMA_crossover'

config_common = init_config(path.join('Configs','config_common_reporting.ini'))


subRunDict = {'EMA_8_21_NO_SL_NO_TP': 'config_run_2_1', 'EMA_15_30_NO_SL_NO_TP': 'config_run_2_2',
              'EMA_50_160_NO_SL_NO_TP': 'config_run_2_3'}

subRunDict = {'SMA_8_21_NO_SL_NO_TP': 'config_run_4_1', 'SMA_15_30_NO_SL_NO_TP': 'config_run_4_2',
              'SMA_50_160_NO_SL_NO_TP': 'config_run_4_3','SMA_20_50_NO_SL_NO_TP': 'config_run_4_4'}
subRunDict = {'SMA_8_21_NO_SL_NO_TP': 'config_run_1_1', 'SMA_15_30_NO_SL_NO_TP': 'config_run_1_2',
              'SMA_50_160_NO_SL_NO_TP': 'config_run_1_3', 'SMA_20_50_NO_SL_NO_TP': 'config_run_1_4'}

config_subrunList = ['config_run_1_1','config_run_1_2','config_run_1_3']
config_paths_subruns = ['SMA_8_21_NO_SL_NO_TP','SMA_15_30_NO_SL_NO_TP','SMA_50_160_NO_SL_NO_TP']
config_paths_subruns = [path.join('Configs',item) for item in config_paths_subruns]
#sConfigBaseFilePath = path.join('Configs',config_subrun.get('Inputs','configPath'))

#frequencies = {'D1': config_common.get('AllInputs', 'Frequencies_3')}
                   #, 'W1': config_common.get('AllInputs', 'Frequencies_4')}
def from_freq_to_config_file(in_frequency,in_subRun):

    sConfigFile =(in_subRun + '_' +in_frequency + '.ini')
    return sConfigFile
def run_single_timeframe(in_frequency,in_sMethod,in_sMetaMethod):
    in_sSubrun = subRunDict[in_sMethod]

    sConfigFile = from_freq_to_config_file(in_frequency,in_sSubrun)
    config = (path.join('Configs',in_sMetaMethod,in_sMethod,sConfigFile))
    config_subrun = (path.join('Configs',in_sMetaMethod,in_sSubrun + '.ini'))
    objReporter = Reporter(config,config_subrun,config_common)
    objReporter.run()
def run_multiple_methods(in_sComparaison,in_sRunName,in_freq,config_subrunList,config_paths_subruns,sMetaMethod):
    sBaseConfig = 'Configs'
    reporters  = [Reporter((path.join(sBaseConfig,sMethod,subRunPath,from_freq_to_config_file(in_freq,sSubRunName))),(path.join(sBaseConfig,sMethod,sSubRunName + '.ini')),config_common) for subRunPath,sSubRunName,sMethod in zip(config_paths_subruns,config_subrunList,sMetaMethod)]
    sRunName = config_common.get('Names', 'runName')
    objMultipleReporter = MultiTFReporter(reporters,in_sComparaison,in_sRunName,config_common,config_common.get('FilePth','sBasePath'))
    #objMultipleReporter.plot_durations_comparisons()
#    objMultipleReporter.plot_profits_all_timeframes()
    [item.make_waterfall_return_figure() for item in reporters]

def run_multiple_timeframes():
    reporters  = [Reporter(init_config(from_freq_to_config_file(freq)),config_subrun,config_common) for freq in frequencies]
    objMultipleReporter = MultiTFReporter(reporters,'All_parameters',config_common,reporters[0].sBasePath)
    objMultipleReporter.bar_all_profits()

    objMultipleReporter.plot_profits_all_timeframes_with_save()
def run_SMA_vs_EMA() :
    frequencies = {'H1': config_common.get('AllInputs', 'Frequencies_1'),
                   'H4': config_common.get('AllInputs', 'Frequencies_2'),
                   'D1': config_common.get('AllInputs', 'Frequencies_3')}
    sMethod = 'SMA_50_160_NO_SL_NO_TP'
    config_subrunList = ['config_run_1_1', 'config_run_2_1', 'config_run_1_2', 'config_run_2_2', 'config_run_1_3',
                         'config_run_2_3']
    config_paths_subruns = ['SMA_8_21_NO_SL_NO_TP', 'EMA_8_21_NO_SL_NO_TP', 'SMA_15_30_NO_SL_NO_TP',
                            'EMA_15_30_NO_SL_NO_TP', 'SMA_50_160_NO_SL_NO_TP', 'EMA_50_160_NO_SL_NO_TP']
    sMetaMethod = ['SMA_crossover', 'EMA_crossover', 'SMA_crossover', 'EMA_crossover', 'SMA_crossover', 'EMA_crossover']
    sRunName = 'All_comparisons'
    #  run_single_timeframe('D1','EMA_15_30_NO_SL_NO_TP','EMA_crossover')
    [run_multiple_methods(path.join('Comparaisons', sRunName), sRunName, item, config_subrunList, config_paths_subruns,
                          sMetaMethod) for item in frequencies]

def run_SMA_vs_SMA_hysreresis() :






    frequencies = {
                   'D1': config_common.get('AllInputs', 'Frequencies_3')}

    frequencies = {
                   'H4': config_common.get('AllInputs', 'Frequencies_2'),
                   'D1': config_common.get('AllInputs', 'Frequencies_3')}
    sMethod = 'SMA_15_160_NO_SL_NO_TP'
    config_subrunList = ['config_run_1_1', 'config_run_4_1', 'config_run_1_2', 'config_run_4_2', 'config_run_1_3',
                         'config_run_4_3']
    config_paths_subruns = ['SMA_8_21_NO_SL_NO_TP', 'SMA_8_21_NO_SL_NO_TP', 'SMA_15_30_NO_SL_NO_TP',
                            'SMA_15_30_NO_SL_NO_TP', 'SMA_50_160_NO_SL_NO_TP', 'SMA_50_160_NO_SL_NO_TP', 'SMA_20_50_NO_SL_NO_TP', 'SMA_20_50_NO_SL_NO_TP']

    config_subrunList = ['config_run_1_2', 'config_run_4_2']
    config_paths_subruns = ['SMA_15_30_NO_SL_NO_TP', 'SMA_15_30_NO_SL_NO_TP']

    sMetaMethod = ['SMA_crossover', 'SMA_crossover_DynamicHysteresis', 'SMA_crossover', 'SMA_crossover_DynamicHysteresis', 'SMA_crossover', 'SMA_crossover_DynamicHysteresis']
    sRunName = 'Run1.2_vs_Run4.2' \
               ''
    #  run_single_timeframe('D1','EMA_15_30_NO_SL_NO_TP','EMA_crossover')
    [run_multiple_methods(path.join('Comparaisons', sRunName), sRunName, item, config_subrunList, config_paths_subruns,
                          sMetaMethod) for item in frequencies]

def exec_run_single_timeframe() :
    run_SMA_vs_SMA_hysreresis()
    #run_single_timeframe('H4','SMA_20_50_NO_SL_NO_TP','SMA_crossover')
    pass
if __name__ == '__main__':
    exec_run_single_timeframe()