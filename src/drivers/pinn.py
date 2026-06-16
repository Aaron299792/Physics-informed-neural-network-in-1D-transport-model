# -------------------------------
# Modules
# -------------------------------
import numpy as np
from ruamel.yaml import YAML
import argparse
import torch
import torch.nn.functional as F
import deepxde as dde
import matplotlib.pyplot as plt
from scipy.constants import epsilon_0, e, electron_mass
from cherab.core.atomic import hydrogen
from cherab.openadas.parse.adf11 import parse_adf11

import sys
import os

sys.path.append(os.path.abspath('../'))

from modules import pinn
from modules import RateCoeff2D as sv

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

yaml = YAML(typ='safe')
pathInput = '../../parameters/' + param_file
pathOutput = '../../data/profile/' + out_file

with open(pathInput, 'r') as file:
    params = yaml.load(file)
# -------------------------------
# Global Constants and Parameters
# -------------------------------
B = params['physical_params']['B'] #T
E_ION = params['physical_params']['E_ION'] #eV
N0 = params['physical_params']['N_0'] # cm^{-3}
N_MIN = params['physical_params']['N_MIN']
T_MIN = params['physical_params']['T_MIN']
N_MAX = params['physical_params']['N_MAX'] # eV
T_MAX = params['physical_params']['T_MAX'] # cm^-3
R = params['physical_params']['R'] # cm
P_EXT = params['physical_params']['P_EXT'] # cm^{-3}
VAR = params['physical_params']['VAR']
MU = params['physical_params']['MU']
l = params['physical_params']['l']
h = 1.0e10 * (epsilon_0 * B)**(-2) * e**1.5 * l * np.sqrt(electron_mass / np.pi**3)
#WB = 1.0e-4 * e * R * R * B * B / (1836.7 * electron_mass)
WB = 1.0
DELTA_T = T_MAX - T_MIN
DELTA_N = N_MAX - N_MIN
NORMC1 =  R * R * np.sqrt(DELTA_T) / (h * DELTA_N)
#--------------------------------
# MODEL PARAMETERS
#--------------------------------
HIDDEN_LAYERS = params['hidden_layers']
NUM_DOMAIN = params['model_params']['NUM_DOMAIN']
NUM_BOUNDARY = params['model_params']['NUM_BOUNDARY']
NUM_TEST = params['model_params']['NUM_TEST']
LOSS_WEIGHTS = params['model_params']['LOSS_WEIGHTS']
ADAM_ITER1 = params['model_params']['ADAM_ITER1']
ADAM_ITER2 = params['model_params']['ADAM_ITER2']
OBSERVATIONS = params['num_observations']

# -------------------------------
# Device Settings
# -------------------------------
DTYPE = torch.float64
EPS   = params['epsilon']
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.set_default_device(DEVICE)


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

