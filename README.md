# Physics-informed neural network in 1D transport model

This repository contains an implementation of a PINN to obtain electronic profiles of density and temperature from a derived 1D reduced model treatment of a plasma column exhibiting classical transport.

The PINN was implemented using [`DeepXDE`](https://deepxde.readthedocs.io/en/latest/) with a backend on [`PyTorch`](https://pytorch.org/). Library [`Cherab_v1.5`](https://www.cherab.info/welcome.html) is also used to obtain $\langle\sigma\nu\rangle$ rates for the gas used in the runs. 

## Environment setting

To run the code, the user must set a virtual environment with all the required compatible packages. The easiest way to do it is to run the command:

`conda env create -f environment.yml`

This will set up the environment. Users are free to handle the package version and environment settings on their own. However, be aware that the code may not run as intended. Users may find the required packages and versions in the file [environment](environment.yaml). 
