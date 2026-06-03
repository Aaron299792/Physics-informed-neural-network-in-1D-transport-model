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
    u = y[:, 0:1]
    v = y[:, 1:2]
    du_xx = dde.grad.hessian(y, x, component=0)
    dv_xx = dde.grad.hessian(y, x, component=1)
    return [du_xx - v**2, dv_xx + u**2]

def du_op(x, y, X):
    du_x = dde.grad.jacobian(y, x, i=0, j=0)
    return du_x

def dv_op(x, y, X):
    dv_x = dde.grad.jacobian(y, x, i=1, j=0)
    return dv_x

def boundary(x, on_boundary):
    return on_boundary and dde.utils.isclose(x[0], 0)

def fsol(x):
    def ode(t, y):
        p, q, u, v = y
        return [v**2, -u**2, p, q]

    y0 = [0, 0, 1, 1]
    t_span = (0,1)
    t_eval = x.reshape(len(x),)
    sol = solve_ivp(ode, t_span ,y0, t_eval = t_eval,  rtol = 1e-8, atol=1e-10)
    return sol.y[2,:], sol.y[3,:]

geom = dde.geometry.TimeDomain(0.0, 1.0)
bc1 = dde.icbc.IC(geom, lambda x : 1.0, boundary, component=0)
bc2 = dde.icbc.IC(geom, lambda x : 1.0, boundary, component=1)
bc3 = dde.icbc.OperatorBC(geom, du_op, boundary)
bc4 = dde.icbc.OperatorBC(geom, dv_op, boundary)

x_eval = geom.uniform_points(30, True)
solver = pinn(1, 32, 2, 500, 1, 100, 2000, 5000)
sol, res = solver.sol(ode, geom, [bc1, bc2, bc3, bc4], x_eval, weights=[1, 1, 0.01, 0.01, 0.01, 0.01], refinement=True)

#print(f"Residual average: {res.mean():.5f}")
#print(f"Residual std: {res.std():.5f}")
#print(f"Residual's maximum value: {res.max():.5f}")

u_ivp, v_ivp = fsol(x_eval)
plt.plot(x_eval, u_ivp, label="u(x) solve_ivp")
plt.plot(x_eval, v_ivp, label="v(x) solve_ivp")
plt.scatter(x_eval, sol[:,0], marker='h', color='k', label="u(x) PINN")
plt.scatter(x_eval, sol[:,1], marker='p', color='b', label="v(x) PINN")
plt.xlabel("x")
plt.ylabel("Solution")
#plt.text(0.110,0.8, r"$\frac{d^2y}{dx^2} + \frac{1}{1 + e^x}y^2 = 0$", fontsize=14)
plt.legend()
plt.show()
