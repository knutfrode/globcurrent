#!/usr/bin/env python

from opendrift.models.oceandrift3D import OceanDrift3D
from opendrift.readers import reader_ROMS_native
from opendrift.readers import reader_netCDF_CF_generic

forcing = 'norshelf'
forcing = 'globcur-total'
#forcing = 'globcur-total15m'

time = datetime(2013, 3, 1, 12)

r = reader_netCDF_CF_generic(time.strftime(''))
