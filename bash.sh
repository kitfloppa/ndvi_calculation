#!/bin/bash

export OCSSWROOT=/home/kitfloppa/ocssw
source $OCSSWROOT/OCSSW_bash.env

file=$1
path="/mnt/d/Andrey/FEFU/Dissertation/Data/MODIS_ndvi_250"

curl -O -b ~/.urs_cookies -c ~/.urs_cookies -L -n "https://oceandata.sci.gsfc.nasa.gov/ob/getfile/$file.bz2"
bzip2 -d "$file.bz2"

~/ocssw/bin/modis_L1A "$file" -o "$path/$file.L1A" -m aqua
~/ocssw/bin/modis_GEO "$path/$file.L1A" -o "$path/$file.GEO"
~/ocssw/bin/modis_L1B "$path/$file.L1A" -o "$path/$file.L1B_1KM" -k "$path/$file.L1B_HKM" -q "$path/$file.L1B_QKM"
~/ocssw/bin/l2gen ifile="$path/$file.L1B_1KM" geofile="$path/$file.GEO" ofile="$path/$file.L2" maskland=off resolution=250 l2prod=ndvi

rm "$path/$file.L1A"
rm "$path/$file.GEO"
rm "$path/$file.L1B_1KM"
rm "$path/$file.L1B_HKM"
rm "$path/$file.L1B_QKM"