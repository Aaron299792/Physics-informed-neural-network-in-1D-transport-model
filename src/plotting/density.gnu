set term epslatex standalone color

set output ARG1

set ylabel "\\textbf{Density} $\\hat{n}$"
set xlabel "\\textbf{Radius} $\\rho$"
set border linewidth 5
set key left bottom Left reverse

plot ARG2 using 1:2 with linespoints lw 2 pt 13 ps 1.5 lc rgb ARG3 title "density"
