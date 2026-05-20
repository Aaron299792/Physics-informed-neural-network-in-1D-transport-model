set term epslatex standalone color

set output "pr08_rtpn.tex"

set yrange [0:1.1]
set ylabel "\\textbf{Density} $n / n_{max}$"
set xlabel "\\textbf{Radius} $\\rho$"
set border linewidth 5
set key left bottom Left reverse

plot "pr08_rtp.dat" using 1:3 with linespoints lw 2 pt 15 ps 1.5 lc rgb "#0A36AF" title "shot 96040237, time = 0.19s", \
     "pr08_rtp.dat" using 1:5 with linespoints lw 2 pt 7 ps 1.5 lc rgb "#800000" title "shot 97052261, time = 0.30s", \
     "pr08_rtp.dat" using 1:7 with linespoints lw 2 pt 13 ps 1.5 lc rgb "#154406" title "shot 97053056, time = 0.30s"
