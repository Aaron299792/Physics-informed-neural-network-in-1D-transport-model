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

def ode(r, y):
    n = y[:, 0:1]
    T = y[:, 1:2]
    dn_r = dde.grad.jacobian(y, r, i=0)
    dT_r = dde.grad.jacobian(y, r, i=1)
    dn_rr = dde.grad.hessian(y, r, component=0)
    dT_rr = dde.grad.hessian(y, r, component=1)

    exp1n = r * n * T * dn_rr
    exp2n = n * T * dn_r
    exp3n = r * T * (dn_r)**2
    exp4n = - 0.5 * r * n * dn_r * dT_r
    exp5n = - r * n * T**1.5 * torch.log(1 + r)
    exp6n = r * n**2 * T**1.5 * torch.sqrt(torch.log(1 + r))
    ode1 = exp1n + exp2n + exp3n + exp4n + exp5n + exp6n

    exp1T = r * n**2 * T * dT_rr
    exp2T = n**2 * T * dT_r
    exp3T = r * n * T * dn_r * dT_r
    exp4T = - 0.5 * r * n ** 2 * (dT_r)**2
    exp5T = torch.log(1 + r) * r * n * T**3
    exp6T = - torch.sqrt(torch.log(1 + r)) * r * n**2 * T**3
    exp7T = - r * T**1.5 * torch.exp(-r**2)
    exp8T = r * n**2 * T
    ode2 = exp1T + exp2T + exp3T + exp4T + exp5T + exp6T + exp7T + exp8T
    return [ode1, ode2]

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
        eps = 0
        n, T, u, v = y
        dn_r = u
        dT_r = v
        du_r = - (u / (t + 1e-30)) - (u**2 / n) + (0.5 * (u * v) / T) + np.sqrt(T) * np.log(1 + t) - np.sqrt(T * np.log(1 + t)) * n
        dv_r = -(v / (t + 1e-30)) - (u * v) / n + 0.5 * v**2 / T - np.log(1 + t)*T**2 / n + np.sqrt(np.log(1 + t))* T**2 + np.sqrt(T)*np.exp(-t**2) / n**2 - 1
        return [dn_r, dT_r, du_r, dv_r]

    y0 = [1, 1, 0, 0]
    t_span = [0, 3.0]
    t_eval = x.reshape(len(x),)
    sol = solve_ivp(ode, t_span ,y0, t_eval = t_eval,  rtol = 1e-11, atol=1e-13)
    return sol.y[0,:], sol.y[1,:]

x = np.linspace(0, 3.0, 200)
u_ivp, v_ivp = fsol(x)

geom = dde.geometry.TimeDomain(0.0, 3.0)
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
plt.plot(x, u_ivp, label="u(x) solve_ivp")
plt.plot(x, v_ivp, label="v(x) solve_ivp")
plt.scatter(x_eval, sol[:,0], marker='h', color='k', label="u(x) PINN")
plt.scatter(x_eval, sol[:,1], marker='p', color='b', label="v(x) PINN")
plt.xlabel("x")
plt.ylabel("Solution")
#plt.text(0.110,0.8, r"$\frac{d^2y}{dx^2} + \frac{1}{1 + e^x}y^2 = 0$", fontsize=14)
plt.legend()
plt.show()
