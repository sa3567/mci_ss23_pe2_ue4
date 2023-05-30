import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

class FindPeaks:
    def __init__(self):
        self.scan_col = 0
        self.time_col = 0
        self.baselines = pd.DataFrame()
        self.df_peaks = pd.DataFrame()
        self.df_raw = pd.DataFrame()

    def importData(self, a_file_name):
        if not os.path.exists(a_file_name):
            print("File name not valid!")
            return

        self.df_raw = pd.read_csv(a_file_name, sep=";", header=None)
        if self.df_raw.empty:
            print("Data file is empty!")
            return

        print(self.df_raw.head())

    def detectPeaks(self, a_column=0):
        self.scan_col = a_column
        self.time_col = 1

        _indices = []
        _up = -1
        _curr = 0
        _prev = self.df_raw.iloc[0][self.scan_col]

        for i in range(1, len(self.df_raw[self.scan_col])):
            _curr = self.df_raw.iloc[i][self.scan_col]
            _prev = self.df_raw.iloc[i - 1][self.scan_col]

            if _curr > _prev:
                _up = i

            if (_up > -1) and (_curr < _prev):
                _indices.append(_up)
                _up = -1

        self.df_peaks = pd.DataFrame(_indices, columns=["Indices"])
        self.df_peaks.set_index("Indices", inplace=True)
        self.df_peaks["Value"] = self.df_raw.iloc[_indices][self.scan_col]

        print(self.df_peaks.head())

        _prev = 0
        _curr = 0
        _next = 0
        _deltaPrev = []
        _deltaNext = []

        for i in range(0, len(_indices)):
            _curr = self.df_raw.iloc[_indices[i]][self.time_col]
            if i != 0:
                _prev = self.df_raw.iloc[_indices[i - 1]][self.time_col]
            else:
                _prev = _curr

            if i < len(_indices) - 1:
                _next = self.df_raw.iloc[_indices[i + 1]][self.time_col]
            else:
                _next = _curr

            _deltaPrev.append(_curr - _prev)
            _deltaNext.append(_next - _curr)

        self.df_peaks["Next Peak"] = _deltaNext
        self.df_peaks["Previous Peak"] = _deltaPrev

        print(self.df_peaks.head())

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

            _delta_base = _dpy - _dpx * (_dby / _dbx)
            _delta_base_list.append(_delta_base)

        self.df_peaks["Left Base"] = _lbase_list
        self.df_peaks["Right Base"] = _rbase_list
        self.df_peaks["Vert. distance to Baseline"] = _delta_base_list

        print(self.df_peaks.head())

    def plotPeaks(self):
        _peak_indices = self.df_peaks.index.values.tolist()

        # Convert peak indices to integers
        _peak_indices = [int(idx) for idx in _peak_indices]

        # Calculate time differences to previous and next peaks in milliseconds
        prev_peak_times = self.df_raw.iloc[np.array(_peak_indices) - 1][self.time_col]
        next_peak_times = self.df_raw.iloc[np.array(_peak_indices) + 1][self.time_col]
        peak_diffs_prev = self.df_raw.iloc[_peak_indices][self.time_col] - prev_peak_times
        peak_diffs_next = next_peak_times - self.df_raw.iloc[_peak_indices][self.time_col]

        self.df_peaks["Time Diff Prev (ms)"] = peak_diffs_prev * 1000
        self.df_peaks["Time Diff Next (ms)"] = peak_diffs_next * 1000

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

        self.df_raw[self.scan_col].plot(figsize=(20, 8))
        self.df_raw.iloc[_peak_indices][self.scan_col].plot(style='.', lw=10, color='red', marker="v")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.title("Peaks in Data")

        # Plot histogram of peak distances
        distances = self.df_peaks["Next Peak"] - self.df_peaks["Previous Peak"]
        plt.figure(figsize=(10, 4))
        plt.hist(distances, bins=20, color='b', alpha=0.7)
        plt.xlabel("Peak Distance")
        plt.ylabel("Frequency")
        plt.title("Histogram of Peak Distances")

        # Plot boxplot of peak time differences
        #plt.figure(figsize=(8, 4))
        #sns.boxplot(data=self.df_peaks[["Time Diff Prev (ms)", "Time Diff Next (ms)"]])
        #plt.ylabel("Time Difference (ms)")
        #plt.title("Boxplot of Peak Time Differences")

        plt.show(block=True)


script_dir = os.path.dirname(__file__)  # absolute dir the script is in
rel_path = "../data/"  # relative path of the .csv file
file1 = "test.csv"
abs_file_path = os.path.join(script_dir, rel_path, file1)

myPeaks = FindPeaks()
myPeaks.importData(abs_file_path)
myPeaks.detectPeaks(0)
myPeaks.add_baseline()
myPeaks.plotPeaks()
