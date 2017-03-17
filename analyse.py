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

for with_stokes in [True, False]:
    for forcing in ['globcur', 'norshelf']:
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
            if len(lon) != len(time):
                lon = lon[0:len(time)]
                lat = lat[0:len(time)]

            itime = []
            dt = time[0]
            print len(lon), len(lat), len(time), 'TI'
            while dt < time[-1]:
                itime.append(dt)
                dt += timedelta(hours=1)
            ilon = np.interp([calendar.timegm(t.timetuple()) for t in itime],
                             [calendar.timegm(t.timetuple()) for t in time],
                             lon)
            ilat = np.interp([calendar.timegm(t.timetuple()) for t in itime],
                             [calendar.timegm(t.timetuple()) for t in time],
                             lat)
            lon = ilon; lat=ilat; time=itime

            trajectory_dict = {'lon': lon, 'lat': lat, 'time': time,
                               'linestyle': s, 'name': typ}

            o = OceanDrift3D()
            # Forcing data
            if with_stokes is True:
                filename = 'output/' + typ + '_' + forcing + \
                            start_time.strftime('_%Y%m%d%H%M_') + str(d)
            else:
                filename = 'output/' + typ + '_' + forcing + '_nostokes' + \
                            start_time.strftime('_%Y%m%d%H%M_') + str(d)

            o.io_import_file(filename + '.nc')
            print np.size(lon)
            print o.history['lon'].shape
            #lon_drift = lon[0:o.history['lon'].shape[1]+1]
            #lat_drift = lat[0:o.history['lat'].shape[1]+1]
            o.history = o.history[:,0:len(lon)]
            print np.size(lon)
            print  o.history['lon'].shape
            plt.plot(lon, o.history['lon'].T)
            plt.plot([lon.min(), lon.max()], [lon.min(), lon.max()], '-k')
            plt.show()

            #o.plot(trajectory_dict=trajectory_dict, buffer=.2,
            #       linecolor='wind_drift_factor')
            plt.imshow(o.history['lat'])
            plt.show()
