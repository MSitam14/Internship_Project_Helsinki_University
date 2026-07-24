# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #

# Converts a value or the default one according to the type requested by the program
# In : (s) main value to convert, (s) expected type,
# In : (s) default value if the first cannot be converted
# Out : (x) the converted value
import datetime

# Parameters
from lib import global_parameters as gp
# Extracts the content of a file
# In : (p) file's path
# Out : (l(s)) the file's content
from lib.convert_value_type import convert_value_type
# General library
from lib.read_file_content import read_file_content


# Contains the global variables
# ---------------------------------------------------------------------------- #



# Main function -------------------------------------------------------------- #

def extract_valid_parameters(p_file, d_parameters, d_expected_parameters):
	"""
	Extract parameters from a file and checks the validity of the values
	:param p_file: Path to the file containing the parameters to load and verify
	:param d_parameters: Dictionary of parameters to fill
	:param d_expected_parameters: Dictionary of the expected parameters and their default values
	"""
	date = datetime.datetime.now().strftime("%d_%m_%Y-%H_%M")
	# STEP 0 : Preparing variables ---------------------- #
	l_s_comment_delimiters = gp.D_PARAMETERS_GLOBAL["l_s_comment_delimiters"]		# Comment delimiters as a string
	l_c_comment_delimiters = gp.D_PARAMETERS_GLOBAL["l_c_comment_delimiters"]		# Comment delimiters as characters
	l_s_logs = []																	# Creates an empty list for errors
	# END STEP 0 ---------------------------------------- #


	# STEP 1 : Reading the parameters ------------------- #
	l_s_content = read_file_content(		# Retrieves the content of the file
		p_file=p_file,						# Path to the file to read
	)
	# END STEP 1 ---------------------------------------- #


	# STEP 2 : Loading and curating parameters ---------- #
	# For each line in the file of parameters
	for s_line in l_s_content:

		s_line_buffer = s_line.strip()		# Removes empty spaces

		# If the line is not empty
		if len(s_line_buffer) < 2:
			pass		# Skips this line

		# If the line does not start with a comment delimiter
		elif s_line_buffer[0] not in l_c_comment_delimiters:

			# If the line contains a equal symbol
			if '=' in s_line_buffer:

				l_s_line_split = s_line_buffer.split('=')			# Splits the line between the key and it's value
				s_key = l_s_line_split[0].rstrip()					# Extracts the key and removes empty trailing spaces

				# Tries to retrieve the value
				try:
					s_value = "".join(l_s_line_split[1:]).lstrip()		# Extracts the values and removes empty leading space

					# If there is a comment at the end of the value field
					if s_value[0] in l_c_comment_delimiters:
						s_value = ""		# Defines the value as empty

				# If there is no value
				except IndexError:
					s_value = ""		# Defines the value as empty

				# For each comment delimiter
				for s_comment_delimiter in l_s_comment_delimiters:

					# If the value contains a comment
					if s_comment_delimiter in s_value:
						s_value = s_value.split(s_comment_delimiter)[0].rstrip()		# Removes the comment and trailing spaces
				# End for

				# If the parameter is expected
				if s_key in d_expected_parameters:
					# add the date to the output directory
					if s_key in ['path_to_output_directory','path_to_cleaned_directory']:
						s_value = s_value + date + '/'
					l_properties = d_expected_parameters[s_key]		# Loads the properties of the parameter
					s_verified_value = convert_value_type(			# Converts the values
						s_value=s_value,							# The raw value to convert
						s_type=l_properties[1],						# The expected type for the value
						s_default_value=l_properties[2]				# The default value if the first one is not valid
					)
					d_parameters[l_properties[0]] = s_verified_value		# Saves the parameters with a valid value
			# End if
		# End if
	# End for
	# END STEP 2 ---------------------------------------- #
# ---------------------------------------------------------------------------- #




# Reference ------------------------------------------------------------------ #

# Importation
# from extract_valid_parameters import extract_valid_parameters
	# Extract parameters from a file and checks the validity of the values
	# In : (p) path to the parameters, (d) dictionary to complete,
	# In : (d) expected parameters, type and default values
	# Out : None

# Usage
# extract_valid_parameters(									# Retrieves the program parameters
# 	p_file=p_global_parameters,								# The path to the file containing the parameters
# 	d_parameters=D_PARAMETERS_GLOBAL,						# The dictionary container for the parameters
# 	d_expected_parameters=D_EXPECTED_PARAMETERS_GLOBAL		# The dictionary guiding the extraction
# )

# ---------------------------------------------------------------------------- #
