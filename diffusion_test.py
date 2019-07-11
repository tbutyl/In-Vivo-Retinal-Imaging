# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 15:38:45 2019

@author: emiller5
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani

nx = 101
dx = 10/(nx-1) #10um divided into 100 steps
nt = 10001
nu = 0.01 #??
sigma = 0.2 #??
dt = sigma * dx**2 / nu #10s divided
#dc = 0.1 #diffusion coefficient

#u = np.ones(nx)
#u[int(4.5/dx):int(5.5/dx)]=np.abs(np.sin(0.01*np.linspace(int(4.5/dx),int(5.5/dx),int(5.5/dx)-int(4.5/dx))))
u = np.sin(np.linspace(0,np.pi,nx))

out = np.zeros((nx,nt))
out[:,0] = u

for t in range(1,nt):
    s = t-1
    for n in range(1, nx-1):
        out[n,t] = out[n,s] + sigma * (out[n+1,s] - 2*out[n,s] + out[n-1,s])
        out[0,t] = out[1,t]
        out[-1,t] = out[-2,t]

#==============================================================================
# anal_out = np.ones((nx,nt+1))
# anal_out[:,0]=u
# def anal(x,t):
#     return np.exp(-sigma*t)*np.sin(x)
#     
# for (i,j),k in np.ndenumerate(anal_out):
#     if j==anal_out.shape[1]:
#         break
#     else:
#         anal_out[i,j] = anal(i,j)
#==============================================================================
