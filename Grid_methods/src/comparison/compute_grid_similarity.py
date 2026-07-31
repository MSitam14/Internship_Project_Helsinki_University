# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : July 2020
# Updated :
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #

# Universal modules
import numpy as np

# Parameters
from Grid_methods.src.lib import global_parameters as gp
# General library
from Grid_methods.src.lib.terminate_program_process import terminate_program_process


# Allows Numpy array manipulation
# Contains the global variables
# Stops the program and prints content
	# In : (l(s)) content to prompt
	# Out : None

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def compute_grid_similarity(d_parameters, o_first_structure, o_second_structure):
	"""
	Computes the similarity between two grids
	:param d_parameters:
	:param o_first_structure:
	:param o_second_structure:
	:return: The similarity score
	"""
	print("Computing similarity between {} and {}".format(o_first_structure.s_name, o_second_structure.s_name))

	# STEP 0 : Preparing variables ---------------------- #
	s_normalisation = gp.D_PARAMETERS_COMPARISON["s_comparison_normalisation"].upper()		# Retrieves the normalisation method to use
	l_s_logs = []																			# A list for logs messages

	gp.O_SYSTEM_COMPARISON.generate_grid(			# Creates a grid, loads the structure into it, place VdW volumes
		o_structure=o_first_structure,				# The structure to place into a grid
		d_parameters=gp.D_PARAMETERS_COMPARISON		# Parameters used for the VdW volumes generation
	)
	gp.O_SYSTEM_COMPARISON.generate_grid(			# Creates a grid, loads the structure into it, place VdW volumes
		o_structure=o_second_structure,				# The structure to place into a grid
		d_parameters=gp.D_PARAMETERS_COMPARISON		# Parameters used for the VdW volumes generation
	)
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : Determining the normalization value ------ #
	if s_normalisation == "MIN":
		i_normalize = min(										# Retrieves the minimal number of non empty points
			np.count_nonzero(o_first_structure.a_grid),			# Counts the number of non empty points in the first grid
			np.count_nonzero(o_second_structure.a_grid),		# Counts the number of non empty points in the second grid
		)

	elif s_normalisation == "MAX":
		i_normalize = max(										# Retrieves the maximal number of non empty points
			np.count_nonzero(o_first_structure.a_grid),			# Counts the number of non empty points in the first grid
			np.count_nonzero(o_second_structure.a_grid),		# Counts the number of non empty points in the second grid
		)
	elif s_normalisation == "TANIMOTO":
		i_normalize = np.count_nonzero(						# Retrieves the number of non empty points in the union of the two grids
			np.bitwise_or(o_first_structure.a_grid, o_second_structure.a_grid)		# Computes the union of the two grids
		)
	else:
		i_normalize = d_parameters["i_atom_total"]		# Total of non empty points in the system
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Determining the similarity score --------- #
	try:
		f_similarity = (np.count_nonzero(
			np.bitwise_and(o_first_structure.a_grid, o_second_structure.a_grid)) / i_normalize		# Computes the similarity percentage
		)

	except ZeroDivisionError:
		l_s_logs.append("ERROR : One grid does not contain any valid atom")		# Defines the error message
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save in the logs
		)
	# END STEP 2 ---------------------------------------- #


	# STEP 3 : Returning the similarity score ----------- #
	return f_similarity		# Returns the percentage of similarity
	# END STEP 3 ---------------------------------------- #

# ---------------------------------------------------------------------------- #



# Reference ------------------------------------------------------------------ #

# Importation
# from compute_grid_similarity import compute_grid_similarity
	# Computes the similarity between two grids
	# In : (d) comparison parameters, (o) the first structure to compare,
	# In : (o) the second structure to compare
	# Out : (f) the percentage of similarity

# Usage
# compute_grid_similarity(						# Computes the similarity between two structures
#	d_parameters=d_parameters,					# Comparison parameters
#	o_first_structure=o_first_structure,		# The first structure to compare
#	o_second_structure=o_second_structure,		# The second structure to compare
# )

# ---------------------------------------------------------------------------- #
