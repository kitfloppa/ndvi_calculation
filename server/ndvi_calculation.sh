#!/bin/bash

export OCSSWROOT=/home/floppa/ocssw
source $OCSSWROOT/OCSSW_bash.env

function date_from_nday() {
    local i=0
    
    date=${1:7:7}
    
    let day=$((date % 1000))
    local year=${date::-3}
    
    declare -a months
    local months=( 31 28 31 30 31 30 31 31 30 31 30 31)
    local month=${months[i]}

    if [ $((year % 4)) -eq 0 ] && [ ! $((year % 100)) -eq 0 ] || [ $((year % 500)) -eq 0 ]; then
        let months[1]++
    fi

    while [ "$day" -gt "$month" ] 
    do
        let i++
        let day=$day-$month
        month=${months[i]}
    done

    let i++

    if [ "$i" -gt 9 ]; then
        if [ "$day" -gt 9 ]; then
            date="$day.$i.$year"
        else
            date="0$day.$i.$year"
        fi
    else
        if [ "$day" -gt 9 ]; then
            date="$day.0$i.$year"
        else
            date="0$day.0$i.$year"
        fi
    fi
}
export -f date_from_nday

function process_l2() {
    file=$(echo $1|tr -d '\r')
    file=${file::-4}
    date_from_nday $file

    if [ ! -d "../NDVI_Data/NDVI_[$date]" ]; then
        mkdir ../NDVI_Data/"NDVI_[$date]"
        cd ../NDVI_Data/"NDVI_[$date]"/
        mkdir Data
        cd Data/
    else
        cd ../NDVI_Data/"NDVI_[$date]"/
        
        if [ ! -d "Data" ]; then
            mkdir Data
            cd Data/
        else
            cd Data/
        fi
    fi

    if [ ! -f "$file.L2.nc" ]; then
        curl -O -b ~/.urs_cookies -c ~/.urs_cookies -L -n "https://oceandata.sci.gsfc.nasa.gov/ob/getfile/$file.PDS.bz2"
        bzip2 -d "$file.PDS.bz2"

        ~/ocssw/bin/modis_L1A "$file.PDS" -o "$file.L1A" -m aqua
        ~/ocssw/bin/modis_GEO "$file.L1A" -o "$file.GEO"
        ~/ocssw/bin/modis_L1B "$file.L1A" -o "$file.L1B_1KM" -k "$file.L1B_HKM" -q "$file.L1B_QKM"
        ~/ocssw/bin/l2gen ifile="$file.L1B_1KM" geofile="$file.GEO" ofile="$file.L2.nc" maskland=off resolution=250 l2prod=ndvi,Rrs_nnn,chlor_a,aot_nnn,Lt_nnn,Lr_nnn,La_nnn

        find . -type f -name 'MCFWrite*' -exec rm -f {} +
        find ../../../LCFR-2021 -type f -name "LCFR01_${file:7:4}_${file:11:3}*" -exec cp {} . \;

        rm "$file.PDS"
        rm "$file.L1A"
        rm "$file.GEO"
        rm "$file.L1B_1KM"
        rm "$file.L1B_HKM"
        rm "$file.L1B_QKM"
    fi
}
export -f process_l2

if [ ! -d "../NDVI_Data" ]; then
    mkdir ../NDVI_Data
fi

if [ ! -d "../NDVI_Data/Report" ]; then
    mkdir ../NDVI_Data/Report
fi

parallel -j 8 -a data_list.txt process_l2
