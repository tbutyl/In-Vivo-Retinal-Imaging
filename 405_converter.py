# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 10:51:30 2019

@author: emiller5
"""

import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')

#cross sec could be 1.87e-17 cm^2 NEED TO CONVER TTO m^2!!!!
#normal time (6*10**-6)*450
def f(power=(100*10**-6), time=0.005, diameter=(3*10**-6), molec_cs=(2*10**-21), photo_j=(4.9*10**-19)):
    photons = ((power*time)/photo_j)/(np.pi*(diameter/2)**2)
    photons_abs = photons*molec_cs
    conv_frac = 1 - np.exp(-(2*10**-3)*photons_abs)
    base_pa = molec_cs*(((145*10**-6)*time)/photo_j)/(np.pi*(diameter/2)**2)
    ref = 1 - np.exp(-(2*10**-3)*base_pa)
    
    return base_pa,ref,photons_abs, conv_frac

powarr=np.linspace(0,5000,50001)*10**-6
bpa,ref, pa,conv = f(power=powarr)
#vi = np.mean(np.gradient(conv)[50])

fig, ax1 = plt.subplots(1,1)
#ax2 = ax1.twiny()
ax1.plot(pa,conv, lw=3)
#ax1.plot(pa[:5],vi*pa[:5])
ax1.scatter(bpa,ref,s=100, zorder=3)
ax1.text(0.95,0.05,s='P absorbed at standard: {:8G}\nFraction converted in area: {:4.2f}'.format(int(bpa),ref), fontsize=14, \
    verticalalignment='bottom', horizontalalignment='right', \
    transform=ax1.transAxes, bbox=dict(facecolor='#cccccc', alpha=1, edgecolor='blue'))
ax1.set_ylim(-0.02,1.05)
ax1.set_xlim(-50,4000)
ax1.set_xlabel('Photons Absorbed')
ax1.set_ylabel('Fraction Dendra2 Converted')
#ax2.set_xlim(ax1.get_xlim())
#ax2.set_xticks(ax1.get_xticks())
#ax2.set_xticklabels(tick_function(new_tick_locations))
#ax2.grid(False)
#ax2.set_xlabel('Power (µW)')
#plt.savefig('C:\\Users\\emiller5\\Desktop\\dendra_pc.pdf')
