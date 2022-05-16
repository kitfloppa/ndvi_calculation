import yaml
import numpy as np
import sqlite3 as sl
import statistics as std

from datetime import date

if __name__ == "__main__":
    try:
        ndvi, fitches = {}, {}
        years = set()
        
        sl_connection = sl.connect("../ndvi_database.db", detect_types=sl.PARSE_DECLTYPES)
        cursor = sl_connection.cursor()
        cursor.execute("SELECT date, modis_ndvi_data, station_ndvi_data, modis_azimut, station_wv, station_solar_az, station_solar_zen FROM ndvi")

        while True:
            row = cursor.fetchone()
            if row:
                ndvi[row[0]] = np.insert(np.frombuffer(row[2]), 0, std.fmean(np.frombuffer(row[1])))
                fitches[row[0]] = np.array([row[3], row[4], row[5], row[6]])
                years.add(date.fromisoformat(row[0]).year)
            else:
                break

        data = [ndvi, fitches, years]

        with open('data.yaml', 'w') as out:
            yaml.dump(data, out)

    except sl.Error as error:
        print("Error", error)
    finally:
        if (sl_connection):
            sl_connection.close()
