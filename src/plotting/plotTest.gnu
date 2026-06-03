set term epslatex standalone color

set output "expDecay1D.tex"

set label "$y^{\\prime} + y = 0$" at graph 0.7, graph 0.5 right
set ylabel "$y(x)$"
set xlabel "$x$"
set border linewidth 5

plot "../../data/tests/expDecay1D.dat" u 1:3 w p pt 13 ps 1.5 title "PINN",\
     "../../data/tests/expDecay1D.dat" u 1:2 w l lw 2 lc rgb "#000000" title "$y(x) = e^{-x}$"
