import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
##import matplotlib as mp
from scipy.signal import argrelextrema

class FindPeaks:
    def __init__(self):   
        self.headers = [] 
        self.dfPeaks = pd.DataFrame
        self.dfRaw = pd.DataFrame
        pass
    

    def importData(self, fileName, headers):
        """Loads a .csv file into the class own dataframe and checks if empty"""
        if (open(fileName, "r") == None):
            print("FileName not valid!")
            return
        
        self.headers = headers
        self.dfRaw = pd.read_csv(fileName, sep = ";", header = 0, names = headers)
        if(self.dfRaw.empty):
            print("DataFile was empty!")
            return
        
        ##self.dfRaw = self.dfRaw.set_index("Zeit")
        print(self.dfRaw.head())
        pass


    def detectPeaks(self):
        """Scans dataframe for Peaks and stores them in a seperate dataframe"""
        _length = len(self.dfRaw["value"])
        _prev = 0
        _curr = 0
        _next = 0
        _index = 0
        _indices = []

        while _index < _length:
            _curr = self.dfRaw.iloc[_index]["value"]
            if _index != 0:
                _prev = self.dfRaw.iloc[_index - 1]["value"]
            if _index < _length - 1:
                _next = self.dfRaw.iloc[_index + 1]["value"]

            if (_curr > _prev) & (_curr > _next):
                _indices.append(_index)   

            elif _curr > _prev:       
                while (_curr >= _prev) & (_index < _length):
                    _curr = self.dfRaw.iloc[_index]["value"]
                    if _index != 0:
                        _prev = self.dfRaw.iloc[_index - 1]["value"]

                    if _curr < _prev:
                        _indices.append(_index - 1)
                    _index += 1

            _index += 1

        self.dfPeaks = pd.DataFrame(_indices, index=None, columns=["Indices"])    
        self.dfPeaks = self.dfPeaks.set_index("Indices")    
        self.dfPeaks["Value"] = self.dfRaw.iloc[_indices]["value"]   
        print(self.dfPeaks.head())

        _prev = 0
        _curr = 0
        _next = 0
        _length = len(_indices)
        _timesBefore = []
        _timesAfter = []
            
        for i in range(0, _length):
            _curr = self.dfRaw.iloc[_indices[i]]["time"]
            if i != 0:
                _prev = self.dfRaw.iloc[_indices[i - 1]]["time"]
            else:
                _prev = _curr

            if i < _length - 1:
                _next = self.dfRaw.iloc[_indices[i + 1]]["time"]

            _timesBefore.append(_curr - _prev)
            _timesAfter.append(_next - _curr)

        self.dfPeaks["Next Peak"] = _timesAfter
        self.dfPeaks["Previous Peak"] = _timesBefore

        print(self.dfPeaks.head())


    def getAbsolute(self):
        max = self.dfRaw[0]["value"]
        if self.dfPeaks.empty():          
            for index, row in self.dfRaw.iterrows():
                if row["value"] > max:
                    max = row["value"]
        
        else:
            for index, row in self.dfPeaks.iterrows():
                if row["value"] > max:
                    max = row["value"]
        
        return max
    
    def plotPeaks(self):
        self.dfRaw["value"].plot(figsize=(20,8))
        self.dfRaw.iloc[self.dfPeaks["Indices"]]["value"].plot(style='.', lw=10, color='red', marker="v")
                 


script_dir = os.path.dirname(__file__) #absolute dir the script is in
rel_path = "../data/" #realtive path of the .csv file
file1 = "test.csv"
abs_file_path = os.path.join(script_dir, rel_path, file1)
headers = ["value", "time"]

myPeaks = FindPeaks()
myPeaks.importData(abs_file_path, headers)
myPeaks.detectPeaks()

plt.show(block = True)



## Anlegen einer Zeitreihe der Herzfrequenz aus den EKG-Daten

#%% UC 2.3 Analysieren der Daten auf Abbruch-Kriterium

## Vergleich der Maximalen Herzfrequenz mit Alter des Patienten

#%% UC 2.4 Erstellen einer Zusammenfassung

## Ausgabe einer Zusammenfassung

#%% UC 2.5 Visualisierung der Daten

## Erstellung eines Plots

#%% UC 2.6 Manuelle Eingabe eines Abbruchkritierums

## Abfrage an Nutzer:in, ob Abgebrochen werden soll

#%% UC 2.7 Speichern der Daten

# Speichern der Daten