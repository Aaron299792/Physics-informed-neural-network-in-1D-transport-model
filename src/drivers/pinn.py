# -------------------------------
# Modules
# -------------------------------
import numpy as np
import torch
import deepxde as dde
import argparse
from scipy.constants import e
import matplotlib.pyplot as plt
from cherab.core.atomic import hydrogen


import sys
import os

sys.path.append(os.path.abspath('../'))

from modules import pinn
from modules import RateCoeff2D as sv
from modules import net_params as netp
from modules import phys_params as pp

parser = argparse.ArgumentParser(description='Parameter file name')

parser.add_argument('--f', action='store', dest='param_file', type=str,
                    help='[STR] filename of the parameter file')
parser.add_argument('--o', action='store', dest='out_file', type=str,
                    help='[STR] filename of the output file')


args = parser.parse_args()
param_file = args.param_file
out_file = args.out_file
assert param_file != None, 'Input File was not find. Make sure it exists in the path "../../parameters". Usage --f [input filename] --o [output filename]'
assert out_file != None, 'Output file not given. Usage --f [input filename] --o [output filename]'
# -------------------------------
# Device Settings
# -------------------------------
DTYPE = torch.float64
DEVICE = 'cpu'
torch.set_default_device(DEVICE)

pathInput = '../../parameters/' + param_file
pathOutput = '../../data/profile/' + out_file

"""------------------------------
Rate objects

Particle sources and drains:
    sigma_ion: <sigma nu>_ion n0 * n
    sigma_rec: <sigma nu>_rec n^2

power loss rates:
    p_rec = <E_rec><sigma nu>_rec n ^ 2 (contains Bremsstrahlung radiation)
    p_rad_i: <E_rad^i><sigma nu>_rad^i n^2
    p_rad_0: <E_rad^0><sigma nu>_rad^0 n
------------------------------"""

phys_params = pp(pathInput)
net_params = netp(pathInput)

sigma_ion = sv('../../data/adas/scd96_h.dat', hydrogen, n_max=phys_params.nmax, T_max = phys_params.tmax)
sigma_rec = sv('../../data/adas/acd96_h.dat', hydrogen, n_max=phys_params.nmax, T_max = phys_params.tmax)
p_rec = sv('../../data/adas/prb96_h.dat', hydrogen, n_max=phys_params.nmax, T_max = phys_params.tmax)
p_rad_i = sv('../../data/adas/plt96_h.dat', hydrogen, n_max=phys_params.nmax, T_max = phys_params.tmax)
p_rad_0 = sv('../../data/adas/prc96_h.dat', hydrogen, n_max=phys_params.nmax, T_max = phys_params.tmax)


# -------------------------------
# Functions
# -------------------------------

def ode_gen(param = phys_params, sion = sigma_ion, srec = sigma_rec, prec = p_rec , pradi = p_rad_i, prad0 = p_rad_0):
    def ode(rho, y):
       n_hat = y[:, 0:1]
       T_hat = y[:, 1:2]
       dn_rho = dde.grad.jacobian(y, rho, i=0)
       dT_rho = dde.grad.jacobian(y, rho, i=1)
       d2n_rho = dde.grad.hessian(y, rho, component=0)
       d2T_rho = dde.grad.hessian(y, rho, component=1)
       nf = lambda x : x + param.nmin / param.Dn
       Tf = lambda x : x + param.tmin / param.Dt
       nD = nf(n_hat)
       TD = Tf(T_hat)
       n = nD * param.Dn
       T = TD * param.Dt

       # Particle Flux
       NnD = -n * srec.rate(n, T) + param.n0 * sion.rate(n, T)
       term11 = nD * TD * (rho * d2n_rho + dn_rho)
       term12 = rho * TD * dn_rho * dn_rho
       term13 = -0.5 * rho * nD * dn_rho * dT_rho
       term14 = rho * param.norm * nD * TD * torch.sqrt(TD) * NnD
       ode1 = term11 + term12 + term13 + term14

       #Energy Flux
       SnD = (n * (pradi.rate(n, T) + prec.rate(n, T)) \
              + param.n0 * prad0.rate(n, T)) / e + param.n0 * param.e_ion * sion.rate(n,T)
       Pow = param.p0 / (np.sqrt(2.0 * np.pi) * param.s * param.Dn * param.Dt)
       term21 = 4.7 * nD * nD * TD * (rho * d2T_rho + dT_rho) #checked and correct
       term22 = 10.4 * rho * nD * TD * dn_rho * dT_rho #checked and correct
       term23 = - 1.0e4 * 2.35 * rho * nD * nD * dT_rho * dT_rho #checked and correct
       term25 = - rho * param.norm * nD * TD * TD * torch.sqrt(TD) * NnD #checked and correct
       term26 = - rho * param.norm * nD * TD * torch.sqrt(TD) * SnD / param.Dt #checked and correct
       term24 = 3.0 * param.wb * rho * TD * nD * nD / param.Dt
       term27 = Pow * param.norm * rho * TD * torch.sqrt(TD) * torch.exp(-0.5 * ((rho - param.mu) * param.a / param.s) ** 2)
       ode2 =  1.0e-3 * (term21 + term22 + term23 + term24 + term25 + term26 + term27)
       return [ode1, ode2]
    return ode

def dn_op(rho, y, X):
    dn_rho = dde.grad.jacobian(y, rho, i=0)
    return dn_rho

def dT_op(rho, y, X):
    dT_rho = dde.grad.jacobian(y, rho, i=1)
    return dT_rho

def boundary(rho, on_boundary):
    return on_boundary and dde.utils.isclose(rho[0], 0.0)

ode = ode_gen()
geom = dde.geometry.TimeDomain(0.0, 0.975)
bc1 = dde.icbc.IC(geom, lambda rho : 1.0, boundary, component=0)
bc2 = dde.icbc.IC(geom, lambda rho : 1.0, boundary, component=1)
bc3 = dde.icbc.OperatorBC(geom, dn_op, boundary)
bc4 = dde.icbc.OperatorBC(geom, dT_op, boundary)

x_eval = geom.uniform_points(net_params.obs, True)
solver = pinn(1, net_params.hidden_layers, 2, net_params.num_domain, net_params.num_boundary, net_params.obs, net_params.preiter, net_params.iter)
sol, res = solver.sol(ode, geom, [bc1, bc2, bc3, bc4], x_eval, weights=net_params.weights, refinement=True)

n_pred = sol[:,0]
T_pred = sol[:,1]
res = np.array(res)

print(res.mean())
print(res.max())
print(res.std())

#with open(pathOutput, 'w') as f:
#    for i in range(x_eval.shape[0]):
#        print(x_eval[i][0], n_pred[i], T_pred[i], file=f, sep=' ')
print("Output written in '../../data/profile/'")
plt.scatter(x_eval, sol[:,0], marker='h', color='k', label="n(x) PINN")
plt.scatter(x_eval, sol[:,1], marker='p', color='b', label="T(x) PINN")
plt.xlabel("x")
plt.ylabel("Solution")
plt.legend()
plt.show()
#print(x_eval)
