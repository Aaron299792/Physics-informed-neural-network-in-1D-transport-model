#!/bin/bash
#SBATCH --partition=serial
#SBATCH --time=03:00:00
#SBATCH --ntasks=14
#SBATCH --job-name="PINN_RUN"
#SBATCH --output=test.out.%j
#SBATCH --mail-user=aaron.sanabria@ucr.ac.cr
#SBATCH --mail-type=END,FAIL

source /home/aaron.sanabria/miniconda3/etc/profile.d/conda.sh
conda activate /home/aaron.sanabria/miniconda3/envs/cherab 

export OMP_NUM_THREADS=14
export MKL_NUM_THREADS=14
export OMP_PROC_BIND=close
export OMP_PLACES=cores

cd /home/aaron.sanabria/Transporte-Clasico-de-transporte-perpendicular-en-1D/src/drivers

python pinn.py --f 1.yaml 
python pinn.py --f 2.yaml 
python pinn.py --f 3.yaml 
python pinn.py --f 4.yaml 
python pinn.py --f 5.yaml 
python pinn.py --f 6.yaml 
python pinn.py --f 7.yaml 
python pinn.py --f 8.yaml 
python pinn.py --f 9.yaml 
python pinn.py --f 10.yaml 
python pinn.py --f 11.yaml 
python pinn.py --f 12.yaml 
