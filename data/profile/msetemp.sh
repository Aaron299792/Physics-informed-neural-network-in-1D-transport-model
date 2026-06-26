#!/bin/bash

touch tmp tmp1 msetemp.dat

for f in 20260623*.dat; do
  awk '
    FNR==NR { if (!/^#/) ref[++refline] = $3; next }
    !/^#/   { print ($3 - ref[++datline]) * ($3 - ref[++datline])}
  ' avg_shots.dat "$f" > "sqsubs${f}"
done

paste sqsubs* > tmp

awk '{for (i=1; i<=NF; i++) sum[i] += $i} END {for (i=1; i<=NF; i++) printf "%f%s", sum[i]/40, (i==NF ? ORS : OFS)}' tmp > tmp1

awk '{for(i=1; i<=9; i++) print $i}' tmp1 > msetemp.dat

rm sqsubs* tmp tmp1
