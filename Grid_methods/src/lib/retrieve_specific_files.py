# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #

# Universal modules
import os
# Allows file system operations
from glob import glob

# General library
from lib.terminate_program_process import terminate_program_process


# Searching for patterns within file system
# Stops the program and prints content
	# In : (l(s)) content to prompt
	# Out : None

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def retrieve_specific_files(p_directory, s_pattern="*", b_recursive=False, i_min_match=1, i_max_match=999999):
	"""
	Retrieves files path, recursively or not, matching a specific pattern, or not
	:param p_directory: Path to the directory to explore
	:param s_pattern: Pattern to match
	:param b_recursive: If the search needs to be recursive
	:param i_min_match: Minimum number of match
	:param i_max_match: Maximum number of match
	:return: The list of files path to be returned
	"""

	# STEP 0 : Preparing variables ---------------------- #
	l_i_directory_indexes = []		# A list of directories indexes
	l_s_logs = []					# A list for logs messages
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : Directory verification ------------------- #
	# If the directory does not exist
	if not os.path.isdir(p_directory):
		l_s_logs.append("ERROR : The '{}' directory does not exist".format(p_directory))		# Defines the error message
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save in the logs
		)
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Building the search pattern -------------- #
	# If the search needs to be recursive
	if b_recursive:
		s_requested_pattern = p_directory + "/**/" + s_pattern		# Creates the search pattern

	# If the search is in direct directory
	else:
		s_requested_pattern = p_directory + '/' + s_pattern		# Creates the search pattern
	# END STEP 2 ---------------------------------------- #


	# STEP 3 : Retrieving the files --------------------- #
	l_p_files = glob(s_requested_pattern, recursive=b_recursive)		# Searches the pattern within the directory
	# END STEP 3 ---------------------------------------- #

	# STEP 4 : Curating the search results -------------- #
	# For each retrieved file
	for i_path in range(len(l_p_files)):

		# If the path leads to a directory
		if os.path.isdir(l_p_files[i_path]):
			l_i_directory_indexes.append(i_path)		# Saves the index of the directory to delete

	# For each directory to delete
	for i_path in reversed(l_i_directory_indexes):
		l_p_files.pop(i_path)  # Deletes the path from the list

	# If there is less than the requested amount of file
	if len(l_p_files) < i_min_match:
		l_s_logs.append("ERROR : Not enough files in '{}', at least '{}' files were expected".format(p_directory, i_min_match))		# Defines the error message
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save in the logs
		)

	# If there is more than the requested amount of file
	if len(l_p_files) > i_max_match:
		l_s_logs.append("ERROR : Too many files in '{}', no more than '{}' files were expected".format(p_directory, i_max_match))		# Defines the error message
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save in the logs
		)
	# END STEP 4 ---------------------------------------- #


	# STEP 5 : Returning valid file paths --------------- #
	return l_p_files		# Returns the list of matched paths
	# END STEP 5 ---------------------------------------- #

# ---------------------------------------------------------------------------- #



# Reference ------------------------------------------------------------------ #

# Importation
# from retrieve_specific_files import retrieve_specific_files
	# Retrieves files path, recursively or not, matching a specific pattern, or not
	# In : (p) directory to retrieve files from, (s) pattern to match,
	# In : (b) if the search needs to be recursive, (i) minimum number of match,
	# In : (i) maximum number of match
	# Out : (l(p)) a list of the file paths founds

# Usage
# l_p_input_pdb = retrieve_specific_files(		# Retrieves PDB paths
# 	p_directory=p_input_pdb,					# Path to the input directory
# 	s_pattern="*",								# Pattern to match within the directories
# 	b_recursive=False,							# Also searches in the subdirectories
# 	i_min_match=1,								# Minimum number of files to retrieve
# 	i_max_match=999999							# Maximum number of files to retrieve
# )

# ---------------------------------------------------------------------------- #
