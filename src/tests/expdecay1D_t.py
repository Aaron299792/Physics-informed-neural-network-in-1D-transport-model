import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import torch
import deepxde as dde

import os
import sys

sys.path.append(os.path.abspath("../"))

from modules import pinn

mpl.rcParams.update({
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "text.usetex": True,
    "lines.antialiased": True,
})

def ode(x, y):
    dy_x = dde.grad.jacobian(y,x)
    return dy_x + y

def boundary(x, on_boundary):
    return on_boundary and dde.utils.isclose(x[0], 0)

geom = dde.geometry.Interval(0.0, 1.0)
bc = dde.icbc.DirichletBC(geom, lambda x : 1.0, boundary)

x_eval = geom.uniform_points(30, True)
solver = pinn(1, 64, 1, 1000, 1, 100, 2000, 5000, solution= lambda x : np.exp(-x))
sol, res = solver.sol(ode, geom, [bc], x_eval, weights=[1, 0.1], refinement=True)
analytic = np.exp(-x_eval)

"""
print(f"Residual average: {res.mean():.5f}")
print(f"Residual std: {res.std():.5f}")
print(f"Residual's maximum value: {res.max():.5f}")

plt.plot(x_eval, analytic, label="Exact")
plt.scatter(x_eval, sol, marker='h', color='k', label="PINN")
plt.xlabel("x")
plt.ylabel("y(x)")
plt.text(0.110,0.45, r"$\frac{dy}{dx} + y = 0$", fontsize=14)
plt.legend()
plt.show()
"""

pathOutput = "../../data/tests/expdecay1D.dat"

with open(pathOutput, 'w') as f:
    for i in range(x_eval.shape[0]):
        print(x_eval[i][0], analytic[i][0], sol[i][0], file=f, sep=' ')

print(analytic.shape)
print(f"Output written in {pathOutput}")
