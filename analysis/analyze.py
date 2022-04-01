import os
import sys
import numpy as np
import netCDF4 as nc
import seaborn as sns
import statistics as std
import matplotlib.dates as mlt
import matplotlib.pyplot as plt

from processing.Point import Point as pn
from parse_station_file import read_file
from classes.NDVI_Data import NDVI_Data as nd
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages


def find_file(path, extension):
    for file in os.listdir(path):
        if file.endswith('.' + extension):
            return os.path.join(path, file)


def station_ndvi(srf):
    return (srf[860][0] - srf[650][0]) / (srf[860][0] + srf[650][0])


def regression(x, y, z, pdf):
    x = mlt.date2num(x)
    
    sns.regplot(x, y, color='blue', marker='+')
    sns.regplot(x, z, color='magenta', marker='+')

    pdf.savefig()


def add_plot(x, y, z, pdf):
    plt.figure()
    plt.clf()
    plt.plot(x, y, x, z)
    plt.xlabel('data axis')
    plt.ylabel('ndvi axis')
    
    pdf.savefig()


def date_from_nday(file_name):
    i = 0
    
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    month = months[i]
    
    date = file_name[7:14]
    year = int(file_name[7:11])
    day = int(file_name[11:14])
    
    if ((year % 4 == 0) and (not (year % 100 == 0))) or (year % 400 == 0):
        months[1] += 1

    while day > month:
        i += 1
        day -= month
        month = months[i]

    i += 1

    if (day > 9):
        if (i > 9):
            date = str(day) + '.' + str(i) + '.' + str(year)
        else:
            date = str(day) + '.0' + str(i) + '.' + str(year)
    else:
        if (i > 9):
            date = '0' + str(day) + '.' + str(i) + '.' + str(year)
        else:
            date = '0' + str(day) + '.0' + str(i) + '.' + str(year)

    return date


def get_pixn_ndvi(file, target):
    lati = np.flipud(np.fliplr(file.groups['navigation_data'].variables['latitude'][:]))
    long = np.flipud(np.fliplr(file.groups['navigation_data'].variables['longitude'][:]))

    distance = np.abs(lati - target[0]) ** 2 + np.abs(long - target[1]) ** 2
    i, j = np.unravel_index(distance.argmin(), distance.shape)

    return i, j


def ndvi_pix_data(file, path, x, y):
    ndvi_band = np.flipud(np.fliplr(file.groups['geophysical_data'].variables['ndvi'][:]))
    ndvi_area = np.zeros((3, 3))
    x, y = x - 1, y - 1

    for i in range(ndvi_area.shape[0]):
        for j in range(ndvi_area.shape[1]):
            ndvi_area[i, j] = ndvi_band[x + i, y + j]
            ndvi_band[x + i, y + j] = 2

    plt.imsave(path + 'ndvi_band.png', ndvi_band)

    return np.ravel(ndvi_area)


if __name__ == "__main__":
    # La Crau station coordinates
    latitude = 43.55885
    longitude = 4.864472

    target = pn(latitude, longitude)
    dates, modis_ndvi_data, station_ndvi_data, ndvi_files = [], [], [], []

    pdf = PdfPages('../NDVI_Data/Report/Research.pdf')
    
    with open(sys.argv[1], 'r') as file:
        files_name = file.readlines()

    for name in files_name:
        name = name.replace('\n', '')
        name = name.replace('PDS', 'L2.nc')

        nday = int(name[11:14])
        date = date_from_nday(name)
        path = '../NDVI_Data/NDVI_' + '[' + date + ']' + '/'
        date = datetime.strptime(date, '%d.%m.%Y').date()
        
        srf = read_file(find_file(path + 'Data', 'input'))
        file = nc.Dataset(path + 'Data/' + name, "r", format="NETCDF4")
        i, j = get_pixn_ndvi(file, target)
        lacrau_ndvi = ndvi_pix_data(file, path, i, j)

        modis_ndvi_mean = std.fmean(lacrau_ndvi)
        modis_ndvi_deviation = std.pstdev(lacrau_ndvi)

        print(mlt.date2num(date))
        dates.append(date)
        modis_ndvi_data.append(modis_ndvi_mean)
        station_ndvi_data.append(station_ndvi(srf))
        ndvi_files.append(nd(target, nday, date, path + 'Data', lacrau_ndvi))

        with open(path + 'Report.txt', 'w') as file:
            file.write('Mean = ' + str(modis_ndvi_mean) + '\n' + 'Deviation = ' + str(modis_ndvi_deviation))

    add_plot(dates, modis_ndvi_data, station_ndvi_data, pdf)
    regression(dates, modis_ndvi_data, station_ndvi_data, pdf)
    pdf.close()
