# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #


# Importations --------------------------------------------------------------- #

import os

import mendeleev
import numpy as np


# Allows file system operations

# ---------------------------------------------------------------------------- #


# Main function -------------------------------------------------------------- #

def init():
    """
	Initializes global variables used all across the software
	Initializes global variables used all across the software
	"""

    # STEP 0 : Preparing variables ---------------------- #
    global O_SYSTEM_COMPARISON  # Object containing the whole comparison system
    global O_SYSTEM_HOTSPOT  # Object containing the whole hotspot system

    global D_PARAMETERS_GLOBAL  # Dictionary of the program main parameters
    global D_PARAMETERS_COMPARISON  # Dictionary of the parameters specific to the structure comparison
    global D_PARAMETERS_HOTSPOT  # Dictionary of the parameters specific to the structure hotspot

    global D_EXPECTED_PARAMETERS_GLOBAL  # Dictionary of the expected parameters for the main program
    global D_EXPECTED_PARAMETERS_COMPARISON  # Dictionary of the expected parameters for the structure comparison
    global D_EXPECTED_PARAMETERS_HOTSPOT  # Dictionary of the expected parameters for the structure hotspot

    global D_ELEMENT_NUMBER  # Dictionary of atomic number associated to the atom type
    global D_NUMBER_ELEMENT  # Dictionary of atom type associated to the atomic number
    global D_SYBYL_NUMBER  # Dictionary of atom number associated to the atom type
    global D_SYBYL_TYPE  # Dictionary of the nature of atom associated to the atom type
    global D_POCKET_RES_ID # Dictionary of the pocket residue ID will be used to generate the pocket subset

    global D_WATER_POSITION  # Dictionary of positions of the water
    global D_WATER_SCORING   # Dictionary of the association grid position - score
    global D_PDB_SCORING     # Dictionary of the association pdb position - score
    global a_atom_dtype      # Array of the atom dtype
    global p_atom_dtype      # Array of the pseudo atom dtype
    global a_vdw_dtype       # Array of the vdw dtype
    global s_hotspot_type      # Type of hotspot to use
    # END STEP 0 ---------------------------------------- #

    # STEP 1 : Initializing variables ------------------- #
    O_SYSTEM_COMPARISON = None
    O_SYSTEM_HOTSPOT = None

    D_PARAMETERS_GLOBAL = {}
    D_PARAMETERS_COMPARISON = {}
    D_PARAMETERS_HOTSPOT = {}

    D_WATER_POSITION = {}
    D_WATER_SCORING = {}
    D_PDB_SCORING = {}

    # Contains the parameter's name, it's key, it's type and it's default value
    D_EXPECTED_PARAMETERS_GLOBAL = {

        # Base parameters
        "path_to_logs": ["p_log", "path", "project.log"],  # Not shown in global_parameters.txt
        "cpu_allocated": ["i_cpu_allocated", "int", "None"],
        "memory_allocated": ["f_memory_allocated", "float", "4.0"],

        # Features requested
        "run_comparison": ["run_comparison", "bool", "True"],
        "run_hotspot": ["run_hotspot", "bool", "True"],

        # Parsing parameters
        "path_to_global_parameters": ["p_global_parameters", "path", "../config/global_parameters.txt"],
        # Not shown in global_parameters.txt
        "path_to_comparison_parameters": ["p_comparison_parameters", "path", "../config/comparison_parameters.txt"],
        "path_to_hotspot_parameters": ["p_hotspot_parameters", "path",
                                              "../config/hotspot_parameters.txt"],
        "comment_delimiters_string": ["l_s_comment_delimiters", "list_str", ["# ", "\"\"\" ", "// "]],
        # Not shown in global_parameters.txt
        "comment_delimiters_char": ["l_c_comment_delimiters", "list_char", ["#", "\""]],
        # Not shown in global_parameters.txt

        # CLEANING INPUT STRUCTURES
        "discard_hetatm": ["b_discard_hetatm", "bool", "False"],
        "discard_atom": ["b_discard_atom", "bool", "False"],
        "discard_hydrogen": ["b_discard_hydrogen", "bool", "False"],
        "discard_water": ["b_discard_water", "bool", "False"],
        "discard_alternative": ["b_discard_alternative", "bool", "False"],
        "keep_chains": ["l_keep_chain", "list_char", ""],
        "discard_chains": ["l_chain_discard", "list_char", ""],
        "keep_residues": ["l_keep_residues", "list_str", ""],
        "discard_residues": ["l_discard_residues", "list_str", ""],
        "keep_residue_ids": ["l_keep_res_ids", "list_int", ""],
        "discard_residue_ids": ["l_discard_res_ids", "list_int", ""],
        "keep_atoms": ["l_keep_atoms", "list_str", ""],
        "discard_atoms": ["l_discard_atoms", "list_str", ""],

        # Grid parameters
        "explicit_grid": ["explicit_grid", "bool", "False"],
        "atom_type": ["atom_type", "str", "SYBYL"],
        "grid_spacing": ["f_grid_spacing", "float", "0.1"],
        "grid_padding": ["f_grid_padding", "float", "0.0"],
        "align_principal_axes": ["align_principal_axes", "bool", "False"],


        # Pymol
        "watch_live": ["watch_live", "bool", "False"],
        "create_pymol_session": ["pymol_session", "bool", "False"],
        # Pocket parameters
        "pocket_res_name": ["pocket_res_name", "str", "None"],
        "pocket_res_id": ["pocket_res_id", "str", "None"],
        "lig_chain": ["lig_chain", "str", "None"],
        "pocket_size": ["pocket_size", "str", '4.5'],
        "session_name": ["session_name", "str", "hotspot"],

    }
    D_EXPECTED_PARAMETERS_COMPARISON = {

        # Input paths
        "path_to_PDB_directory": ["p_input_pdb", "path", "input/structures_comparison/"],

        # Clean paths
        "path_to_cleaned_PDB_directory": ["p_cleaned_pdb", "path", "output/structures_comparison/cleaned_pdb/"],

        # Output paths
        "path_to_output_directory": ["p_output_comparison", "path", "output/structures_comparison/"],

        # Database
        "database": ["database", "str", "GPCRs"],

        # Pymol
        "align_principal_axes": ["align_principal_axes", "bool", "False"],
        "dataset_status": ["dataset_status", "int", 0],
        "session_name": ["session_name", "str", "structural_alignment"],
        "tmalign_reference": ["tmalign_reference", "str", "None"],
        "pocket_res_name": ["pocket_res_name", "str", "None"],
        "pocket_res_id": ["pocket_res_id", "str", "None"],
        "lig_chain": ["lig_chain", "str", "None"],
        "pocket_size": ["pocket_size", "str", '4.5'],

        # Comparison parameters
        "consider_elements": ["b_consider_elements", "bool", "True"],
        "comparison_normalisation": ["s_comparison_normalisation", "str", "Max"],
        "grid_geometry": ["s_grid_geometry", "str", "Sphere"],
        "Delete_grid": ["Delete_grid", "bool", "True"],

        # Tree generation
        "tree": ["tree", "str", "structures"],
        "tree_name": ["tree_name", "str", "None"],
        "display_alignment": ["display_alignment", "bool", "False"],
        "node_name": ["node_name", "str", "None"],
        "line_width": ["line_width", "float", "100"],
        "spheres_size": ["spheres_size", "float", "100"],
        "sphere_color": ["sphere_color", "bool", "False"],
        "label_color": ["label_color", "bool", "False"],
        "save_structures_tree": ["save_structures_tree", "bool", 'True'],
        "save_sequences_tree": ["save_sequences_tree", "bool", 'True'],
        "show_distances": ["show_distances", "bool", "False"],
        "tree_scale": ["tree_scale", "float", "100"],
        "show_structures_tree": ["show_structures_tree", "bool", "True"],
        "show_sequences_tree": ["show_sequences_tree", "bool", "True"],
        "tree_shape": ["tree_shape", "str", "Circular"],
        "only_topology": ["only_topology", "bool", "True"],
        "leaf_name": ["leaf_name", "bool", "True"],
        "branch_length": ["branch_length", "bool", "True"],

        # Output parameters
        "save_sybyl_lists": ["save_sybyl_lists", "str", "False"],
        "save_newick_files": ["save_newick_files", "str", "False"],
        "save_parameters_file": ["save_parameters_file", "str", "True"],

    }
    D_EXPECTED_PARAMETERS_HOTSPOT = {

        # Input paths
        "path_to_PDB_directory": ["p_input_pdb", "path", "input/hotspot/"],


        # Output paths
        "path_to_output_directory": ["p_output_hotspot", "path", "output/hotspot/"],


        # Hotspot parameters

        "grid_geometry": ["s_grid_geometry", "str", "Sphere"],
        "max_neighbor_number": ["i_max_neighbor_number", "int", "10"],

        # Hotspot
        "hotspot_type": ["s_hotspot_type", "str", "None"],
        "tag_threshold": ["f_tag_threshold", "int", "6"],
        "bad_score_threshold": ["f_bad_score_threshold", "float", "0.4"],
        "good_score_threshold": ["f_good_score_threshold", "float", "0.6"],
        "number_of_rounds": ["i_number_of_rounds", "int", "3"],
        # Atom scoring
        "electronic_densities_folder": ["p_electronic_densities", "path", "resources/densities"],
        "normalize_electronic_densities": ["b_normalize_densities", "bool", "False"],


    }
    D_POCKET_RES_ID = {}
    D_ELEMENT_NUMBER = {}
    for e in mendeleev.elements.__all__:
        tmp = eval('mendeleev.' + e + '.atomic_number')
        D_ELEMENT_NUMBER[e] = tmp

    D_ELEMENT_NUMBER.update({
        "Du": 200, "C.3": 206, "C.2": 207, "C.1": 208, "C.ar": 209, "C.cat": 210, "N.3": 215, "N.2": 216,
        "N.1": 217, "N.ar": 218, "N.am": 219, "N.pl3": 220, "N.4": 221, "O.3.wat": 226, "O.3": 227, "O.2": 228,
        "O.co2": 229, "S.3": 230, "S.2": 231, "S.o": 232, "S.o2": 233, "P.3": 234, "Ti.th": 235, "Ti.oh": 236,
        "Cr.th": 237, "Cr.oh": 238, "Co.oh": 239, "Ru.oh": 240, "Oow": 241, 'Car': 250, 'Nam': 251, 'Nbas': 252,
        'Nlys': 253, 'Oc': 254, 'Oh': 255, 'Oox': 256, 'Xot': 257, 'Meta': 258, 'Hetatm': 259,'elt.symbol': 260,
        'S.O2': 261, 'S.O': 262
    })

    # merge the two dictionaries
    D_SYBYL_TYPE = {"C.3": 'C', "C.2": 'C', "C.1": 'C', "C.ar": 'C', "C.cat": 'C', "N.3": 'N', "N.2": 'N',
                   "N.1": 'N', "N.ar": 'N', "N.am": 'N', "N.pl3": 'N', "N.4": 'N', "O.3.wat": 'O', "O.3": 'O',
                   "O.2": 'O', "O.co2": 'O',"Oow": 'O', "S.3": 'S', "S.2": 'S', "S.o": 'S', "S.o2": 'S', "P.3": 'P',
                   "Ti.th": 'TI', "Ti.oh": 'TI', "Cr.th": 'CR', "Cr.oh": 'CR', "Co.oh": 'CO', "Ru.oh": 'RU',
                    # add custom atomtype to the dictionary
                   'Oow':'Oow',"Car": "C", "Nam": "N", "Nbas": "N", "Nlys": "N", "Oc": "O", "Oh": "O", "Oox": "O",
                   "Xot": "C", "Meta": "Meta",
                    }
    a_atom_dtype = np.dtype([
                ("HetAtom", str, 6),  # ATOM or HETATM
                ("atom_serial", np.uint16, 1),  # Atom serial number
                ("atom_name", str, 4),  # Atom name
                ("alternative_location", str, 1),  # Alternate location indicator
                ("residue_name", str, 3),  # Residue name
                ("chain_id", str, 1),  # Chain identifier
                ("residue_serial", np.int16, 1),  # Residue sequence number
                ("residue_insertion", str, 1),  # Code for insertion of residues
                ("coord_x", np.float32, 1),  # Orthogonal coordinates for X in Angstroms
                ("coord_y", np.float32, 1),  # Orthogonal coordinates for Y in Angstroms
                ("coord_z", np.float32, 1),  # Orthogonal coordinates for Z in Angstroms
                ("occupancy", np.float16, 1),  # Occupancy
                ("temperature_factor", np.float16, 1),  # Temperature factor
                ("element_symbol", str, 2),  # Element symbol
                ("element_charge", str, 2),  # Charge on the atom
                ("element_mass", np.float16, 1),  # Mass of the atom
                ("grid_x", np.int16, 1),  # X coordinates in the grid
                ("grid_y", np.int16, 1),  # Y coordinates in the grid
                ("grid_z", np.int16, 1),  # Z coordinates in the grid
                ("custom_type", str, 6),  # A custom name for the element
                ("sybyl_type", str, 7),  # Sybyl type for the element
                ("type_number", np.int16, 1),  # Number of the element type in the dictionary of types
                ('score_1',np.float16,1), # score based on the first neighbor
                ('score_2',np.float16,1), # score based on the second neighbor
                ('score_3',np.float16,1), # score based on the third neighbor
                ('score_total',np.float16,1) # total score
            ])
    p_atom_dtype = np.dtype([('grid_x', '<i2'), ('grid_y', '<i2'), ('grid_z', '<i2'), ('tag_1', '<f2'), ('tag_2', '<f2'),
                              ('tag_3', '<f2'), ('tag_total','<f2'), ('score_1', '<f2'), ('score_2', '<f2'),
                              ('score_3', '<f2'), ('score_total', '<f2'),("residue_serial", np.int16, 1)], )

    a_vdw_dtype = np.dtype([("type_number", np.int16, 1), ("grid_x", np.int16, 1), ("grid_y", np.int16, 1),
                            ("grid_z", np.int16, 1)])

# END STEP 1 ---------------------------------------- #


# STEP 2 : ------------------------------------------ #
# END STEP 2 ---------------------------------------- #

# ---------------------------------------------------------------------------- #


# Auxiliary functions -------------------------------------------------------- #

def loads_default_parameters():
    D_PARAMETERS_GLOBAL["p_log"] = os.path.abspath(D_EXPECTED_PARAMETERS_GLOBAL["path_to_logs"][2])
    D_PARAMETERS_GLOBAL["p_global_parameters"] = os.path.abspath(
        D_EXPECTED_PARAMETERS_GLOBAL["path_to_global_parameters"][2])
    D_PARAMETERS_GLOBAL["l_s_comment_delimiters"] = D_EXPECTED_PARAMETERS_GLOBAL["comment_delimiters_string"][2]
    D_PARAMETERS_GLOBAL["l_c_comment_delimiters"] = D_EXPECTED_PARAMETERS_GLOBAL["comment_delimiters_char"][2]

# ---------------------------------------------------------------------------- #

# Reference ------------------------------------------------------------------ #

# Importation
# from import global_parameters as gp
# Contains the global variables

# Usage
# init()		# Initializes the global variables

# ---------------------------------------------------------------------------- #
