
import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# list of folder names to parse
os.chdir('/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/Fitness_score/Fitness_score/data')
l_fold = os.listdir('./input/3DRobot_set/')

#create a table to store the Protein_name, Fitness Score, and name_decoy
table = pd.DataFrame(columns = ['Protein_name', 'Fitness Score', 'name_decoy'])

for name in l_fold:
    # get folder name
    fold_time = os.listdir('./output/3d_robot/' + name)
    os.chdir('./output/3d_robot/' + name + '/' + fold_time[0] + '/pdb_color_custom')
    f_rmsd = '/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/Fitness_score/Fitness_score/data/input/3DRobot_set/' + name + '/list.txt'
    # read the list of decoys
    df_rmsd = pd.read_csv(f_rmsd, delim_whitespace=True)
    # loop over files
    for file in os.listdir():
        if 'native' in file:
            name_decoy = 'Native'
            rmsd = 0
        else:
            name_decoy = '_'.join(file.split('_')[1:3])
            rmsd = df_rmsd[df_rmsd['NAME'] == name_decoy+'.pdb']['RMSD'].values[0]
        with open(file, 'r') as f:
            lines = f.readlines()
            line = lines[2]
            # extract the fitness score from the 3rd line
            score = float(line.split()[-1])
            # add the protein name, fitness score, and name of the decoy to the table
            table = table.append({'Protein_name': name, 'Fitness Score': score, 'name_decoy': name_decoy,'RMSD':rmsd}, ignore_index=True)

    os.chdir('/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/Fitness_score/Fitness_score/data')

# save the table to a csv file
table.to_csv('3DRobot_table_25.csv', index=False)

read_table = pd.read_csv('3DRobot_table_25.csv')

l_rank = [] # list of rank that native arrive
for name in l_fold:
    df_table = read_table[read_table['Protein_name'] == name]
    # order the table by fitness score
    df_table = df_table.sort_values(by='Fitness Score', ascending=False)
    #reset the index
    df_table = df_table.reset_index(drop=True)
    # get the rank of the native structure
    rank = df_table[df_table['name_decoy'] == 'Native'].index[0]
    l_rank.append(rank)

# name of the protein that rank > 0
l_name = np.take(l_fold, np.where(np.array(l_rank) > 0)[0])
# print the name of the protein that rank > 0 and the rank
print(l_name)
print(np.take(l_rank, np.where(np.array(l_rank) > 0)[0]))
# same but rank >0 and sorted by rank
l_name = np.take(l_fold, np.where(np.array(l_rank) > 0)[0])
l_rank = np.take(l_rank, np.where(np.array(l_rank) > 0)[0])
l_name = np.take(l_name, np.argsort(l_rank))
l_rank = np.take(l_rank, np.argsort(l_rank))
print(l_name)
print(l_rank)
# sort the list of rank descending
l_rank.sort(reverse=True)
# print info of the list of rank
print('Mean rank:', np.mean(l_rank))
print('Std rank:', np.std(l_rank))
print('Min rank:', np.min(l_rank))
print('Max rank:', np.max(l_rank))

