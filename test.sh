#!/bin/bash

date="19.06.2020"
exist=$(sqlite3 ndvi_database.db "SELECT * FROM ndvi WHERE date='$date'")

if [ -z "$exist" ]; then
    echo "EMPTY"
else
    echo "NOT EMPTY"
fi
