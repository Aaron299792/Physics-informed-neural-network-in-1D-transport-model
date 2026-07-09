set term epslatex standalone color

set output "out.tex"

#set xrange [0:6999.99]
#set yrange [0: 0.08]
#set logscale y
#set format y "$10^{%L}$" 
set ylabel "Funci\\'on de p\\'erdida $\\mathcal{L}$"
set xlabel "\\textbf{Radio} $\\rho$"
set border linewidth 5

plot  "../../data/profile/loss_history.dat" u 1:4 w l lw 3.0 lc rgb "#0A36AF" title "$n$",\
      "../../data/profile/loss_history.dat" u 1:10 w l lw 3.0 lc rgb "#670010" title "$T$",\

#set label "$n_0 = 1.000$" at graph 0.27, graph 0.28 right 
#set label "$\\mathcal{P} = 0.403$" at graph 0.27, graph 0.21 right
#set label "$\\alpha_n = 5.798$" at graph 0.27, graph 0.14 right
#set label "$\\gamma_n = 1.000$" at graph 0.27, graph 0.07 right 

#plot "fit.dat" u 1:2 w l lw 5 lc rgb "#000000" title "$\\hat{n}(\\rho) = n_0[(1 - \\mathcal{P})(1 - \\rho^2)^{\\alpha_n} + \\mathcal{P}(1 - \\gamma_n\\rho^2)^{1/2}]$",\
#plot  "avg_shots.dat" u 1:3 w p pt 11 ps 2.0 lc rgb "#670010" title "descargas $\\langle \\hat{T}_{m} \\rangle$",\
#     "../../data/profile/test.out" u 1:3 w p pt 15 ps 2.0 lc rgb "#0A36AF" title "PINN $\\hat{T}(\\rho)$",\
    
    
