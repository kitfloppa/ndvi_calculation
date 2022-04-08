#!/bin/bash

export OCSSWROOT=/home/kitfloppa/ocssw
source $OCSSWROOT/OCSSW_bash.env
source ../.env/bin/activate

function date_from_nday() {
    local i=0
    
    date=${1:7:7}
    hh=${1:15:2}
    mm=${1:17:2}
    datetime="${hh}-${mm}"
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
    lists_path="./lists"

    echo -n > "$lists_path/right_data_list.txt"
    echo -n > "$lists_path/intermediate_data_list.txt"

    for i in LCFR/* ; do
        name=$(basename "$i")
        grep -h "${name:7:4}${name:12:3}" "$lists_path/full_data_list.txt" >> "$lists_path/intermediate_data_list.txt"
    done
}
export -f list_preparation

function right_list() {
   cat "$lists_path/intermediate_data_list.txt" | while read line ; do
        f=$(echo $line|tr -d '\n')
        f=${f::-4}
        date_from_nday $f
        db_date="${date:6:4}-${date:3:2}-${date::2}"

        time_exist=$(sqlite3 ../ndvi_database.db "SELECT modis_time FROM ndvi WHERE date='$db_date'")

        if [ "$time_exist" == "${hh}:${mm}:00" ]; then
            echo "$line.PDS" >> "$lists_path/right_data_list.txt"
        fi
    done
}
export -f right_list

function process_l2() {
    datapath="NDVI_Data"
    
    file=$(echo $1|tr -d '\n')
    file=${file::-4}
    oceandata_path="https://oceandata.sci.gsfc.nasa.gov/ob/getfile/$file.PDS"
    
    date_from_nday $file
    year=${file:7:4}
    nday=${file:11:3}
    db_date="${date:6:4}-${date:3:2}-${date::2}"

    exist=$(sqlite3 ../ndvi_database.db "SELECT * FROM ndvi WHERE date='$db_date'")

    if [ -z "$exist" ]; then
        if [ ! -d "$datapath/NDVI_${date}_$datetime" ]; then
            mkdir "$datapath/NDVI_${date}_$datetime"
            cd "$datapath/NDVI_${date}_$datetime"
        fi

        curl -O -b ~/.urs_cookies -c ~/.urs_cookies -L -n --connect-timeout 900 "$oceandata_path.bz2" > "/dev/null" 2>&1
    
        if ! bzip2 -d "$file.PDS.bz2" > "/dev/null" 2>&1 ; then
            mv "$file.PDS.bz2" "$file.PDS.xz" > "/dev/null" 2>&1
            xz -d "$file.PDS.xz" > "/dev/null" 2>&1
        fi

        if ! ~/ocssw/bin/modis_L1A "$file.PDS" -o "$file.L1A" -m aqua > "/dev/null" 2>&1 ; then
            echo "$file -> L1A Processing error!"
        else
            echo "$file -> L1A Processing done!"
        fi
        
        if ! ~/ocssw/bin/modis_GEO "$file.L1A" -o "$file.GEO" > "/dev/null" 2>&1 ; then
            echo "$file -> GEO Processing error!"
        else
            echo "$file -> GEO Processing done!"
        fi
        wait $!

        if ! ~/ocssw/bin/modis_L1B "$file.L1A" -o "$file.L1B_1KM" -k "$file.L1B_HKM" -q "$file.L1B_QKM" > "/dev/null" 2>&1 ; then
            echo "$file -> L1B Processing error!"
        else
            echo "$file -> L1B Processing done!"
        fi
        
        if ~/ocssw/bin/l2gen ifile="$file.L1B_1KM" geofile="$file.GEO" ofile="$file.L2.nc" maskland=off resolution=250 l2prod=ndvi > "/dev/null" 2>&1 ; then
            echo "$file -> L2 Processing done!"
            echo "### PROCESSING SUCCESS !!! ###"
            echo
        else
            echo "$file -> L2 Processing error!"
            echo "### PROCESSING ERROR !!! ###"
            echo
        fi

        find . -type f -name 'MCFWrite*' -exec rm -f {} +

        find "../../LCFR" -name "LCFR01_${year}_${nday}*" | xargs python "../../parse_modis_file.py" "$file.L2.nc"

        cd ..
        rm -rf "NDVI_${date}_$datetime"
    fi
}
export -f process_l2

if [ ! -d "NDVI_Data" ]; then
    mkdir "NDVI_Data"   
fi

if [ ! -f "../ndvi_database.db" ]; then
    sqlite3 "../ndvi_database.db" "CREATE TABLE ndvi(date text, modis_time text, modis_ndvi_data blob, modis_ndvi_band blob, station_time text, 
    station_ndvi_data blob, constraint pk_ndvi primary key (date))"
fi

parallel -j 8 -a "./lists/right_data_list.txt" process_l2
deactivate

rm -rf "NDVI_Data"
