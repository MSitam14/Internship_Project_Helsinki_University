# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : July 2020
# Updated :
# ---------------------------------------------------------------------------- #
from random import random

import numpy as np
# Importing modules ---------------------------------------------------------- #

# Universal modules
import pandas as pd
import os
import shutil
from sklearn.neighbors import KDTree
from pymol import cmd
from Grid_methods.src.cla.systeme_class import System
from Grid_methods.src.hotspots.compute_structure_score import *
from Grid_methods.src.lib.cif_generation import hotspot_cif, build_hotspot_rows
from Grid_methods.src.lib.parse_pdb_file import parse_pdb_file
from Grid_methods.src.lib.retrieve_specific_files import retrieve_specific_files
from Grid_methods.src.lib.Grid_plot import *
from Grid_methods.src.lib.read_file_content import read_file_content

def launch_structure_hotspot(l_o_structures=None):
    explicit_grid = gp.D_PARAMETERS_GLOBAL['explicit_grid']
    d_parameters = gp.D_PARAMETERS_HOTSPOT

    # Initialize hotspot system object and set global parameters
    gp.O_SYSTEM_HOTSPOT = System()
    gp.O_SYSTEM_HOTSPOT.initialize_system(d_parameters)
    
    # If structures are provided, use them directly (from prepare_dataset)
    if l_o_structures is not None:
        gp.O_SYSTEM_HOTSPOT.l_o_structures = l_o_structures
    else:
        # Fallback: load from disk (backward compatibility)
        l_p_input_pdb = retrieve_specific_files(d_parameters["p_input_pdb"], "*.pdb")

        # For each PDB file to parse, extract the PDB structure into an object
        for p_pdb in l_p_input_pdb:
            o_structure = parse_pdb_file(p_pdb)
            gp.O_SYSTEM_HOTSPOT.l_o_structures.append(o_structure)  # Registers the structure in the system
    
    # Actualize the system properties depending of the structures
    gp.O_SYSTEM_HOTSPOT.update_system_properties()

    # Loop over the registered structures and solubilize each structure
    for o_structure in gp.O_SYSTEM_HOTSPOT.l_o_structures:
        try:
            fold_out = d_parameters['p_output_hotspot'] + '/' + o_structure.s_name
            os.makedirs(fold_out, exist_ok=True)
            gp.O_FINAL_STRUCTURE = o_structure
            d_parameters["max_score"] = 0  # Initialize the hotspot score for this structure
            # Generate a grid for the structure
            gp.O_SYSTEM_HOTSPOT.generate_grid(o_structure, d_parameters)
            # plot_grid_3D(o_structure.a_grid['element_symbol'])
            # plot_grid_2D(o_structure.a_grid['element_symbol'])
            # plot_heatmap(o_structure.a_grid['element_symbol'],palette='viridis')
            gp.O_SYSTEM_HOTSPOT.a_offset = o_structure.a_offset
            # accumulates every hotspot candidate point found across every round/type/tier,
            # written out in one combined CIF (see hotspot_cif() calls below)
            l_hotspot_rows = []
            # loop over the rounds to add hotspot atoms
            if d_parameters['i_number_of_rounds'] == 0:
                # just score the atoms
                a_atom_coord = np.array(
                    [[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in o_structure.a_atoms])

                # Create a KDTree using atom coordinates
                o_structure.o_tree = KDTree(a_atom_coord, leaf_size=50000, metric='euclidean')
                origin_coord = np.array([[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in
                                         o_structure.a_atoms[o_structure.pocket_indexes]])

                l_score_1 = score_environment(origin_coord, o_structure, True)
                score_total_1 = [np.sum(score) / 3 for score in l_score_1]

                # write the score in the a_atoms
                o_structure.a_atoms['score_1'][o_structure.pocket_indexes] = np.array(l_score_1)[:, 0]
                o_structure.a_atoms['score_2'][o_structure.pocket_indexes] = np.array(l_score_1)[:, 1]
                o_structure.a_atoms['score_3'][o_structure.pocket_indexes] = np.array(l_score_1)[:, 2]
                o_structure.a_atoms['score_total'][o_structure.pocket_indexes] = score_total_1
                file_name = fold_out + '/' + o_structure.s_name
                # write all the atoms in a pdb
                write_pdb(file_name + '_scored.pdb', o_structure.a_atoms)
                # combined CIF equivalent - no hotspot search ran, so no _hotspot rows
                hotspot_cif(fold_out + '/' + o_structure.s_name + '_combined.cif', o_structure,
                           gp.O_SYSTEM_HOTSPOT, d_parameters, l_hotspot_rows=[],
                           d_view_meta=gp.D_HOTSPOT_VIEW_META.get(o_structure.s_name))
                print('No hotspot atoms added')
                continue
            for hotspots_round in range(1,d_parameters['i_number_of_rounds']+1):
                print('Round : ', hotspots_round)
                for hotspots_type in d_parameters['s_hotspot_type'].split():
                    resn_spot = hotspots_type.replace('.', '')[0:3]
                    if hotspots_round > 1:
                        try:
                            o_structure.a_atoms = getattr(o_structure, resn_spot + '_a_atoms')
                        except AttributeError:
                            break
                        try:
                            o_structure.pocket_indexes = getattr(o_structure, resn_spot + '_pocket_indexes')
                        except AttributeError:
                            pass
                    ### STEP 1 : Compute the score of each atom in the structure
                    a_atom_coord = np.array(
                        [[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in o_structure.a_atoms])

                    # Create a KDTree using atom coordinates
                    o_structure.o_tree = KDTree(a_atom_coord, leaf_size=50000, metric='euclidean')
                    origin_coord = np.array([[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in
                                             o_structure.a_atoms[o_structure.pocket_indexes]])

                    l_score_1 = score_environment(origin_coord, o_structure, True)
                    score_total_1 = [np.sum(score) / 3 for score in l_score_1]

                    # write the score in the a_atoms
                    o_structure.a_atoms['score_1'][o_structure.pocket_indexes] = np.array(l_score_1)[:, 0]
                    o_structure.a_atoms['score_2'][o_structure.pocket_indexes] = np.array(l_score_1)[:, 1]
                    o_structure.a_atoms['score_3'][o_structure.pocket_indexes] = np.array(l_score_1)[:, 2]
                    o_structure.a_atoms['score_total'][o_structure.pocket_indexes] = score_total_1
                    file_name = fold_out + '/' + o_structure.s_name + '_' + '_round_' + str(hotspots_round)


                    # write all the atoms in a pdb
                    write_pdb(file_name + '_scored.pdb', o_structure.a_atoms)
                    file_name = (fold_out + '/' + o_structure.s_name + '_' +hotspots_type.replace('.','_') +
                                 '_round_' + str(hotspots_round))

                    random = False
                    # Place random atoms in the structure
                    if random:
                        f_name = '/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/test_set_hotspot/Water_prediction_test_set/'+o_structure.s_name+'/O_3_wat/'+o_structure.s_name+'_O_3_wat_round_1_step_3.pdb'
                        nb_o3w = 0
                        with open(f_name, 'r') as file:
                            for line in file:
                                if 'O3w' in line:
                                    nb_o3w += 1
                        for i in range(10):
                            for j in [True,False]:
                                if j:
                                    clean = 'clean'
                                else:
                                    clean = 'full_random'
                                l_p_atoms = place_water_random(o_structure,nb_o3w,j)
                                df_clean = pd.DataFrame(l_p_atoms)
                                p_atoms = df_clean.to_records(index=False)
                                # convert to numpy array
                                a_hotspot_coord = np.array([p_atoms['grid_x'], p_atoms['grid_y'], p_atoms['grid_z']]).T

                                # get only the first distance
                                l_p_score = score_environment(a_hotspot_coord, o_structure, False, hotspots_type)

                                p_atoms['score_1'] = np.array(l_p_score)[:, 0]
                                p_atoms['score_2'] = np.array(l_p_score)[:, 1]
                                p_atoms['score_3'] = np.array(l_p_score)[:, 2]
                                p_atoms['score_total'] = [np.sum(score) / 3 for score in l_p_score]
                                l_atoms = update_atoms_and_write(o_structure.a_atoms, p_atoms,
                                                                 file_name + '_random_'+clean+str(i)+'.pdb',
                                                                 res_name=resn_spot, hotspot_type=hotspots_type)
                        pdb = o_structure.s_name

                        distance_random_water(fold_out,
                                              '/home/dreano/Desktop/Grid_methods/data/output/hotspot/Score_test_set/test_set_scored/'+pdb+'/'+pdb+'_scored.pdb')
                        print('Random atoms added to', o_structure.s_name)
                    else:
                        ### STEP 2: Find all optimal position to place a hotspot atom around atoms with a score < 0.4 and keep the one
                        ### tagged at leat 3 times as optimal

                        # Compute the optimal distance for each atom and return the cells that has been tagged as optimal
                        t_hotspot_atm = time.time()
                        l_p_atoms = multiprocess_over_ranks(o_structure.a_atoms[o_structure.pocket_indexes],
                                                            hotspots_type,
                                                            ranks=[1, 2, 3],
                                                            score_lim=d_parameters['f_bad_score_threshold'])
                        print("Optimal distance computed in {:.1f} seconds".format(
                            time.time() - t_hotspot_atm))
                        print('')

                    # Filter the hotspot atoms to keep only the one interesting
                        # Convert the list of hotspot atoms to a pandas dataframe
                        df_hotspot = pd.DataFrame(l_p_atoms)  # convert to pandas dataframe
                        # Group by coordinates and residue serial, to weight the impact by residue
                        df_hotspot = df_hotspot.groupby(['grid_x', 'grid_y', 'grid_z',  # group by grid position and residue
                                                       'residue_serial']).min().reset_index() # serial and keep the lowest score
                        # Drop the residue serial column
                        df_hotspot = df_hotspot.drop(columns=['residue_serial'])
                        # Group by coordinates to give a score corresponding to the number of time the hotspot atom has been tagged as optimal
                        df_hotspot = df_hotspot.groupby(
                            ['grid_x', 'grid_y', 'grid_z']).sum().reset_index()  # group by grid position and sum the score

                        df_hotspot = df_hotspot.sort_values(by='score_total', ascending=True)  # sort by score total

                        # remove score total > -tag_threshold to keep position that has been tagged at least threshold times
                        df_clean = []
                        tag = d_parameters['f_tag_threshold']
                        # loop to reduce the threshold until we have at least 1000 tag position
                        while len(df_clean) < 1000 and tag > 0:
                            # remove score total > value to not keep atoms that we will never place
                            df_clean = df_hotspot[df_hotspot['tag_total'] <= - tag]
                            tag -= 1
                        # df_clean = df_hotspot[df_hotspot['score_1']< 0]
                        if len(df_clean) == 0:
                            print('No hotspot atoms found')
                            continue
                        # check the distances between the hotspot atoms and remove the one that are too close using a KDTree
                        p_atoms = df_clean.to_records(index=False)  # convert to structured numpy array
                        if explicit_grid:
                            # add the hotspot atoms to the a_grid
                            o_structure.a_grid['atom_serial'] = o_structure.a_grid['element_symbol']
                            # remove the atoms out of the grid
                            limit = o_structure.a_grid['element_symbol'].shape
                            p_atoms = p_atoms[(p_atoms['grid_x'] >= 0) & (p_atoms['grid_x'] < limit[0]) &
                                                    (p_atoms['grid_y'] >= 0) & (p_atoms['grid_y'] < limit[1]) &
                                                    (p_atoms['grid_z'] >= 0) & (p_atoms['grid_z'] < limit[2])]
                        # o_structure.a_grid['score_2'][p_atoms['grid_x'], p_atoms['grid_y'], p_atoms['grid_z']] = p_atoms['score_1']
                        #
                        # o_structure.a_grid["score_2"][  # Loads the elements symbols in the grid
                        #     o_structure.a_atoms["grid_x"],
                        #     o_structure.a_atoms["grid_y"],
                        #     o_structure.a_atoms["grid_z"]
                        # ] = o_structure.a_atoms["score_1"]
                        # plot_heatmap(o_structure.a_grid['score_2'],palette='viridis',neg=True,z=52)
                        # plot_heatmap(o_structure.a_grid['score_2'], palette='viridis', neg=True, z=52, x1=15, x2=100, y1=85,
                        #              y2=145, lab=False, fmt=".2f")
                        #
                        # for zi in range(25,30):
                        #     plot_heatmap(o_structure.a_grid['score_1'],palette='viridis',neg=True,z=zi)
                        # #focus plot heatmap
                        # plot_heatmap(o_structure.a_grid['score_2'],palette='viridis',neg=True,z=52)
                        # plot_heatmap(o_structure.a_grid['score_2'],palette='viridis',neg=True,z=99)
                        # plot_heatmap(o_structure.a_grid['score_2'],palette='viridis',neg=True,z=46)
                        #
                        # plot_heatmap(o_structure.a_grid['score_2'],palette='viridis',neg=True,z=46,x1=190,x2=240,y1=50,y2=100,lab=False,fmt=".2f")
                        # plot_heatmap(o_structure.a_grid['score_2'],palette='viridis',neg=True,z=99,x1=190,x2=240,y1=80,y2=130,lab=True,fmt=".2f")


                        # # write all the atoms in a pdb
                        # update_atoms_and_write(o_structure.a_atoms, p_atoms, file_name + '_step_1.pdb',res_name='resn_spot',
                        #                        res_number=900,atm_number=10000,hotspot_type=hotspots_type)

                        ### STEP 3: Compute the score at the first position of each hotspot and keep the one with a score > 0.6
                        ### to prevent clashes with the protein

                        # convert to numpy array
                        a_hotspot_coord = np.array([p_atoms['grid_x'], p_atoms['grid_y'], p_atoms['grid_z']]).T

                        # get only the first distance
                        l_p_score = score_environment(a_hotspot_coord, o_structure, False, hotspots_type)

                        p_atoms['score_1'] = np.array(l_p_score)[:, 0]
                        p_atoms['score_2'] = np.array(l_p_score)[:, 1]
                        p_atoms['score_3'] = np.array(l_p_score)[:, 2]
                        p_atoms['score_total'] = [np.sum(score) / 3 for score in l_p_score]
                        p_atoms['coord_x'], p_atoms['coord_y'], p_atoms['coord_z'] = box_coordinates_to_euclidean_coordinates(
                            p_atoms['grid_x'], p_atoms['grid_y'], p_atoms['grid_z'])
                        p_atoms['generation'] = 1 # generation round of the hotspot atom initialization to 1 
                        # write all the atoms in a pdb
                        update_atoms_and_write(o_structure.a_atoms, p_atoms, file_name + '_step_1.pdb',res_name=resn_spot,
                                               res_number=900,atm_number=10000,hotspot_type=hotspots_type,b_factor='score_1')
                        # accumulate this round/type's tier-1 candidates (all points past the tag threshold)
                        
                        # find the hotspot score greater than score_lim_hotspot
                        # ind_step_2 = np.where(p_atoms['score_1'] > d_parameters['f_good_score_threshold']) # HERE we can change which score we want to keep
                        # select ind where p_atoms['score_1'] > d_parameters['f_good_score_threshold'] and p_atoms['score_total'] > 0.6
                        ind_step_2 = np.where((p_atoms['score_1'] > d_parameters['f_good_score_threshold']) & (p_atoms['score_total'] > 0.3))
                        if len(ind_step_2[0]) == 0:
                            print('No hotspot atoms found')
                            continue
                        p_atoms_2 = p_atoms[ind_step_2]
                        p_atoms['generation'][ind_step_2] = 2 # generation round of the hotspot atom initialization to 2
                        # write all the atoms in a pdb
                        update_atoms_and_write(o_structure.a_atoms, p_atoms_2, file_name + '_step_2.pdb',res_name=resn_spot,
                                               res_number=901, atm_number=10000,hotspot_type=hotspots_type)
                        # accumulate this round/type's tier-2 candidates (past the good-score filter)
                        


                        ### STEP 4: Merge hotspot atoms to close from each other into only one point

                        # sort the atoms by score decreasing
                        ord_score = np.argsort(-p_atoms_2['score_total'], kind='stable')  # sort by score decreasing
                        p_atoms_3 = p_atoms_2[ord_score]
       
                        # convert to numpy array
                        a_hotspot_coord_2 = np.array([p_atoms_3['grid_x'], p_atoms_3['grid_y'], p_atoms_3['grid_z']]).T

                        o_hotspot_tree = KDTree(a_hotspot_coord_2, leaf_size=50000, metric='euclidean')  # create KDTree

                        # get the optimal distance between two hotspot type at the first position
                        type_hotspot = gp.D_ELEMENT_NUMBER[hotspots_type]
                        d_opti = gp.O_SYSTEM_HOTSPOT.d_d_distance_score[type_hotspot][type_hotspot][1]['optimal_distance']
                        # calculate the distance inferior to optimal distance -1 to have two of the atoms as first neighbors to remove clashes
                        # query the tree to get the index of the neighbors
                        p_i_index = o_hotspot_tree.query_radius(a_hotspot_coord_2,d_opti)
                        ind_step_3 = []
                        # Keep the hotspot with minimum tag by keeping only the index if he is the minimum of his environment
                        for h_ind in range(len(p_i_index)): # loop over the indexes
                            if p_i_index[h_ind][0] == h_ind: # if the first neighbor is the atom itself
                                ind_step_3.append(h_ind) # keep the atom

                        if len(ind_step_3) == 0:
                            print('No hotspot atoms found')
                            continue
                        p_atoms_cleaned = p_atoms_3[ind_step_3]
                        # update generation round of the hotspot atom initialization to 3
                        ind_final_hotspot = ind_step_2[0][ord_score[ind_step_3]] # get the index of the final hotspot in the original p_atoms
                        p_atoms['generation'][ind_final_hotspot] = 3

                        print('Number of', hotspots_type, 'hotspot atoms added to', o_structure.s_name, ': ',
                              len(p_atoms_cleaned))
                        l_atoms = update_atoms_and_write(o_structure.a_atoms, p_atoms_cleaned, file_name + '_step_3.pdb',
                                                         res_name=resn_spot,hotspot_type=hotspots_type)
                        # accumulate this round/type's tier-3 candidates (final, deduplicated positions)
                    
                        l_hotspot_rows.extend(build_hotspot_rows(
                            p_atoms,  int(o_structure.a_atoms['residue_serial'][-1]), hotspots_round, resn_spot, hotspots_type))
                    setattr(o_structure, resn_spot + '_a_atoms', l_atoms)
                    # save the atoms as CSV
                    pd.DataFrame(getattr(o_structure,resn_spot + '_a_atoms')).to_csv(file_name + '_scored.csv', index=False)
                    # add the new atoms indexes to the pocket indexes
                    if type(o_structure.pocket_indexes) is not slice:
                        l_p_index = np.append(o_structure.pocket_indexes,
                                              np.arange(len(o_structure.a_atoms),
                                                        len(o_structure.a_atoms) + len(p_atoms_cleaned)))
                        setattr(o_structure, resn_spot + '_pocket_indexes', l_p_index)

                # Create pymol session of the different steps
                l_hotspot = d_parameters['s_hotspot_type'].split()
                pymol_time = time.time()
                if hotspots_round == 1:
                    cmd.reinitialize()
                    # os.chdir(fold_out)
                    os.chdir(d_parameters["p_unprocessed_pdb"])
                    # os.chdir('/home/dreano/Desktop/Grid_methods/data/input/hotspot/') # to FIX
                    cmd.load(o_structure.s_name + '.pdb')
                else:
                    cmd.load(fold_out + '/' + o_structure.s_name + '_hotspot.pse')

                pdb = o_structure.s_name
                os.chdir(fold_out)
                files = os.listdir()
                for file in files:
                    if 'step_3' in file:
                        cmd.load(file)
                    if 'step_2' in file:
                        cmd.load(file)
                    if 'step_1' in file:
                        cmd.load(file)
                if hotspots_round == 1:
                    cmd.align(pdb, pdb+'*_step_2')
                for hotspots_type in l_hotspot:
                    sele_name = hotspots_type.replace('.','')[0:3]
                    cmd.create(sele_name + '_' + str(hotspots_round) + '_s1', 'resn '+sele_name + ' and ' + pdb+'*step_1')
                    cmd.create(sele_name + '_' + str(hotspots_round) + '_s2', 'resn '+sele_name + ' and ' + pdb+'*step_2')
                    cmd.create(sele_name + '_' + str(hotspots_round) + '_s3', 'resn '+sele_name + ' and ' + pdb+'*step_3')
                cmd.delete(pdb+'*step_*')
                # cmd.group('grp_'+ pdb , '*'+pdb + '*')
                # cmd.color('green', 'all')
                # Define PyMOL's default color cycle list
                cmd.show('spheres', '*_s1')
                cmd.show('spheres', '*_s2')
                cmd.show('spheres', '*_s3')
                cmd.show('nonbonded', '*_s3')
                default_colors = [
                     'green','cyan', 'magenta', 'yellow', 'orange', 'slate', 'purple', 'wheat',
                    'white', 'black', 'red', 'blue', 'bluewhite', 'tv_blue', 'density'
                ]
                cmd.util.cbag('all')
                for ind_col in range(1,len(l_hotspot)+1):
                    cmd.color(default_colors[ind_col], '*'+l_hotspot[ind_col-1].replace('.','')[0:3]+'_*')

                # Set the sphere scale and color for each hotspot steps
                cmd.set('sphere_scale', 0.05, '*_s1')
                cmd.set('sphere_scale', 0.2, '*_s2')
                cmd.set('sphere_scale', 0.5, '*_s3')

                cmd.set('sphere_transparency', 0.5, '*_s2')
                cmd.set('sphere_transparency', 0.5, '*_s3')
                # set step 1 in b_factor range 0-1
                cmd.spectrum("b", selection="*_s1",minimum=0,maximum=1)
                # organize output folder to have one folder par hotspot type
                for h_type in l_hotspot:
                    cmd.group(h_type, h_type.replace('.','')[0:3]+'_*')
                    hotspots_type = h_type.replace('.','_')
                    mask = pdb+'_'+hotspots_type+'_round'
                    os.makedirs(fold_out + '/' + hotspots_type, exist_ok=True)
                    for file in os.listdir():
                        if mask in file:
                            shutil.move(file, fold_out + '/' + hotspots_type)
                for obj in cmd.get_names():
                    if cmd.get_type(obj) == 'object:molecule':
                        if cmd.count_atoms(obj) == 0:
                            cmd.delete(obj)
                    elif cmd.get_type(obj) == 'object:group':
                        if len(cmd.get_object_list(obj)) == 0:
                            cmd.delete(obj)
                cmd.save(fold_out + '/' + hotspots_type + '/' + pdb + '_aligned.pdb',pdb,0,'pdb')
                if gp.D_PARAMETERS_GLOBAL['pymol_session'] is True:
                    cmd.save(fold_out + '/' + o_structure.s_name + '_hotspot.pse')
                print("Pymol session created in {:.1f} seconds".format(time.time() - pymol_time))
                if 'O_3_wat' in os.listdir(fold_out):
                    distance_hotspot_water(fold_out+'/O_3_wat', str(hotspots_round),
                    gp.D_PARAMETERS_HOTSPOT['p_input_pdb'] + '/' + o_structure.s_name + '.pdb')
                    #'/home/dreano/Desktop/Grid_methods/data/output/hotspot/Score_test_set/test_set_scored/'+pdb+'/'+pdb+'_scored.pdb')
                    # '/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/test_set_hotspot/04_11_2024-17_37/5WQC/5WQC_scored.pdb')
            # combined CIF : scored structure atoms + every hotspot candidate point found
            # across every round/type/tier, in one file
            hotspot_cif(fold_out + '/' + o_structure.s_name + '_hotspot.cif', o_structure,
                       gp.O_SYSTEM_HOTSPOT, d_parameters, l_hotspot_rows=l_hotspot_rows,
                       d_view_meta=gp.D_HOTSPOT_VIEW_META.get(o_structure.s_name))
        except Exception as e:
            print('Error in structure hotspot', o_structure.s_name)
            print(e)
        # ---------------------------------------------------------------------------- #

#
# ### STEP 5: Compute the score of each atom in the structure after integration of the hotspot atoms
#
# a_atom_coord_2 = np.array(
#     [[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in o_structure.a_atoms])
#
# # Create a KDTree using atom coordinates
# o_structure.o_tree = KDTree(a_atom_coord_2, leaf_size=50000, metric='euclidean')
#
# origin_coord_2 = np.array([[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in
#                            o_structure.a_atoms[o_structure.pocket_indexes]])
#
# l_score_2 = score_environment(origin_coord, o_structure, True, hotspots_type)
# score_total_2 = [np.sum(score) / 3 for score in l_score_2]
#
# ## TO IMPROVE
# h = 0
# l = 0
# e = 0
# for i in range(len(l_score_2)):
#     if score_total_2[i] > score_total_1[i]:
#         l += 1
#         print('LOWER ' + str(i) + ' : ' + str(score_total_1[i]) + ' -> ' + str(score_total_2[i]))
#     elif score_total_2[i] < score_total_1[i]:
#         h += 1
#         print('HIGHER ' + str(i) + ' : ' + str(score_total_1[i]) + ' -> ' + str(score_total_2[i]))
#     else:
#         e += 1
#         print('EGUAL ' + str(i) + ' : ' + str(score_total_1[i]) + ' -> ' + str(score_total_2[i]))
# o_structure.a_atoms = o_structure.a_atoms_bk
# function to extract coordinates of water molecules (residu HOH) from a pdb file

def distance_random_water(folder,pdb_ref):
    os.chdir(folder)
    l_s_files = os.listdir()
    # remove the file ending with 'round_1_scored.pdb'
    l_s_files = [s_file for s_file in l_s_files if 'round_1_scored.pdb' not in s_file]

    # align the reference pdb file with the pdb file of the round 1
    cmd.reinitialize()
    cmd.load(pdb_ref)
    cmd.load(l_s_files[0])

    cmd.align(pdb_ref.split('/')[-1][:-4], l_s_files[0][:-4])
    cmd.save('aligned_ref.pdb', pdb_ref.split('/')[-1][:-4], 0, 'pdb')
    pdb_ref = read_file_content('aligned_ref.pdb')
    l_hoh_coord = []
    l_hoh_resid = []
    l_score_water = []
    for s_line in pdb_ref:
        if s_line.startswith("HETATM") and s_line[17:20] == "HOH":
            l_hoh_coord.append([s_line[30:38].strip(),s_line[38:46].strip(),s_line[46:54].strip()])
            l_hoh_resid.append(int(s_line[22:26].strip()))
            l_score_water.append(1-float(s_line[60:66].strip()))
    l_hoh_resid = np.array(l_hoh_resid)
    l_hoh_coord = np.array(l_hoh_coord)
    l_score_water = np.array(l_score_water)

    o_water_tree = KDTree(l_hoh_coord, leaf_size=50000, metric='euclidean')

    for pdb in l_s_files:
        f_rd = read_file_content(pdb)
        if 'clean' in pdb:
            method = 'clean'
        if 'full_random' in pdb:
            method = 'full_random'
        n_run = pdb.split('.')[0][-1]
        l_spot = []
        l_score = []
        l_spot_resid = []
        for s_line in f_rd:
            if s_line.startswith("HETATM") and s_line[17:20] == "O3w":
                l_spot.append([s_line[30:38].strip(), s_line[38:46].strip(), s_line[46:54].strip()])
                l_spot_resid.append(int(s_line[22:26].strip()))
                l_score.append(1 - float(s_line[60:66].strip()))
        l_spot = np.array(l_spot)
        l_score = np.array(l_score)
        l_spot_resid = np.array(l_spot_resid)
        a_f_distance, a_i_index = o_water_tree.query(l_spot, k=1)
        df = pd.DataFrame({'Spot residual number': l_spot_resid,
                           'Water residual number': l_hoh_resid[a_i_index].flatten(),
                           'distance': a_f_distance.flatten(),
                            'step': 1, 'score_water': l_score_water[a_i_index].flatten(), 'score_spot': l_score,
                            'coordinate_x': l_spot[:, 0].flatten(), 'coordinate_y': l_spot[:, 1].flatten(),
                            'coordinate_z': l_spot[:, 2].flatten()})
        df = df.sort_values(by=['Spot residual number', 'distance']).reset_index(drop=True)
        df.to_csv('Closest_water_distance_'+method+'_'+n_run+'.csv',index=False)

        o_rand_tree = KDTree(l_spot, leaf_size=50000, metric='euclidean')
        rand_dist, rand_ind = o_rand_tree.query(l_hoh_coord, k=1)
        df_rand = pd.DataFrame({'Water residual number': l_hoh_resid.flatten(), 'Spot residual number': l_spot_resid[rand_ind].flatten(),
                                'distance': rand_dist.flatten(), 'score_water': l_score_water.flatten(), 'score_spot' : l_score[rand_ind].flatten(),
                              'coordinate_x': l_hoh_coord[:, 0].flatten(), 'coordinate_y': l_hoh_coord[:, 1].flatten(),
                              'coordinate_z': l_hoh_coord[:, 2].flatten()})

        df_rand = df_rand.sort_values(by=['Water residual number', 'distance']).reset_index(drop=True)
        df_rand.to_csv('Closest_spot_distance_'+method+'_'+n_run+'.csv',index=False)

    return 0

def distance_hotspot_water(folder,round,pdb_ref):
    os.chdir(folder)
    l_s_files = os.listdir()
    for pdb in l_s_files:
        if 'round_'+round+'_step_1.pdb' in pdb:
            # align the reference pdb file with the pdb file of the round 1
            cmd.reinitialize()
            cmd.load(pdb_ref)
            cmd.load(pdb)
            cmd.align(pdb_ref.split('/')[-1][:-4], pdb[:-4])
            cmd.save('aligned_ref.pdb',pdb_ref.split('/')[-1][:-4],0,'pdb')
            f_step1 = read_file_content(pdb)
        if 'round_'+round+'_step_2.pdb' in pdb:
            f_step2 = read_file_content(pdb)
        if 'round_'+round+'_step_3.pdb' in pdb:
            f_step3 = read_file_content(pdb)

    pdb_ref = read_file_content('aligned_ref.pdb')
    if not f_step3:
        print('No pdb file found')
        return

    # l_hoh_coord = np.array([[s_line[30:38].strip(),s_line[38:46].strip(),s_line[46:54].strip()]
    #                         for s_line in water_file if s_line.startswith("HETATM") and s_line[17:20] == "HOH"])
    l_spot_s1 = []
    l_score_s1 = []
    for s_line in f_step1:
        if s_line.startswith("HETATM") and s_line[17:20] == "O3w":
            l_spot_s1.append([s_line[30:38].strip(), s_line[38:46].strip(), s_line[46:54].strip()])
            l_score_s1.append(1-float(s_line[60:66].strip()))
    l_spot_s1 = np.array(l_spot_s1)
    l_score_s1 = np.array(l_score_s1)

    l_spot_s2 = []
    l_score_s2 = []
    for s_line in f_step2:
        if s_line.startswith("HETATM") and s_line[17:20] == "O3w":
            l_spot_s2.append([s_line[30:38].strip(), s_line[38:46].strip(), s_line[46:54].strip()])
            l_score_s2.append(1-float(s_line[60:66].strip()))
    l_spot_s2 = np.array(l_spot_s2)
    l_score_s2 = np.array(l_score_s2)

    l_spot_s3 = []
    l_score_s3 = []
    for s_line in f_step3:
        if s_line.startswith("HETATM") and s_line[17:20] == "O3w":
            l_spot_s3.append([s_line[30:38].strip(), s_line[38:46].strip(), s_line[46:54].strip()])
            l_score_s3.append(1-float(s_line[60:66].strip()))
    l_spot_s3 = np.array(l_spot_s3)
    l_score_s3 = np.array(l_score_s3)

    # l_spot_s2 = np.array([[s_line[30:38].strip(),s_line[38:46].strip(),s_line[46:54].strip()]
    #                     for s_line in f_step2 if s_line.startswith("HETATM") and s_line[17:20] == "O3w"])
    # # l_spot_s3 = np.array([[s_line[30:38].strip(),s_line[38:46].strip(),s_line[46:54].strip()]
    # #                     for s_line in f_step3 if s_line.startswith("HETATM") and s_line[17:20] == "O3w"])

    l_hoh_coord = []
    l_hoh_resid = []
    l_score_water = []
    for s_line in pdb_ref:
        if s_line.startswith("HETATM") and s_line[17:20] == "HOH":
            l_hoh_coord.append([s_line[30:38].strip(),s_line[38:46].strip(),s_line[46:54].strip()])
            l_hoh_resid.append(int(s_line[22:26].strip()))
            l_score_water.append(1-float(s_line[60:66].strip()))
    l_hoh_resid = np.array(l_hoh_resid)
    l_hoh_coord = np.array(l_hoh_coord)
    l_score_water = np.array(l_score_water)

    # create a KDTree object with the coordinates of the water molecules
    o_water_tree = KDTree(l_hoh_coord, leaf_size=50000, metric='euclidean')
    # create a KDTree object with the coordinates of the hotspots in step 1
    o_step1_tree = KDTree(l_spot_s1, leaf_size=50000, metric='euclidean')
    # create a KDTree object with the coordinates of the hotspots in step 2
    o_step2_tree = KDTree(l_spot_s2, leaf_size=50000, metric='euclidean')
    # create a KDTree object with the coordinates of the hotspots in step 3
    o_step3_tree = KDTree(l_spot_s3, leaf_size=50000, metric='euclidean')

    # calculate the distance between each hotspot in step 1 and the closest water molecule
    # d_s1_wat -> d for distance, s1 for the origin coordinates, wat for the destination coordinates (tree)
    d_s1_wat, i_s1_wat = o_water_tree.query(l_spot_s1, k=1)

    # caluculate the distance between each water molecule and the closest hotspot in step 1
    d_wat_s1, i_wat_s1 = o_step1_tree.query(l_hoh_coord, k=1)

    # caluculate the distance between each water molecule and the closest hotspot in step 2
    d_wat_s2, i_wat_s2 = o_step2_tree.query(l_hoh_coord, k=1)

    # caluculate the distance between each water molecule and the closest hotspot in step 3
    d_wat_s3, i_wat_s3 = o_step3_tree.query(l_hoh_coord, k=1)

    df_spot_s2 = pd.DataFrame(l_spot_s2, columns=['coordinate_x', 'coordinate_y', 'coordinate_z'])
    df_spot_s3 = pd.DataFrame(l_spot_s3, columns=['coordinate_x', 'coordinate_y', 'coordinate_z'])

    # create a dataframe with the water molecules as origin
    df_water = pd.DataFrame(l_hoh_coord, columns=['HOH_x', 'HOH_y', 'HOH_z'])
    df_water['HOH_resid'] = l_hoh_resid
    df_water['Score_water'] = l_score_water
    df_water['Step'] = 1
    df_water['HOTSPOT_x_s1'] = l_spot_s1[i_wat_s1, 0].flatten()
    df_water['HOTSPOT_y_s1'] = l_spot_s1[i_wat_s1, 1].flatten()
    df_water['HOTSPOT_z_s1'] = l_spot_s1[i_wat_s1, 2].flatten()
    df_water['Distance_s1'] = d_wat_s1.flatten()
    df_water['HOTSPOT_score_s1'] = l_score_s1[i_wat_s1].flatten()
    df_water['HOTSPOT_x_s2'] = l_spot_s2[i_wat_s2, 0].flatten()
    df_water['HOTSPOT_y_s2'] = l_spot_s2[i_wat_s2, 1].flatten()
    df_water['HOTSPOT_z_s2'] = l_spot_s2[i_wat_s2, 2].flatten()
    df_water['Distance_s2'] = d_wat_s2.flatten()
    df_water['HOTSPOT_score_s2'] = l_score_s2[i_wat_s2].flatten()
    df_water['HOTSPOT_x_s3'] = l_spot_s3[i_wat_s3, 0].flatten()
    df_water['HOTSPOT_y_s3'] = l_spot_s3[i_wat_s3, 1].flatten()
    df_water['HOTSPOT_z_s3'] = l_spot_s3[i_wat_s3, 2].flatten()
    df_water['Distance_s3'] = d_wat_s3.flatten()
    df_water['Score_spot_s3'] = l_score_s3[i_wat_s3].flatten()
    df_water.loc[df_water[['HOTSPOT_x_s1', 'HOTSPOT_y_s1', 'HOTSPOT_z_s1']].apply(tuple, 1).isin(df_spot_s2.apply(tuple,1)), 'Step'] = 2
    df_water.loc[df_water[['HOTSPOT_x_s1', 'HOTSPOT_y_s1', 'HOTSPOT_z_s1']].apply(tuple, 1).isin(df_spot_s3.apply(tuple,1)), 'Step'] = 3

    # create a dataframe with the hotspot atoms as origin
    df_hotspot = pd.DataFrame(l_spot_s1, columns=['HOTSPOT_x', 'HOTSPOT_y', 'HOTSPOT_z'])
    df_hotspot['Score_spot'] = l_score_s1
    df_hotspot['Step'] = 1
    df_hotspot['HOH_x'] = l_hoh_coord[i_s1_wat, 0].flatten()
    df_hotspot['HOH_y'] = l_hoh_coord[i_s1_wat, 1].flatten()
    df_hotspot['HOH_z'] = l_hoh_coord[i_s1_wat, 2].flatten()
    df_hotspot['Distance'] = d_s1_wat.flatten()
    df_hotspot['HOH_resid'] = l_hoh_resid[i_s1_wat].flatten()
    df_hotspot['Score_water'] = l_score_water[i_s1_wat].flatten()
    df_hotspot.loc[df_hotspot[['HOTSPOT_x', 'HOTSPOT_y', 'HOTSPOT_z']].apply(tuple, 1).isin(df_spot_s2.apply(tuple,1)), 'Step'] = 2
    df_hotspot.loc[df_hotspot[['HOTSPOT_x', 'HOTSPOT_y', 'HOTSPOT_z']].apply(tuple, 1).isin(df_spot_s3.apply(tuple,1)), 'Step'] = 3

    # write in a csv file
    df_water.to_csv('water_distance_'+round+'.csv', index=False)
    df_hotspot.to_csv('hotspot_distance_'+round+'.csv', index=False)
    #
    # df = pd.DataFrame({'HOH_resid': l_hoh_resid[i_wat_s1].flatten(), 'HOH_x': l_hoh_coord[i_wat_s1, 0].flatten(),
    #                    'HOH_y': l_hoh_coord[i_wat_s1, 1].flatten(), 'HOH_z': l_hoh_coord[i_wat_s1, 2].flatten(),
    #                    'HOTSPOT_x': l_spot_s1[:, 0].flatten(), 'HOTSPOT_y': l_spot_s1[:, 1].flatten(),
    #                    'HOTSPOT_z': l_spot_s1[:, 2].flatten(), 'distance': d_wat_s1.flatten(),
    #                    'distance': d_wat_s1.flatten(),
    #                    'step': 1, 'score_water': l_score_water[i_wat_s1].flatten(), 'score_spot' : l_score_s1,
    #                    'coordinate_x': l_spot_s1[:, 0].flatten(), 'coordinate_y': l_spot_s1[:, 1].flatten(),
    #                    'coordinate_z': l_spot_s1[:, 2].flatten()})


    # sort the dataframe by "Water residual number" and "distance" and reset the index
    # df= df.sort_values(by=['Water residual number', 'distance']).reset_index(drop=True)
    #
    # # Convert l_spot_s2 to a DataFrame for easier comparison
    # df_spot_s2 = pd.DataFrame(l_spot_s2, columns=['coordinate_x', 'coordinate_y', 'coordinate_z'])
    #
    # # Update 'step' value to 2 where coordinates match with those in l_spot_s2
    # df.loc[df[['coordinate_x', 'coordinate_y', 'coordinate_z']].apply(tuple, 1).isin(df_spot_s2.apply(tuple, 1)), 'step'] = 2
    # # Update 'step' value to 3 where coordinates match with those in l_spot_s3
    # df_spot_s3 = pd.DataFrame(l_spot_s3, columns=['coordinate_x', 'coordinate_y', 'coordinate_z'])
    # df.loc[df[['coordinate_x', 'coordinate_y', 'coordinate_z']].apply(tuple, 1).isin(df_spot_s3.apply(tuple, 1)), 'step'] = 3
    #
    # df['step'] = df['step'].astype('category')
    # write in a csv file
    # df.to_csv('water_distance'+round+'.csv', index=False)
    # import matplotlib.pyplot as plt
    # from matplotlib.colors import ListedColormap
    #
    # # Define a colormap
    # cmap = ListedColormap(['red', 'green', 'blue'])  # Add more colors if you have more categories
    # plt.figure(figsize=(10, 6))
    # # order df by step
    # df = df.sort_values(by='step')
    # # Create a scatter plot
    # scatter = plt.scatter(df['distance'],df['score_spot'], c=df['step'].cat.codes, cmap=cmap)
    # # fix x limit
    # plt.xlim(0, 10)
    # plt.ylim(0, 1)
    # # Set the labels for the x and y axes
    # plt.xlabel('Distance')
    # plt.ylabel('Score')
    #
    # # Add a colorbar to the plot
    # cbar = plt.colorbar(scatter, ticks=[0, 1, 2])  # Assuming you have 3 categories: 1, 2, 3
    # cbar.set_label('Step')
    # cbar.set_ticklabels(df['step'].cat.categories)
    #
    # # save the plot
    # plt.savefig('water_distance'+round+'.png')
    # plt.savefig('water_distance'+round+'.svg', format='svg')
    # #coordinate of hotspot step_2
    #
    # # distance between hotspot atoms and water molecules with hotspot as origin
    # o_hotspot_tree = KDTree(l_spot_s3, leaf_size=50000, metric='euclidean')
    # dist_hotspot, index_hotspot = o_hotspot_tree.query(l_hoh_coord, k=1)
    #
    # # create a dataframe with the field "Water residual number", "distance" and "coordinates"
    # df_2 = pd.DataFrame({'Water residual number': l_hoh_resid.flatten(), 'distance': dist_hotspot.flatten(),
    #                       'score_water': l_score_water.flatten(), 'score_spot' : l_score_s3[index_hotspot].flatten(),
    #                       'coordinate_x': l_hoh_coord[:, 0].flatten(), 'coordinate_y': l_hoh_coord[:, 1].flatten(),
    #                       'coordinate_z': l_hoh_coord[:, 2].flatten()})
    # # write in a csv file
    # df_2.to_csv('Closest_hotspot_distance_'+round+'.csv', index=False)
    # # plot the distance between hotspot atoms and water molecules
    # plt.figure(figsize=(10, 6))
    # # Create a scatter plot
    # scatter = plt.scatter(df_2['distance'],df_2['score_water'], c=df_2['score_spot'], cmap='viridis')
    #
    # # set the x limit
    # plt.xlim(0, 10)
    # plt.ylim(0, 1)
    #
    # # Set the labels for the x and y axes
    # plt.xlabel('Distance')
    # plt.ylabel('Score_water')
    #
    # # Add a colorbar to the plot
    # cbar = plt.colorbar(scatter)
    # cbar.set_label('Score_spot')
    #
    # # save the plot
    # plt.savefig('water_distance_hotspot'+round+'.png')
    # plt.savefig('water_distance_hotspot'+round+'.svg', format='svg')


    return l_hoh_coord


# # function that place randomly water molecules in the grid
def place_water_random(o_structure,nb_water,remove_clashes=False):
    # get the grid size
    val_max = 0
    for x in gp.O_SYSTEM_HOTSPOT.d_d_distance_score.keys():
        try:
            tmp = gp.O_SYSTEM_HOTSPOT.d_d_distance_score[x][226][3]['optimal_distance']
            if val_max < tmp:
                val_max = tmp
        except KeyError:
            continue
    # get nb_water random coordinates

    min_x = np.min(o_structure.a_atoms['grid_x'])-val_max
    max_x = np.max(o_structure.a_atoms['grid_x'])+val_max
    min_y = np.min(o_structure.a_atoms['grid_y'])-val_max
    max_y = np.max(o_structure.a_atoms['grid_y'])+val_max
    min_z = np.min(o_structure.a_atoms['grid_z'])-val_max
    max_z = np.max(o_structure.a_atoms['grid_z'])+val_max

    l_hots_rd = np.zeros(0,dtype=gp.p_atom_dtype)
    while len(l_hots_rd) < nb_water:
        nb_random = nb_water - len(l_hots_rd)
        l_water = np.zeros(nb_random, dtype=gp.p_atom_dtype)
        l_water['grid_x'] = np.random.randint(min_x, max_x, nb_random)
        l_water['grid_y'] = np.random.randint(min_y, max_y, nb_random)
        l_water['grid_z'] = np.random.randint(min_z, max_z, nb_random)
        if remove_clashes:
            ori = np.array([[a_atom['grid_x'], a_atom['grid_y'], a_atom['grid_z']] for a_atom in l_water])
            a_f_distance, a_i_index = o_structure.o_tree.query(ori,k=1)
            # find all distances < 2A and append the water molecules to the l_hots_rd list so we need to scale the distance based on the grid spacing
            l_water = l_water[np.where(a_f_distance * gp.D_PARAMETERS_GLOBAL["f_grid_spacing"] > 1 )[0]]
        l_hots_rd = np.append(l_hots_rd,l_water)
    return l_hots_rd