sigma_ion = sv('../../data/adas/scd96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
sigma_rec = sv('../../data/adas/acd96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
p_rec = sv('../../data/adas/prb96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
p_rad_i = sv('../../data/adas/plt96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
p_rad_0 = sv('../../data/adas/prc96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)


# -------------------------------
# Functions
# -------------------------------

def ode(rho, y):
    n_hat = y[:, 0:1]
    T_hat = y[:, 1:2]
    dn_rho = dde.grad.jacobian(y, rho, i=0)
    dT_rho = dde.grad.jacobian(y, rho, i=1)
    d2n_rho = dde.grad.hessian(y, rho, component=0)
    d2T_rho = dde.grad.hessian(y, rho, component=1)
    nf = lambda x : x + T_MIN / DELTA_T
    Tf = lambda x : x + T_MIN / DELTA_T
    nD = nf(n_hat)
    TD = Tf(T_hat)
    n = nD * DELTA_N
    T = TD * DELTA_T

    SnD = n * (p_rad_i.rate(n, T) + p_rec.rate(n, T))  + N0 * (p_rad_0.rate(n, T) + E_ION * sigma_ion.rate(n,T))

    Pow = P_EXT / (np.sqrt(2.0 * np.pi) * VAR * DELTA_N * DELTA_T) * torch.exp(-0.5 * (1 / VAR)**2 * (rho - MU)**2)

    #Correct and checked expression for electron density
    NnD = -n * sigma_rec.rate(n, T) + N0 * sigma_ion.rate(n, T)
    term11 = nD * TD * (rho * d2n_rho + dn_rho)
    term12 = rho * TD * dn_rho * dn_rho
    term13 = -0.5 * rho * nD * dn_rho * dT_rho
    term14 = rho * NORMC1 * nD * TD * torch.sqrt(TD) * NnD
    ode1 = term11 + term12 + term13 + term14

    # Up to term25 everything is in order, not but results actually.
    SnD = (n * (p_rad_i.rate(n, T) + p_rec.rate(n, T)) \
        + N0 * p_rad_0.rate(n, T)) / e + N0 *E_ION * sigma_ion.rate(n,T)
    term21 = 4.7 * nD * nD * TD * (rho * d2T_rho + dT_rho) #checked and correct
    term22 = 10.4 * rho * nD * TD * dn_rho * dT_rho #checked and correct
    term23 = -2.35 * rho * nD * nD * dT_rho * dT_rho #checked and correct
    # Here everything goes smoth
    term25 = - rho * NORMC1 * nD * TD * TD * torch.sqrt(TD) * NnD #checked and correct
    term26 = - rho * NORMC1 * nD * TD * torch.sqrt(TD) * SnD / DELTA_T #checked and correct
    #Troublesome terms
    term24 = 3.0 * WB * TD * nD * nD / DELTA_T
    term27 = torch.exp(-0.5 * ((rho - MU) / 0.07) ** 2)
    ode2 = term21 + term22 + term23 + term24 + term25 + term26 + term27
    return [ode1, ode2]

def dn_op(rho, y, X):
    dn_rho = dde.grad.jacobian(y, rho, i=0, j=0)
    return dn_rho - 0.001 * y[:, 0:1]

def dT_op(rho, y, X):
    dT_rho = dde.grad.jacobian(y, rho, i=1, j=0)
    return dT_rho - 0.001 * y[:, 1:2]

def boundary(rho, on_boundary):
    return on_boundary and dde.utils.isclose(rho[0], 0)

def boundary2(rho, on_boundary):
    return on_boundary and dde.utils.isclose(rho[-1], 1)

geom = dde.geometry.TimeDomain(0.0, 1.0)
bc1 = dde.icbc.IC(geom, lambda rho : 1.0, boundary, component=0)
bc2 = dde.icbc.IC(geom, lambda rho : 1.0, boundary, component=1)
bc3 = dde.icbc.OperatorBC(geom, dn_op, boundary)
bc4 = dde.icbc.OperatorBC(geom, dT_op, boundary)

x_eval = geom.uniform_points(OBSERVATIONS, True)
solver = pinn(1, HIDDEN_LAYERS, 2, NUM_DOMAIN, NUM_BOUNDARY, NUM_TEST, ADAM_ITER1, ADAM_ITER2)
sol, res = solver.sol(ode, geom, [bc1, bc2, bc3, bc4], x_eval, weights=LOSS_WEIGHTS, refinement=True)

res = np.array(res)
#print(f"{DELTA_N:.2e}")
#print(DELTA_T)
#print(sigma_rec.rate(torch.tensor([N_MIN]), torch.tensor([T_MIN])))

#P0 = P_EXT / (np.sqrt(2.0 * np.pi) * VAR * DELTA_N * DELTA_T)
#print(f"{P0:.3e}")

print(res.mean())
print(res.max())
print(res.std())

plt.scatter(x_eval, sol[:,0], marker='h', color='k', label="n(x) PINN")
plt.scatter(x_eval, sol[:,1], marker='p', color='b', label="T(x) PINN")
plt.xlabel("x")
plt.ylabel("Solution")
plt.legend()
plt.show()
print("success")

#for i in range(x_eval.shape[0]):
#    print(x_eval[i][0], " ", sol[i, 0], " ", sol[i,1])

