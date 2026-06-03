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
    u = y[:, 0:1]
    v = y[:, 1:2]
    du_x = dde.grad.jacobian(y, x, i=0)
    dv_x = dde.grad.jacobian(y, x, i=1)
    return du_x - v, dv_x + u

def boundary(x, on_boundary):
    return on_boundary and dde.utils.isclose(x[0], 0)

def func(x):
    """
    y1 = sin(x)
    y2 = cos(x)
    """
    return np.hstack((np.sin(x), np.cos(x)))

geom = dde.geometry.TimeDomain(0.0, 1.0)
bc1 = dde.icbc.IC(geom, lambda x : 0.0, boundary, component=0)
bc2 = dde.icbc.IC(geom, lambda x : 1.0, boundary, component=1)

x_eval = geom.uniform_points(30, True)
solver = pinn(1, 32, 2, 1000, 2, 100, 2000, 5000, solution=func)
sol, res = solver.sol(ode, geom, [bc1, bc2], x_eval, weights=[1, 1, 0.1, 0.1], refinement=True)

#print(f"Residual average: {res.mean():.5f}")
#print(f"Residual std: {res.std():.5f}")
#print(f"Residual's maximum value: {res.max():.5f}")

plt.plot(x_eval, np.sin(x_eval), label="u(x) = sin(x)")
plt.plot(x_eval, np.cos(x_eval), label="v(x) = cos(x)")
plt.scatter(x_eval, sol[:,0], marker='h', color='k', label="u(x) PINN")
plt.scatter(x_eval, sol[:,1], marker='p', color='r', label='v(x) PINN')
plt.xlabel("x")
plt.ylabel("Solution")
#plt.text(0.110,0.45, r"$\frac{dy}{dx} + y = 0$", fontsize=14)
plt.legend()
plt.show()
