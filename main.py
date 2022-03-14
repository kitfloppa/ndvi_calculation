import netCDF4 as nc
import numpy as np
import statistics as std
import matplotlib.pyplot as plt

file = nc.Dataset('../Data/MODIS_la_crau_ndvi/MOD00.P2020140.1150_1.PDS.nc', "r", format="NETCDF4")

print(file.groups)
print(file.dimensions['number_of_lines'].size)
print(file.dimensions['pixels_per_line'].size)
print(file.groups['geophysical_data'].variables['ndvi'].scale_factor)
lati = np.flipud(np.fliplr(file.groups['navigation_data'].variables['latitude'][:]))
long = np.flipud(np.fliplr(file.groups['navigation_data'].variables['longitude'][:]))

distance = (np.abs(lati - 43.55885) ** 2 + np.abs(long - 4.864472) ** 2)

i, j = np.unravel_index(distance.argmin(), distance.shape)

print(i, j)

ndvi = np.flipud(np.fliplr(file.groups['geophysical_data'].variables['ndvi'][:]))

ndvi[distance < 0.0002] = 2

plt.imshow(ndvi)
plt.show()
