# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:17:50 2019

@author: emiller5
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import time
from scipy.stats import norm

class molecule:
    """Dendra2 molecule that undergoes brownian motion"""
    def __init__(self, c,x,y,mi,mx):
        self.x = x #position
        self.y = y
        self.c = c #color
        self.mi = mi #minimum positional value
        self.mx = mx #max positional value
        
    def move(self):
        """Random movement"""
        if np.random.rand(1)>=0.5:
            self.x+=1
        else:
            self.x-=1
        if np.random.rand(1)>=0.5:
            self.y+=1
        else:
            self.y-=1
        #Keep the particles within the bounds
        if self.x > self.mx:
            self.x = self.mx
        if self.x < self.mi:
            self.x = self.mi
        if self.y > self.mx:
            self.y = self.mx
        if self.y < self.mi:
            self.y = self.mi
    
    def convert(self,c):
        pass #???
        
def crwt(molec=1000,timepoints=50000):
    t0 = time.clock()
    points = np.ones((molec,2,timepoints), dtype='float32')*500
    points[:,:,1:] = points[:,:,1:]+np.cumsum(norm.rvs(size=(molec,2,timepoints-1)),axis=-1)
    t1 = time.clock()
    return points, t1-t0
    
def vector_brown(molec=1000,timepoints=50000):
    if molec*timepoints > 10**8:
        raise Exception("You're gonna kill the memory!! {} ref {} vs".format(molec*timepoints,1000*100000))
    t0 = time.clock()
    points = np.ones((molec,2,timepoints), dtype='uint16')*500
    #moves = np.random.choice([-1,1],size=(molec,2,timepoints-1))
    #cummoves = np.cumsum(moves,axis=-1)
    points[:,:,1:] = points[:,:,1:]+np.cumsum(np.random.choice([-1,1],size=(molec,2,timepoints-1)),axis=-1)
    t1=time.clock()
    
    return points, t1-t0

def obj_brown(molec=1000,timepoints=50000):
    mol_list = []
    for i in range(0,molec):
        mol_list.append(molecule(0,500,500,0,1000))
    arr = np.empty((len(mol_list),2,timepoints))
    for i in range(0,timepoints):
        for j,v in enumerate(mol_list):
            arr[j,0,i]=v.x
            arr[j,1,i]=v.y
            v.move()
    return arr

def paths(arr, a=0.01):
    
    fig, ax = plt.subplots(1,1)
    ax.set(xlim=(-10,1010),ylim=(-10,1010))
    for l in range(arr.shape[0]):
        ax.plot(arr[l,0,:],arr[l,1,:], c='k', alpha=a)
    
    plt.show()


def scatplot(arr):    
    #This has to be global, have to copy and paste
    #https://stackoverflow.com/questions/41625518/matplotlib-funcanimation-isnt-calling-the-passed-function
    fig1, ax1 = plt.subplots(1,1)
    
    ax1.set(xlim=(0,1000),ylim=(0,1000))
    scat = ax1.scatter(arr[:,0,0],arr[:,1,0], alpha=0.2, edgecolors=None)

    def update(nf):
        scat.set_offsets(arr[:,:,nf])
        #return scat,        
        
    anim = ani.FuncAnimation(fig1, update, interval=1,frames=arr.shape[-1])
    plt.show()