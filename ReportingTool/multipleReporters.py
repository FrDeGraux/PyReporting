
from reporter import Reporter
import matplotlib.pyplot as plt
from os import path

class MultipleReporter :
    def __init__(self,in_MultiTFreporters,in_commonconfig):
        pass
        self.commonconfig = in_commonconfig
        self.multi_tf_reporters = in_MultiTFreporters
        self.color_durations_list  = ['b','r']
        if(len(in_MultiTFreporters) != 2) :
            print("can only handle two ")
    def plot_profits_all_run_list(self):
      #sFilesList = [[k.sFileName for k in n.lst_reporters] for n in self.multi_tf_reporters]
      self.plot_profits_many_runs()
    def plot_profits_many_runs(self):
            # Reporter H1, Reporter H4
      [item.plot_profits_all_timeframes_no_save() for item in self.multi_tf_reporters]
      plt.title(self.commonconfig.get('Returns', 'Graph_Title') + self.multi_tf_reporters.name + " VS " + self.multi_tf_reporters.name + "_" + "_ALL TIMEFRAMES")
      plt.legend(loc="best")
      plt.savefig(path.join(self.sMotherPath, 'All_returns' + '.png'))

    def plot_returns_durations_compare(self,in_symbol):
      plt.figure()

      [item.plot_return_durations( in_symbol, self.commonconfig, color) for (item,color) in zip(self.multi_tf_reporters,self.color_durations_list)]
      plt.legend(["With static", "Without static"])
      plt.savefig(path.join(self.sDurationReturnPath, self.sRunName + '_durations_vs_returns_' + "_" + self.config.get('Inputs',
                                                                                                           'Frequency') + "_" + in_symbol + '.png'))
