#!usr/bin/env python3

import copy
import itertools
##### Extraire les séquences des fichiers pdb #####
import os
from time import time

from tqdm import tqdm
from Bio.Align.Applications import MuscleCommandline
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

from lib import global_parameters as gp
from lib.progress_bar_color import get_color

########### 1 : GLOBAL ###########
def multiple_alignment():
    t_multi = time()
    sequences = {}
    parser = PDBParser()
    cleaned_dataset = gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/cleaned_dataset'
    pdbs = [file for file in os.listdir(cleaned_dataset) if file.endswith('.pdb')]
    if len(pdbs) == 0:
        print("No cleaned dataset found.")
        exit()
    with tqdm(total=len(pdbs), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
        # pbar.set_description('\033[38;2;250;223;54m' + f"Processing muscle multiple alignement")
        for index, pdb_file in enumerate(pdbs):
            if len(pdbs) > 1:
                pbar.set_description(get_color(index / (len(pdbs) - 1)) + f"Processing PDB files loading")
            else:
                pbar.set_description(get_color(1)+"Processing PDB files loading")
            # pbar.set_description(get_color(index / (len(pdbs)-1)) + f"Processing muscle multiple alignement")
            # Vérifier si le fichier est un fichier PDB
            if pdb_file.endswith('.pdb'):
                # Extraire le code de la protéine à partir du nom de fichier
                protein_code = pdb_file.split('.')[0]

                # Analyser le fichier PDB et extraire la séquence de la protéine
                structure = parser.get_structure(protein_code, os.path.join(cleaned_dataset, pdb_file))
                sequence = ''
                for model in structure:
                    for chain in model:
                        sequence += seq1(''.join([residue.get_resname() for residue in chain.get_residues()]))
                pbar.update()
                sequences[protein_code] = sequence

    couples = {}
    for id1, id2 in itertools.combinations(sequences.keys(), 2):
        couple_name = id1 + '/' + id2
        couples[couple_name] = (sequences[id1], sequences[id2])
    for key in couples:
        couples[key] = None

    couples_positions = copy.deepcopy(couples)
    folder_path = gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + "/input_muscle.fasta"
    folder_output_path = gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + "/output_muscle.fasta"

    # créer le fichier input muscle contenant toutes les séquences
    with open(folder_path, "w") as f:
        for seq_id, sequence in sequences.items():
            f.write(">{}\n{}\n".format(seq_id, sequence.replace("X", "")))



    # run = ['resources/./muscle', '-align', folder_path, '-output', folder_output_path]
    # subprocess.run(run, capture_output=True, text=True)
    muscle_cline = MuscleCommandline(input=folder_path, out=folder_output_path)
    try:
        muscle_cline()
        print(get_color(index / len(pdbs)) + "Muscle multiple alignment done in {:.1f} seconds".format(time() - t_multi))
        print('')
    except:
        print("Muscle multiple alignment failed")
