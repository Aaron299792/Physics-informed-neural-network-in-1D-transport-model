set term epslatex standalone color

set output "out.tex"

set yrange [0:1.1]
set ylabel "\\textbf{Temperatura} $\\hat{T}$"
set xlabel "\\textbf{Radio} $\\rho$"
set border linewidth 5
set key left bottom Left reverse

plot "96040237.dat" using 1:3 w p pt 15 ps 1.5 lc rgb "#0A36AF" title "descarga 96040237, tiempo = 0.19s", \
     "97052261.dat" using 1:3 w p pt 7 ps 1.5 lc rgb "#800000" title "descarga 97052261, tiempo = 0.30s", \
     "97053056.dat" using 1:3 w p pt 13 ps 1.5 lc rgb "#154406" title "descarga 97053056, tiempo = 0.30s"
