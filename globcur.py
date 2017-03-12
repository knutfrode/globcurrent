#!/usr/bin/env python

import pickle
import numpy as np
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_ROMS_native

#readers = [reader_ROMS_native.Reader('http://thredds.met.no/thredds/dodsC/retrospect/qck/control_qck_201004.ncml')]

f = '/disk1/data/drifter/all_trajectories_wind_unfiltered.dat'
data = pickle.load(open(f))

print dir(data)
print data.keys()
print data[12].keys()


for d in data:
    typ = data[d]['type']
    print typ
    if typ == 'iSphere':
        s = 'r-'
    elif typ == 'SLMDB':
        s = 'b-'
    else:
        error


    time = data[d]['time']
    start_time = time[0].replace(tzinfo=None)
    if start_time < datetime(2011, 5, 1):
        print 'Too early: %s' % time[0]
        continue
    filename = typ + start_time.strftime('_%Y%m%d%H%M_') + str(d) + '.mp4'

    lon = data[d]['lon']
    lat = data[d]['lat']

    o = OceanDrift()
    readerURL = time[0].strftime('http://thredds.met.no/thredds/dodsC/retrospect/qck/control_qck_%Y%m.ncml')
    print readerURL
    reader = reader_ROMS_native.Reader(readerURL)
    o.add_reader(reader)
    o.seed_elements(lon=lon[0], lat=lat[0], time=start_time)
    o.fallback_values['land_binary_mask'] = 0

    o.run(duration=timedelta(hours=50),
          time_step_output=timedelta(hours=1),
          time_step=timedelta(minutes=30))
    reader.buffer = 2
    o.animation(background=['x_sea_water_velocity',
                            'y_sea_water_velocity'],
                markersize=16, skip=2, buffer=.5, fps=6, scale=5, 
                filename=filename)
