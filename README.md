[![Download Aqua/MODIS data](https://i.ibb.co/tM6Jvd5/Screenshot-2022-04-08-223819.png)](https://oceancolor.gsfc.nasa.gov/cgi/browse.pl) 
[![Download RadCalNet data](https://www.radcalnet.org/modules/core/img/header/RADCALNET-LOGO-COMPLET.png)](https://www.radcalnet.org/#!/)

# Investigation of the accuracy of NDVI calculations

## Installation Python packages

```bash
python -m venv .env
source .env/bin/activate

pip install netCDF4
pip install matplotlib
pip install statistics
```

## Installation OCCSW

Install [OCSSW](https://seadas.gsfc.nasa.gov/downloads/) for processing satellite data to L2.

## Aqua/MODIS data

Aqua/MODIS satellite data was downloaded from [NASA Ocean Color](https://oceancolor.gsfc.nasa.gov/cgi/browse.pl) 

## RadCalNet data

Bottom Of Atmosphere (BOA) reflectance data was downloaded from [RadCalNet](https://www.radcalnet.org/#!/) (You need to send a request for access to the data)
