# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #

# Universal modules
import os

# Parameters
from lib import global_parameters as gp
# Writes content to a file
# In : (p) output file's path, (c) writing mode,
# In : (l(s)) content to write
# Out : None
from lib.terminate_program_process import terminate_program_process
# General library
from lib.write_file_content import write_file_content


# Allows file system operations
# Contains the global variables
# Stops the program and prints content
	# In : (l(s)) content to prompt
	# Out : None

# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def convert_value_type(s_value, s_type, s_default_value=None):
	"""
	Converts a value or the default one according to the type requested by the program
	:param s_value: The value to convert
	:param s_type: The type requested for the value
	:param s_default_value: The value to convert if the first one is not valid
	:return: The converted value
	"""

	# STEP 0 : Preparing variables ---------------------- #
	d_types_converter = {				# Dictionary containing the conversion functions
		"bool": convert_to_bool,		# Function converting a value into a boolean
		"char": convert_to_char,		# Function converting a value into a character
		"float": convert_to_float,		# Function converting a value into a floating number
		"int": convert_to_int,			# Function converting a value into a integer
		"path": convert_to_path,		# Function converting a value into a file system path
		"str": convert_to_str			# Function converting a value into a string
	}
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : Converting values ------------------------ #
	# If the type is a simple one
	if '_' not in s_type:
		x_valid = d_types_converter[s_type](		# Converts the values to the proper type
			s_value=s_value,						# The first value to convert
			s_default_value=s_default_value			# The value to convert if the first fails
		)

	# If the type is composed
	else:
		x_valid = convert_to_list(						# Converts the values to a list
			s_value=s_value,							# The first value to convert
			s_default_value=s_default_value,			# The value to convert if the first fails
			s_type="".join(s_type.split('_')[1:])		# The types contained within the list
		)
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Returning the converted value ------------ #
	return x_valid		# Returns the converted value
	# END STEP 2 ---------------------------------------- #

# ---------------------------------------------------------------------------- #



# Auxiliary functions -------------------------------------------------------- #

def convert_to_bool(s_value, s_default_value):
	"""
	Checks if the value can be used as a boolean
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:return: A boolean value if the conversion succeeds
	"""

	# Preparing variables
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]					# Loads the path to the log file
	l_s_logs = []										# Creates an empty list for errors
	l_true_values = ["TRUE", "T", "YES", "Y", "1"]		# A list of possible true values
	l_false_values = ["FALSE", "F", "NO", "N", "0"]		# A list of possible false values

	# If the first value is not None
	if s_value is not None:

		# If the value is true
		if s_value.upper() in l_true_values:
			return True

		# If the value is false
		elif s_value.upper() in l_false_values:
			return False

		# If the value is none
		elif s_value.upper() == "NONE":
			return None

		l_s_content = ["The '{}' value cannot be converted into a boolean".format(s_value)]		# The message to save in the logs
		write_file_content(				# Writes the error to the logs
			p_file=p_log,				# Path to the file to be written
			s_writing_mode='a',			# Writing mode
			l_s_content=l_s_content		# Content to write
		)

	# If the first value is incorrect and if there is a default value
	if s_default_value is not None:

		# If the value is true
		if s_value.upper() in l_true_values:
			return True

		# If the value is false
		elif s_value.upper() in l_false_values:
			return False

		# If the value is none
		elif s_value.upper() == "NONE":
			return None

	# If the value cannot be converted into a boolean
	l_s_logs.append(				# Defines the error's message
		"ERROR : The value '"
		+ s_value
		+ "' cannot be used as a boolean"
	)
	terminate_program_process(		# Stops the program
		l_s_content=l_s_logs		# Content to save in the logs
	)
# End function ------------------------------------------ #


