set term epslatex standalone color

set output ARG1

set label "$L=$ " . ARG4 at graph 0.2, graph 0.93 right
set label "$N_c=$ " . ARG5 at graph 0.235, graph 0.86 right
set label "$w=$ " . ARG6 at graph 0.6, graph 0.79 right
set label "$t_1=$ " . ARG7 at graph 0.43, graph 0.93 right
set label "$t_2=$ " . ARG8 at graph 0.44, graph 0.86 right

set ylabel "\\textbf{Density} $\\hat{n}$"
set xlabel "\\textbf{Radius} $\\rho$"
set border linewidth 5
set key left bottom Left reverse

plot ARG2 using 1:2 with linespoints lw 2 pt 13 ps 1.5 lc rgb ARG3 title "density"
