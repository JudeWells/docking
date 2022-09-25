import os
from ligand_processing_pipeline import lig_mol2_2_pdbqt

lig_dir = 'enamine_collections/ess_frag320/processed'
for f in lig_dir:
    in_path = os.path.join(lig_dir, f)
    lig_mol2_2_pdbqt(in_path, del_mol2=False)