def convert_to_char(s_value, s_default_value):
	"""
	Checks if the value can be used as a character
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:return: A character value if the conversion succeeds
	"""

	# Preparing variables
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file
	l_s_logs = []							# Creates an empty list for errors

	# If the first value is not None
	if s_value is not None:

		# If the value is empty
		if s_value == "":
			return s_value

		# If the value is one character long
		if len(s_value) == 1:
			return s_value

		# If the value is none
		elif s_value.upper() == "NONE":
			return None

		l_s_content = ["The '{}' value cannot be converted into a character".format(s_value)]		# The message to save in the logs
		write_file_content(				# Writes the error to the logs
			p_file=p_log,				# Path to the file to be written
			s_writing_mode='a',			# Writing mode
			l_s_content=l_s_content		# Content to write
		)

	# If the first value is incorrect and if there is a default value
	if s_default_value is not None:

		# If the value is empty
		if s_default_value == "":
			return s_default_value

		# If the value is one character long
		if len(s_default_value) == 1:
			return s_default_value

		# If the value is none
		elif s_default_value.upper() == "NONE":
			return None

	# If the value cannot be converted into a character
	l_s_logs.append(		# Defines the error's message
		"ERROR : The value '"
		+ s_value
		+ "' cannot be used as a character"
	)
	terminate_program_process(		# Stops the program
		l_s_content=l_s_logs		# Content to save in the logs
	)
# End function ------------------------------------------ #


def convert_to_float(s_value, s_default_value):
	"""
	Checks if the value can be used as a float
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:return: A float value if the conversion succeeds
	"""

	# Preparing variables
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file
	l_s_logs = []							# Creates an empty list for errors

	# If the first value is not None
	if s_value is not None:

		# If the value is empty
		if s_value == "":
			return s_value

		# Tries to convert the value
		try:
			return float(s_value)

		# If the value cannot be converted into a float
		except ValueError:

			# If the value is none
			if s_value.upper() == "NONE":
				return None

		l_s_content = ["The '{}' value cannot be converted into a float".format(s_value)]		# The message to save in the logs
		write_file_content(				# Writes the error to the logs
			p_file=p_log,				# Path to the file to be written
			s_writing_mode='a',			# Writing mode
			l_s_content=l_s_content		# Content to write
		)

	# If the first value is incorrect and if there is a default value
	if s_default_value is not None:

		# If the value is empty
		if s_default_value == "":
			return s_default_value

		# Tries to convert the value
		try:
			return float(s_default_value)

		# If the value cannot be converted into a float
		except ValueError:

			# If the value is none
			if s_default_value.upper() == "NONE":
				return None

	# If the value cannot be converted into a float
	l_s_logs.append(		# Defines the error's message
		"ERROR : The value '"
		+ s_value
		+ "' cannot be used as a float"
	)
	terminate_program_process(		# Stops the program
		l_s_content=l_s_logs		# Content to save in the logs
	)
# End function ------------------------------------------ #


def convert_to_int(s_value, s_default_value):
	"""
	Checks if the value can be used as an int
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:return: An int value if the conversion succeeds
	"""

	# Preparing variables
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file
	l_s_logs = []							# Creates an empty list for errors

	# If the first value is not None
	if s_value is not None:

		# If the value is empty
		if s_value == "":
			return s_value

		# Tries to convert the value
		try:
			return int(s_value)

		# If the value cannot be converted into a float
		except ValueError:

			# If the value is none
			if s_value.upper() == "NONE":
				return None

		l_s_content = ["The '{}' value cannot be converted into an int".format(s_value)]		# The message to save in the logs
		write_file_content(				# Writes the error to the logs
			p_file=p_log,				# Path to the file to be written
			s_writing_mode='a',			# Writing mode
			l_s_content=l_s_content		# Content to write
		)

	# If the first value is incorrect and if there is a default value
	if s_default_value is not None:

		# If the value is empty
		if s_default_value == "":
			return s_default_value

		# Tries to convert the value
		try:
			return int(s_default_value)

		# If the value cannot be converted into an int
		except ValueError:

			# If the value is none
			if s_default_value.upper() == "NONE":
				return None

	# If the value cannot be converted into an int
	l_s_logs.append(		# Defines the error's message
		"ERROR : The value '"
		+ s_value
		+ "' cannot be used as an int"
	)
	terminate_program_process(		# Stops the program
		l_s_content=l_s_logs		# Content to save in the logs
	)
# End function ------------------------------------------ #


