set term epslatex standalone color

set output "out.tex"

#set yrange [0:1.1]
set logscale y
set format y "$10^{%L}$" 
set ylabel "\\textbf{Residuo} $|\\mathcal{N}(r, \\partial_r \\hat{n}, \\partial_r \\hat{T}, \\partial_r^2 \\hat{n}, \\partial_r^2\\hat{T}, \\Psi)|$"
set xlabel "\\textbf{Radio} $\\rho$"
set border linewidth 5

plot  "202606221339.dat" u 1:(abs($4)) w lp lw 3.0 ps 1.5 pt 15 lc rgb "#0A36AF" title "ODE $\\hat{n}$",\
      "202606221339.dat" u 1:(abs($5)) w lp lw 3.0 ps 1.5 pt 11 lc rgb "#670010" title "ODE $\\hat{T}$",\

#set label "$n_0 = 1.000$" at graph 0.27, graph 0.28 right 
#set label "$\\mathcal{P} = 0.403$" at graph 0.27, graph 0.21 right
#set label "$\\alpha_n = 5.798$" at graph 0.27, graph 0.14 right
#set label "$\\gamma_n = 1.000$" at graph 0.27, graph 0.07 right 

#plot "fit.dat" u 1:2 w l lw 5 lc rgb "#000000" title "$\\hat{n}(\\rho) = n_0[(1 - \\mathcal{P})(1 - \\rho^2)^{\\alpha_n} + \\mathcal{P}(1 - \\gamma_n\\rho^2)^{1/2}]$",\
#plot  "avg_shots.dat" u 1:3 w p pt 11 ps 2.0 lc rgb "#670010" title "descargas $\\langle \\hat{T}_{m} \\rangle$",\
#     "../../data/profile/test.out" u 1:3 w p pt 15 ps 2.0 lc rgb "#0A36AF" title "PINN $\\hat{T}(\\rho)$",\
    
    
