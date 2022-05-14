import datetime
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt

from math import atan2, pi

def date_from_modis_filename(file_name):
    i = 0
    
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    month = months[i]
    
    fdate = file_name[7:14]
    year = int(file_name[7:11])
    day = int(file_name[11:14])
    ftime = file_name[15:17] + ':' + file_name[17:19]
    
    if ((year % 4 == 0) and (not (year % 100 == 0))) or (year % 400 == 0):
        months[1] += 1

    while day > month:
        i += 1
        day -= month
        month = months[i]

    i += 1

    if (day > 9):
        if (i > 9):
            fdate = str(year) + '-' + str(i) + '-' + str(day)
        else:
            fdate = str(year) + '-0' + str(i) + '-' + str(day)
    else:
        if (i > 9):
            fdate = str(year) + '-' + str(i) + '-0' + str(day)
        else:
            fdate = str(year) + '-0' + str(i) + '-0' + str(day)

    return fdate, datetime.time.fromisoformat(ftime)


def get_pixn_ndvi(file, target):
    lati = np.flipud(np.fliplr(file.groups['navigation_data'].variables['latitude'][:]))
    long = np.flipud(np.fliplr(file.groups['navigation_data'].variables['longitude'][:]))

    distance = np.abs(lati - target[0]) ** 2 + np.abs(long - target[1]) ** 2
    i, j = np.unravel_index(distance.argmin(), distance.shape)
    
    if distance.min() > 0.001:
        i, j = -1, -1

    return i, j


def get_azimut(file, target):
    clat = file.groups['scan_line_attributes'].variables['clat'][:]
    clon = file.groups['scan_line_attributes'].variables['clon'][:]
    
    distance = (np.abs(clat - target[0]) ** 2 + np.abs(clon - target[1]) ** 2)
    x = np.unravel_index(distance.argmin(), distance.shape)[0]

    azimut = (180.0 / pi) * atan2(clon[x] - target[1], clat[x] - target[0])
    if azimut < 0: azimut += 360

    return azimut


def ndvi_pix_data(file, x, y):
    ndvi_band = np.flipud(np.fliplr(file.groups['geophysical_data'].variables['ndvi'][:]))
    ndvi_area = np.zeros((3, 3))
    x, y = x - 1, y - 1

    for i in range(ndvi_area.shape[0]):
        for j in range(ndvi_area.shape[1]):
            ndvi_area[i, j] = ndvi_band[x + i, y + j]
            ndvi_band[x + i, y + j] = 2

    plt.imsave('ndvi_band.png', ndvi_band)

    return np.ravel(ndvi_area)
