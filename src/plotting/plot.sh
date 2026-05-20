#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "Error: No arguments provided. First argument must be the number of the data profile. Ex. verify path '../../data/profile/profiles_[number].dat' and use plot.sh [number]"
    echo "Optional argument: hex_code for color of density plot."
    echo "Optional argument: hex_code for color of temperature plot "
    exit 1
fi

path=../../data/profile/profiles_$1.dat

if [ "$#" -eq 1 ]; then
    color1="#B00000"
    color2="#0A36AF"
elif [ "$#" -eq 2]; then
    color1=$2
    color2="#0A36AF"
else
    color1=$2
    color2=$3
fi

gnuplot -c density.gnu density_profile_$1.tex $path $color1
gnuplot -c temperature.gnu temperature_profile_$1.tex $path $color2

echo "Plot saved. PATH: ../../plots"
exec > /dev/null 2>&1

pdflatex density_profile_$1.tex
pdflatex temperature_profile_$1.tex

rm *.tex *.aux *.log *.eps density_profile_$1-* temperature_profile_$1-*

mv *pdf ../../plots
