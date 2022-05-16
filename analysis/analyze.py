import yaml
import numpy as np
import pandas as pd
import statistics as std
import matplotlib.pyplot as plt

from datetime import date
from matplotlib.backends.backend_pdf import PdfPages


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
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    ax.scatter(x, y, marker='o', s=2, label=r'$R^2 = {}$'.format(r_2))
    ax.plot(x, y_pred, color='g', label=f"a = {b[0]}, \nb = {b[1]}")
    plt.suptitle(f'{title}')
    plt.xlabel('MODIS NDVI')
    plt.ylabel('Station NDVI')
    plt.legend()

    pdf.savefig()
    plt.close()


def add_scatter_plot(x, y, pdf, title, labels):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    ax.scatter(x, y, marker='o', s=2)
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])

    pdf.savefig()
    plt.close()


def add_ndvi_plot(x, data, pdf, title, labels):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    for i, j in zip(data, labels):
        ax.plot(x, i, label=j)

    ax.legend()
    plt.suptitle(f'{title}')
    plt.xlabel('Date')
    plt.ylabel('NDVI')
    
    pdf.savefig()
    plt.close()


def ndvi_filter(dates, satellite_ndvi, in_situ_ndvi):
    filtered_ndvi, filtered_in_situ, filtered_dates, error = [], [], [], []

    for i, m_ndvi in enumerate(satellite_ndvi):
        error.append(np.fabs(m_ndvi - in_situ_ndvi[i]) / np.fabs(in_situ_ndvi[i]))

    stddev = std.pstdev(error)

    for i, value in enumerate(error):
        if value < (2 * stddev):
            filtered_dates.append(dates[i])
            filtered_ndvi.append(satellite_ndvi[i])
            filtered_in_situ.append(in_situ_ndvi[i])

    return filtered_dates, filtered_ndvi, filtered_in_situ


if __name__ == "__main__":
    pdf = PdfPages('Analyze.pdf')

    with open('data.yaml', 'r') as inp:
        data = yaml.load(inp, Loader=yaml.Loader)

    ndvi, fitches, years = data[0], data[1], data[2]
    water_vapor = {key: value[1] for key, value in fitches.items()}
    solar_zen = {key: value[3] for key, value in fitches.items()}
    angles = {key: np.fabs(value[0] - value[2]) for key, value in fitches.items()}

    ndvi, angles, water_vapor, solar_zen = sorted(ndvi.items()), sorted(angles.items()), sorted(water_vapor.items()), sorted(solar_zen.items())
    ndvi_keys, ndvi = zip(*ndvi)
    angles_keys, angles = zip(*angles)
    solar_zen_keys, solar_zen = zip(*solar_zen)
    water_vapor_keys, water_vapor = zip(*water_vapor)

    ndvi = np.array(ndvi)
    
    data = {'date': ndvi_keys, 'modis_ndvi': ndvi[:, 0], 'mc_station_ndvi': ndvi[:, 1], 'sc_station_ndvi': ndvi[:, 2], 'l8_station_ndvi': ndvi[:, 3], 
            'l9_station_ndvi': ndvi[:, 4], 'kv_station_ndvi': ndvi[:, 5], 'angle': angles, 'water_vapor': water_vapor, 'solar_zen': solar_zen}

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    data_plot = [df['mc_station_ndvi'].values, df['sc_station_ndvi'].values, df['l8_station_ndvi'].values, df['l9_station_ndvi'].values, df['kv_station_ndvi'].values]
    lables_plot = ['Station NDVI in MODIS channels', 'Station NDVI in standard channels', 'Station NDVI in Landsat 8 channels', 'Station NDVI in Landsat 9 channels', 'Station NDVI in Kanopus channels']
    add_ndvi_plot(df['date'].values, data_plot, pdf, 'NDVI 2015-2021', lables_plot)

    for i in sorted(years):
        year_df = df.query(f'date.dt.year=={i}')

        data_plot = [year_df['mc_station_ndvi'].values, year_df['sc_station_ndvi'].values, year_df['l8_station_ndvi'].values, year_df['l9_station_ndvi'].values, year_df['kv_station_ndvi'].values]
        add_ndvi_plot(year_df['date'].values, data_plot, pdf, f'NDVI {i}', lables_plot)
    
    filtered_dates, modis_ndvi, station_ndvi = ndvi_filter(df['date'].values, df['modis_ndvi'].values, df['mc_station_ndvi'].values)
    add_ndvi_plot(filtered_dates, [modis_ndvi, station_ndvi], pdf, 'NDVI 2015-2021 in MODIS channels', ['MODIS NDVI', 'Station NDVI in MODIS channels'])
    add_regression_plot(np.array(modis_ndvi), np.array(station_ndvi), pdf, 'Linear regression 2015-2021 in MODIS channels')

    for i in sorted(years):
        year_df = df.query(f'date.dt.year=={i}')

        filtered_dates, modis_ndvi, station_ndvi = ndvi_filter(year_df['date'].values, year_df['modis_ndvi'].values, year_df['mc_station_ndvi'].values)
        add_ndvi_plot(filtered_dates, [modis_ndvi, station_ndvi], pdf, f'NDVI {i} in MODIS channels', ['MODIS NDVI', 'Station NDVI in MODIS channels'])
        add_regression_plot(np.array(modis_ndvi), np.array(station_ndvi), pdf, f'Linear regression {i} in MODIS channels')

    filtered_dates, modis_ndvi, station_ndvi = ndvi_filter(df['date'].values, df['modis_ndvi'].values, df['sc_station_ndvi'].values)
    add_ndvi_plot(filtered_dates, [modis_ndvi, station_ndvi], pdf, 'NDVI 2015-2021 in standart channels', ['MODIS NDVI', 'Station NDVI in standard channels'])
    add_regression_plot(np.array(modis_ndvi), np.array(station_ndvi), pdf, 'Linear regression 2015-2021 in standart channels')

    for i in sorted(years):
        year_df = df.query(f'date.dt.year=={i}')

        filtered_dates, modis_ndvi, station_ndvi = ndvi_filter(year_df['date'].values, year_df['modis_ndvi'].values, year_df['sc_station_ndvi'].values)
        add_ndvi_plot(filtered_dates, [modis_ndvi, station_ndvi], pdf, f'NDVI {i} in standart channels', ['MODIS NDVI', 'Station NDVI in standard channels'])
        add_regression_plot(np.array(modis_ndvi), np.array(station_ndvi), pdf, f'Linear regression {i} in standart channels')

    df = df.query('water_vapor<9999')
    
    error = np.fabs(df['modis_ndvi'].values - df['mc_station_ndvi'].values) / np.fabs(df['mc_station_ndvi'].values)
    water_vapor = df['water_vapor'].values
    solar_zen = df['solar_zen'].values
    angle = df['angle'].values

    add_scatter_plot(error, water_vapor, pdf, 'Water vapor dependence of the NDVI', ['Error', 'Water vapor'])
    add_scatter_plot(error, angle, pdf, 'Angle difference dependence of the NDVI', ['Error', 'Angle difference'])
    add_scatter_plot(error, solar_zen, pdf, 'Solar zenith dependence of the NDVI', ['Error', 'Solar zenith'])

    pdf.close()
