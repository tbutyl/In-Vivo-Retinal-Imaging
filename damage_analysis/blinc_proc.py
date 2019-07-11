from tkinter.filedialog import askdirectory
import numpy as np
import skimage.io as io
import pandas as pd
from pathlib import Path
import os, sys, csv

"""
ebm 2018-11-20:
For processing the blinc experiments done in october 2018 to look at functional recovery of photoreceptors after 860nm damage.
Repeated bscans over ~333 seconds.
Disp Comp, hand flattened (specific software - fine flat), cropped, IS/OS band in bkg and dmg found manually and recorded in an excel file (locs),
Stacks processed using relevant locations and saved to csv for processing in a jupyter notebook.
"""
def extract(ready_path, bkg, peri):
    stack = io.imread(ready_path)
    #Background
    bkg_dark = np.average(stack[0:16,bkg[1]:bkg[1]+16,bkg[0]:bkg[0]+31])
    bkg_light = np.average(stack[100:150,bkg[1]:bkg[1]+16,bkg[0]:bkg[0]+31])
    bkg_time = np.average(stack[:,bkg[1]:bkg[1]+16,bkg[0]:bkg[0]+31], axis=(1,2))
    bkg_ascan_dark = np.average(stack[0:16,:,bkg[0]:bkg[0]+31],axis=(0,2))
    bkg_ascan_light = np.average(stack[100:150,:,bkg[0]:bkg[0]+31],axis=(0,2))
    
    #Dmg area A-scan
    dmg_ascan_dark = np.average(stack[0:16,:,peri[0]:peri[0]+31], axis=(0,2))
    dmg_ascan_light = np.average(stack[100:150,:,peri[0]:peri[0]+31], axis=(0,2))
    
    #core
    core_dark = np.average(stack[0:16,peri[1]:peri[1]+16,peri[0]+11:peri[0]+21])
    core_light = np.average(stack[100:150,peri[1]:peri[1]+16,peri[0]+11:peri[0]+21])
    core_time = np.average(stack[:,peri[1]:peri[1]+16,peri[0]+11:peri[0]+21], axis=(1,2))
    
    #peri
    x = np.concatenate((np.linspace(peri[0], peri[0]+9,10, dtype=int), np.linspace(peri[0]+20,peri[0]+29,10,dtype=int)))
    peri_dark = np.average(stack[0:16,peri[1]:peri[1]+16,x])
    peri_light = np.average(stack[100:150,peri[1]:peri[1]+16,x])
    peri_time = np.average(stack[:,peri[1]:peri[1]+16,x], axis=(1,2))
#    peri_dark1 = np.average(stack[0:16,peri[1]:peri[1]+16,peri[0]:peri[0]+11])
#    peri_dark2 = np.average(stack[0:16,peri[1]:peri[1]+16,peri[0]+21:peri[0]+31])
#    peri_light1 = np.average(stack[100:150,peri[1]:peri[1]+16,peri[0]:peri[0]+11])
#    peri_light2 = np.average(stack[100:150,peri[1]:peri[1]+16,peri[0]+21:peri[0]+31])
#    peri_time1 = np.average(stack[:,peri[1]:peri[1]+16,peri[0]:peri[0]+11], axis=(1,2))
#    peri_time2 = np.average(stack[:,peri[1]:peri[1]+16,peri[0]+21:peri[0]+31], axis=(1,2))
    
#    peri_dark = np.average(np.array([peri_dark1, peri_dark2]))
#    peri_light = np.average(np.array([peri_light1, peri_light2]))
#    peri_time = np.average(np.array(peri_time1, peri_time2), axis=0)
    
    
    return bkg_ascan_dark, bkg_ascan_light, dmg_ascan_dark, dmg_ascan_light, \
            bkg_dark, bkg_light, core_dark, core_light, peri_dark, peri_light, bkg_time, core_time, peri_time

def find_amp(top_path):
    
    top_path = Path(top_path)
    locs = pd.read_excel(str(Path('C:/Users/emiller5/Box Sync/2018-10 BLINC locations.xlsx')), header=[0,1], na_values='z', index_col=[0,1]).stack()
    a = locs.reset_index()
    a.rename(index=str, columns={'level_0':'Time', 'level_1':'Mouse','mouse':'Coord'}, inplace=True)
    a.set_index(['Time','Mouse', 'Coord'], inplace=True)
    a.reset_index(inplace=True)
    b = a.set_index(['Time','Mouse','Coord'])
    c = pd.DataFrame(b['bkg left'])
    d = pd.DataFrame(b['peri left'])
    c['peri left'] = d['peri left']
    
    csv_path = top_path/"extracted_data.csv"
    
    amp_folders = top_path.rglob('**/ready_stack.tif')
    with open(str(csv_path), 'w') as f:
        csvf = csv.writer(f, delimiter=',')
        for folder in amp_folders:
            print('\n*****\nProcessing:\t{}\n*****\n'.format(str(folder)))
            time, mouse = folder.parts[3:5]
            bkg_x, peri_x = c.xs((time, mouse, 'x'))
            bkg_y, peri_y = c.xs((time, mouse, 'y'))
            bkg = (bkg_x, bkg_y)
            peri = (peri_x,peri_y)
            labels = ('Bkg Ascan Dark', 'Bkg Ascan Light', 'Dmg Ascan Dark',\
                    'Dmg Ascan Light', 'Bkg Dark', 'Bkg Light', 'Core Dark',\
                    'Core Light', 'Peri Dark', 'Peri Light', 'Bkg Time', 'Core Time', 'Peri Time')
            data = extract(folder, bkg, peri)
            for each in zip(labels, data):
                datalst = each[1].tolist()
                try:
                    csvf.writerow([time, mouse, each[0], *datalst])
                except TypeError:
                    csvf.writerow([time, mouse, each[0], datalst])

def main():

    top_path = askdirectory()
    if top_path=='':
            sys.exit('\nExited: No directory was selected')
    elif os.path.isfile(top_path):
            sys.exit('Exited: File selected. Please select top directory')
    find_amp(top_path)


    print('\n--------\nComplete\n--------')


if __name__ == '__main__':
        main()

