#!/usr/bin/env python

import calendar
import pickle
import numpy as np
from mpl_toolkits.basemap import pyproj
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from opendrift.models.oceandrift3D import OceanDrift3D
from opendrift.readers import reader_ROMS_native
from opendrift.readers import reader_netCDF_CF_generic

geod = pyproj.Geod(ellps='WGS84')

recalc = False

alldata = {'CODE': {'norshelf': {'stokes': None, 'nostokes': None},
                    'globcur':  {'stokes': None, 'nostokes': None}},
           'iSphere': {'norshelf': {'stokes': None, 'nostokes': None},
                        'globcur':  {'stokes': None, 'nostokes': None}}
            }

# Read drifter data
f = '/disk1/data/drifter/all_trajectories_wind_unfiltered.dat'
data = pickle.load(open(f))
#print data.keys()
#print data[12].keys()

if recalc is True:
    for with_stokes in [True, False]:
        if with_stokes is True:
            hasstokes = 'stokes'
        else:
            hasstokes = 'nostokes'
        for forcing in ['globcur', 'norshelf']:
            # Loop through drifters
            for d in data:
                typ = data[d]['type']
                print typ
                if typ == 'iSphere':
                    s = 'r-'
                elif typ == 'SLMDB':
                    typ = 'CODE'
                    s = 'b-'
                else:
                    error
                #if alldata[typ][forcing][hasstokes] is None:
                #    alldata[typ][forcing][hasstokes] = \
                #        np.ma.zeros((48, 1000))  # Assumed big enough
                #separr = alldata[typ][forcing][hasstokes]  # pointer
                #separr.mask = True
                #print separr
                #print separr.shape
                #stop

                time = data[d]['time']
                time = [t.replace(tzinfo=None) for t in time]
                start_time = time[0]
                if start_time < datetime(2011, 5, 1):
                    print 'Before Retrospect start: %s' % time[0]
                    continue

                lon = data[d]['lon']
                lat = data[d]['lat']
                if len(lon) != len(time):
                    lon = lon[0:len(time)]
                    lat = lat[0:len(time)]

                itime = []
                dt = time[0]
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

                print filename
                try:
                    o.io_import_file(filename + '.nc')
                except:
                    continue
                    
                o.history = o.history[:,0:len(lon)]
                #plt.plot(lon, o.history['lon'].T)
                #plt.plot([lon.min(), lon.max()], [lon.min(), lon.max()], '-k')
                #plt.show()

                if typ == 'iSphere':
                    wdfs = [0, .1, .2, .3]
                else:
                    wdfs = [0]
                numwdfs = len(wdfs)
                num_elements = o.history['lon'].shape[0]
                traj_lon = np.zeros((48, num_elements, numwdfs))
                traj_lat = np.zeros((48, num_elements, numwdfs))
                dr_lon = np.zeros((48, num_elements, numwdfs))
                dr_lat = np.zeros((48, num_elements, numwdfs))
                for e in range(num_elements):
                    tlon = o.history['lon'][e, :]
                    if np.sum(~tlon.mask) != 49:
                        continue
                    wdf = o.history['wind_drift_factor'][e,~tlon.mask][0]
                    wdf = int(wdf*10)
                    print wdf
                    tlon = o.history['lon'][e, :]
                    traj_lon[:,e,wdf] = tlon[~tlon.mask][0:48]
                    tlat = o.history['lat'][e, :]
                    traj_lat[:,e,wdf] = tlat[~tlat.mask][0:48]
                    dr_lon[:,e,wdf] = lon[~tlat.mask][0:48]
                    dr_lat[:,e,wdf] = lat[~tlon.mask][0:48]
                ind = np.where(dr_lon[0,:] != 0)[0]
                traj_lon = traj_lon[:,ind,:]
                traj_lat = traj_lat[:,ind,:]
                dr_lon = dr_lon[:,ind,:]
                dr_lat = dr_lat[:,ind,:]

                fa, ba, sep = geod.inv(dr_lon.ravel(), dr_lat.ravel(), traj_lon.ravel(), traj_lat.ravel())
                #fa, ba, sep = geod.inv(dr_lon, dr_lat, traj_lon, traj_lat)
                sep = np.reshape(sep, traj_lon.shape)
                if alldata[typ][forcing][hasstokes] is None:
                    print 'oppretting'
                    alldata[typ][forcing][hasstokes] = sep
                else:
                    print 'reusing'
                    alldata[typ][forcing][hasstokes] = \
                        np.concatenate((alldata[typ][forcing][hasstokes], sep),
                                       axis=1)
                #plt.plot(alldata[typ][forcing][hasstokes])
                #plt.title(typ + str(alldata[typ][forcing][hasstokes].shape))
                #plt.show()
        
    pickle.dump(alldata, open('alldata.dat', 'w'))
else:
    alldata = pickle.load(open('alldata.dat'))

#for typ in ['iSphere']:
#    for forcing in ['globcur', 'norshelf']:
#        for hasstokes in ['stokes', 'nostokes']:
#            print alldata[typ][forcing][hasstokes].shape
#            print alldata[typ][forcing][hasstokes][0,0,0]
#            print alldata[typ][forcing][hasstokes][0,0,1]
#            print alldata[typ][forcing][hasstokes][0,0,2]
#            stop
#            for i in range(4):
#                wdf = i/10.
#                print i
#                plt.plot(np.mean(alldata[typ][forcing][hasstokes][:,:,i], 1),
#                     label='%s  %s (%s)' % (forcing, hasstokes, wdf))
#    plt.title('%s' % (typ))
#    plt.legend(loc='best')
#    plt.show()
#stop

forleg = {'globcur': 'GlobCurrent total_hs',
          'norshelf': 'NorShelf ocean model'}
stokleg = {'stokes': 'with Stokes drift',
           'nostokes': 'no Stokes drift'}
for typ in ['iSphere', 'CODE']:
    plt.figure(figsize=(10, 6.))
    for forcing in ['globcur', 'norshelf']:
        if forcing == 'globcur':
            ltb = 'r-'
        else:
            ltb = 'b-'
        for hasstokes in ['stokes', 'nostokes']:
            if hasstokes == 'nostokes':
                lt = ltb + '.'
            else:
                lt = ltb
            plt.plot(np.mean(alldata[typ][forcing][hasstokes][:,:,0], 1)/1000,
                     lt,
                     label='%s - %s' % (forleg[forcing],
                                       stokleg[hasstokes]),
                     linewidth=3)
            plt.xlabel('Time [hours]')
            plt.ylabel('Separation forecast - drifter [km]')
            plt.xlim([0, 48])
    plt.title('%s' % (typ))
    plt.legend(loc='best')
    plt.savefig('GlobCur_%s_%s.png' % (typ, forcing))
    plt.close()
    #plt.show()

