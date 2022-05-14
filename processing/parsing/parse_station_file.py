import datetime as dt


aerosol_types = {'R': '?', 'C': '?', 'D': 'Desert', 'M': 'Marine'}


def find_station_time(modis_time, station_time):
    modis_time = min_time = dt.timedelta(hours=modis_time.hour, minutes=modis_time.minute).total_seconds()
    item = 0

    for i, s_time in enumerate(station_time):
        s_time = dt.timedelta(hours=s_time.hour, minutes=s_time.minute)
        if min_time > abs(modis_time - s_time.total_seconds()):
            min_time = abs(modis_time - s_time.total_seconds())
            item = i

    return item


def block_iter(lineiter):
    block = []
    
    for line in lineiter:
        if line.strip() == '':
            if block:
                yield block
            block = []
        else:
            block.append(line.rstrip().split('\t'))

    if block:
        yield block


def parse_metadata_block(block):
    meta = {key.rstrip(':'): val for key, val in block}
    meta['Site'] = meta['Site'].strip()
    
    assert len(meta['Site']) == 6, 'Invalid site name'
    
    for float_field in ['Lat', 'Lon', 'Alt']:
        meta[float_field] = float(meta[float_field])
    
    return meta


def read_data_subblock(line_iter, last_header):
    rows = {}
    
    for head, *vals in line_iter:
        head = head.rstrip(':')
        rows[head] = vals
        if head == last_header:
            break
    
    return rows


def read_times_subblock(line_iter):
    rows = read_data_subblock(line_iter, 'Local')
    times = []
    
    for utc_time in rows['UTC']:
        times.append(dt.time.fromisoformat(utc_time))
    
    return times


def read_weather_subblock(line_iter):
    rows = read_data_subblock(line_iter, 'Ang')
    
    for key in ['P', 'T', 'WV', 'O3', 'AOD', 'Ang']:
        rows[key] = [float(val) for val in rows[key]]
    
    return rows

def read_angle_subblock(data, line_iter):
    rows = read_data_subblock(line_iter, 'esd')
    
    for key in ['Zen', 'Azi', 'esd']:
        data[key] = [float(val) for val in rows[key]]


def read_srf_subblock(line_iter):
    rows = {}
    
    for head, *vals in line_iter:
        rows[int(head)] = [float(x) for x in vals]
    
    return rows


def read_types_line(line_iter):
    head, *vals = next(line_iter)
    
    assert head == 'Type:', 'Unexpected header, ' + head
    
    for val in vals:
        assert val in aerosol_types, 'Unexpected Aerosol type: ' + val
    
    return vals


def parse_main_data_block(block, file_type):
    lineiter = iter(block)
    times = read_times_subblock(lineiter)
    weather = read_weather_subblock(lineiter)
    weather['Type'] = read_types_line(lineiter)

    if file_type != 'input':
        read_angle_subblock(weather, lineiter)

    srf = read_srf_subblock(lineiter)
    
    return times, weather, srf


def parse_errors_data_block(block):
    lineiter = iter(block)
    weather_errs = read_weather_subblock(lineiter)
    srf_errs = read_srf_subblock(lineiter)
    
    return weather_errs, srf_errs


def read_station_file(file, file_type='input'):
    if isinstance(file, str):
        file = open(file, 'rt')
    blockiter = iter(block_iter(file))

    metadata = parse_metadata_block(next(blockiter))
    times, weather, srf = parse_main_data_block(next(blockiter), file_type)
    
    return times, weather, srf