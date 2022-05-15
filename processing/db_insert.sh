#!/bin/bash

source ../.env/bin/activate

count=0

for i in /mnt/e/NDVI_Data/* ; do
    file=$(find $i -name "*.nc")
    name=$(basename $file)

    year=${name:7:4}
    nday=${name:11:3}

    find "LCFR" -name "LCFR01_${year}_${nday}*" | xargs python "db_recording.py" "$file"
    let count++

    echo "Record $count done !"
    echo

done
