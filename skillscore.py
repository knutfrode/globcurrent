# -*- coding: utf-8 -*-


import scipy as sp # scientific python

def dist(x1,y1,x2,y2):
    return sp.sqrt(sp.square(x2-x1) + sp.square(y2-y1))

def skillscore(a, b, n=1.):
    ''' calculate skill score from normalized cumulative seperation 
    distance. Liu and Weisberg 2011.
    a,b: trajectories. a and b contain lists of x and y positions: 
         a = [x, y] 
         where x and y are lists or 1d-arrays of position components.
    n:   skillscore demand parameters as defined by Liu and Weisberg
    
    returns the skill score bewteen 0. and 1.
    '''
    d = dist(a[0], a[1], b[0], b[1])[1:-1]
    dl = dist(b[0][:-1], b[1][:-1], b[0][1:], b[1][1:])
    l = dl.cumsum()
    s = d.sum() / l.sum()
    ss = max(0, 1 - s/n)
    if sp.isnan(s):
        ss=sp.nan
    return ss


