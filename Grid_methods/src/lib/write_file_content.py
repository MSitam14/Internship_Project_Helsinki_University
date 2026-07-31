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
import time

# Parameters
from Grid_methods.src.lib import global_parameters as gp


# Enables time manipulation
# Contains global variables

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def write_file_content(p_file, s_writing_mode, l_s_content):
	"""
	Writes content to a file
	:param p_file: Path to the file to be written
	:param s_writing_mode: Writing mode
	:param l_s_content: The content to be written
	"""

	# STEP 0 : Preparing variables ---------------------- #
	l_s_logs = []		# Creates an empty list for logs
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : ------------------------------------------ #
	# If the path to the file is not set to none
	if p_file is not None:

		# Tries to write to the file
		try:
			f_output = open(p_file, s_writing_mode)		# Opens the file

			# For each content's lines
			for s_line in l_s_content:
				f_output.write(s_line)		# Writes the line
				f_output.write('\n')

			f_output.close()		# Closes the input file

		# If the file cannot be opened or written
		except OSError:
			l_s_logs.append(		# Defines the error's message
				"ERROR : Impossible to write in the '"
				+ p_file
				+ "' file"
			)
			write_file_content(				# Writes the error to the logs
				p_file=None,				# Path to the file to be written
				s_writing_mode='a',			# File writing mode
				l_s_content=l_s_logs		# Content to write
			)

	# If the function needs to write to the log file
	else:
		p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file

		# Tries to write to the file
		try:
			f_output = open(p_log, 'a')		# Opens the file

			t_current = time.gmtime()				# Gets the current time
			t_current = time.asctime(t_current)		# Converts time to be readable

			# For each content's lines
			for s_line in l_s_content:
				f_output.write('[' + t_current + ']	')		# Writes the current time
				f_output.write(s_line)						# Writes the line
				f_output.write('\n')

			f_output.close()		# Closes the lof file

		# If the file cannot be opened or written
		except OSError:
			os._exit(1)		# Stops the program with the error exit code
	# End if
	# END STEP 1 ---------------------------------------- #

# ---------------------------------------------------------------------------- #



# Reference ------------------------------------------------------------------ #

# Importation
# from write_file_content import write_file_content
	# Writes content to a file
	# In : (p) output file's path, (c) writing mode,
	# In : (l(s)) content to write
	# Out : None

# Usage
# write_file_content(			# Writes the error to the logs
# 	p_file=None,				# Path to the file to be written
# 	s_writing_mode='a',			# Writing mode
# 	l_s_content=l_s_content		# Content to write
# )

# ---------------------------------------------------------------------------- #
