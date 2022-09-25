cd ${2}
if ! test -f "file_list.txt";
  then ls > file_list.txt
fi
fname="$(sed "${1}q;d" file_list.txt)"
prepare_ligand4.py -l $fname -o $fname$.pdbqt -U nphs_lps -v

