#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Error: No filepath to parameters file provided. Ex. verify path '../../params/[param file] and use plot [param file] [number]'"
    echo "Error: No arguments provided. Second argument must be the number of the data profile. Ex. verify path '../../data/profile/profiles_[number].dat' and use plot.sh [param file] [number]"
    echo "Optional argument: hex_code for color of density plot."
    echo "Optional argument: hex_code for color of temperature plot "
    exit 1
fi

export hidden_layers=$(yq '.hidden_layers' ../../parameters/$1)
export num_domain=$(yq '.model_params.NUM_DOMAIN' ../../parameters/$1)
export loss_weights=$(yq '.model_params.LOSS_WEIGHTS' ../../parameters/$1)
export iter1=$(yq '.model_params.ADAM_ITER1' ../../parameters/$1)
export iter2=$(yq '.model_params.ADAM_ITER2' ../../parameters/$1)

path=../../data/profile/profiles_$2.dat

if [ "$#" -eq 2 ]; then
    color1="#B00000"
    color2="#0A36AF"
elif [ "$#" -eq 3 ]; then
    color1=$4
    color2="#0A36AF"
else
    color1=$3
    color2=$4
fi

gnuplot -c density.gnu density_profile_$2.tex $path $color1 "$hidden_layers" "$num_domain" "$loss_weights" "$iter1" "$iter2"
gnuplot -c temperature.gnu temperature_profile_$2.tex $path $color2 "$hidden_layers" "$num_domain" "$loss_weights" "$iter1" "$iter2"

echo "Plot saved. PATH: ../../plots"
#exec > /dev/null 2>&1

pdflatex density_profile_$2.tex
pdflatex temperature_profile_$2.tex

rm *.tex *.aux *.log *.eps density_profile_$2-* temperature_profile_$2-*

mv *pdf ../../plots
