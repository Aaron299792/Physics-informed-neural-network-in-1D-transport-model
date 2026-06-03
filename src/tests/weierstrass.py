import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import torch
import deepxde as dde
from scipy.integrate import solve_ivp

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
    dy_xx = dde.grad.hessian(y,x)
    return dy_xx - y**2

def loss_diff(x, y, X):
    dy_x = dde.grad.jacobian(y,x)
    return dy_x

def boundary(x, on_boundary):
    return on_boundary and dde.utils.isclose(x[0], 0)

def fsol(x):
    def ode(t, y):
        u, v = y
        return [v, u**2]

    y0 = [1, 0]
    t_span = (0,1)
    t_eval = x.reshape(len(x),)
    sol = solve_ivp(ode, t_span ,y0, t_eval = t_eval,  rtol = 1e-8, atol=1e-10)
    return sol.y[0,:]


geom = dde.geometry.TimeDomain(0.0, 1.0)
bcD = dde.icbc.IC(geom, lambda x : 1.0, boundary)
bcO = dde.icbc.OperatorBC(geom, loss_diff, boundary)

x_eval = geom.uniform_points(30, True)
solver = pinn(1, 32, 1, 500, 1, 100, 2000, 5000)
sol, res = solver.sol(ode, geom, [bcD, bcO], x_eval, weights=[1, 0.01, 0.01], refinement=True)
sol_ivp = fsol(x_eval)

print(f"Residual average: {res.mean():.5f}")
print(f"Residual std: {res.std():.5f}")
print(f"Residual's maximum value: {res.max():.5f}")

plt.plot(x_eval, sol_ivp, label="solve_ivp")
plt.scatter(x_eval, sol, marker='h', color='k', label="PINN")
plt.xlabel("x")
plt.ylabel("y(x)")
plt.text(0.110,1.1, r"$\frac{d^2y}{dx^2} - y^2 = 0$", fontsize=14)
plt.legend()
plt.show()
