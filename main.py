import netCDF4 as nc
import numpy as np
import statistics as std
import matplotlib.pyplot as plt

def get_pixn_ndvi(file, target):
    lati = np.flipud(np.fliplr(file.groups['navigation_data'].variables['latitude'][:]))
    long = np.flipud(np.fliplr(file.groups['navigation_data'].variables['longitude'][:]))

    distance = (np.abs(lati - 43.55885) ** 2 + np.abs(long - 4.864472) ** 2)

    i, j = np.unravel_index(distance.argmin(), distance.shape)

    ndvi = np.flipud(np.fliplr(file.groups['geophysical_data'].variables['ndvi'][:]))
    ndvi[distance < 0.0002] = 2

    return i, j


file = nc.Dataset('../Data/MODIS_la_crau_ndvi/MOD00.P2020140.1150_1.PDS.nc', "r", format="NETCDF4")
target = 1

i, j = get_pixn_ndvi(file, target)