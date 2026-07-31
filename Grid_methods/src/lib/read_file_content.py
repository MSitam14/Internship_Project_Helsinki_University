# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #

# Universal modules
from os import path

# General library
from Grid_methods.src.lib.terminate_program_process import terminate_program_process


# Interacting with OS paths
# Stops the program and prints content
	# In : (l(s)) content to prompt
	# Out : None

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def read_file_content(p_file):
	"""
	Reads the content of a file
	:param p_file: Path to the file to read
	:return: The content of the file read
	"""

	# STEP 0 : Preparing variables ---------------------- #
	l_s_logs = []								# A list for logs messages
	l_s_content = []							# Defines a list for the file's content
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : Loading the file content ----------------- #
	if path.exists(p_file):

		# Tries to read the file
		try:
			f_input = open(p_file)					# Opens the file
			l_s_content = f_input.readlines()		# Loads the file's content
			f_input.close()							# Closes the input file

		# If the file cannot be read
		except OSError:
			l_s_logs.append(		# Defines the error's message
				"ERROR : Impossible to read the '"
				+ p_file
				+ "' file"
			)
			terminate_program_process(		# Stops the program
				l_s_content=l_s_logs		# Content to save in the logs
			)

	# If the file does not exists
	else:
		l_s_logs.append(		# Defines the error's message
			"ERROR : The file '"
			+ p_file
			+ "' does not exist"
		)
		terminate_program_process(		# Stops the program
			l_s_content=l_s_logs		# Content to save in the logs
		)
	# End if
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Returning the content of the file -------- #
	return l_s_content		# Returns content
	# END STEP 2 ---------------------------------------- #

# ---------------------------------------------------------------------------- #



# Reference ------------------------------------------------------------------ #

# Importation
# from read_file_content import read_file_content
	# Extracts the content of a file
	# In : (p) file's path
	# Out : (l(s)) the file's content

# Usage
# read_file_content(		# Retrieves the content of the file
# 	p_file=p_file,			# Path to the file to read
# )

# ---------------------------------------------------------------------------- #
