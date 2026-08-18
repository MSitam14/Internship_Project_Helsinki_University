# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #


# Universal modules
import os

# General library
from Grid_methods.src.lib.write_file_content import write_file_content


# Allows file system operations
# Writes content to a file
	# In : (p) output file's path, (c) writing mode,
	# In : (l(s)) content to write
	# Out : None

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def terminate_program_process(l_s_content=None):
	"""
	Kills the current process, stops the program
	:param l_s_content: Content to write to the log file
	"""

	# STEP 0 : Preparing variables ---------------------- #
	l_s_content.insert(0, "FATAL ERROR")		# Indicates a fatal error
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : ------------------------------------------ #
	write_file_content(				# Writes the error to the logs
		p_file=None,				# Path to the file to be written
		s_writing_mode='a',			# Writing mode
		l_s_content=l_s_content		# Content to write
	)
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Printing errors -------------------------- #
	# For each line to print
	for s_line in l_s_content:
		print(s_line)		# Prints the error
	# END STEP 2 ---------------------------------------- #


	# STEP 3 : Stopping the program --------------------- #
	raise Exception("Error : error during the program : "+ l_s_content)		# Stops the program
	# END STEP 3 ---------------------------------------- #

# ---------------------------------------------------------------------------- #



# Reference ------------------------------------------------------------------ #

# Importation
# from terminate_program_process import terminate_program_process
	# Stops the program and prints content
	# In : (l(s)) content to prompt
	# Out : None

# Usage
# terminate_program_process(		# Stops the program
# 	l_s_content=l_s_logs			# Content to save in the logs
# )

# ---------------------------------------------------------------------------- #
