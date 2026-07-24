# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : June 2020
# Updated :
# ---------------------------------------------------------------------------- #

# Importing modules ---------------------------------------------------------- #
import numpy as np

from cla.pdb_structure import PdbStructure
from lib.read_file_content import read_file_content
from lib.terminate_program_process import terminate_program_process


def parse_pdb_file(p_file):
    """
    Extracts a PDB structure from a file and applies filters
    :param p_file: Path to the PDB file to extract
    :return: The PDB structure extracted and saved in an object
    """
    l_s_logs = []  # A list for logs
    l_s_leading_pdb = []  # List of lines before the atoms records
    l_s_trailing_pdb = []  # List of lines after the atom records
    i_line_count = -1  # Index of the current line of the file
    l_ligand_coordinates = []
    b_atom_encountered = False  # If the first atom line has been encountered
    l_s_keys = [  # A list of PDB fields to save
        "HetAtom", "atom_serial", "atom_name", "alternative_location", "residue_name",
        "chain_id", "residue_serial", "residue_insertion", "coord_x", "coord_y",
        "coord_z", "occupancy", "temperature_factor", "element_symbol", "element_charge"
    ]

    # For each one of the 15 useful fields in the PDB file, create an empty list
    d_atoms = {key: [] for key in l_s_keys}

    # Read file content
    l_s_content = read_file_content(p_file)

    # If the PDB file is empty, save error message to log file
    if len(l_s_content) < 2:
        l_s_logs.append("ERROR : The '{}' PDB file is empty".format(p_file))
        terminate_program_process(l_s_logs)

    # Parsing the PDB file, including only ATOM and HETATM lines are saved in the output
    for s_line in l_s_content:
        i_line_count += 1
        if s_line.startswith("ATOM") or s_line.startswith("HETATM"):
            b_atom_encountered = True  # Used for determining when to save leading and trailing lines

            # List of element properties
            l_s_atom_properties = [     # Contains the element properties
                s_line[0:6].strip(),    # ATOM or HETATM
                s_line[6:11].strip(),   # Atom serial number
                s_line[12:16].strip(),  # Atom name
                s_line[16].strip(),     # Alternate location indicator
                s_line[17:20].strip(),  # Residue name
                s_line[21].strip(),     # Chain identifier
                s_line[22:26].strip(),  # Residue sequence number
                s_line[26].strip(),     # Code for insertion of residues
                s_line[30:38].strip(),  # Orthogonal coordinates for X in Angstroms
                s_line[38:46].strip(),  # Orthogonal coordinates for Y in Angstroms
                s_line[46:54].strip(),  # Orthogonal coordinates for Z in Angstroms
                s_line[54:60].strip(),  # Occupancy
                s_line[60:66].strip(),  # Temperature factor
                s_line[76:78].strip(),  # Element symbol
                s_line[78:80].strip(),  # Charge on the atom
            ]



            # If the line is validated by the filters, try to save the line
            # if b_valid:
            try:
                d_atoms["HetAtom"].append(l_s_atom_properties[0].strip())               # ATOM or HETATM
                d_atoms["atom_serial"].append(int(l_s_atom_properties[1].strip()))      # Atom serial number
                d_atoms["atom_name"].append(l_s_atom_properties[2].strip())             # Atom name
                d_atoms["alternative_location"].append(l_s_atom_properties[3].strip())  # Alternate location indicator
                d_atoms["residue_name"].append(l_s_atom_properties[4].strip())          # Residue name
                d_atoms["chain_id"].append(l_s_atom_properties[5].strip())              # Chain identifier
                d_atoms["residue_serial"].append(int(l_s_atom_properties[6].strip()))   # Residue sequence number
                d_atoms["residue_insertion"].append(l_s_atom_properties[7].strip())     # Code for insertion of residues
                d_atoms["coord_x"].append(float(l_s_atom_properties[8].strip()))        # X coordinates in Angstroms
                d_atoms["coord_y"].append(float(l_s_atom_properties[9].strip()))        # Y coordinates in Angstroms
                d_atoms["coord_z"].append(float(l_s_atom_properties[10].strip()))       # Z coordinates in Angstroms
                d_atoms["occupancy"].append(float(l_s_atom_properties[11].strip()))     # Occupancy
                d_atoms["temperature_factor"].append(float(l_s_atom_properties[12].strip()))  # Temperature factor
                d_atoms["element_symbol"].append(l_s_atom_properties[13].strip())       # Element symbol
                d_atoms["element_charge"].append(l_s_atom_properties[14].strip())       # Element symbol

            # If there is an error during the conversion, save error message to log file
            except OSError:
                l_s_logs.append("ERROR : Incorrect value type in '{}' at line '{}'".format(p_file, i_line_count))
                terminate_program_process(l_s_logs)

        # If the line does not contain atom data, save trailing or leading lines
        else:
            if b_atom_encountered:
                l_s_trailing_pdb.append(s_line)
            else:
                l_s_leading_pdb.append(s_line)

    i_last_serial = max(d_atoms["atom_serial"])
    i_last_resid_serial = max(d_atoms["residue_serial"])

    s_name = p_file.split('/')[-1].split('.')[0]    # Extracts the name of the structure
    o_structure = PdbStructure()                    # Creates a PDB structure object
    o_structure.load_structure(  # Loads the structure into the object
        s_name=s_name,  # Name of the structure
        l_s_leading_data=l_s_leading_pdb,  # Structure information
        l_s_trailing_data=l_s_trailing_pdb,  # Remarks on the structure
        d_atoms=d_atoms  # Dictionary of atom propertiespycallgraph
    )
    o_structure.i_last_atm_serial = i_last_serial
    o_structure.i_last_res_serial = i_last_resid_serial

    return o_structure





