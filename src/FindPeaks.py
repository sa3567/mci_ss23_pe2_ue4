import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math
import sys
##import matplotlib as mp
##from scipy.signal import argrelextrema

class FindPeaks:
    def __init__(self):   
        self.scan_col = 0
        self.time_col = 0
        self.baselines = pd.DataFrame
        self.df_peaks = pd.DataFrame
        self.df_raw = pd.DataFrame
        pass
    

    def importData(self, a_file_name):
        """Loads a .csv file into the class own dataframe"""
        if (open(a_file_name, "r") == None):
            print("FileName not valid!")
            return
        
        self.df_raw = pd.read_csv(a_file_name, sep = ";", header = None, names = None)
        if(self.df_raw.empty):
            print("DataFile was empty!")
            return
        
        print(self.df_raw.head())
        pass


    def detectPeaks(self, a_column=0):
        """Scans the selected column of source-dataframe for Peaks and stores the peak-information in a seperate dataframe"""
        self.scan_col = a_column
        self.time_col = 1
        #%% Detect Peaks
        _indices = []    
        _up = -1
        _curr = 0 
        _prev = self.df_raw.iloc[0][self.scan_col]

        for i in range(1, len(self.df_raw[self.scan_col])):
            _curr = self.df_raw.iloc[i][self.scan_col]          #get 2 adjacent values from data
            _prev = self.df_raw.iloc[i - 1][self.scan_col]      

            if _curr > _prev:       #if upwards-flank, remember index
                _up = i

            if (_up > -1) & (_curr < _prev):    #if previously, an upward flank detected, it was a peak
                _indices.append(_up)            #peak start-index is value of _up
                _up = -1

        self.df_peaks = pd.DataFrame(_indices, index=None, columns=["Indizes"])     #create new dataframe from peak indices
        self.df_peaks = self.df_peaks.set_index("Indizes")                          #make peak indices table key
        self.df_peaks["Value"] = self.df_raw.iloc[_indices][self.scan_col]          #add peak values
        print(self.df_peaks.head())
        #%% Calculate delta t
        _prev = 0
        _curr = 0
        _next = 0
        _deltaPrev = []
        _deltaNext = []
            
        for i in range(0, len(_indices)):                           #iterate through peaks to get time between each peak
            _curr = self.df_raw.iloc[_indices[i]][self.time_col]
            if i != 0:
                _prev = self.df_raw.iloc[_indices[i - 1]][self.time_col]  
            else:
                _prev = _curr       #if first iteration, _prev = _curr, so that distance to previous = 0

            if i < len(_indices) - 1:
                _next = self.df_raw.iloc[_indices[i + 1]][self.time_col]
            else:
                _next = _curr       #if last iteration, _next = _curr, so that distance to next = 0

            _deltaPrev.append(_curr - _prev)
            _deltaNext.append(_next - _curr)

        self.df_peaks["Next Peak"] = _deltaNext         #add columns to Dataframe
        self.df_peaks["Previous Peak"] = _deltaPrev

        print(self.df_peaks.head())
        pass


    def get_absolute(self):
        max = self.df_raw[0]["value"]
        if self.df_peaks.empty():          
            for index, row in self.df_raw.iterrows():
                if row["value"] > max:
                    max = row["value"]
                    break
        
        else:
            for index, row in self.df_peaks.iterrows():
                if row["value"] > max:
                    max = row["value"]
                    break

        return max
        pass

    def add_baseline(self):
        self.baselines = pd.DataFrame(columns=[])
        _peak_indices = self.df_peaks.index.values.tolist()
        _rbase_list = []
        _lbase_list = []
        _delta_base_list = []

        for i in range(0, len(_peak_indices)):
            _step = _peak_indices[i]
            _curr = 0
            _next = 0
            while _step < 2 + len(self.df_raw[self.scan_col]):
                _curr = self.df_raw.iloc[_step][self.scan_col]
                _next = self.df_raw.iloc[_step + 1][self.scan_col]  
                if _next > _curr:
                    _rbase_list.append(_step)
                    break
                _step += 1

            _step = _peak_indices[i]
            while _step > 0:
                _curr = self.df_raw.iloc[_step][self.scan_col]
                _next = self.df_raw.iloc[_step - 1][self.scan_col]  
                if _next > _curr:
                    _lbase_list.append(_step)
                    break
                _step -= 1
            
            _x = _peak_indices[i]
            _y = self.df_raw.iloc[_peak_indices[i]][self.scan_col]
            _xl = _lbase_list[i]
            _yl = self.df_raw.iloc[_lbase_list[i]][self.scan_col]
            _xr = _rbase_list[i]
            _yr = self.df_raw.iloc[_rbase_list[i]][self.scan_col]

            _dbx = _xl - _xr
            _dby = _yl - _yr

            _dpy = _y - _yl
            _dpx = _x - _xl

            _delta_base = _dpy - _dpx * (_dby / _dbx)       #Smart Math
            _delta_base_list.append(_delta_base)

            #self.baselines = pd.DataFrame()
            #plt.plot([_xl, _xr], [_yl, _yr], color='m', linestyle='--', linewidth=1)
            #plt.plot([_x, _x], [_y, _y - _delta_base], color='m', linestyle='--', linewidth=1)


        self.df_peaks["Left Base"] = _lbase_list         #add columns to Dataframe
        self.df_peaks["Right Base"] = _rbase_list
        self.df_peaks["Vert. distance to Baseline"] = _delta_base_list

        print(self.df_peaks.head())
        pass
    

    def plotPeaks(self):
        "Visualizes the data with marked peak locations"
        _peak_indices = self.df_peaks.index.values.tolist()

        for idx, row in self.df_peaks.iterrows():
            _x = idx
            _y = self.df_raw.iloc[_x][self.scan_col]

            _xl = row["Left Base"]
            _yl = self.df_raw.loc[_xl][self.scan_col]

            _xr = row["Right Base"]
            _yr = self.df_raw.loc[_xr][self.scan_col]

            _delta_base = row["Vert. distance to Baseline"]

            plt.plot([_xl, _xr], [_yl, _yr], color='m', linestyle='--', linewidth=1)
            plt.plot([_x, _x], [_y, _y - _delta_base], color='m', linestyle='--', linewidth=1)
           


        self.df_raw[self.scan_col].plot(figsize=(20,8))
        self.df_raw.iloc[_peak_indices][self.scan_col].plot(style='.', lw=10, color='red', marker="v")
        ##self.df_raw.iloc[_rbase_list + _lbase_list][self.scan_col].plot(style='.', lw=10, color='green', marker="^")
        pass
                 


script_dir = os.path.dirname(__file__) #absolute dir the script is in
rel_path = "../data/" #realtive path of the .csv file
file1 = "test.csv"
abs_file_path = os.path.join(script_dir, rel_path, file1)

myPeaks = FindPeaks()
myPeaks.importData(abs_file_path)
myPeaks.detectPeaks(0)
myPeaks.add_baseline()
myPeaks.plotPeaks()

plt.show(block = True)
sys.exit(0)