def convert_to_list(s_value, s_default_value, s_type):
	"""
	Checks if the value can be used as a list
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:param s_type: The type of the items contained in the list
	:return: A list of items if the conversion succeeds
	"""

	# Preparing variables
	l_c_item_delimiters = ",;"				# Possibles items delimiters
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file
	l_s_logs = []							# Creates an empty list for errors

	# If the first value is not None
	if s_value is not None:

		# If the value is empty
		if s_value == "":
			return []

		# For each possible delimiter
		for c_delimiter in l_c_item_delimiters:

			# If the delimiter is present
			if c_delimiter in s_value:
				l_list = s_value.split(c_delimiter)		# Splits the list with the present delimiter

				# For each item in the list
				for i_item in range(len(l_list)):

					l_list[i_item] = convert_value_type(		# Converts the item
						s_value=l_list[i_item].strip(),			# The raw item to convert
						s_type=s_type,							# The expected type for the value
						s_default_value=None					# The default value if the first one is not valid
					)

				return l_list		# Returns the completely converted list
			# End if
		# End for

		# If the value is none
		if s_value.upper() == "NONE":
			return None

		l_s_content = ["The '{}' value cannot be converted into a list".format(s_value)]		# The message to save in the logs
		write_file_content(				# Writes the error to the logs
			p_file=p_log,				# Path to the file to be written
			s_writing_mode='a',			# Writing mode
			l_s_content=l_s_content		# Content to write
		)

	# If the first value is incorrect and if there is a default value
	if s_default_value is not None:

		# If the value is empty
		if s_default_value == "":
			return []

		# For each possible delimiter
		for c_delimiter in l_c_item_delimiters:

			# If the delimiter is present
			if c_delimiter in s_value:
				l_list = s_default_value.split(c_delimiter)		# Splits the list with the present delimiter

				# For each item in the list
				for i_item in range(len(l_list)):

					l_list[i_item] = convert_value_type(		# Converts the item
						s_value=l_list[i_item].strip(),			# The raw item to convert
						s_type=s_type,							# The expected type for the value
						s_default_value=None					# The default value if the first one is not valid
					)

				return l_list		# Returns the completely converted list
			# End if
		# End for

		# If the value is none
		if s_default_value.upper() == "NONE":
			return None

	# If the value cannot be converted into a list
	l_s_logs.append(		# Defines the error's message
		"ERROR : The value '"
		+ s_value
		+ "' cannot be used as a list"
	)
	terminate_program_process(		# Stops the program
		l_s_content=l_s_logs		# Content to save in the logs
	)
# End function ------------------------------------------ #


