import numpy as np
import sqlite3 as sl
import statistics as std
import matplotlib.pyplot as plt

from datetime import date
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages


def add_fitch_plot(x, y, w, z, pdf, title):
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), dpi=150)

    ax[0].scatter(x, y, marker='o')
    ax[1].scatter(w, z, marker='o')
    plt.suptitle(f'{title}')

    pdf.savefig()
    plt.close()


def add_ndvi_plot(x, y, z, pdf, title, channel):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    ax.plot(x, y, label='MODIS NDVI')
    ax.plot(x, z, label=f'Station NDVI in {channel} channels')
    ax.legend()
    plt.suptitle(f'{title}')
    plt.xlabel('Date')
    plt.ylabel('NDVI')
    
    pdf.savefig()
    plt.close()

def r2(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
    
    return r_squared


def estimate_coeff(x, y):
    n = len(x)

    mean_x, mean_y = np.mean(x), np.mean(y)
    ssxy = np.sum(y * x - n * mean_y * mean_x)
    ssxx = np.sum(x * x - n * mean_x * mean_x)

    b_1 = ssxy / ssxx
    b_0 = mean_y - (b_1 * mean_x)

    return (b_0, b_1)


def add_regression_plot(x, y, pdf, title):
    b = estimate_coeff(x, y)
    r_2 = r2(x.astype('float64'), y.astype('float64'))
    y_pred = b[0] + b[1] * x
    patch = mpatches.Patch(label=r'$R^2 = {}$'.format(r_2))
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    ax.scatter(x, y, marker='o')
    ax.plot(x, y_pred, color='g')
    ax.legend(handles=[patch])
    plt.suptitle(f'{title}')
    plt.xlabel('MODIS NDVI')
    plt.ylabel('Station NDVI')

    pdf.savefig()
    plt.close()


def ndvi_filter(dates, modis_ndvi, station_ndvi, fithes):
    error, filter_dates, filtered_modis_ndvi, filtered_station_ndvi, filtered_fithes = [], [], [], [], []
    error_date = []

    for i, m_ndvi in enumerate(modis_ndvi):
        error.append(abs(m_ndvi - station_ndvi[i]) / abs(station_ndvi[i]))

    mc_mean = std.fmean(error)

    for i, error in enumerate(error):
        if error < (2 * mc_mean):
            filter_dates.append(dates[i])
            filtered_modis_ndvi.append(modis_ndvi[i])
            filtered_station_ndvi.append(station_ndvi[i])
            filtered_fithes.append(fithes[i])
        else:
            error_date.append((dates[i], modis_ndvi[i], station_ndvi[i]))

    print(error_date)
    return np.array([filter_dates, filtered_modis_ndvi, filtered_station_ndvi, filtered_fithes])


def filtered_dict(dict):
    dict = sorted(dict.items())
    adates_key, ndvi = zip(*dict)
    dates, modis_ndvi, mc_station_ndvi, sc_station_ndvi, fithes = [], [], [], [], []

    for i, ndvi_data in enumerate(ndvi):
        dates.append(date.fromisoformat(adates_key[i]))
        modis_ndvi.append(ndvi_data[0])
        mc_station_ndvi.append(ndvi_data[1])
        sc_station_ndvi.append(ndvi_data[4])
        fithes.append(np.array([ndvi_data[5], ndvi_data[6], ndvi_data[7]]))

    return ndvi_filter(dates, modis_ndvi, mc_station_ndvi, fithes), ndvi_filter(dates, modis_ndvi, sc_station_ndvi, fithes)


def ndvi_for_year(mc_pack, sc_pack, year):
    mc_date, mc_modis_ndvi, mc_station_ndvi = [], [], []
    sc_date, sc_modis_ndvi, sc_station_ndvi = [], [], []
    
    for i, date in enumerate(mc_pack[0]):
        if date.year == year:
           mc_date.append(date)
           mc_modis_ndvi.append(mc_pack[1][i])
           mc_station_ndvi.append(mc_pack[2][i])

    for i, date in enumerate(sc_pack[0]):
        if date.year == year:
           sc_date.append(date)
           sc_modis_ndvi.append(sc_pack[1][i])
           sc_station_ndvi.append(sc_pack[2][i])

    return np.array([mc_date, mc_modis_ndvi, mc_station_ndvi]), np.array([sc_date, sc_modis_ndvi, sc_station_ndvi])


if __name__ == "__main__":
    pdf = PdfPages('Analyze.pdf')
    
    try:
        ndvi = {}
        years = set()
        
        sl_connection = sl.connect("../ndvi_database.db", detect_types=sl.PARSE_DECLTYPES)
        cursor = sl_connection.cursor()
        cursor.execute("SELECT date, modis_ndvi_data, station_ndvi_data, modis_azimut, station_wv, station_solar_az FROM ndvi")

        while True:
            row = cursor.fetchone()
            if row:
                ndvi[row[0]] = np.insert(np.frombuffer(row[2]), 0, std.fmean(np.frombuffer(row[1])))
                ndvi[row[0]] = np.insert(ndvi[row[0]], 5,  np.array([float(row[3]), float(row[4]), float(row[5])]))
                years.add(date.fromisoformat(row[0]).year)
            else:
                break

        years = sorted(years)
        water_vapor, angles = {}, {}
        mc_filtered, sc_filtered = filtered_dict(ndvi)
        
        for i in range(mc_filtered[1].shape[0]):
            if mc_filtered[3][i][1] != 9999.0:
                water_vapor[np.fabs(mc_filtered[1][i] - mc_filtered[2][i]) / mc_filtered[2][i]] = mc_filtered[3][i][1]
            
            if mc_filtered[3][i][0] != float('nan'):
                if mc_filtered[3][i][2] < 0: mc_filtered[3][i][2] += 360
                angles[np.fabs(mc_filtered[1][i] - mc_filtered[2][i]) / mc_filtered[2][i]] = np.fabs(mc_filtered[3][i][0] - mc_filtered[3][i][2])

        #add_ndvi_plot(mc_filtered[0], mc_filtered[1], mc_filtered[2], pdf, 'NDVI 2015-2021 in MODIS channels', 'MODIS')
        #add_ndvi_plot(sc_filtered[0], sc_filtered[1], sc_filtered[2], pdf, 'NDVI 2015-2021 in standart channels', 'standard')
        
        #add_regression_plot(mc_filtered[1], mc_filtered[2], pdf, 'Linear regression 2015-2021 in MODIS channels')
        #add_regression_plot(sc_filtered[1], sc_filtered[2], pdf, 'Linear regression 2015-2021 in standart channels')

        water_vapor = sorted(water_vapor.items(), key=lambda x: x[0])
        water_vapor_key, water_vapor_val = zip(*water_vapor)

        angles = sorted(angles.items(), key=lambda x: x[0])
        angles_key, angles_val = zip(*angles)
        
        add_fitch_plot(water_vapor_key, water_vapor_val, angles_key, angles_val, pdf, 'Error from WV and angles')

        #for year in years:
            #mc_year, sc_year = ndvi_for_year(mc_filtered, sc_filtered, year)

            #add_ndvi_plot(mc_year[0], mc_year[1], mc_year[2], pdf, f'NDVI {year} in MODIS channels', 'MODIS')
            #add_ndvi_plot(sc_year[0], sc_year[1], sc_year[2], pdf, f'NDVI {year} in standart channels', 'standard')
            
            #add_regression_plot(mc_year[1], mc_year[2], pdf, f'Linear regression {year} in MODIS channels')
            #add_regression_plot(sc_year[1], sc_year[2], pdf, f'Linear regression {year} in standart channels')

    except sl.Error as error:
        print("Error", error)
    finally:
        if (sl_connection):
            sl_connection.close()
        
    pdf.close()
