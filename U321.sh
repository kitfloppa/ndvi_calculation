
file=$1

cd ../NDVI_Data/"NDVI_[06.01.2021]"/Data

find ../../../LCFR-2021 -type f -name "LCFR01_${file:7:4}_${file:11:3}*" -exec cp {} . \;