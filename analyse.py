#!/usr/bin/env python

import calendar
import pickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from opendrift.models.oceandrift3D import OceanDrift3D
from opendrift.readers import reader_ROMS_native
from opendrift.readers import reader_netCDF_CF_generic

forcing = 'norshelf'
#forcing = 'globcur-total'
#forcing = 'globcur-total15m'


# Read drifter data
f = '/disk1/data/drifter/all_trajectories_wind_unfiltered.dat'
data = pickle.load(open(f))
print data.keys()
print data[12].keys()

# Loop through drifters
for d in data:
    typ = data[d]['type']
    print typ
    if typ == 'iSphere':
        s = 'r-'
    elif typ == 'SLMDB':
        continue
        typ = 'CODE'
        s = 'b-'
    else:
        error

    time = data[d]['time']
    time = [t.replace(tzinfo=None) for t in time]
    start_time = time[0]
    if start_time < datetime(2011, 5, 1):
        print 'Before Retrospect start: %s' % time[0]
        continue
    print time

    lon = data[d]['lon']
    lat = data[d]['lat']
    trajectory_dict = {'lon': lon, 'lat': lat, 'time': time,
                       'linestyle': s, 'name': typ}

    o = OceanDrift3D()
    # Forcing data
    filename = typ + '_' + forcing + start_time.strftime('_%Y%m%d%H%M_') + str(d)

    o.io_import_file(filename + '.nc')
    print lon

    otime = o.get_time_array()[0]
    time_rel = [calendar.timegm(t.timetuple()) for t in time]
    otime_rel = [calendar.timegm(t.timetuple()) for t in otime]
    lonH = np.interp(otime_rel, time_rel, lon[0:-1])
    latH = np.interp(otime_rel, time_rel, lat[0:-1])
    plt.plot(lonH, o.history['lon'][:,:].T)
    plt.show()

    #o.plot(trajectory_dict=trajectory_dict, buffer=.2,
    #       linecolor='wind_drift_factor')
    plt.imshow(o.history['lat'])
    plt.show()
