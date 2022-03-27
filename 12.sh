#!/bin/bash

lcfr_path="../LCFR/*"
lists_path="./server/lists"

echo -n > "$lists_path/right_data_list.txt"

for file in $lcfr_path
do
    file_name=${file:8}
    grep -h "${file_name:7:4}${file_name:12:3}" "$lists_path/full_data_list.txt" >> "$lists_path/right_data_list.txt"
done
