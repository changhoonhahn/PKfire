'''

plots using pk


'''
import numpy as np
import pk as PK

import matplotlib.pyplot as plt
from ChangTools.plotting import prettyplot
from ChangTools.plotting import prettycolors


def PlotPk(name, version): 
    '''
    '''
    peek = PK.Pk(name, version) 
    peek.Read()
    
    prettyplot() 
    pretty_colors = prettycolors() 

    fig = plt.figure(figsize=(10,10))
    sub = fig.add_subplot(111)

    sub.plot(peek.k, peek.p0k, lw=3, c=pretty_colors[3]) 
    sub.set_xlabel('$\mathtt{k} (h/\mathtt{Mpc})$', fontsize=30)
    sub.set_ylabel('$\mathtt{P_0(k)}$', fontsize=30)

    plt.show() 
    return None 


def PlotkPk(name, version): 
    peek = PK.Pk(name, version) 
    peek.Read()
    
    prettyplot() 
    pretty_colors = prettycolors() 

    fig = plt.figure(figsize=(10,10))
    sub = fig.add_subplot(111)

    sub.plot(peek.k, peek.k * peek.p0k, lw=3, c=pretty_colors[3]) 
    sub.set_xlabel('$\mathtt{k} (h/\mathtt{Mpc})$', fontsize=30)
    sub.set_ylabel('$\mathtt{k P_0(k)}$', fontsize=30)

    plt.show() 


def PlotkPk_forcomp(name, version): 
    '''
    '''
    peek = PK.Pk(name, version) 
    peek.Read()
    
    #prettyplot() 
    pretty_colors = prettycolors() 

    fig = plt.figure(1, figsize=(10,10))
    sub = fig.add_subplot(111)

    sub.plot(peek.k, peek.k * peek.p2k, lw=3, c=pretty_colors[0]) 
    peek._Rebin_k(np.arange(0.005, 0.41, 0.01)) 
    sub.plot(peek.k, peek.k * peek.p2k, lw=3, c=pretty_colors[3]) 

    # axes
    sub.set_xlim([0.0, 0.4]) 
    sub.set_xticks(np.arange(0., 0.45, 0.05)) 
    sub.set_xlabel('$\mathtt{k} (h/\mathtt{Mpc})$', fontsize=30)
    sub.set_ylim([0., 700.])
    #sub.set_yticks(np.arange(0., 1100., 100.)) 
    sub.set_ylabel('$\mathtt{k P_0(k)}$', fontsize=30)
    
    fig.savefig('comp.png') 
    plt.close() 
    return None 



if __name__=='__main__': 
    PlotkPk_forcomp('eBOSS_QSO', 'v1.6_N') 
