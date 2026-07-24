#!/usr/bin/python3

# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano, Samuel Besseau
# Contact : samuelbesseau77@gmail.com
# University of Helsinki
# Created : June 2020
# Updated : May 2023
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #
# Universal modules
import os
# Allows file system operations
# Allows file system operations
import time
# Enables time manipulation
import warnings

# Specific modules
from comparison.launch_structure_comparison import launch_structure_comparison
from comparison.multiple_alignement import multiple_alignment
from pymol_plugins.clean_dataset import prepare_dataset
from comparison.tree_building import  plot_tree
from comparison.tree_sequences import tree_sequences
# Manages the comparison of structures
# In : None
# Out : None
from hotspots.launch_structure_hotspots import launch_structure_hotspot
# Parameters
from lib import global_parameters as gp
# General library
from lib.extract_valid_parameters import extract_valid_parameters
# Contains the global variables
from lib.save_parameters import save_parameters

# Extract parameters from a file and checks the validity of the values
# In : (p) path to the parameters, (d) dictionary to complete,
# In : (d) expected parameters, type and default values
# Out : None


# ---------------------------------------------------------------------------- #

warnings.filterwarnings("ignore")

# Main function -------------------------------------------------------------- #

def main():
	"""
	TODO
	:param :
	:return:
	"""
	# STEP 0 : Loading parameters ----------------------- #
	gp.init()							# Initializes the global parameters variables
	gp.loads_default_parameters()		# Loads the base parameters

	extract_valid_parameters(										# Retrieves the program global parameters
		p_file=gp.D_PARAMETERS_GLOBAL["p_global_parameters"],		# The path to the file containing the parameters
		d_parameters=gp.D_PARAMETERS_GLOBAL,						# The dictionary container for the parameters
		d_expected_parameters=gp.D_EXPECTED_PARAMETERS_GLOBAL		# The dictionary guiding the extraction
	)
	# END STEP 0 ---------------------------------------- #

	# STEP 1 : Structure comparison --------------------- #
	# If a structure comparison must be done
	if gp.D_PARAMETERS_GLOBAL["run_comparison"]:

		t_start = time.time()												# Gets the actual time
		extract_valid_parameters(											# Retrieves the program structure comparison parameters
			p_file=gp.D_PARAMETERS_GLOBAL["p_comparison_parameters"],		# The path to the file containing the parameters
			d_parameters=gp.D_PARAMETERS_COMPARISON,						# The dictionary container for the parameters
			d_expected_parameters=gp.D_EXPECTED_PARAMETERS_COMPARISON		# The dictionary guiding the extraction
		)

		save_parameters(gp.D_PARAMETERS_GLOBAL)
		prepare_dataset(gp.D_PARAMETERS_COMPARISON)

		if len(os.listdir(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/cleaned_dataset/')) == 0:
			print("No valid cleaned structures found in the dataset.")
			exit()
		time_mid = time.time()

		if gp.D_PARAMETERS_COMPARISON['display_alignment'] == True or gp.D_PARAMETERS_COMPARISON['tree'] == 'both' or gp.D_PARAMETERS_COMPARISON['tree'] == 'sequences':
			multiple_alignment()

		if gp.D_PARAMETERS_COMPARISON['tree'] == 'both':
			try :
				t1 = launch_structure_comparison(gp.D_PARAMETERS_COMPARISON)
				print("Comparison done in {:.1f} seconds".format(time.time() - time_mid))
				t2 = tree_sequences()

			except:
				pass

		elif gp.D_PARAMETERS_COMPARISON['tree'] == 'structures':
			try :
				t1 = launch_structure_comparison(gp.D_PARAMETERS_COMPARISON)
				t2 = None
				print("Comparison done in {:.1f} seconds".format(time.time() - time_mid))
			except:
				pass

		elif gp.D_PARAMETERS_COMPARISON['tree'] == 'sequences':
			try :
				t1 = None
				t2 = tree_sequences()
			except:
				pass

		plot_tree(gp.D_PARAMETERS_COMPARISON, t1, t2)


		if gp.D_PARAMETERS_COMPARISON['save_newick_files'] == 'False':
			for filename in os.listdir(gp.D_PARAMETERS_COMPARISON['p_output_comparison']+'/'):
				if filename.endswith(".nwk"):
					os.remove(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/' + filename)

		print('')
		print('')

	# END STEP 1 ---------------------------------------- #

	# STEP 2 : Structure hotspot ----------------- #
	# If a structure hotspot must be done

	print(gp.D_PARAMETERS_GLOBAL["run_hotspot"])

	if gp.D_PARAMETERS_GLOBAL["run_hotspot"]:

		print("RUN EXCTRACTION OF HOTSPOT PARAMETERS")

		t_start = time.time()													# Gets the actual time
		extract_valid_parameters(												# Retrieves the program structure hotspot parameters
			p_file=gp.D_PARAMETERS_GLOBAL["p_hotspot_parameters"],		# The path to the file containing the parameters
			d_parameters=gp.D_PARAMETERS_HOTSPOT,						# The dictionary container for the parameters
			d_expected_parameters=gp.D_EXPECTED_PARAMETERS_HOTSPOT		# The dictionary guiding the extraction
		)

		save_parameters(gp.D_PARAMETERS_GLOBAL)
		prepare_dataset(gp.D_PARAMETERS_HOTSPOT)

		if len(os.listdir(gp.D_PARAMETERS_HOTSPOT['p_input_pdb'])) == 0:
			print("No valid cleaned structures found in the dataset.")
			exit()
		time_mid = time.time()



		launch_structure_hotspot()		# Manages the comparison of structures
		print("Hotspot done in {:.1f} seconds".format(time.time() - t_start))
	# END STEP 2 ---------------------------------------- #



# Auxiliary functions -------------------------------------------------------- #

if __name__ == "__main__":
	main()		# Launches the main function

# ---------------------------------------------------------------------------- #



