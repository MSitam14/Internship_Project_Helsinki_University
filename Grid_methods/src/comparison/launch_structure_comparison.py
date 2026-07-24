# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano, Samuel Besseau
# Contact : samuelbesseau77@gmail.com
# University of Helsinki
# Created : June 2020
# Updated : May 2023
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #


import multiprocessing as mp
import subprocess
import time

import ete3
from collections import Counter
import pandas as pd
import psutil
import seaborn as sns
# Universal modules
from tqdm import tqdm
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

from scipy.cluster.hierarchy import linkage, leaves_list, dendrogram
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
# Contains the global variables
# Classes
from cla.systeme_class import System
# Specific modules
from comparison.compute_grid_similarity import compute_grid_similarity
from comparison.tree_object import TreePlot
# Parameters
from lib import global_parameters as gp
# Retrieves files path, recursively or not, matching a specific pattern, or not
# In : (p) directory to retrieve files from, (s) pattern to match,
# In : (b) if the search needs to be recursive, (i) minimum number of match,
# In : (i) maximum number of match
# Out : (l(p)) a list of the file paths founds
from lib.parse_pdb_file import parse_pdb_file
# General library
from lib.retrieve_specific_files import retrieve_specific_files
# Extracts a PDB structure from a file and applies filters
# In : (p) PDB file to extract, (d) parsing filters to apply
# Out : (o) the object containing the structure
from lib.terminate_program_process import terminate_program_process
from lib.Grid_plot import *
from lib.progress_bar_color import get_color
# Generates, renders and saves trees
# Stops the program and prints content
# In : (l(s)) content to prompt
# Out : None
# Computes the similarity between two grids
	# In : (d) comparison parameters, (o) the first structure to compare,
	# In : (o) the second structure to compare
	# Out : (f) the percentage of similarity

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #



