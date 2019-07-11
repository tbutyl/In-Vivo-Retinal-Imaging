# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 13:41:19 2019

@author: emiller5
"""

#Vectorized FTCS method

"""
For eqns:

u_t = a*u_xx on (0,L)
u=0 on x=0,l for t in (o,T]
Initial condiiton = u(x,0) = I(x)

Vars:

Nx: #mesh points, 0 to Nx
F: diffusion number a*dt/dx**2, specifies time step, must be <=0.5
T: time
I: initial condiiton function
a: constant diffusion coefficient
L: length
x: mesh point in space
t: mesh points in time
n: time index
u: unknown/current function
u_1: know/preivous function
dx: const mesh spacing in x
dt: const mehs spacing in t
"""

import matplotlib.pyplot as plt
import sys, time
#from scitools.std import *
import scipy.sparse
import scipy.sparse.linalg
import numpy as np
import scipy.linalg

def FTCS(I,a,L,Nx,F,T):
    import time
    t0 = time.clock()
    
    x = np.linspace(0,L,Nx+1)
    dx = x[1]-x[0]
    dt = F*dx**2/a
    Nt=int(round(T/float(dt)))
    t = np.linspace(0,T,Nt+1)
    
    u = np.zeros(Nx+1)
    u_1 = np.zeros(Nx+1)
    out = np.empty((Nx+1,Nt+1))
    
    #init
    for i in range(0,Nx+1):
        u_1[i]=I(x[i])
    out[:,0] = u_1
        
    for n in range(1,Nt+1):
        u[1:Nx] = u_1[1:Nx] + F*(u_1[0:Nx-1] - 2*u_1[1:Nx] + u_1[2:Nx+1])#vector update step
        u[0],u[-1] = 0,0#u[1],u[-2] #reflecting boundary, no material is lost
        out[:,n] = u #update the master array
        
        u_1,u=u,u_1 #update, I assume swtiching is quicker?
    t1=time.clock()
    
    return u,x,t,t1-t0, out
    
def BTCS(I,a,L,Nx,F,T):
    
    """Back time center space algorithm. Uses sparse matrix for solving the sytem of eqns"""

    import time
    t0 = time.clock()
    
    x = np.linspace(0,L,Nx+1)
    dx = x[1]-x[0]
    dt = F*dx**2/a
    Nt=int(round(T/float(dt)))
    t = np.linspace(0,T,Nt+1)
    
    u = np.zeros(Nx+1) #solution at t[n+1]
    u_1 = np.zeros(Nx+1) # solution at t[n]  
    out = np.empty((Nx+1,Nt+1))
    
    #representing the sparse matix and right hand side of matrix eqn
    diagonal = np.zeros(Nx+1)
    lower = np.zeros(Nx)
    upper = np.zeros(Nx)
    b = np.zeros(Nx+1)
    
    #precomp sparse matrix
    diagonal[:] = 1 + 2*F
    lower[:] = -F
    upper[:] = -F
    #boundary init
    diagonal[0] = 1
    upper[0] = 0
    diagonal[Nx] = 1
    lower[-1] = 0
    
    A = scipy.sparse.diags(
        diagonals=[diagonal,lower,upper],
        offsets=[0,-1,1], shape=(Nx+1, Nx+1),
        format='csr')
    #print(A.todense())
    
    #set boundary
    for i in range(0, Nx+1):
        u_1[i] = I(x[i])
    out[:,0] = u_1
        
    for n in range(0, Nt):
        b = u_1
        b[0] = b[-1] = 0.0
        u[:] = scipy.sparse.linalg.spsolve(A,b)
        out[:,n] = u
        
        u_1, u = u, u_1
    
    t1 = time.clock()
    return u,x,t,t1-t0,out
    
def solver_BE_simple(I, a, L, Nx, F, T):
    """
    Simplest expression of the computational algorithm
    for the Backward Euler method, using explicit Python loops
    and a dense matrix format for the coefficient matrix.
    """
    import time
    t0 = time.clock()
    x = np.linspace(0, L, Nx+1)   # mesh points in space
    dx = x[1] - x[0]
    dt = F*dx**2/a
    Nt = int(round(T/float(dt)))
    t = np.linspace(0, T, Nt+1)   # mesh points in time
    u   = np.zeros(Nx+1)
    u_1 = np.zeros(Nx+1)

    # Data structures for the linear system
    A = np.zeros((Nx+1, Nx+1))
    b = np.zeros(Nx+1)

    for i in range(1, Nx):
        A[i,i-1] = -F
        A[i,i+1] = -F
        A[i,i] = 1 + 2*F
    A[0,0] = A[Nx,Nx] = 1

    # Set initial condition u(x,0) = I(x)
    for i in range(0, Nx+1):
        u_1[i] = I(x[i])

    for n in range(0, Nt):
        # Compute b and solve linear system
        for i in range(1, Nx):
            b[i] = u_1[i]
        b[0] = b[Nx] = 0
        u[:] = scipy.linalg.solve(A, b)

        # Update u_1 before next step
        #u_1[:]= u
        u_1, u = u, u_1

    t1 = time.clock()
    return u, x, t, t1-t0