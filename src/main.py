import matplotlib as mp
import pandas as pd
import os

script_dir = os.path.dirname(__file__) #absolute dir the script is in
rel_path = "../data/" #realtive path of the .csv file
file1 = "01_Ruhe.csv"

abs_file_path = os.path.join(script_dir, rel_path, file1)
headers = ["Zeit", "Messwerte [mV]"]

