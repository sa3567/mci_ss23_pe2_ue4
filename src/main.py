import FindPeaks
import os
from matplotlib import pyplot as plt

script_dir = os.path.dirname(__file__) #absolute dir the script is in
rel_path = "../data/" #realtive path of the .csv file
file1 = "test.csv"
abs_file_path = os.path.join(script_dir, rel_path, file1)

myPeaks = FindPeaks.FindPeaks()
myPeaks.importData(abs_file_path)
myPeaks.detectPeaks(0)
myPeaks.add_baseline()
myPeaks.plotPeaks()

plt.show(block = True)