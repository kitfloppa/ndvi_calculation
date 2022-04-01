import datetime as dt


aerosol_types = {'R': '?', 'C': '?', 'D': 'Desert', 'M': 'Marine'}


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


def parse_main_data_block(block):
    lineiter = iter(block)
    times = read_times_subblock(lineiter)
    weather = read_weather_subblock(lineiter)
    weather['Type'] = read_types_line(lineiter)
    srf = read_srf_subblock(lineiter)
    
    return times, weather, srf


def parse_errors_data_block(block):
    lineiter = iter(block)
    weather_errs = read_weather_subblock(lineiter)
    srf_errs = read_srf_subblock(lineiter)
    
    return weather_errs, srf_errs


def read_file(file):
    if isinstance(file, str):
        file = open(file, 'rt')
    blockiter = iter(block_iter(file))

    metadata = parse_metadata_block(next(blockiter))
    times, weather, srf = parse_main_data_block(next(blockiter))
    weather_errs, srf_errs = parse_errors_data_block(next(blockiter))
    
    return times, srf