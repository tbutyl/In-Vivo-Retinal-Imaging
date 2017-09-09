import csv
import math as m
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from string import ascii_uppercase as alpha
import matplotlib
from matplotlib.externals import six
from pandas.tools.plotting import table
import os
import shutil
import re
import seaborn as sns
import time
matplotlib.style.use('ggplot')
from scipy import optimize as op

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

def fit(function, parameters, y, x = None):
    def fit2(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    return op.leastsq(fit2, p)

def processOCT(path,i):
    with open(path, "r") as f:
        data = csv.reader(f)
        intensity_values = [row[2] for row in data]
    intensity_values = np.array(intensity_values[1:]).astype(float)
    param_out = fit(offeset_gauss,[sigma,a,b],intensity_values)
    param_dict = {"Sigma":param_out[0][0],"Offset":param_out[0][1], "Height":param_out[0][2],"Depth":i}
        
    file_folder = path.rstrip(os.sep)
    split_path = file_folder.split(os.sep)
    eye = split_path[-2]
    mouse = split_path[-3]
    geno = split_path[-4]
    date = split_path[-6]
    file_folder = file_folder.rsplit(os.sep,1)[0]
    file_info_dict = {"Eye":eye,"Mouse":mouse,"Genotype":geno,"Date":date}
    df = pd.DataFrame(param_dict, index=[0])
    file_info = pd.DataFrame(file_info_dict, index=[0])
    new_frame = file_info.merge(df,left_index=True,right_index=True)
    
    
    return new_frame

flag = 0
old_frame = None
new_frame = None
def sorting(source):
    file_list = os.listdir(source)
    global flag
    global old_frame
    global new_frame
    i=0
    
    for each_file in file_list:
        file_path = os.path.join(source, each_file)
        if os.path.isfile(file_path) and "damage_analysis" in file_path and not each_file.startswith("."):
            new_frame = processOCT(file_path,i)
            if flag == 0:
                flag = 1
                old_frame = new_frame
            elif not flag==0:
                old_frame = old_frame.append(new_frame)
            i+=1
            #print("Processed",file_path)
        elif os.path.isfile(file_path) and "microglia_concentric_intensity_analysis.csv" in file_path and not each_file.startswith("."):
            #~~~~process slo shit
            print("Processed",file_path)
        elif os.path.isdir(file_path):
            sorting(file_path)
        else:
            continue

def processOCT(path,i):
    with open(path, "r") as f:
        data = csv.reader(f)
        intensity_values = [row[2] for row in data]
    intensity_values = np.array(intensity_values[1:]).astype(float)
    sigma = Parameter(10)
    a = Parameter(10000)
    b = Parameter(25000)
    def offeset_gauss(x): return a()+(b()-a())*np.exp(-(x/(2*sigma()))**2)
    param_out = fit(offeset_gauss,[sigma,a,b],intensity_values)
    #print(param_out)
        
    file_name_split = path.rsplit(os.sep, 1)
    file_name = file_name_split[1]
    split_name = file_name.split("_")
    depth_frame = int(split_name[1])
    param_dict = {"Sigma":param_out[0][0],"Offset":param_out[0][1], "Height":param_out[0][2], "Depth":depth_frame}
    file_folder = path.rstrip(os.sep)
    split_path = file_folder.split(os.sep)
    eye = split_path[-2]
    mouse = split_path[-3]
    geno = split_path[-4]
    date = split_path[-6]
    file_folder = file_folder.rsplit(os.sep,1)[0]
    file_info_dict = {"Eye":eye,"Mouse":mouse,"Genotype":geno,"Date":date}
    df = pd.DataFrame(param_dict, index=[0])
    file_info = pd.DataFrame(file_info_dict, index=[0])
    new_frame = file_info.merge(df,left_index=True,right_index=True)
    
    
    return new_frame
