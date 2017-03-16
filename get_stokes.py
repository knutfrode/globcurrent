#!/usr/bin/env python

import os
from datetime import datetime

def is_leap_year(year):
    """ if year is a leap year return True
        else return False """
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0

def doy(Y,M,D):
    """ given year, month, day return day of year
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return N

def ymd(Y,N):
    """ given year = Y and day of year = N, return year, month, day
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """    
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    M = int((9 * (K + N)) / 275.0 + 0.98)
    if N < 32:
        M = 1
    D = N - int((275 * M) / 9.0) + K * int((M + 9) / 12.0) + 30
    return Y, M, D

url_base = 'http://www.ifremer.fr/opendap/cerdap1/globcurrent/v3.0/global_050_deg/stokes/%Y/%3.3i/%Y%m%d%H%M%S-GLOBCURRENT-L4-CURstk_hs-WW3_IFR-v01.0-fv01.0.nc'
stokesfile = 'stokes.nc'
for year in range(2010, 2011):
    for doy in range(1,366):
        for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
            y,m,d = ymd(year, doy)
            t = datetime(y, m, d, hour)
            url = t.strftime(url_base) % doy
            outfile = t.strftime('stokes/stokes_%Y%m%d%H.nc')
            if os.path.exists(outfile):
                continue
            command = 'ncks -4 -dlat,270,305 -dlon,350,425 ' + url + ' ' + outfile
            print command
            try:
                os.system(command)
            except:
                pass
