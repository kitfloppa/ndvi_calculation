#!/bin/bash

export OCSSWROOT=/home/kitfloppa/ocssw
source $OCSSWROOT/OCSSW_bash.env

function process_l2() {
    file=$(echo $1|tr -d '\r')
    mkdir ../Data/"${file::-4}"
    cd ../Data/"${file::-4}"

    curl -O -b ~/.urs_cookies -c ~/.urs_cookies -L -n "https://oceandata.sci.gsfc.nasa.gov/ob/getfile/$file.bz2"
    bzip2 -d "$file.bz2"

    ~/ocssw/bin/modis_L1A "$file" -o "$file.L1A" -m aqua
    ~/ocssw/bin/modis_GEO "$file.L1A" -o "$file.GEO"
    ~/ocssw/bin/modis_L1B "$file.L1A" -o "$file.L1B_1KM" -k "$file.L1B_HKM" -q "$file.L1B_QKM"
    ~/ocssw/bin/l2gen ifile="$file.L1B_1KM" geofile="$file.GEO" ofile="$file.L2" maskland=off resolution=250 l2prod=ndvi

    find . -type f -name 'MCFWrite*' -exec rm -f {} +

    rm "$file"
    rm "$file.L1A"
    rm "$file.GEO"
    rm "$file.L1B_1KM"
    rm "$file.L1B_HKM"
    rm "$file.L1B_QKM"
}
export -f process_l2

parallel -j 8 -a test.txt process_l2
