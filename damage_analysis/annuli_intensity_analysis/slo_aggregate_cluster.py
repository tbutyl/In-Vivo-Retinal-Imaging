import os, csv, sys, re , glob
from tkinter.filedialog import askdirectory
import pandas as pd 
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search_function as sf 

mouse_find = re.compile('(?!(20))(?<!\d)(\d{4})(?!\d)')
eye_find = re.compile('([lr]|(right|left)\s)eye', re.IGNORECASE)
#date_find = re.compile('\d{4}-\d\d-\d\d_\d{6}')
date_find = re.compile('\d{4}-\d{1,2}-\d{1,2}')
#date_find = re.compile('\d{1,2} hour')
geno_find = re.compile('ccr2|arr|cx3cr1|gfp/gfp|gfp/+|het|homo|gnat2|c57bl6|lox-cre|lox', re.IGNORECASE)
ear_find = re.compile('([rlnb]|(right|left|both|neither)\s)ear', re.IGNORECASE)
#set_find = re.compile('II\b|I\b')
set_find = re.compile('I+')

def procPath(path):
    eym = eye_find.search(path)
    eam = ear_find.search(path)
    dm = date_find.search(path)
    mm = mouse_find.search(path)
    gm = geno_find.search(path)
    sm = set_find.search(path)

    try: date = dm.group()
    except: 
        print('no date')
        date = ''
    try: mouse = mm.group()
    except: 
        print('no mouse number')
        mouse = ''
    try: ear = eam.group()
    except: 
        print('no ear')
        ear = ''
    try: eye = eym.group()
    except: 
        print('no eye')
        eye = ''
    try: sett = sm.group()
    except: 
        print('no set')
        sett = ''
    try: geno = gm.group()
    except: 
        print('no genotype')
        geno = ''

    return [sett.lower(), date.lower(), mouse.lower(), eye.lower(), geno.lower()]

#annoying I can't use the decorator... can't really acces top_path or the list to save in csv correctly
def agg(top_path):
    seek = '{}{}**{}cluster_intensity_annuli.npy'.format(top_path, os.sep,os.sep)
    paths = glob.iglob(seek, recursive=True)

    with open('{}{}slo_annuli_data.csv'.format(top_path, os.sep), 'w') as f:
        csvf = csv.writer(f,delimiter=',')
        csvf.writerow(['Set', 'Date', 'Mouse Number', 'Eye','Genotype','Radius', 'Intensity'])      
        for path in paths:
            print('\n{}'.format(path))
            arr = np.load(path)
            path_info = procPath(path)
            for rad in range(0,60):
                csvf.writerow(path_info+[rad,arr[rad]])

def main():
    top_path = askdirectory()
    if top_path=='':
        sys.exit('\nExited: No directory was selected')
    elif os.path.isfile(top_path):
        sys.exit('Exited: File selected. Please select top directory')
    agg(top_path)
    print('\n--------\nComplete\n--------')


if __name__ == '__main__':
    main()
