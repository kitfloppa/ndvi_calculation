import os
import sys
import numpy as np
import netCDF4 as nc
import sqlite3 as sl

from Point import Point as pn
from parsing.parse_modis_file import *
from parsing.parse_station_file import *


def ndvi_calculation(red_channel, nir_chanel):
    return (nir_chanel - red_channel) / (nir_chanel + red_channel)


if __name__ == "__main__":
    modis_file = sys.argv[1]
    station_file_input = sys.argv[2]
    station_file_output = sys.argv[3]
    
    # Read input station file
    analyzed_date, modis_time = date_from_modis_filename(os.path.basename(modis_file))
    station_time, station_weather, station_data = read_station_file(station_file_input)
    station_item_time = find_station_time(modis_time, station_time)
    station_time = station_time[station_item_time]
    water_vapor = station_weather['WV'][station_item_time]

    # Read output station file
    output_time, output_weather, output_data = read_station_file(station_file_output, 'output')
    solar_azimut = output_weather['Azi'][station_item_time]
    solar_zenith = output_weather['Zen'][station_item_time]
    
    # La Crau station coordinates
    latitude = 43.55885
    longitude = 4.864472

    target = pn(latitude, longitude)
    modis_file = nc.Dataset(modis_file, "r", format="NETCDF4")
    
    modis_azimut = get_satellite_azimut(modis_file, target)
    i, j = get_pixn_ndvi(modis_file, target)

    if solar_azimut < 0: solar_azimut += 360

    if not (i == -1 and j == -1):
        modis_ndvi = ndvi_pix_data(modis_file, i, j)

        mc_station_ndvi = ndvi_calculation(station_data[640][station_item_time], station_data[860][station_item_time])  # Modis channels
        sc_station_ndvi = ndvi_calculation(station_data[670][station_item_time], station_data[800][station_item_time])  # Standard channels
        l8_station_ndvi = ndvi_calculation(station_data[660][station_item_time], station_data[870][station_item_time])  # Landsat 8 channels
        l9_station_ndvi = ndvi_calculation(station_data[660][station_item_time], station_data[840][station_item_time])  # Landsat 9 channels
        kv_station_ndvi = ndvi_calculation(station_data[670][station_item_time], station_data[800][station_item_time])  # Kanopus-V channels
        
        station_ndvi = np.array([mc_station_ndvi, sc_station_ndvi, l8_station_ndvi, l9_station_ndvi, kv_station_ndvi])
        
        with open('ndvi_band.png', 'rb') as pic:
            ndvi_band = pic.read()
        
        try:
            sl_connection = sl.connect("../../../ndvi_database.db", detect_types=sl.PARSE_DECLTYPES)
            cursor = sl_connection.cursor()

            cursor.execute("INSERT INTO ndvi VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (analyzed_date, str(modis_time), 
                                                                                    modis_ndvi, sl.Binary(ndvi_band), 
                                                                                    modis_azimut, str(station_time), 
                                                                                    station_ndvi, water_vapor,
                                                                                    solar_azimut, solar_zenith))

            sl_connection.commit()

        except sl.Error as error:
            print("Error", error)
        finally:
            if (sl_connection):
                sl_connection.close()
