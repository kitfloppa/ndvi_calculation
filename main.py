import netCDF4 as nc
import numpy as np
import statistics as std
import matplotlib.pyplot as plt

from Point import Point as pn

def get_pixn_ndvi(file, target):
    lati = np.flipud(np.fliplr(file.groups['navigation_data'].variables['latitude'][:]))
    long = np.flipud(np.fliplr(file.groups['navigation_data'].variables['longitude'][:]))

    distance = np.abs(lati - target[0]) ** 2 + np.abs(long - target[1]) ** 2
    i, j = np.unravel_index(distance.argmin(), distance.shape)

    return i, j


def ndvi_pix_data(file, x, y):
    ndvi_band = np.flipud(np.fliplr(file.groups['geophysical_data'].variables['ndvi'][:]))
    ndvi_area = np.zeros((3, 3))
    x -= 1
    y -= 1

    for i in range(ndvi_area.shape[0]):
        for j in range(ndvi_area.shape[1]):
            ndvi_area[i, j] = ndvi_band[x + i, y + j]

    plt.imshow(ndvi_area)
    plt.show()

    return np.ravel(ndvi_area)


file = nc.Dataset('../Data/MODIS_la_crau_ndvi/MOD00.P2020140.1150_1.PDS.L2', "r", format="NETCDF4")
target = pn(43.55885, 4.864472)

i, j = get_pixn_ndvi(file, target)
print(i, j)
lacrau_ndvi = ndvi_pix_data(file, i, j)

mean = std.fmean(lacrau_ndvi)
deviation = std.pstdev(lacrau_ndvi)

print(mean)
print(deviation)

print((0.2565 - 0.0931) / (0.2565 + 0.0931))
print((0.2442 - 0.0980) / (0.2442 + 0.0980))