def convert_to_path(s_value, s_default_value):
	"""
	Checks if the value can be used as a path
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:return: A path value if the conversion succeeds
	"""

	# Preparing variables
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file
	l_s_logs = []								# Creates an empty list for errors
	s_sub_dir_buffer = ""						# The path to the directories to create

	# If the first value is not None
	if s_value is not None:

		# If the value is empty
		if s_value == "":
			return s_value

		# If the value is none
		if s_value.upper() == "NONE":
			return None

		# Tries to convert the value into an absolute path
		try:
			p_path = os.path.abspath(s_value)		# Converts the value into an absolute path

			# If the path does not exist
			if not os.path.exists(p_path):

				# If the path points towards a file
				if '.' in s_value.split('/')[-1]:
					l_sub_directories = p_path.split('/')[:-1]		# Retrieves the path without the file name

				# If the path points towards a directory
				else:
					l_sub_directories = p_path.split('/')		# Retrieves the path

				# For each subdirectory
				for s_sub_dir in l_sub_directories:

					s_sub_dir_buffer = s_sub_dir_buffer + s_sub_dir + '/'		# Builds the path for the new directories

					# If the directory does not exist
					if not os.path.exists(s_sub_dir_buffer):

						# Tries to create the subdirectory
						try:
							os.mkdir(s_sub_dir_buffer)		# Creates the subdirectory

						# If this is not possible
						except OSError:
							l_s_logs.append(				# Defines the error's message
								"ERROR : The '"
								+ s_sub_dir_buffer
								+ "' path cannot be created"
							)
							terminate_program_process(		# Stops the program
								l_s_content=l_s_logs		# Content to print in the logs
							)
					# End if
				# End for
			# End if
			return p_path		# Returns the path

		# If the value cannot be converted in a path
		except:
			l_s_content = ["The '{}' value cannot be converted into a path".format(s_value)]		# The message to save in the logs
			write_file_content(				# Writes the error to the logs
				p_file=p_log,				# Path to the file to be written
				s_writing_mode='a',			# Writing mode
				l_s_content=l_s_content		# Content to write
			)

	# If the default value is not None
	if s_default_value is not None:

		# If the value is empty
		if s_default_value == "":
			return s_default_value

		# If the value is none
		if s_default_value.upper() == "NONE":
			return None

		# Tries to convert the value into an absolute path
		try:
			p_path = os.path.abspath(s_default_value)		# Converts the value into an absolute path

			# If the path does not exist
			if not os.path.exists(p_path):

				# If the path points towards a file
				if '.' in p_path.split('/')[-1]:
					l_sub_directories = p_path.split('/')[:-1]		# Retrieves the path without the file name

				# If the path points towards a directory
				else:
					l_sub_directories = p_path.split('/')		# Retrieves the path

				# For each subdirectory
				for s_sub_dir in l_sub_directories:

					s_sub_dir_buffer = s_sub_dir_buffer + s_sub_dir + '/'		# Builds the path for the new directories

					# If the directory does not exist
					if not os.path.exists(s_sub_dir_buffer):

						# Tries to create the subdirectory
						try:
							os.mkdir(s_sub_dir_buffer)		# Creates the subdirectory

						# If this is not possible
						except OSError:
							l_s_logs.append(		# Defines the error's message
								"ERROR : The '"
								+ s_sub_dir_buffer
								+ "' path cannot be created"
							)
							terminate_program_process(		# Stops the program
								l_s_content=l_s_logs		# Content to print in the logs
							)
					# End if
				# End for
			# End if
			return p_path		# Returns the path

		# If the value cannot be converted in a path
		except:
			# If the value cannot be converted into a path
			l_s_logs.append(		# Defines the error's message
				"ERROR : The value '"
				+ s_value
				+ "' cannot be used as a path"
			)
			terminate_program_process(		# Stops the program
				l_s_content=l_s_logs		# Content to save in the logs
			)
# End function ------------------------------------------ #


def convert_to_str(s_value, s_default_value):
	"""
	Checks if the value can be used as a string
	:param s_value: Value to convert
	:param s_default_value: The value to use if the first fails
	:return: A string value if the conversion succeeds
	"""

	# Preparing variables
	p_log = gp.D_PARAMETERS_GLOBAL["p_log"]		# Loads the path to the log file
	l_s_logs = []								# Creates an empty list for errors

	# If the first value is not None
	if s_value is not None:

		# If the value is empty
		if s_value == "":
			return s_value

		# If the value is none
		if s_value.upper() == "NONE":
			return None

		# Tries to convert the value
		try:
			return str(s_value)

		# If it is not possible to convert the value
		except ValueError:
			l_s_content = ["The '{}' value cannot be converted into a string".format(s_value)]		# The message to save in the logs
			write_file_content(				# Writes the error to the logs
				p_file=p_log,				# Path to the file to be written
				s_writing_mode='a',			# Writing mode
				l_s_content=l_s_content		# Content to write
			)

	# If the first value is incorrect and if there is a default value
	if s_default_value is not None:

		# If the value is empty
		if s_default_value == "":
			return s_default_value

		# If the value is none
		if s_default_value.upper() == "NONE":
			return None

		# If the value is a string
		else:
			return str(s_default_value)

	# If the value cannot be converted into a string
	l_s_logs.append(		# Defines the error's message
		"ERROR : The value '"
		+ s_value
		+ "' cannot be used as a string"
	)
	terminate_program_process(		# Stops the program
		l_s_content=l_s_logs		# Content to save in the logs
	)
# End function ------------------------------------------ #

# ---------------------------------------------------------------------------- #



# Reference ------------------------------------------------------------------ #

# Importation
# from convert_value_type import convert_value_type
	# Converts a value or the default one according to the type requested by the program
	# In : (s) main value to convert, (s) expected type,
	# In : (s) default value if the first cannot be converted
	# Out : (x) the converted value

# Usage
# convert_value_type(					# Converts the values
# s_value=s_value,						# The raw value to convert
# s_type=s_type,						# The expected type for the value
# s_default_value=s_default_value		# The default value if the first one is not valid
# )

# ---------------------------------------------------------------------------- #
