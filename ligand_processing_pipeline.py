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
   'split_bulk': 'obabel %s -O %s -m',
   'split_bulk_sdf2mol2': 'obabel -isdf %s -omol2 -O %s -m',
   # choose either:
   'smi2mol2': 'obabel %s -O %s --gen3d --best --canonical --conformers --weighted --nconf 50 --ff GAFF',
   # or:
   'smi2mol2_ph74': 'obabel %s -O %s --gen3d best -p 7.4 --canonical',
   # or:
   'smi2mol2_gaff': 'obabel %s -O %s --gen3d --best --canonical --minimize --ff GAFF --steps 10000 --sd',
   'mol22pdbqt': 'prepare_ligand4.py -l %s -o %s -U nphs_lps -v',
  ### docking
   'split_bulk_pdbqt2pdb': 'obabel -ipdbqt %s -opdb -O %s -m',
}

def gen_cmd_str(cmd_str, infile, outfile):
    return cmd_str%(infile, outfile)

### LIGAND
def split_bulk_to_single(bulk_path, single_path, method="no_conversion"):
    if not os.path.exists(os.path.split(single_path)[0]):
        os.makedirs(os.path.split(single_path)[0])
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
    if not os.path.exists(os.path.split(out_dir)[0]):
        os.makedirs(out_dir)
    ligand_out_path = os.path.join(out_dir, ligname).split('.mol2')[0]
    # cmd_ = gen_cmd_str(cmd_dict['smi2mol2'], '%s' % (ligand_in_path), '%s.mol2' % (ligand_out_path))
    cmd_ = f"obabel {ligand_in_path} -O {ligand_out_path}.mol2 --gen3d --best --canonical --conformers --weighted --nconf 50 --ff GAFF"
    print(cmd_)
    exec_shell_command(cmd_)

def lig_mol2_2_pdbqt(ligand_in_path, del_mol2=True):
    ligand_dir, ligname = os.path.split(ligand_in_path)
    ligand_out_path = os.path.join(ligand_dir, ligname.split('.')[0] + '.pdbqt')
    # cmd_ = gen_cmd_str(cmd_dict['mol22pdbqt'], '%s' %(ligand_in_path), '%s'%(ligand_out_path))
    cmd_ = f'prepare_ligand4.py -l {ligand_in_path} -o {ligand_out_path} -U nphs_lps -v'
    print(cmd_)
    exec_shell_command(cmd_)
    if os.path.exists(ligand_out_path + '.pdbqt') and del_mol2:
        os.remove(ligand_in_path)
    return ligand_out_path

def run_docking(receptor, ligand, config, log, out, vina='autodock_vina_1_1_2_linux_x86/bin/vina'):
    cmd_ = f"{vina} --receptor {receptor} --ligand {ligand} \
    --config {config} --log {log} --out {out}"
    exec_shell_command(cmd_)


def prepare_ligand_runner(lig_dir):
    out_dir = os.path.join(lig_dir, 'processed')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    lig_fnames = [f for f in os.listdir(lig_dir) if '.sdf' in f]
    for lig in lig_fnames:
        lig_sdf_2_mol2(os.path.join(lig_dir, lig))
    mol2_ligs = [f for f in os.listdir(out_dir) if '.mol2' in f]
    for lig in mol2_ligs:
        lig_mol2_2_pdbqt(os.path.join(out_dir, lig))



if __name__=="__main__":
    print(os.getcwd())
    library_dir = 'enamine_collections/'
    for library in os.listdir(library_dir):
        bulk_path = os.path.join(library_dir, library)
        out_path = os.path.join(*[library_dir, library.split('.')[0], library.split('.')[0] + '_.sdf'])
        lig_collection_dir = os.path.split(out_path)[0]
        if not os.path.exists(lig_collection_dir):
            split_bulk_to_single(bulk_path, out_path)
        prepare_ligand_runner(lig_collection_dir)

        bp = True
