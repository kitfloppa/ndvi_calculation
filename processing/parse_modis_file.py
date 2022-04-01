import os
import sys
import datetime
import numpy as np
import netCDF4 as nc
import sqlite3 as sl
import matplotlib.pyplot as plt

from Point import Point as pn
from parse_station_file import read_file


def find_station_time(modis_time, station_time):
    modis_time = min_time = datetime.timedelta(hours=modis_time.hour, minutes=modis_time.minute).total_seconds()
    item = 0

    for i, s_time in enumerate(station_time):
        s_time = datetime.timedelta(hours=s_time.hour, minutes=s_time.minute)
        if min_time > abs(modis_time - s_time.total_seconds()):
            min_time = abs(modis_time - s_time.total_seconds())
            item = i

    return item


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
            fdate = str(day) + '.' + str(i) + '.' + str(year)
        else:
            fdate = str(day) + '.0' + str(i) + '.' + str(year)
    else:
        if (i > 9):
            fdate = '0' + str(day) + '.' + str(i) + '.' + str(year)
        else:
            fdate = '0' + str(day) + '.0' + str(i) + '.' + str(year)

    return fdate, datetime.time.fromisoformat(ftime)


def get_pixn_ndvi(file, target):
    lati = np.flipud(np.fliplr(file.groups['navigation_data'].variables['latitude'][:]))
    long = np.flipud(np.fliplr(file.groups['navigation_data'].variables['longitude'][:]))

    distance = np.abs(lati - target[0]) ** 2 + np.abs(long - target[1]) ** 2
    i, j = np.unravel_index(distance.argmin(), distance.shape)
    
    if distance.min() > 0.001:
        i, j = -1, -1

    return i, j


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


if __name__ == "__main__":
    modis_file = sys.argv[1]
    station_file = sys.argv[2]
    
    analyzed_date, modis_time = date_from_modis_filename(modis_file)
    station_time, station_data = read_file(station_file)
    station_item_time = find_station_time(modis_time, station_time)
    station_time = station_time[station_item_time]
    
    # La Crau station coordinates
    latitude = 43.55885
    longitude = 4.864472

    # Modis NDVI channels
    modis_red = station_data[640][station_item_time]
    mosid_nir = station_data[860][station_item_time]

    # Standard NDVI channels
    standard_red = station_data[670][station_item_time]
    standard_nir = station_data[800][station_item_time]

    target = pn(latitude, longitude)
    modis_file = nc.Dataset(modis_file, "r", format="NETCDF4")
    i, j = get_pixn_ndvi(modis_file, target)

    if not (i == -1 and j == -1):
        modis_ndvi = ndvi_pix_data(modis_file, i, j)

        mc_station_ndvi = (mosid_nir - modis_red) / (mosid_nir + modis_red)  # Modis channels
        sc_station_ndvi = (standard_nir - standard_red) / (standard_nir + standard_red) # Standard channels
        station_ndvi = np.array([mc_station_ndvi, sc_station_ndvi])
        
        with open('ndvi_band.png', 'rb') as pic:
            ndvi_band = pic.read()
        
        try:
            sl_connection = sl.connect("../../../ndvi_database.db", detect_types=sl.PARSE_DECLTYPES)
            cursor = sl_connection.cursor()

            cursor.execute("INSERT INTO ndvi VALUES (?, ?, ?, ?, ?, ?)", (analyzed_date, str(modis_time), modis_ndvi, sl.Binary(ndvi_band), str(station_time), station_ndvi))
            sl_connection.commit()

        except sl.Error as error:
            print("Error", error)
        finally:
            if (sl_connection):
                sl_connection.close()
        