#!/usr/bin/python

import math
import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt
import map_info as m
import importlib as imp

N = 25 # Number of extra points added to orbit for fastpace computations
Scale = 1

#=================================================================================#
#                                 Plotting                                        #
#=================================================================================#

# Computes orbit of a point under the given mapping Map
def get_orbit(Map, pt, orbit_len): 
    orbit = []
    tmp = (pt[0], pt[1])
    # We take extra points in order to look back in time when computing the 
    # fastspace for x_n, n >= 0.
    for n in range(orbit_len+N): 
        orbit.append(tmp)
        tmp = Map.next(tmp)
    return orbit

# Generate a set of n random starting points. Use these as initial points in orbits.
def get_points(n):
    pts = []
    np.random.seed()
    a = np.random.rand(n, 2)
    for i in range(n):
        pt = (a[i, 0], a[i, 1])
        pts.append(pt)
    return pts

# Lightning fast now
def plot(Map, n, orbit_len, flag):
    pts = get_points(n)
    plt.axis([0, Scale, 0, Scale])
    plt.title('K = {}'.format(Map.k))
    for pt in pts:
        plot_orbit(Map, pt, orbit_len, plt, flag)
    plt.savefig('./K={}.png'.format(Map.k)) 
    plt.axes().set_aspect('equal', 'datalim')
    plt.show(block=True) 

def plot_orbit(Map, pt, orbit_len, plt, flag):
    # Plots the points along the orbit
    orbit = get_orbit(Map, pt, orbit_len)
    x,y = zip(*orbit[25:])
    plt.scatter(x, y, c='black', s = 0.1)
    if flag[0] == 1:
        plot_fastspace(Map, orbit, plt)
    if flag[1] == 1:
        plot_slowspace(Map, orbit, plt)

# Plot the fastspace at each point, 
def plot_fastspace(Map, orbit, plt):
    K = 25 # Power of jacobian product in find_fastspace
    vec = get_points(1)[0] # Get one random vector in tangent space of x_0
    fast = []
    for i in range(len(orbit)-N):
        # finds the fastspace over the point orbit[i+N]
        tmp = find_fastspace(Map, orbit[i], vec, K)
        fast_v = (tmp[0,0], tmp[1,0])
        fast.append(fast_v)
    x,y = zip(*orbit[25:])
    u,v = zip(*fast)
    plt.quiver(x, y, u, v, width=0.001, headwidth='10', headlength='10', color='r')

# Plot the slowspace at each point
def plot_slowspace(Map, orbit, plt):
    K = 25
    slow = []
    for pt in orbit[25:]:
        tmp = find_slowspace(Map, pt, K)
        slow_v = (tmp[0,0], tmp[1,0])
        slow.append(slow_v)
    x,y = zip(*orbit[25:])
    u,v = zip(*slow)
    plt.quiver(x, y, u, v, width=0.001, headwidth='10', headlength='10', color='b')

#def gen_std_plots():
#    std = m.std
#    for K in [0.6, 0.971635, 1.2, 2.0]:
#        std.K = K
#        for n in [1, 10, 50]:
#            plot_with_spaces(std, n, 50, (0,1))

#=================================================================================#
#                           Fast/Slow Spaces                                      #
#=================================================================================#

def get_jacobian_iterate(Map, pt, n):
    tmp = pt
    J = np.eye(2) # Assume we're dealing with 2x2's
    for i in range(0, n):
        J = check_matrix_size(J)
        J = Map.jacobian(tmp)*J
        tmp = Map.next(tmp)
    return J

# If pt = x_0, this finds the fastspace of x_25
def find_fastspace(Map, pt, vec, K):
    v = np.matrix('{};{}'.format(vec[0], vec[1]))
    J = get_jacobian_iterate(Map, pt, K)
    return (normalize(J*v))

def find_slowspace(Map, pt, n):
    v = np.matrix('0;1') # This is in the tangent space of x_25 if pt=x_0
    J = get_jacobian_iterate(Map, pt, n)
    return (normalize(np.linalg.solve(J, v)))

# This function needs to be redone as find_fastspace doesn't behave nicely anymore. 
def get_info(Map, pt, vec, n):
    print ('Fast subspace: \n{}\n'.format(find_fastspace(Map, pt, vec, n)))
    print ('Slow subspace: \n{}\n'.format(find_slowspace(Map, pt, n)))
    L_exponents(Map, pt)

#=================================================================================#
#                           SVD and Lyapunov Exponents                            #
#=================================================================================#

# Compute J^N at pt, then take the SVD of J^N to find the Lyapunov exponents
def L_exponents(Map, pt):
    N = 10
    tmp = pt 
    J = np.eye(2) # Assume 2x2
    for i in range(0, N):
        J = J*Map.jacobian(tmp)
        tmp = Map.next(pt)
    (U,D,V) = compute_SVD(J)
    l1 = np.log(D[0,0])/float(N)
    l2 = np.log(D[1,1])/float(N)
    print ('Lambda_1 = {} \nLambda_2 = {}.'.format(l1, l2))

# Here we assume that det(A)=1 and that a_ij < 1000
# Computes the SVD decomposition of a matrix by looking at the eigenvectors of
# AA^T and A^TA. 
def compute_SVD(A):
    s, U = LA.eig(A*np.transpose(A))
    d, V = LA.eig(np.transpose(A)*A)
    s_vals = list(reversed(sorted([math.sqrt(x) for x in s])))
    D = np.diag((s_vals))
    return (U, D, np.transpose(V))

#=================================================================================#
#                           Helper Functions                                      #
#=================================================================================#

def normalize(vec):
    n = LA.norm(vec)
    assert n != 0
    v = np.matrix('{};{}'.format(vec[0,0]/n, vec[1,0]/n))
    return (v)

# If the matrix is too large, normalize its entries by dividing through by the sup norm. 
def check_matrix_size(A): 
    l = [A[0,0], A[0,1], A[1,0], A[1,1]]
    m = max(l)
    if len(str(m)) > 7:
        tmp = [x/m for x in l]
        return np.matrix([[tmp[0], tmp[1]], [tmp[2], tmp[3]]])
    else:
        return A
