import sys
import numpy as np
import netCDF4 as nc
import statistics as std
import matplotlib.pyplot as plt

from Point import Point as pn
from matplotlib.backends.backend_pdf import PdfPages

def add_plot(x, y, pdf):
    plt.figure()
    plt.clf()
    plt.plot(x, y)
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    
    pdf.savefig()

def datetime_from_nday(file_name):
    i = 0
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    month = months[i]
    date = file_name[7:14]
    time = file_name[15:17] + '-' + file_name[17:19]
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

    return date, time


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
    plt.imshow(ndvi_area)
    print(x, y)
    plt.show()

    return np.ravel(ndvi_area)

if __name__ == "__main__":
    # La Crau station coordinates
    latitude = 43.55885
    longitude = 4.864472

    target = pn(latitude, longitude)

    pdf = PdfPages('../NDVI_Data/Report/Research.pdf')
    dates, ndvi_data = [], []
    
    with open(sys.argv[1], 'r') as file:
        files_name = file.readlines()

    for name in files_name:
        name = name.replace('\n', '')
        name = name.replace('PDS', 'L2.nc')

        date, time = datetime_from_nday(name)
        dates.append(date)
        path = '../NDVI_Data/NDVI_' + '[' + date + ']' + '[' + time + ']' + '/'
        
        file = nc.Dataset(path + 'Data/' + name, "r", format="NETCDF4")
        i, j = get_pixn_ndvi(file, target)
        lacrau_ndvi = ndvi_pix_data(file, path, i, j)

        ndvi_mean = std.fmean(lacrau_ndvi)
        ndvi_data.append(ndvi_mean)
        ndvi_deviation = std.pstdev(lacrau_ndvi)

        with open(path + 'Report.txt', 'w') as file:
            file.write('Mean = ' + str(ndvi_mean) + '\n' + 'Deviation = ' + str(ndvi_deviation))

    add_plot(dates, ndvi_data, pdf)
    pdf.close()
