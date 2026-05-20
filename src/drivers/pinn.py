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

sys.path.append(os.path.abspath('../modules'))

from sigmav2D import RateCoeff2D

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
N_0 = params['physical_params']['N_0'] # cm^{-3}
N_MIN = params['physical_params']['N_MIN']
T_MIN = params['physical_params']['T_MIN']
N_MAX = params['physical_params']['N_MAX'] # eV
T_MAX = params['physical_params']['T_MAX'] # cm^-3
R = params['physical_params']['R'] # cm
LAMBDA_N = params['physical_params']['LAMBDA_N']
LAMBDA_T = params['physical_params']['LAMBDA_T']
P_EXT = params['physical_params']['P_EXT'] # cm^{-3}
VAR = params['physical_params']['VAR']
MU = params['physical_params']['MU']

D_0 = 1e4 * (2 * np.sqrt(2 * np.pi * electron_mass) / 3) * (e / (4 * np.pi * epsilon_0 * B))**2 * (N_MAX * 1e6  / np.sqrt(T_MAX * e)) #cm^2 s^-1
KAPPA_0 = 4.7 * N_MAX * D_0 # cm^-1 s^-1
C = 2 * np.log(4 * np.pi * np.power(epsilon_0 * T_MAX * e, 1.5) / (e**3 * np.sqrt(N_MAX)))

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

sigma_ion = RateCoeff2D('../../data/adas/scd96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
sigma_rec = RateCoeff2D('../../data/adas/acd96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
p_rec = RateCoeff2D('../../data/adas/prb96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
p_rad_i = RateCoeff2D('../../data/adas/plt96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)
p_rad_0 = RateCoeff2D('../../data/adas/prc96_h.dat', hydrogen, n_max=N_MAX, T_max = T_MAX)


# -------------------------------
# Functions
# -------------------------------

def ode_system(X, y):
    #----------------------------
    # Preamble
    #----------------------------
    rho = X[:, 0:1]
    rho_eps = torch.clamp(rho, min=1e-12) #no puede ser cero, las ecs explotan
    n_hat = y[:, 0:1]
    T_hat = y[:, 1:2]

    n = n_hat * N_MAX
    T = T_hat * T_MAX

    dn_rho = dde.grad.jacobian(y, X, i=0, j=0) #es sobre las normalizadas
    dT_rho = dde.grad.jacobian(y, X, i=1, j=0)

    # T^3/n and log(T^3/n)
    T3n = (T_hat ** 3) / (n_hat)
    logT3n = torch.log(T3n)
    D_hat = n_hat / torch.sqrt(T_hat) * (logT3n + C)

    #----------------------------
    # ODE: Particles
    #----------------------------
    ionization = sigma_ion.rate(n, T) * n_hat**2
    recombination = sigma_rec.rate(n, T) * n_hat * N_0


    S_particle = (R**2 / (D_0 * N_MAX)) * (- ionization + recombination)
    flux_n = rho_eps * D_hat * dn_rho
    dflux_n_rho = dde.grad.jacobian(flux_n, X, i=0, j=0)

    ode1 = dflux_n_rho / rho_eps  - S_particle

    #----------------------------
    # ODE: Energy
    #----------------------------

    flux_T = rho_eps * D_hat * dT_rho
    dflux_T_rho = dde.grad.jacobian(flux_T, X, i=0, j=0)
    conduction = dflux_T_rho / rho_eps

    gaussian_profile = torch.exp(-0.5 * ((rho - MU) / VAR)**2)
    power_dep = (P_EXT * R / (N_MAX * T_MAX * D_0)) * gaussian_profile

    P_rec = p_rec.rate(n, T)
    P_rad_i = p_rad_i.rate(n,T)
    P_rad_0 = p_rad_0.rate(n,T)

    P_loss = P_rec + P_rad_i + P_rad_0

    loss_power = (R**2 / (N_MAX * T_MAX * D_0)) * P_loss

    ode2 = conduction + power_dep - loss_power #me falta agregar coulomb

    #ode1 = torch.nan_to_num(ode1, nan=0.0)
    #ode2 = torch.nan_to_num(ode2, nan=0.0)

    return [ode1, ode2]

def boundary_l(X, on_boundary):
    return on_boundary and dde.utils.isclose(X[0], 0)

def boundary_r(X, on_boundary):
    return on_boundary and dde.utils.isclose(X[0], 1)

def robin_n(X, y):
    n_hat = y[:, 0:1]
    T_hat = y[:, 1:2]

    # T^3/n and log(T^3/n)
    T3n = torch.clamp((T_hat ** 3) / (n_hat + EPS), min=1e-12,max=1e12)
    logT3n = torch.log(T3n)
    D_hat = n_hat / torch.sqrt(T_hat + EPS) * (logT3n + C)
    D_hat = torch.clamp(D_hat, min=1e-8, max=1e8)

    return -n_hat / (LAMBDA_N * D_hat)

def robin_T(X, y):
    n_hat = y[:, 0:1]
    T_hat = y[:, 1:2]

    # T^3/n and log(T^3/n)
    T3n = torch.clamp((T_hat ** 3) / (n_hat + EPS), min=1e-12,max=1e12)
    logT3n = torch.log(T3n)
    D_hat = n_hat / torch.sqrt(T_hat + EPS) * (logT3n + C)
    D_hat = torch.clamp(D_hat, min=1e-8, max=1e8)

    return -T_hat / (LAMBDA_T * D_hat)


#--------------------------------
# Main
# -------------------------------
geom = dde.geometry.Interval(0.0, 1.0)

bc_l_n = dde.icbc.DirichletBC(geom, lambda x: 1.0, boundary_l, component=0)
bc_l_T = dde.icbc.DirichletBC(geom, lambda x: 1.0, boundary_l, component=1)

bc_r_n = dde.icbc.RobinBC(geom, robin_n, boundary_r, component=0)
bc_r_T = dde.icbc.RobinBC(geom, robin_T, boundary_r, component=1)

boundaries = [bc_l_n, bc_l_T, bc_r_n, bc_r_T]

data = dde.data.PDE(geom, ode_system, boundaries, NUM_DOMAIN, NUM_BOUNDARY, num_test=NUM_TEST)

net = dde.nn.FNN([1] + HIDDEN_LAYERS*6 + [2], "tanh", "Glorot normal")

def output_transform(x, y):
    return torch.exp(y)

net.apply_output_transform(output_transform)

net.apply_output_transform(lambda x, y: torch.exp(y))

model = dde.Model(data, net)

model.compile("adam", lr=1e-4, loss_weights=LOSS_WEIGHTS)
model.train(iterations=ADAM_ITER1)

model.compile("adam", lr=1e-5, loss_weights=LOSS_WEIGHTS)
model.train(iterations=ADAM_ITER2)

model.compile("L-BFGS")
model.train()

x = np.linspace(0, 1, OBSERVATIONS)[:, None]
y = model.predict(x)

n_pred = y[:, 0]
T_pred = y[:, 1]

with open(pathOutput, 'w') as f:
    for i in range(len(n_pred)):
        print(x[i][0], " ", n_pred[i], " ", T_pred[i], file=f, sep='')

print("Output written in '../../data/profile'")
