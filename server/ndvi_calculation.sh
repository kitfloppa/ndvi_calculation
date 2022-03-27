#!/bin/bash

export OCSSWROOT=/home/kitfloppa/ocssw
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

function list_preparation() {
    lcfr_path="../../LCFR"
    lists_path="./lists"

    echo -n > "$lists_path/right_data_list.txt"

    for file in $lcfr_path
    do
        file_name=${file:8}
        grep -h "${file_name:7:4}${file_name:12:3}" "$lists_path/full_data_list.txt" >> "$lists_path/right_data_list.txt"
    done
}
export -f list_preparation

function process_l2() {
    datapath="../../NDVI_Data"
    
    file=$(echo $1|tr -d '\n')
    file=${file::-4}
    oceandata_path="https://oceandata.sci.gsfc.nasa.gov/ob/getfile/$file.PDS"
    
    date_from_nday $file

    if [ ! -d "$datapath/NDVI_($date)" ]; then
        mkdir "$datapath/NDVI_($date)"
        cd "$datapath/NDVI_($date)"/
        mkdir "Data"
        cd "Data/"
    else
        cd "$datapath/NDVI_($date)"/
        
        if [ ! -d "Data" ]; then
            mkdir "Data"
            cd "Data/"
        else
            cd "Data/"
        fi
    fi

    if [ ! -f "$file.L2.nc" ]; then
        curl -O -b ~/.urs_cookies -c ~/.urs_cookies -L -n "$oceandata_path.bz2" > "Download.log" 2>&1
    
        if ! bzip2 -d "$file.PDS.bz2" >> "Download.log" 2>&1 ; then
            mv "$file.PDS.bz2" "$file.PDS.xz"
            xz -d "$file.PDS.xz" >> "Download.log" 2>&1
        fi

        if ! ~/ocssw/bin/modis_L1A "$file.PDS" -o "$file.L1A" -m aqua > "/dev/null" 2>&1 ; then
            echo "$file -> L1A Processing error!"
        fi
        
        if ! ~/ocssw/bin/modis_GEO "$file.L1A" -o "$file.GEO" > "/dev/null" 2>&1 ; then
            echo "$file -> GEO Processing error!"
        fi

        if ! ~/ocssw/bin/modis_L1B "$file.L1A" -o "$file.L1B_1KM" -k "$file.L1B_HKM" -q "$file.L1B_QKM" > "/dev/null" 2>&1 ; then
            echo "$file -> L1B Processing error!"
        fi
        
        if ~/ocssw/bin/l2gen ifile="$file.L1B_1KM" geofile="$file.GEO" ofile="$file.L2.nc" maskland=off resolution=250 l2prod=ndvi > "/dev/null" 2>&1 ; then
            echo "$file -> Processing done!"
            echo "### PROCESSING SUCCESS !!! ###" >> "Download.log" 2>&1
        else
            echo "$file -> Processing error!"
            echo "### PROCESSING ERROR !!! ###" >> "Download.log" 2>&1
        fi

        find . -type f -name 'MCFWrite*' -exec rm -f {} +
        find ../../../LCFR -type f -name "LCFR01_${file:7:4}_${file:11:3}*" -exec cp {} . \;

        rm "$file.PDS" > "/dev/null" 2>&1
        rm "$file.L1A" > "/dev/null" 2>&1
        rm "$file.GEO" > "/dev/null" 2>&1
        rm "$file.L1B_1KM" > "/dev/null" 2>&1
        rm "$file.L1B_HKM" > "/dev/null" 2>&1
        rm "$file.L1B_QKM" > "/dev/null" 2>&1
    fi
}
export -f process_l2

if [ ! -d "../../NDVI_Data" ]; then
    mkdir ../NDVI_Data
fi

list_preparation
parallel -j 8 -a ./lists/right_data_list.txt process_l2
