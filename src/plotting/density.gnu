set term epslatex standalone color ""

set output "out.tex"

path1 = "../../data/profile/20260623214241.dat"
path2 = "../../data/profile/20260623214559.dat"
path3 = "../../data/profile/20260623214952.dat"
path4 = "../../data/profile/20260623215527.dat"
path5 = "../../data/profile/20260623215915.dat"
path6 = "../../data/profile/20260623220438.dat"
path7 = "../../data/profile/20260629133044.dat"
path8 = "../../data/profile/20260628124411.dat"
path9 = "../../data/profile/20260623222340.dat"
path10 = "../../data/profile/20260623223520.dat"
path11 = "../../data/profile/20260623223838.dat"
path12 = "../../data/profile/20260623224320.dat"
#set label "$L=$ " . ARG4 at graph 0.67, graph 0.93 right
#set label "$L = 32$" at graph 0.82, graph 0.92 right
#set label "its $= 7000$" at graph 0.90, graph 0.84 right
#set label "$t_2=$ " . ARG8 at graph 0.92, graph 0.86 right

#set logscale y
#set format y "$10^{%L}$"
set xrange [0:1.0]
set yrange [0:1.1]
set ylabel "\\textbf{Densidad} $\\hat{n}$"
set xlabel "\\textbf{Radio} $\\rho$"
set border linewidth 5
set key maxrows 5 right top reverse Right
set key width -2

plot path1 u 1:2 ps 1.2 pt 5 lc rgb "#0A36AF" title "$L_1$, $N_{c,1}$, $w_1$",\
     path2 u 1:2 ps 1.2 pt 7 lc rgb "#670010" title "$L_2$, $N_{c,1}$, $w_1$",\
     path3 u 1:2 ps 1.2 pt 9 lc rgb "#008000" title "$L_3$, $N_{c,1}$, $w_1$",\
     path4 u 1:2 ps 1.2 pt 11 lc rgb "#0A36AF" title "$L_1$, $N_{c,2}$, $w_2$",\
     path5 u 1:2 ps 1.2 pt 13 lc rgb "#670010" title "$L_2$, $N_{c,2}$, $w_2$",\
     path6 u 1:2 ps 1.2 pt 15 lc rgb "#008000" title "$L_3$, $N_{c,2}$, $w_2$",\
     path7 u 1:2 ps 1.2 pt 10 lc rgb "#0A36AF" title "$L_1$, $N_{c,3}$, $w_3$",\
     path8 u 1:2 ps 1.2 pt 12 lc rgb "#670010" title "$L_2$, $N_{c,3}$, $w_3$",\
     path9 u 1:2 ps 1.2 pt 14 lc rgb "#008000" title "$L_3$, $N_{c,3}$, $w_3$",\

