#!/usr/bin/env python

from netCDF4 import Dataset
import calendar
import pickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib import animation
from mpl_toolkits.basemap import pyproj

# Read drifter data
f = '/disk1/data/drifter/all_trajectories_wind_unfiltered.dat'
data = pickle.load(open(f))

drifters = np.arange(63, 68)  # The 5 colocated iSpheres

modis = '/home/knutfd/Downloads/A20111452011152.L3m_8D_SST_sst_4km.nc'
m = Dataset(modis)
sst = m.variables['sst'][:]
modlon = m.variables['lon'][:]
modlat = m.variables['lat'][:]

lons = np.zeros((len(drifters), 641))
lats = np.zeros((len(drifters), 641))
minlength = 641
# Loop through drifters
for i, d in enumerate(drifters):
    time = data[d]['time']
    time = [t.replace(tzinfo=None) for t in time]
    lon = data[d]['lon']
    lat = data[d]['lat']
    if len(lon) != len(time):
        lon = lon[0:len(time)]
        lat = lat[0:len(time)]
    # Interpolate trajectories to half-hourly values
    itime = []
    dt = time[0]
    while dt < time[-1]:
        itime.append(dt)
        dt += timedelta(hours=.5)
    ilon = np.interp([calendar.timegm(t.timetuple()) for t in itime],
                     [calendar.timegm(t.timetuple()) for t in time],
                     lon) 
    ilat = np.interp([calendar.timegm(t.timetuple()) for t in itime],
                     [calendar.timegm(t.timetuple()) for t in time],
                     lat) 
    lons[i,0:len(ilon)] = ilon;
    lats[i,0:len(ilat)] = ilat
    time=itime
    minlength = np.min((minlength, len(ilon)))

#minlength = 300
lons = lons[:,0:minlength].T
lats = lats[:,0:minlength].T
time = time[0:minlength]

# Convert relative distance in [m] in stereographic coordinates
mlon = np.mean(np.mean(lons))
mlat = np.mean(np.mean(lats))
proj = pyproj.Proj(proj="stere", lat_0=mlat, lon_0=mlon, k_0=1.0, x_0=0, y_0=0, ellps="WGS84")
x, y = proj(lons, lats)

meanlon = np.mean(lons, 1)
meanlat = np.mean(lats, 1)
meanx = np.mean(x, 1)
meany = np.mean(y, 1)

deltalon = lons - meanlon[:,None]
deltalat = lats - meanlat[:,None]
deltalat = deltalat*2  # for equal axis lengths
deltax = x - meanx[:,None]
deltay = y - meany[:,None]

def plot_timestep(i):
    ax.set_title('hours: %s' % i)
    points1.set_data(deltax[i,0], deltay[i,0])
    points2.set_data(deltax[i,1], deltay[i,1])
    points3.set_data(deltax[i,2], deltay[i,2])
    points4.set_data(deltax[i,3], deltay[i,3])
    points5.set_data(deltax[i,4], deltay[i,4])
    mpoint.set_data(meanlon[i], meanlat[i])

plt.figure(figsize=(12, 10))
plt.subplot(2,1,1)
lim = 1200 # m
plt.axis('square')
plt.axis([-lim, lim, -lim, lim])
points1, = plt.plot(deltax[0,0], deltay[0,0], 'k.', markersize=15)
points2, = plt.plot(deltax[0,1], deltay[0,1], 'r.', markersize=15)
points3, = plt.plot(deltax[0,2], deltay[0,2], 'b.', markersize=15)
points4, = plt.plot(deltax[0,3], deltay[0,3], 'g.', markersize=15)
points5, = plt.plot(deltax[0,4], deltay[0,4], 'y.', markersize=15)
ax = plt.gcf().gca()
plt.xlabel('Separation [m]')
plt.ylabel('Separation [m]')

# Overview map
plt.subplot(2,1,2)
plt.pcolormesh(modlon, modlat, sst, vmin=5, vmax=8)
plt.colorbar()
plt.plot(meanlon, meanlat)
plt.plot(lons, lats, 'k', alpha=.3)
plt.axis([meanlon.min(), meanlon.max(), meanlat.min(), meanlat.max()])
mpoint, = plt.plot(meanlon[0], meanlat[0], 'r.', markersize=15)
plt.xlabel('Longitude')
plt.ylabel('Latitude')

anim = animation.FuncAnimation(plt.gcf(), plot_timestep, blit=False,
                               frames=deltalon.shape[0], interval=100)
#anim.save(filename='iSphere_dispersion.mp4',
#          bitrate=2000, extra_args=['-pix_fmt', 'yuv420p'])
plt.show()
