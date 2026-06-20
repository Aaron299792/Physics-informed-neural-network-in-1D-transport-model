import numpy as np
from scipy.constants import epsilon_0, e, electron_mass
from ruamel.yaml import YAML

class net_params:
    def __init__(self, pathInput):
        self._params = self._load(pathInput)
        self.hidden_layers = self._params['hidden_layers']
        self.num_domain = self._params['model_params']['NUM_DOMAIN']
        self.num_boundary = self._params['model_params']['NUM_BOUNDARY']
        self.num_test = self._params['model_params']['NUM_TEST']
        self.weights = self._params['model_params']['LOSS_WEIGHTS']
        self.preiter = self._params['model_params']['ADAM_ITER1']
        self.iter = self._params['model_params']['ADAM_ITER2']
        self.obs = self._params['num_observations']

    def _load(self, pathInput):
        yaml = YAML(typ='safe')
        with open(pathInput, 'r') as file:
            params = yaml.load(file)
        return params

    def print(self):
        print('='*65)
        print("PINN solver parameters")
        print('-'*65)
        print(f'  Number of hidden layers: {self.hidden_layers}')
        print(f'  Collocations points within domain: {self.num_domain}')
        print(f'  Collocations points boundaries: {self.num_boundary}')
        print(f'  Number of tests points: {self.num_test}')
        print(f'  Number of observation points: {self.obs}')
        print(f'  Number of pre iterations for adam {self.preiter}')
        print(f'  Number of iterations for adam {self.iter}')
        print(f'  loss functions weights : {self.weights}')
        print('='*65, "\n")

class phys_params(net_params):
    def __init__(self, pathInput):
        super().__init__(pathInput)
        self.devname = self._params['metadata']['device_name']
        self.b = self._params['physical_params']['B']
        self.e_ion = self._params['physical_params']['E_ION']
        self.n0 = self._params['physical_params']['N_0']
        self.nmin = self._params['physical_params']['N_MIN']
        self.tmin = self._params['physical_params']['T_MIN']
        self.nmax = self._params['physical_params']['N_MAX']
        self.tmax = self._params['physical_params']['T_MAX']
        self.a = self._params['physical_params']['A_MIN']
        self.ln = self._params['physical_params']['LAMBDA_N']
        self.lt = self._params['physical_params']['LAMBDA_T']
        self.p0 = self._params['physical_params']['P_EXT']
        self.s = self._params['physical_params']['VAR']
        self.mu = self._params['physical_params']['MU']
        self.l = self._params['physical_params']['l']
        self.h = 1.0e10 * (epsilon_0 * self.b)**(-2) * e**1.5 * self.l * np.sqrt(electron_mass / np.pi**3)
        self.wb = 1.0e-4 * e * (self.a * self.b)**2 / (1836.7 * electron_mass)
        self.Dt = self.tmax - self.tmin
        self.Dn = self.nmax - self.nmin
        self.norm = self.a * self.a * np.sqrt(self.Dt) / (self.h * self.Dn)

    def _load(self, pathInput):
        yaml = YAML(typ='safe')
        with open(pathInput, 'r') as file:
            params = yaml.load(file)
        return params

    def print(self):
        print('='*65)
        print("Magnetic confinenment device's physical parameters")
        print('-'*65)
        print(f'  Device: {self.devname}')
        print(f'  Field Strength B: {self.b} T')
        print(f'  Ionization Energy E_ion: {self.e_ion} eV')
        print(f'  Background neutrals density: {self.n0:.2e} cm^-3')
        print(f'  Minimum electron density: {self.nmin:.2e} cm^-3')
        print(f'  Maximum electron density: {self.nmax:.2e} cm^-3')
        print(f'  Minimum electron temperature: {self.tmin} eV')
        print(f'  Maximum electron temperature: {self.tmax} eV')
        print(f'  Electron density delta: {self.Dn:.2e} cm^-3')
        print(f'  Electron temperature delta: {self.Dt} eV')
        print(f'  Device minor radius: {self.a} cm')
        print(f'  Peak power deposition per unit volumen: {self.p0:.2e} eV cm^-3 s^-1')
        print(f'  Power profile variance: {self.s} cm')
        print(f'  Power profile mean radius {self.mu} (adim)')
        print(f'  Coulomb logararithm {self.l} (adim)')
        print(f'  h constant {self.h:.2e}  eV^(1/2) cm^5 s^-1')
        print(f'  wb constant {self.wb:.2e} eV')
        print(f'  Characteristic electron density decay scale: {self.ln} (adim)')
        print(f'  Characteristic electron temperature decay scale: {self.lt} (adim)')
        print(f'  Equations normalizations constant: {self.norm:.2e} s')
        print('='*65, "\n")

if __name__=='__main__':
    net_p = net_params("../../parameters/config.yaml")
    phys_p = phys_params("../../parameters/config.yaml")
    net_p.print()
    phys_p.print()
