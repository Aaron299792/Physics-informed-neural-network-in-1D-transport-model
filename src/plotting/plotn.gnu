set term epslatex standalone color

set output "out.tex"

set label "$R^2 = 0.969$" at graph 0.02, graph 0.05 left
set label "MAE$= 4.50\\times 10^{-2}$" at graph 0.02, graph 0.15 left
set label "MBE$= -3.13\\times 10^{-2}$" at graph 0.02, graph 0.25 left

set yrange [0:1.1]
set ylabel "\\textbf{Densidad} $\\hat{n}$"
set xlabel "\\textbf{Radio} $\\rho$"
set border linewidth 5
set key right top Right

plot "../../data/profile/pr08_t10_47800.dat" u 1:2 pt 11 ps 1.5 lc rgb "#0A36AF" title "Tokamak T-10", \
     "../../data/profile/20260628124411.dat" u 1:2 pt 15 ps 1.5 lc rgb "#670010" title "PINN"
