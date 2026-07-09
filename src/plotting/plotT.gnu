set term epslatex standalone color

set output "out.tex"

set multiplot
set size 1,1
set origin 0,0
set label "$R^2 = 0.975$" at graph 0.03, graph 0.05 left
set label "MAE$= 5.03\\times 10^{-2}$" at graph 0.03, graph 0.15 left
set label "MBE $= -3.49\\times 10^{-2}$" at graph 0.03, graph 0.25 left
set border linewidth 5

set yrange [0:1.1]
set ylabel "\\textbf{Temperatura} $\\hat{T}$"
set xlabel "\\textbf{Radio} $\\rho$"
set key right top Right

plot "../../data/profile/pr08_t10_47800.dat" u 1:3 pt 11 ps 1.5 lc rgb "#0A36AF" title "Tokamak T-10", \
     "../../data/profile/20260628124411.dat" u 1:3 pt 15 ps 1.5 lc rgb "#670010" title "PINN"

set size 0.4,0.45
set origin 0.55,0.3
set xrange[-1:1]
set yrange[0:70]
#set format y "$10^{%L}$"
unset label
#set label 1 "$\\times10^{4}$" at screen 0.12, 0.92
set tics
set border linewidth 2
set xlabel "\\scriptsize{\\textbf{Radio} $\\rho$}" offset 0,0.3
set ylabel "\\scriptsize{\\textbf{Potencia} ($kW/m^{3}$)}" offset 0.3,0

plot 51.25356 * exp(-0.5 * ( (x + 0.1) / 0.313 )**2) / (sqrt(2*pi) * 0.313) w l lw 3 lc rgb "black" notitle
unset multiplot
