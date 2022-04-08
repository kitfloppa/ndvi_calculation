import sys
import numpy as np
import netCDF4 as nc
import sqlite3 as sl

from Point import Point as pn
from parsing.parse_modis_file import *
from parsing.parse_station_file import read_file, find_station_time


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
        