def launch_structure_comparison(d_parameters):
	"""
	Manages the comparison of structures
		Retrieves the PDB input files
		Extracts the PDB structures
		Compares the structures
		Generates a tree
	"""

	# STEP 0 : Preparing variables ---------------------- #
	l_s_logs = []									# A list for log
	gp.O_SYSTEM_COMPARISON = System()
	gp.O_SYSTEM_COMPARISON.initialize_system(		# Initializes system fields
		d_parameters=gp.D_PARAMETERS_COMPARISON		# The parameters used for the system initial configuration
	)
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : Find PDB files --------------------------- #

	l_p_input_pdb = retrieve_specific_files(						# Retrieves PDB paths
		p_directory=gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/cleaned_dataset',		# Path to the input directory
		s_pattern="*.pdb",											# Pattern to match within the directories
		b_recursive=True,											# Also searches in the subdirectories
		i_min_match=1,												# Minimum number of files to retrieve
		i_max_match=9999											# Maximum number of files to retrieve
	)
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Extracts PDB structures ------------------ #

	# For each PDB file to parse
	for p_pdb in l_p_input_pdb :
		o_structure = parse_pdb_file(p_file=p_pdb) # Extracts a PDB structure into an object
		gp.O_SYSTEM_COMPARISON.l_o_structures.append(o_structure)		# Registers the structure in the system


	gp.O_SYSTEM_COMPARISON.update_system_properties()		# Actualizes the system properties depending on the structures
	# END STEP 2 ---------------------------------------- #

	# STEP 3 : Security check --------------------------- #
	# If there is not enough file
	if len(gp.O_SYSTEM_COMPARISON.l_o_structures) < 2:
		l_s_logs.append("ERROR : There is not enough valid PDB structure to run a comparison, at least 2 are required")		# Defines the error message
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save to logs
		)
	# END STEP 3 ---------------------------------------- #

	# STEP 4 : Grid generation using multiprocess -------------- #
	if gp.D_PARAMETERS_GLOBAL["i_cpu_allocated"] is not None:
		i_cpu_count = gp.D_PARAMETERS_GLOBAL["i_cpu_allocated"]

	# If the user has not defined a number of CPU to use
	else:
		i_cpu_count = mp.cpu_count()  # Retrieves the number of CPU available
		gp.D_PARAMETERS_GLOBAL["i_cpu_allocated"] = i_cpu_count
	starting_time = time.time()
	for structure in gp.O_SYSTEM_COMPARISON.l_o_structures:
		gp.O_SYSTEM_COMPARISON.generate_grid(o_structure=structure, d_parameters=gp.D_PARAMETERS_COMPARISON)

	with mp.Pool(processes=i_cpu_count) as o_pool:
		# Creates a pool of process
		with tqdm(total=len(gp.O_SYSTEM_COMPARISON.l_o_structures), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180,
				  smoothing=1) as pbar:
			l_o_structures_mp = []
			for i, result in enumerate(
					o_pool.imap_unordered(multi_process_generate_grid, gp.O_SYSTEM_COMPARISON.l_o_structures)):
				l_o_structures_mp.append(result)
				progress = i / (len(gp.O_SYSTEM_COMPARISON.l_o_structures) -1)
				pbar.set_description(get_color(progress) + "Generating grids")
				pbar.update()
			o_pool.close()
			o_pool.join()
	print("Grids generated in {:.1f} seconds".format(time.time() - starting_time))
	print('')
		# with tqdm(total=len(gp.O_SYSTEM_COMPARISON.l_o_structures), bar_format='{l_bar}{bar:80}{r_bar}', ncols= 180, smoothing=1) as pbar:
		# 	pbar.set_description('\033[1;38;2;255;190;0m' + "Generating grids")
		# 	l_o_structures_mp = []
		# 	for result in o_pool.imap_unordered(multi_process_generate_grid, gp.O_SYSTEM_COMPARISON.l_o_structures):
		# 		l_o_structures_mp.append(result)
		# 		pbar.update()
		# 	o_pool.close()
		# 	o_pool.join()

	# Update the list of structures
	gp.O_SYSTEM_COMPARISON.l_o_structures = l_o_structures_mp
	del l_o_structures_mp
	# END STEP 4 ---------------------------------------- #


	# STEP 4.1 : Determining the normalisation method ----- #
	s_normalisation = gp.D_PARAMETERS_COMPARISON["s_comparison_normalisation"].upper()		# Retrieves the normalisation method to use

	# If the program needs to retrieve the number of nonempty points for each structure
	if s_normalisation == "GLOBAL_MIN" or s_normalisation == "GLOBAL_MAX":
		l_structure_size = []		# List containing the size of each structure
		# For each loaded structure
		for o_structure in gp.O_SYSTEM_COMPARISON.l_o_structures:
			l_structure_size.append(o_structure.a_vdw.size)		# Counts the number of points containing atoms
			o_structure.a_grid = None
	# If the similarity needs to be based on the minimal number of empty points
	if s_normalisation == "GLOBAL_MIN":
		gp.D_PARAMETERS_COMPARISON["i_atom_total"] = min(l_structure_size)		# Retrieves the minimal number of non empty points

	if s_normalisation == "GLOBAL_MAX":
		gp.D_PARAMETERS_COMPARISON["i_atom_total"] = max(l_structure_size)		# Retrieves the maximal number of non empty points
	if s_normalisation == "MAX" or s_normalisation == "MIN" or s_normalisation == "TANIMOTO":
		pass

	else:
		l_s_logs.append("ERROR : Unknown normalisation method. Known methods are 'Min' and 'Max'")
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save in the logs
		)
	# End if
	# END STEP 4.1 ---------------------------------------- #

	# STEP 5: Compute similarity between structures:

	# STEP 5.1: Create list of pairs to compare -------- #
	pair_list = []		# List of pairs to compare
	for i_first_index in range(len(gp.O_SYSTEM_COMPARISON.l_o_structures)):		# For each structure to compare
		for i_second_index in range(i_first_index+1, len(gp.O_SYSTEM_COMPARISON.l_o_structures)):		# For each other structure to compare
				pair_list.append([gp.O_SYSTEM_COMPARISON.l_o_structures[i_first_index],
								  gp.O_SYSTEM_COMPARISON.l_o_structures[i_second_index] ])

	# END STEP 5.1 ---------------------------------------- #

	compare_pairs(pair_list[0])
	# STEP 5.2 : Running the comparison ------------------ #
	# multiprocessing the creation of the grid
	# If the user has defined a number of process to use
	# o_1 = gp.O_SYSTEM_COMPARISON.l_o_structures[0]
	# plot_heatmap(o_1.a_grid, z=15,lab=True)
	# o_2 = gp.O_SYSTEM_COMPARISON.l_o_structures[1]
	# plot_heatmap(o_2.a_grid, z=15,lab=True)
	with mp.Pool(processes=i_cpu_count) as o_pool:  # Creates a pool of process
		l_l_results = []
		with tqdm(total=len(pair_list), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
			for i, result in enumerate(o_pool.imap_unordered(compare_pairs, pair_list)):
				l_l_results.append(result)
				if len(pair_list) == 1:
					progress = 1
				else:
					progress = i / (len(pair_list) - 1)
				pbar.set_description(get_color(progress) + "Processing structures comparisons")
				pbar.update()
		o_pool.close()
		o_pool.join()

	# with mp.Pool(processes=i_cpu_count) as o_pool:		# Creates a pool of process
	# 	l_l_results=[]
	# 	print('')
	# 	with tqdm(total=len(pair_list), bar_format='{l_bar}{bar:80}{r_bar}', ncols= 180, smoothing=1) as pbar:
	# 		pbar.set_description('\033[1;38;2;255;190;0m' + "Processing structures comparisons")
	# 		for result in o_pool.imap_unordered(compare_pairs, pair_list):
	# 			l_l_results.append(result)
	# 			pbar.update()
	# 	o_pool.close()
	# 	o_pool.join()
	# END STEP 5.2 ---------------------------------------- #

	# STEP 6 : Generating the tree ---------------------- #
	o_tree = TreePlot()		# Creates a tree object

	# For each result to save
	for l_result in l_l_results:
		o_tree.add_score(
			s_first_node=l_result[0],		# The name of the first node to save
			s_second_node=l_result[1],		# The name of the second node to save
			d_comparison= l_result[2] # The score to save (1 - similarity) to have a distance
		)

	# Convert your distance matrix to a NumPy array
	distance_matrix = np.array(o_tree.l_l_distances)

	# Perform hierarchical clustering
	# Convert the symmetric distance matrix to a condensed form (needed for linkage)
	condensed_matrix = squareform(distance_matrix)

	# Perform hierarchical clustering using 'average' linkage
	linkage_matrix = linkage(condensed_matrix, method='average')

	# Compute the optimal leaf ordering
	optimal_order = leaves_list(linkage_matrix)

	# Reorder the distance matrix and labels
	reordered_matrix = distance_matrix[optimal_order, :][:, optimal_order]
	reordered_labels = [o_tree.l_s_nodes[i] for i in optimal_order]
	reordered_coverage = np.array(o_tree.l_l_coverage)[optimal_order, :][:, optimal_order]

	lower_triangular = np.tril(reordered_matrix)

	# lower_triangular = 1 - np.tril(o_tree.l_l_matrix)
	# replace diagonal with 0
	# np.fill_diagonal(lower_triangular, 0)
	# dm2 = DistanceMatrix(t.l_s_nodes, matrix=dm)
	dm = []
	for i in range(lower_triangular.shape[0]):
		row = []
		for j in range(lower_triangular.shape[1]):
			if j <= i:
				row.append(lower_triangular[i, j])
		dm.append(row)

	dm_dist = DistanceMatrix(reordered_labels, matrix=dm)
	## Dataframe
	names = [name[:4] for name in dm_dist.names]
	df_dist = pd.DataFrame(dm_dist.matrix, index=names, columns=names)
	df_dist = df_dist.round(3)
	df_dist.to_excel(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/distances_df.ods', engine='odf')

	df_coverage = pd.DataFrame(reordered_coverage, index=names, columns=names).round(3)
	df_coverage.to_excel(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/coverage_df.ods', engine='odf')

	## Heatmap
	result = subprocess.run(['bash', '-c', f'ls ../data/input/structures_comparison/*.pdb | wc -l'], capture_output=True, text=True)
	structures_number = int(result.stdout.strip())
	# font_scale = structures_number / 486
	# font_size = 20 * font_scale
	font_size = 10
	sns.set(font_scale=0.3)
	plt.figure(figsize=(20, 20), facecolor='white')
	ax = sns.heatmap(df_dist, cmap='YlGnBu', fmt='.2f',
					 cbar_kws={'label': 'Colorbar', 'orientation': 'vertical', 'shrink': 0.5, 'pad': 0.02})
	ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=font_size)
	ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=font_size)
	cbar = ax.collections[0].colorbar
	cbar.ax.tick_params(labelsize=10)
	# plt.savefig(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/distances_heatmap.pdf',
	# 	# 			format='pdf', bbox_inches='tight')
	plt.savefig(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/distances_heatmap.svg',
				format='svg', bbox_inches='tight')

	plt.figure(figsize=(20, 20), facecolor='white')
	ax = sns.heatmap(df_coverage, cmap='YlGnBu_r', fmt='.2f',
					 cbar_kws={'label': 'Colorbar', 'orientation': 'vertical', 'shrink': 0.5, 'pad': 0.02})
	ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=font_size)
	ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=font_size)
	cbar = ax.collections[0].colorbar
	cbar.ax.tick_params(labelsize=10)
	# plt.savefig(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/coverage_heatmap.pdf',
	# 			format='pdf', bbox_inches='tight')
	plt.savefig(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/coverage_heatmap.svg',
				format='svg', bbox_inches='tight')



	## Tree construction
	tree_constructor = DistanceTreeConstructor()
	tree = tree_constructor.nj(dm_dist)
	# Phylo.draw_ascii(tree)
	#global ete3_tree_nj
	ete3_tree_nj = ete3.PhyloTree(tree.format("newick"), format=1)
	ete3_tree_nj.write(outfile=gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/tree_structures.nwk')
	return ete3_tree_nj

	# END STEP 6 ---------------------------------------- #

# ---------------------------------------------------------------------------- #


# Auxiliary functions -------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
def multi_process_generate_grid(structure):
	gp.O_SYSTEM_COMPARISON.generate_grid(o_structure=structure, d_parameters=gp.D_PARAMETERS_COMPARISON)
	return structure


def compare_pairs(pair):
	d_parameters = gp.D_PARAMETERS_COMPARISON
	o_first_structure = pair[0]
	o_second_structure = pair[1]
	if o_first_structure.a_grid is None:
		gp.O_SYSTEM_COMPARISON.generate_grid(o_structure=o_first_structure,d_parameters=d_parameters)
	if o_second_structure.a_grid is None:
		gp.O_SYSTEM_COMPARISON.generate_grid(o_structure=o_second_structure,d_parameters=d_parameters)

	s_normalisation = d_parameters["s_comparison_normalisation"].upper()		# Retrieves the normalisation method to use

	# method using numpy 1D array
	# list of all vdw points in the both structures
	a_atoms_A = o_first_structure.a_vdw
	a_atoms_B = o_second_structure.a_vdw

	# count the number of each atom at each coordinates in the both structures
	count_A = Counter([tuple(row) for row in a_atoms_A])
	count_B = Counter([tuple(row) for row in a_atoms_B])

	# Counts the number of common points between the two structures, taking into account the number of atoms at each point
	intersection = sum(min(count_A[element], count_B[element]) for element in count_A if element in count_B)
	# Determine counts
	len_A = len(a_atoms_A)
	len_B = len(a_atoms_B)

	# containment (overlap relative to smaller set) and coverage (relative to larger set)
	coverage_A_B = 0.0 if len_A == 0 else intersection / len_A # coverage of A by B
	coverage_B_A = 0.0 if len_B == 0 else intersection / len_B # coverage of B by A

	# Tanimoto (Jaccard-like for multisets)
	denom = len_A + len_B - intersection
	tanimoto = 0.0 if denom == 0 else intersection / denom
	d_comparison = { "tanimoto": tanimoto, "coverage_A_by_B": coverage_A_B, "coverage_B_by_A": coverage_B_A }
	# if s_normalisation == "MIN":
	# 	i_normalize = min(len_A, len_B)
	# elif s_normalisation == "MAX":
	# 	i_normalize = max(len_A, len_B)
	# elif s_normalisation == "TANIMOTO":
		# For Tanimoto, denominator is |A| + |B| - intersection
		# i_normalize = len_A + len_B - intersection
	# else:
	# 	i_normalize = d_parameters["i_atom_total"]
	# # similarity calculation (guard division by zero)
	# if i_normalize == 0:
	# 	f_similarity = 0.0
	# else:
	# 	f_similarity = intersection / i_normalize
	# # # #
	if gp.D_PARAMETERS_GLOBAL['explicit_grid']:
		# # ## method using grid so 3D array
		a_grid_A = o_first_structure.a_grid
		a_grid_B = o_second_structure.a_grid
		plot_comparison_heatmap(a_grid_A, a_grid_B, z=9, lab=False,palette=None,
						plot_name=gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/comparison_heatmap.svg')

	return [o_first_structure.s_name, o_second_structure.s_name, d_comparison]




	# # grid_comp = np.bitwise_and(a_grid_A, a_grid_B)
	# #
	# # grid_comp_2 = np.where(a_grid_A == a_grid_B, a_grid_A, 0)
	# # grid_comp_3 = np.where(a_grid_A != a_grid_B, -1, 0)
	# grid_comp_4 = np.where(a_grid_A == a_grid_B, a_grid_A, -1)
	# # plot_heatmap(grid_comp, z=15, lab=True)
	# # plot_heatmap(grid_comp_2, z=15, lab=True)
	# # plot_heatmap(grid_comp_3, z=15, lab=True)
	# plot_heatmap(grid_comp_4, z=15, lab=True)
	# #
	# l_s_logs = []
	#
	# # STEP 1 : Determining the normalization value ------ #
	# if s_normalisation == "MIN":
	# 	i_normalize = min(										# Retrieves the minimal number of non empty points
	# 		np.count_nonzero(a_grid_A),			# Counts the number of non empty points in the first grid
	# 		np.count_nonzero(a_grid_B),		# Counts the number of non empty points in the second grid
	# 	)
	#
	# elif s_normalisation == "MAX":
	# 	i_normalize = max(										# Retrieves the maximal number of non empty points
	# 		np.count_nonzero(a_grid_A),			# Counts the number of non empty points in the first grid
	# 		np.count_nonzero(a_grid_B),		# Counts the number of non empty points in the second grid
	# 	)
	#
	# else:
	# 	i_normalize = d_parameters["i_atom_total"]		# Total of non empty points in the system
	# # END STEP 1 ---------------------------------------- #
	#
	#
	# # STEP 2 : Determining the similarity score --------- #
	# try:
	# 	f_similarity =  (np.count_nonzero(
	# 		np.bitwise_and(a_grid_A, a_grid_B)) / i_normalize		# Computes the similarity percentage
	# 					 )
	# 	a_grid_B.shape
	# 	if d_parameters["Delete_grid"]:
	# 		o_first_structure.delete_grid()  # Frees some memory some memory
	# 		o_second_structure.delete_grid()  # Frees some memory some memory
	# 	return [o_first_structure.s_name,o_second_structure.s_name,f_similarity]
	#
	# except ZeroDivisionError:
	# 	l_s_logs.append("ERROR : One grid does not contain any valid atom")		# Defines the error message
	# 	terminate_program_process(		# Stops the program
	# 		l_s_content=l_s_logs		# Content to save in the logs
	# 	)
	#

	# END STEP 2 ---------------------------------------- #

# Reference ------------------------------------------------------------------ #

# Importation
# from launch_structure_comparison import launch_structure_comparison
	# Manages the comparison of structures
	# In : None
	# Out : None

# Usage
# launch_structure_comparison()		# Manages the comparison of structures

# ---------------------------------------------------------------------------- #
