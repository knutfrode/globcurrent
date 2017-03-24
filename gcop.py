#!/usr/bin/env python

import os
import calendar
import glob
import pickle
import numpy as np
from datetime import datetime, timedelta
from opendrift.models.oceandrift3D import OceanDrift3D
from opendrift.readers import reader_ROMS_native
from opendrift.readers import reader_netCDF_CF_generic

replot = False
with_stokes = False

forcing = 'norshelf'
forcing = 'globcur'
#forcing = 'globcur-total15m'

# Read drifter data
f = '/disk1/data/drifter/all_trajectories_wind_unfiltered.dat'
data = pickle.load(open(f))
print data.keys()
print data[12].keys()

for with_stokes in [True, False]:
    for forcing in ['norshelf', 'globcur']:
        # Loop through drifters
        for d in data:
            typ = data[d]['type']
            if typ == 'iSphere':
                s = 'r-'
            elif typ == 'SLMDB':
                typ = 'CODE'
                s = 'b-'
            else:
                error
            
            #if d != 45 and type != 'CODE':
            #    continue
            #print d

            time = data[d]['time']
            time = [t.replace(tzinfo=None) for t in time]
            start_time = time[0]
            if start_time < datetime(2011, 5, 1):
                print 'Before Retrospect start: %s' % time[0]
                continue

            if with_stokes is True:
                filename = 'output/' + typ + '_' + forcing + \
                            start_time.strftime('_%Y%m%d%H%M_') + str(d)
            else:
                filename = 'output/' + typ + '_' + forcing + '_nostokes' + \
                            start_time.strftime('_%Y%m%d%H%M_') + str(d)

            print filename + '.nc'
            if len(glob.glob(filename + '.nc')) > 0:
                print 'NetCDF output exists, skipping'
                continue

            lon = data[d]['lon']
            lat = data[d]['lat']
            if len(lon) != len(time):
                lon = lon[0:len(time)]
                lat = lat[0:len(time)]

            # Interpolate trajectories to hourly values
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

            o = OceanDrift3D()
            o.set_config('drift:stokes_drift', with_stokes)
            o.max_speed = 7  # Due to future seeding!

            del o.fallback_values['x_sea_water_velocity']
            del o.fallback_values['y_sea_water_velocity']
            del o.fallback_values['x_wind']
            del o.fallback_values['y_wind']

            # Forcing data
            
            if forcing == 'norshelf':
                # NB: waves only for 5 months of 2011
                #waves = '/lustre/storeA/project/fou/om/retrospect/retrospect_data/waves/ECwave_%Y.nc'
                current = 'http://thredds.met.no/thredds/dodsC/retrospect/qck/control_qck_%Y%m.ncml'
                readerURL = time[0].strftime(current)
                readerURLnext = (time[0] + timedelta(days=30)).strftime(current)
                reader = reader_ROMS_native.Reader(readerURL)
                readerNext = reader_ROMS_native.Reader(readerURLnext)
                readers = [readerNext, reader]
                o.add_reader(readers)
            elif forcing == 'globcur':
                current = 'http://tds0.ifremer.fr/thredds/dodsC/CLS-L4-CUREUL_HS-ALT_SUM-V02.0_FULL_TIME_SERIE'
                o.add_readers_from_list([current])
            else:
                unknown_current
            #elif forcing == 'globcur-total15m':
            #    current = 'http://tds0.ifremer.fr/thredds/dodsC/CLS-L4-CUREUL_15M-ALT_SUM-V02.0_FULL_TIME_SERIE'

            # Adding readers
            if with_stokes is True:
                stokes = time[0].strftime('stokes_year/stokes_%Y.nc')
                o.add_readers_from_list([stokes])
            wind = time[0].strftime('/lustre/storeA/project/fou/om/retrospect/retrospect_data/Inputs/Forcing/ECMWF_forecast/ocean_frc_%Y.nc')
            o.add_readers_from_list([wind])
            print o.readers
            stop

            # Interpolation method
            for re in o.readers:
                o.readers[re].interpolation = 'linearND'

            o.fallback_values['land_binary_mask'] = 0  # Run without landmask

            if typ == 'iSphere':
                #wind_drift_factor = 0.01
                wind_drift_factor = [0, 0.01, 0.02, 0.03]
                z = 0.0
            elif typ == 'CODE':
                wind_drift_factor = [0]
                z = -0.7

            # Seed elements along trajectory at given timesteps
            o.seed_along_trajectory(lon, lat, time, number=len(wind_drift_factor),
                                    release_time_interval=timedelta(hours=48),
                                    wind_drift_factor=wind_drift_factor, z=z)

            # Set lifetime of numerical drifters
            o.set_config('drift:max_age_seconds', 3600*48)

            trajectory_dict = {'lon': lon, 'lat': lat, 'time': time,
                               'linestyle': s, 'name': typ}

            #if replot is True:
            #    o.io_import_file(filename + '.nc')
            #else:
            #    o.run(end_time=time[-1] + timedelta(hours=48),
            #          outfile=filename + '.nc', stop_on_error=False)
            print o
            if typ == 'CODE':
                o.plot(trajectory_dict=trajectory_dict, buffer=.2,
                   filename=filename + '.png')
            elif typ == 'iSphere':
                o.plot(trajectory_dict=trajectory_dict, buffer=.2,
                   linecolor='wind_drift_factor',
                   filename=filename + '.png')
            #reader.buffer = 2
            #o.animation(background=['x_sea_water_velocity',
            #                        'y_sea_water_velocity'],
            #            markersize=16, skip=2, buffer=.5, fps=6, scale=5, 
            #            filename=filename)
