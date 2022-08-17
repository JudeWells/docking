import os
import subprocess

def exec_shell_command(cmd_):
  # cmd_ = shlex.split(cmd_)
  process = subprocess.Popen(cmd_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  stdout, stderr = process.communicate()
  print(stdout, stderr)


### DOCKING / OPENBABEL COMMANDS
cmd_dict = {
  ### target prep
  # choose either this option:
   'pdb2pdbqt': 'prepare_receptor4.py -r %s -o %s -A hydrogens -U nphs_lps -v',
   # or these two commands:
   'pdb2pqr': 'pdb2pqr --ff=amber --chain --with-ph=7.4 --verbose %s %s',
   'pqr2pdbqt': 'prepare_receptor4.py -r %s -o %s -C -U nphs_lps -v',
  ### ligand prep
   'split_bulk': '/home/jwells/Tools/bin/obabel %s -O %s -m',
   'split_bulk_sdf2mol2': '/home/jwells/Tools/bin/obabel -isdf %s -omol2 -O %s -m',
   # choose either:
   'smi2mol2': '/home/jwells/Tools/bin/obabel %s -O %s --gen3d --best --canonical --conformers --weighted --nconf 50 --ff GAFF',
   # or:
   'smi2mol2_ph74': '/home/jwells/Tools/bin/obabel %s -O %s --gen3d best -p 7.4 --canonical',
   # or:
   'smi2mol2_gaff': '/home/jwells/Tools/bin/obabel %s -O %s --gen3d --best --canonical --minimize --ff GAFF --steps 10000 --sd',
   'mol22pdbqt': '/SAN/orengolab/nsp13/docking/miniconda3/bin/prepare_ligand4.py -l %s -o %s -U nphs_lps -v',
  ### docking
   'split_bulk_pdbqt2pdb': '/home/jwells/Tools/bin/obabel -ipdbqt %s -opdb -O %s -m',
}

def gen_cmd_str(cmd_str, infile, outfile):
    return cmd_str%(infile, outfile)

### LIGAND
def split_bulk_to_single(bulk_path, single_path, method="no_conversion"):
    os.makedirs(os.path.split(single_path)[0], exist_ok=True)
    method_dict = {
          'no_conversion': cmd_dict['split_bulk'],
          'pdbqt2pdb': cmd_dict['split_bulk_pdbqt2pdb'],
          'sdf2mol2': cmd_dict['split_bulk_sdf2mol2'],
      }

    cmd_ = gen_cmd_str(method_dict[method], bulk_path, single_path)
    print(cmd_)
    exec_shell_command(cmd_)

def prepare_ligand(ligand, input_type='mol2', method='gaff'):
    method_dict = {
        'gaff': cmd_dict['smi2mol2'],
        'ph74': cmd_dict['smi2mol2_ph74'],
        'gaff_opt': cmd_dict['smi2mol2_gaff'],
    }
    if input_type=='smi':
      # generate 3D coordinates
      cmd_ = gen_cmd_str(method_dict[method], '%s.smi'%(ligand), '%s.mol2'%(ligand))
      print(cmd_)
      exec_shell_command(cmd_)
      input_type='mol2'

    if input_type=='mol2':
      # prepare for docking
      cmd_ = gen_cmd_str(cmd_dict['mol22pdbqt'], '%s.mol2'%(ligand), '%s.pdbqt'%(ligand))
      print(cmd_)
      exec_shell_command(cmd_)
    else:
      raise TypeError('only `mol2` supported for docking')

def lig_sdf_2_mol2(ligand_in_path):
    ligand_dir, ligname = os.path.split(ligand_in_path)
    out_dir = os.path.join(ligand_dir, 'processed')
    os.makedirs(out_dir, exist_ok=True)
    ligand_out_path = os.path.join(out_dir, ligname).split('.mol2')[0]
    cmd_ = gen_cmd_str(cmd_dict['smi2mol2'], '%s' % (ligand_in_path), '%s.mol2' % (ligand_out_path))
    print(cmd_)
    exec_shell_command(cmd_)

def lig_mol2_2_pdbqt(ligand_in_path):
    ligand_dir, ligname = os.path.split(ligand_in_path)
    ligand_out_path = os.path.join(ligand_dir, ligname.split('.')[0])
    cmd_ = gen_cmd_str(cmd_dict['mol22pdbqt'], '%s' %(ligand_in_path), '%s.pdbqt'%(ligand_out_path))
    exec_shell_command(cmd_)
    os.remove(ligand_in_path)

def prepare_ligand_runner(lig_dir):
    out_dir = os.path.join(lig_dir, 'processed')
    os.makedirs(out_dir, exist_ok=True)
    # lig_fnames = [f for f in os.listdir(lig_dir) if '.sdf' in f]
    # for lig in lig_fnames:
    #     lig_sdf_2_mol2(os.path.join(lig_dir, lig))
    mol2_ligs = [f for f in os.listdir(out_dir) if '.mol2' in f]
    for lig in mol2_ligs:
        lig_mol2_2_pdbqt(os.path.join(out_dir, lig))



if __name__=="__main__":
    print(os.getcwd())
    library_dir = 'enamine_collections/'
    output_dir = 'enamine_processed'
    for library in os.listdir(library_dir):
        bulk_path = os.path.join(library_dir, library)
        out_path = os.path.join(*[library_dir, library.split('.')[0], library.split('.')[0] + '_.sdf'])
        lig_collection_dir = os.path.split(out_path)[0]
        if not os.path.exists(lig_collection_dir):
            split_bulk_to_single(bulk_path, out_path)
        prepare_ligand_runner(lig_collection_dir)

        bp = True
