import os
import argparse

"""
This module requires a directory full of individual mol2 files that will be used for running
docking experiments
"""
from ligand_processing_pipeline import exec_shell_command, run_docking, lig_mol2_2_pdbqt



def prep_and_dock_mol2(mol2_path, receptor, config, log):
    ligand = lig_mol2_2_pdbqt(mol2_path, del_mol2=False)
    out_dir, ligname = os.path.split(ligand)
    out = os.path.join(out_dir, ligname.split('.')[0] + '_out.pdbqt')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    run_docking(receptor, ligand, config, log, out, vina='autodock_vina_1_1_2_linux_x86/bin/vina')


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lig_dir", required=True, help="Directory with mol2 lig files")
    parser.add_argument("-r", "--rec", required=True, help="Prepared receptor file")
    parser.add_argument("-c", '--config', required=False, default='config.txt')
    args = parser.parse_args()


    lig_dir = args.lig_dir
    receptor = args.rec
    config = args.config
    ligand_paths = [os.path.join(lig_dir, l) for l in os.listdir(lig_dir) if '.mol2' in l]
    for ligpath in ligand_paths:
        prep_and_dock_mol2(ligpath, receptor, config, log=ligpath.split('.')[0] + '.log')
