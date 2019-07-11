# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 15:44:55 2019

@author: emiller5
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
import matplotlib.pyplot as plt
from pathlib import Path as p
from scipy.ndimage import uniform_filter1d as bc
plt.style.use('ggplot')


bkg = np.load(str(p(r'D:\Dendra2_tests_Jan_2019\kaity\20190204_Dendra2\10442_REP\RE\2019-02-04_143837\avg_spec.npy')))
x = bkg.T[0]
yb = bkg.T[1]
zero = np.load(str(p(r'D:\Dendra2_tests_Jan_2019\kaity\20190204_Dendra2\10442_REP\RE\2019-02-04_145353\avg_spec.npy')))
y0 = zero.T[1]


#adjust specs for bkg subtraction
specs = [y0]

adj_specs = np.empty((len(specs)+1, y0.shape[0]))
adj_specs[0,:] = yb
yb_bc = bc(yb,5)
yb_max = np.max(yb_bc)
yb_ind = np.where(yb_bc==yb_max)
for i, spec in enumerate(specs):
    ratio = yb_max/bc(spec,5)[yb_ind]
    adj = (spec*ratio)-yb
    base = np.mean(adj[0:100])
    adj_specs[i+1,:] = adj-base
    

f, (ax1,ax2) = plt.subplots(2,1, figsize=(10,10))

ax1.set_title('Dendra2 Photoconversion', fontsize=20)
ax1.set_ylabel('Counts', fontsize=16)
ax1.set_xlabel('Wavelength(nm)', fontsize=16)
ax1.set_xlim(561, 800)

ax1.plot(x, yb, label='BKG', c='#42f4d4')
ax1.plot(x, y0, label='Post')
ax1.legend(fontsize=12)

ax2.set_title('Dendra2 Photoconversion Bkg Sub', fontsize=20)
ax2.set_ylabel('Counts', fontsize=16)
ax2.set_xlabel('Wavelength(nm)', fontsize=16)
ax2.set_xlim(561, 800)

#labels = ['Post']
#for i,row in enumerate(adj_specs[1:]):
    #ax2.plot(x,bc(row,15), label=labels[i])
ax2.plot(x, bc(y0-yb,15), label='Raw Sub')    
#ax2.legend(fontsize=12)

plt.tight_layout()
 
#plt.show()   
plt.savefig(r'D:\dendra2_spectrum.pdf')
