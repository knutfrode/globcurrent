#!/usr/bin/env python

import pickle
import numpy as np
from datetime import datetime, timedelta
from opendrift.models.oceandrift3D import OceanDrift3D
from opendrift.readers import reader_ROMS_native
from opendrift.readers import reader_netCDF_CF_generic

# Forcing data
waves = '/lustre/storeA/project/fou/om/retrospect/retrospect_data/waves/ECwave_%Y.nc'
current = 'http://thredds.met.no/thredds/dodsC/retrospect/qck/control_qck_%Y%m.ncml'
wind = '/lustre/storeA/project/fou/om/retrospect/retrospect_data/Inputs/Forcing/ECMWF_forecast/ocean_frc_%Y.nc'

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
    filename = typ + start_time.strftime('_%Y%m%d%H%M_') + str(d) + '.png'

    lon = data[d]['lon']
    lat = data[d]['lat']

    o = OceanDrift3D()
    readerURL = time[0].strftime(current)
    readerURLnext = (time[0] + timedelta(days=30)).strftime(current)
    reader = reader_ROMS_native.Reader(readerURL)
    readerNext = reader_ROMS_native.Reader(readerURLnext)
    ECfile = time[0].strftime(wind)
    ECMWF_reader = reader_netCDF_CF_generic.Reader(ECfile)
    reader_waves = reader_netCDF_CF_generic.Reader(time[0].strftime(waves))
    reader_waves.interpolation = 'linearND'  # To interpolate towards coast
    o.add_reader([reader, readerNext, ECMWF_reader, reader_waves])

    print reader, readerNext, ECMWF_reader, reader_waves
    o.fallback_values['land_binary_mask'] = 0  # Run without landmask

    if typ == 'iSphere':
        wind_drift_factor = 0.03
        z = 0.0
    elif typ == 'CODE':
        wind_drift_factor = 0
        z = -0.7

    # Seed elements along trajectory at given timesteps
    o.seed_along_trajectory(lon, lat, time,
                            release_time_interval=timedelta(hours=12),
                            wind_drift_factor=wind_drift_factor, z=z)
    print o
    print o.elements_scheduled
    print o.elements_scheduled_time
    # Set lifetime of numerical drifters
    o.set_config('drift:max_age_seconds', 3600*48)

    trajectory_dict = {'lon': lon, 'lat': lat, 'time': time,
                       'linestyle': s, 'name': typ}

    o.run()
    print o
    o.plot(trajectory_dict=trajectory_dict, buffer=.2, filename=filename)
    #reader.buffer = 2
    #o.animation(background=['x_sea_water_velocity',
    #                        'y_sea_water_velocity'],
    #            markersize=16, skip=2, buffer=.5, fps=6, scale=5, 
    #            filename=filename)

