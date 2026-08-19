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
import base64
import json
import os
# Allows file system operations
# Allows file system operations
import shutil
import time
# Enables time manipulation
import warnings

from pkg_resources import require
from pymol import cmd

# Specific modules
from Grid_methods.src.comparison.launch_structure_comparison import launch_structure_comparison
from Grid_methods.src.comparison.multiple_alignement import multiple_alignment
from Grid_methods.src.pymol_plugins.clean_dataset import prepare_dataset
from Grid_methods.src.comparison.tree_building import  plot_tree
from Grid_methods.src.comparison.tree_sequences import tree_sequences
# Manages the comparison of structures
# In : None
# Out : None
from Grid_methods.src.hotspots.launch_structure_hotspots import launch_structure_hotspot
# Parameters
from Grid_methods.src.lib import global_parameters as gp
# General library
from Grid_methods.src.lib.extract_valid_parameters import extract_valid_parameters
from Grid_methods.src.lib.extract_valid_parameters import extract_valid_parameters_json
# Contains the global variables
from Grid_methods.src.lib.save_parameters import save_parameters, save_parameters_for_api

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


def main_api(json_parameters):
	"""
	TODO
	:param :
	:return:
	"""

	cmd.reinitialize()
	cmd.delete("all")
	
	# STEP 0 : Loading parameters ----------------------- #
	gp.init()							# Initializes the global parameters variables
	gp.loads_default_parameters()		# Loads the base parameters

	extract_valid_parameters_json(										# Retrieves the program global parameters
		json_parameters=json_parameters["global_parameters"],		# The path to the file containing the parameters
		d_parameters=gp.D_PARAMETERS_GLOBAL,						# The dictionary container for the parameters
		d_expected_parameters=gp.D_EXPECTED_PARAMETERS_GLOBAL		# The dictionary guiding the extraction
	)
	# END STEP 0 ---------------------------------------- #

	# STEP 1 : Structure comparison --------------------- #
	# If a structure comparison must be done
	if gp.D_PARAMETERS_GLOBAL["run_comparison"]:

		print("RUN EXCTRACTION OF COMPARISON PARAMETERS")

		t_start = time.time()												# Gets the actual time
		extract_valid_parameters_json(											# Retrieves the program structure comparison parameters
			json_parameters=json_parameters["comparison_parameters"],		# The path to the file containing the parameters
			d_parameters=gp.D_PARAMETERS_COMPARISON,						# The dictionary container for the parameters
			d_expected_parameters=gp.D_EXPECTED_PARAMETERS_COMPARISON		# The dictionary guiding the extraction
		)

		save_parameters_for_api(gp.D_PARAMETERS_GLOBAL ,json_parameters, comp=True)
		prepare_dataset(gp.D_PARAMETERS_COMPARISON)

		if len(os.listdir(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/cleaned_dataset/')) == 0:
			print("No valid cleaned structures found in the dataset.")
			exit()
		time_mid = time.time()

		if gp.D_PARAMETERS_COMPARISON['display_alignment'] == True or gp.D_PARAMETERS_COMPARISON['tree'] == 'both' or gp.D_PARAMETERS_COMPARISON['tree'] == 'sequences':
			multiple_alignment()

		# t1, t2 = None, None  # Initialize t1 and t2 to None

		print("Running comparison with the following parameters:")

		print(f"Tree option selected: {gp.D_PARAMETERS_COMPARISON['tree']}")

		if gp.D_PARAMETERS_COMPARISON['tree'] == 'both':
			try :
				t1 = launch_structure_comparison(gp.D_PARAMETERS_COMPARISON)
				print("Comparison done in {:.1f} seconds".format(time.time() - time_mid))
				t2 = tree_sequences()

			except Exception as e:
				print(f"Error during tree generation: {str(e)}")
				pass

		elif gp.D_PARAMETERS_COMPARISON['tree'] == 'structures':
			try :
				t1 = launch_structure_comparison(gp.D_PARAMETERS_COMPARISON)
				t2 = None
				print("Comparison done in {:.1f} seconds".format(time.time() - time_mid))
			except Exception as e:
				print(f"Error during tree generation: {str(e)}")
				pass

		elif gp.D_PARAMETERS_COMPARISON['tree'] == 'sequences':
			try :
				t1 = None
				t2 = tree_sequences()
			except Exception as e:
				print(f"Error during tree generation: {str(e)}")
				pass

		print(f"t1: {t1}, t2: {t2}")  # Debugging line to check the values of t1 and t2

		plot_tree(gp.D_PARAMETERS_COMPARISON, t1, t2)

		print("Tree plotting completed.")

		if gp.D_PARAMETERS_COMPARISON['save_newick_files'] == 'False':
			for filename in os.listdir(gp.D_PARAMETERS_COMPARISON['p_output_comparison']+'/'):
				if filename.endswith(".nwk"):
					os.remove(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/' + filename)

		print('')
		print('')

		json_return = compileFolderToJson(gp.D_PARAMETERS_COMPARISON['p_output_comparison'])

		shutil.rmtree(gp.D_PARAMETERS_COMPARISON['p_output_comparison'])

		return json_return

	# END STEP 1 ---------------------------------------- #

	# STEP 2 : Structure hotspot ----------------- #
	# If a structure hotspot must be done

	if gp.D_PARAMETERS_GLOBAL["run_hotspot"]:

		print("RUN EXCTRACTION OF HOTSPOT PARAMETERS")

		t_start = time.time()													# Gets the actual time
		extract_valid_parameters_json(											# Retrieves the program structure hotspot parameters
			json_parameters=json_parameters["hotspot_parameters"],		# The path to the file containing the parameters
			d_parameters=gp.D_PARAMETERS_HOTSPOT,						# The dictionary container for the parameters
			d_expected_parameters=gp.D_EXPECTED_PARAMETERS_HOTSPOT		# The dictionary guiding the extraction
		)

		save_parameters_for_api(gp.D_PARAMETERS_GLOBAL, json_parameters, hot=True)
		prepare_dataset(gp.D_PARAMETERS_HOTSPOT)

		if len(os.listdir(gp.D_PARAMETERS_HOTSPOT['p_input_pdb'])) == 0:
			print("No valid cleaned structures found in the dataset.")
			exit()
		time_mid = time.time()

		launch_structure_hotspot()		# Manages the comparison of structures
		print("Hotspot done in {:.1f} seconds".format(time.time() - t_start))

		print('')
		print('')

		os.chdir("../../../../../../") 

		json_return = compileFolderToJson(gp.D_PARAMETERS_HOTSPOT['p_output_hotspot'])
		
		shutil.rmtree(gp.D_PARAMETERS_HOTSPOT['p_output_hotspot'])
		
		return json_return
	# END STEP 2 ---------------------------------------- #


# Auxiliary functions -------------------------------------------------------- #

if __name__ == "__main__":
	# main()		# Launches the main function
	params = None
	
	with open('Grid_methods/config/parameters.json', 'r') as file:
		params = json.load(file)

	main_api(params)


# ---------------------------------------------------------------------------- #

# def compileFolderToJson(folderPath):
# 	"""
# 	Compiles all files in a folder into a JSON object, recursively handling subfolders.
# 	:param folderPath: Path to the folder containing the files.
# 	:return: A JSON object with file names as keys and their contents as values.
# 	"""
# 	result = {}
# 	for filename in os.listdir(folderPath):
# 		print(f"Processing {filename}...")
# 		filePath = os.path.join(folderPath, filename)
# 		if os.path.isfile(filePath):
# 			with open(filePath, 'r', encoding='utf-8', errors='replace') as file:
# 				result[filename] = file.read()
# 		elif os.path.isdir(filePath):
# 			result[filename] = compileFolderToJson(filePath)
# 	return result

def compileFolderToJson(folderPath):
    """
    Compiles all files in a folder into a JSON-compatible dictionary.

    Text files:
        {
            "encoding": "utf8",
            "content": "..."
        }

    Binary files:
        {
            "encoding": "base64",
            "content": "..."
        }

    Subfolders are handled recursively.

    :param folderPath: Path to the folder to compile
    :return: Dictionary representing the folder structure
    """

    result = {}

    # Files that should be treated as text
    text_extensions = {
        ".txt",
        ".svg",
        ".pdb",
        ".json",
        ".csv",
        ".fasta",
        ".fa",
        ".xml",
        ".html",
        ".css",
        ".js",
        ".py",
        ".yaml",
        ".yml",
        ".ini",
        ".log",
        ".nwk",
        ".newick"
    }

    for filename in os.listdir(folderPath):
        print(f"Processing {filename}...")
        filePath = os.path.join(folderPath, filename)
        # FILE
        if os.path.isfile(filePath):

            extension = os.path.splitext(filename)[1].lower()
            # Text file
            if extension in text_extensions:
                with open(filePath, "r", encoding="utf-8") as file:
                    result[filename] = {"encoding": "utf8","content": file.read()}
            # Binary file
            else:
                with open(filePath, "rb") as file:
                    content = file.read()
                result[filename] = {
                    "encoding": "base64",
                    "content": base64.b64encode(content).decode("ascii")
                }
        # FOLDER
        elif os.path.isdir(filePath):
            result[filename] = compileFolderToJson(filePath)

    return result


