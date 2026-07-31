# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano, Samuel Besseau, Teemu Rönkkö
# Contact : samuelbesseau77@gmail.com
# University of Helsinki
# Created : June 2020
# Updated : May 2023
# ---------------------------------------------------------------------------- #

##### SCRIPT ROLE : extract every information from a structure pdb file #####

# Importations --------------------------------------------------------------- #
import os

import mendeleev
# Universal modules
import numpy as np
from openbabel import openbabel as ob
from openbabel import pybel

# Program external resources
from Grid_methods.src.lib import elem_config
# Parameters
from Grid_methods.src.lib import global_parameters as gp
from Grid_methods.src.lib.terminate_program_process import terminate_program_process


# Contains chemical elements custom properties
# Contains the global variables


# ---------------------------------------------------------------------------- #


# Class ---------------------------------------------------------------------- #

class PdbStructure:
    """
	A class representing the fields contained in a PDB file
	"""

    def __init__(self):
        """
		Initializes the fields of the structure
		"""

        # PDB fields
        self.s_name = ""  # Name of the structure
        self.l_s_leading_data = []  # PDB information written above the atom properties
        self.l_s_trailing_data = []  # PDB information written under the atom properties

        # Structural fields
        self.i_atom_count = 0  # Number of atoms in the structure
        self.a_atoms = None  # Array of atoms properties
        self.a_max_coord = None  # Maximal coordinates for each axis
        self.a_min_coord = None  # Minimal coordinates for each axis

        # Grid fields
        self.a_grid = None  # 3D grid containing the structure
        self.l_l_elements = None  # Set of atoms contained in the structure

        # Hotspot fields
        self.o_tree = None  # A KDTree object representing the exact placement of atoms, used for distance determination

        # Comparison fields
        self.b_loaded = False  # Keeps tracks of the state of the structure

        # Ligands fields
        self.l_o_ligands = []  # A list for the ligands

        # Pocket fields
        self.pocket_indexes = np.s_[:]  # List of the residues included in the pocket
        self.a_pocket_atoms = None  # Array of the pocket atoms properties
        self.a_pocket_grid = None  # 3D grid containing the pocket

        # Miscellaneous fields
        self.a_min_coord = None  # Minimum coordinates of the structure
        self.a_max_coord = None  # Maximum coordinates of the structure
        self.f_mass = 0.0  # Mass of the structure

        # Last serials
        self.i_last_atm_serial = None  # Last atom serial number of the file
        self.i_last_res_serial = None  # Last residue serial number of the file

        # Score dictionary
        self.d_water_position = {}  # Dictionary of positions of the water
        self.d_water_scoring = {}  # Dictionary associating grid position with a score
        self.d_pdb_scoring = {}  # Dictionary associating pdb position with a score

        self.s_content_computed = []  # Content of the computed file

    # End method

    def __repr__(self):
        """
		Creates a human friendly representation of the information contained in the object
		"""
        # Preparing variables
        l_s_content = ["> The structure object :"]

        # PDB fields
        l_s_content += [f"s_name : {self.s_name}"]

        # Structural fields
        l_s_content += [f"i_atom_count : {self.i_atom_count}"]
        l_s_content += [f"a_atoms : {len(self.a_atoms)}" if self.a_atoms is not None else "a_atoms : None"]
        l_s_content += [
            f"a_pocket_atoms : {len(self.a_pocket_atoms)}" if self.a_pocket_atoms is not None else "a_pocket_atoms : None"]

        # Grid fields
        l_s_content += [f"b_loaded : {self.b_loaded}"]
        l_s_content += [
            f"a_grid : {self.a_grid is not None}"]
            # f"a_grid : {self.a_grid.size}" if hasattr(self, 'a_grid') and self.a_grid is not None else "a_grid : None"]
        # Dynamically added fields
        dynamic_fields = ['a_max_grid', 'a_min_grid', 'a_grid_size', 'i_points_count','a_offset','a_vdw']
        l_s_content += [f"{attr} : {len(getattr(self, attr))}" if attr == 'a_vdw' and hasattr(self, attr) else
                        f"{attr} : {getattr(self, attr)}" for attr in dynamic_fields if hasattr(self, attr)]
        return "\n".join(l_s_content)  # Returns the content to show

    # End method

    def load_structure(self, **kwargs):
        """
        Loads in the object the base information about the structure
        """
        # PDB fields
        self.s_name = kwargs["s_name"]  # Name of the structure
        self.l_s_leading_data = kwargs["l_s_leading_data"]  # PDB information written above the atom properties
        self.l_s_trailing_data = kwargs["l_s_trailing_data"]  # PDB information written under the atom properties
        # Structural fields
        self.i_atom_count = len(kwargs["d_atoms"]["HetAtom"])  # Retrieves the number of atoms
        self.a_atoms = np.arange(self.i_atom_count).astype(  # Array of atoms properties
            gp.a_atom_dtype  # Creates an array of the right size and type
        )

        # For each field to save
        for s_key in kwargs["d_atoms"]:
            self.a_atoms[s_key] = kwargs["d_atoms"][s_key]  # Saves each field of the dictionary of atom properties

        # Retrieve and save the masses of the elements using an element symbol and its "backup" symbol in case of error
        # self.a_atoms["element_mass"] = self.retrieve_element_mass()  # Retrieves the atomic mass of the given elements
        # CLEAR ELEMENT MASS
        # intial all the score to 0
        self.a_atoms['score_1'] = 0
        self.a_atoms['score_2'] = 0
        self.a_atoms['score_3'] = 0
        self.a_atoms['score_total'] = 0.5
        # Translate custom and Sybyl element types
        self.translate_custom_types()
        self.translate_sybyl_types()

        # Actualize the properties of the structure
        if gp.D_PARAMETERS_GLOBAL['atom_type'].lower() == 'sybyl':
            l_type = 'sybyl_type'
            self.a_atoms["type_number"] = [gp.D_ELEMENT_NUMBER[atom.capitalize()] for atom in
                                           self.a_atoms["sybyl_type"]]
            self.l_l_elements = set(
                self.a_atoms["sybyl_type"])  # List all the different elements contained in the structure
        else:
            l_type = 'custom_type'
            self.a_atoms["type_number"] = [gp.D_ELEMENT_NUMBER[atom.capitalize()] for atom in
                                           self.a_atoms['custom_type']]
            self.l_l_elements = set(self.a_atoms["custom_type"])

            # l_type = 'element_symbol'
            # self.a_atoms["type_number"] = [gp.D_ELEMENT_NUMBER[atom.capitalize()] for atom in
            #                                self.a_atoms["element_symbol"]]
            # self.l_l_elements = set(
            #     self.a_atoms["element_symbol"])  # List all the different elements contained in the structure

        if self.s_name in gp.D_POCKET_RES_ID.keys():
            self.pocket_indexes = np.where(np.isin(self.a_atoms['residue_serial'], gp.D_POCKET_RES_ID[self.s_name]))[0]
            self.a_pocket_atoms = self.a_atoms[self.pocket_indexes]

        l_s_elements = [None] * 300  # Creates an empty list with a slot for each possible element

        # For each chemical element
        for s_element in self.l_l_elements:
            if l_type == 'sybyl_type':
                try:
                    i_element_number = gp.D_ELEMENT_NUMBER[s_element.capitalize()]
                except KeyError:
                    print("The SYBYL type {} is not supported".format(s_element))
                    i_element_number = 999
                # Retrieves the indexes of the elements
                a_element_indexes = np.where(self.a_atoms["sybyl_type"] == s_element)
            else:
                # Retrieves the atomic number of the element
                i_element_number = gp.D_ELEMENT_NUMBER[s_element.capitalize()]
                # Retrieves the indexes of the elements
                a_element_indexes = np.where(self.a_atoms["custom_type"] == s_element)

            l_s_elements[i_element_number] = [  # Orders each element by their atomic number
                s_element,  # Element symbol
                i_element_number,  # Atomic number of the element
                a_element_indexes,  # Indexes of the element in the structure
                None,  # Coordinates of the element in the grid
                None,  # VdW radius of the element
                None  # Sphere coordinates of the element
            ]
        # End for

        self.l_l_elements = list(filter(None, l_s_elements))  # Removes empty elements in the list

        # Miscellaneous fields
        self.f_mass = sum(self.a_atoms["element_mass"])  # Sums the mass of each element

    # End method ---------------------------------------- #

    def update_extrema_coordinates(self):
        """
        Updates the minimum and maximum coordinates of the structure
        """
        self.a_max_coord = np.array((  # Computes the maximal coordinates
            max(self.a_atoms["coord_x"]),  # For the x axis
            max(self.a_atoms["coord_y"]),  # For the y axis
            max(self.a_atoms["coord_z"])  # For the z axis
        ))
        self.a_min_coord = np.array((  # Computes the minimal coordinates
            min(self.a_atoms["coord_x"]),  # For the x axis
            min(self.a_atoms["coord_y"]),  # For the y axis
            min(self.a_atoms["coord_z"])  # For the z axis
        ))

    # End method ---------------------------------------- #

    def delete_grid(self):
        """
		Deletes the grid and frees memory
		"""

        self.a_grid = None  # Deletes the object from memory

    # End method ---------------------------------------- #

    def translate_sybyl_types(self):
        """
        Translate element types to sybyl type. Reads a PDB file using Openbabel package and
        returns a list of translated element types.
        """
        obConversion = ob.OBConversion()
        obConversion.SetInFormat('pdb')
        obConversion.SetInAndOutFormats("pdb", "mol2")
        ttab = ob.ttab
        ttab.SetFromType("INT")
        ttab.SetToType("SYB")
        ob.obErrorLog.SetOutputLevel(0)
        # Find the path to the pdb file
        if gp.D_PARAMETERS_GLOBAL['run_hotspot']:
            pdb_file = gp.D_PARAMETERS_HOTSPOT["p_input_pdb"] + self.s_name + ".pdb"
        elif gp.D_PARAMETERS_GLOBAL['run_comparison']:
            pdb_file = gp.D_PARAMETERS_COMPARISON["p_input_pdb"] + "/" + self.s_name + ".pdb"
        if os.path.isfile(pdb_file) == False:
            if gp.D_PARAMETERS_GLOBAL['run_hotspot']:
                pdb_file = gp.D_PARAMETERS_HOTSPOT["p_output_hotspot"] + "/" + self.s_name + ".pdb"
            elif gp.D_PARAMETERS_GLOBAL['run_comparison']:
                pdb_file = gp.D_PARAMETERS_COMPARISON[
                               'p_output_comparison'] + '/cleaned_dataset/' + self.s_name + '.pdb'

        l_syb = []  # Empty list for the Sybyl atom types

        # Setting up Openbabel atom type conversion and iterating through the atoms
        mol = ob.OBMol()
        obConversion = ob.OBConversion()
        obConversion.ReadFile(mol, pdb_file)
        for obatom in ob.OBMolAtomIter(mol):
            if obatom.GetResidue().GetName() == 'HOH':  # Use a special type for oxygens in water molecules
                l_syb.append('O.3.wat')
            else:
                l_syb.append(str(ttab.Translate(obatom.GetType())).capitalize())

        self.a_atoms["sybyl_type"] = l_syb  # Saves the list of translated sybyl types
    # def translate_sybyl_types(self):
    #     """
    #     Translate element types to SYBYL types using Open Babel.
    #     Reads a PDB file, standardizes the structure, and returns a list of translated element types.
    #     """
    #     # Initialize Open Babel conversion
    #     obConversion = ob.OBConversion()
    #     obConversion.SetInFormat('pdb')
    #     ttab = ob.OBTypeTable()
    #     ttab.SetFromType("INT")
    #     ttab.SetToType("SYB")
    #     ob.obErrorLog.SetOutputLevel(0)  # Suppress error logging
    #
    #     # Determine the path to the PDB file
    #     if gp.D_PARAMETERS_GLOBAL['run_hotspot']:
    #         pdb_file = os.path.join(gp.D_PARAMETERS_HOTSPOT["p_input_pdb"], f"{self.s_name}.pdb")
    #     elif gp.D_PARAMETERS_GLOBAL['run_comparison']:
    #         pdb_file = os.path.join(gp.D_PARAMETERS_COMPARISON["p_input_pdb"], f"{self.s_name}.pdb")
    #
    #     if not os.path.isfile(pdb_file):
    #         if gp.D_PARAMETERS_GLOBAL['run_hotspot']:
    #             pdb_file = os.path.join(gp.D_PARAMETERS_HOTSPOT["p_output_hotspot"], f"{self.s_name}.pdb")
    #         elif gp.D_PARAMETERS_GLOBAL['run_comparison']:
    #             pdb_file = os.path.join(gp.D_PARAMETERS_COMPARISON['p_output_comparison'], 'cleaned_dataset',
    #                                     f"{self.s_name}.pdb")
    #
    #     if not os.path.isfile(pdb_file):
    #         raise FileNotFoundError(f"PDB file not found: {pdb_file}")
    #
    #     l_syb = []  # List to store SYBYL atom types
    #
    #     # Read the PDB file using Pybel to standardize the structure
    #     mol = next(pybel.readfile("pdb", pdb_file))
    #     mol.addh()  # Add hydrogens to standardize protonation state
    #     mol.make3D()  # Generate 3D coordinates to standardize stereochemistry
    #     mol.localopt()  # Optimize geometry to a local minimum
    #
    #     # Iterate through the atoms in the molecule and translate to SYBYL types
    #     for atom in mol:
    #         obatom = atom.OBAtom
    #         residue_name = obatom.GetResidue().GetName()
    #         if residue_name == 'HOH':  # Special case for water molecules
    #             l_syb.append('O.3.wat')
    #         else:
    #             sybyl_type = ttab.Translate(obatom.GetType())
    #             if sybyl_type == 'H':
    #                 continue  # Skip hydrogens
    #             elif sybyl_type:
    #                 l_syb.append(sybyl_type.capitalize())
    #             else:
    #                 l_syb.append('Unknown')  # Fallback for unidentified atom types
    #     # l_syb[0] = 'N.am'
    #     # l_syb[2] = 'C.3'
    #     # l_syb[1] = 'C.3'
    #     self.a_atoms["sybyl_type"] = l_syb  # Save the list of translated SYBYL types

    def translate_custom_types(self):
        """
		Defines a new element type according to the element role within the structure
		"""
        a_residue_names = self.a_atoms["residue_name"]  # Names of the residues
        a_atom_name = self.a_atoms["atom_name"]  # Names of the atoms
        a_atom_symbol = self.a_atoms["element_symbol"]  # The elements symbols
        l_s_custom_types = []  # List of converted custom types

        # Converting the atom types
        for i in range(len(a_residue_names)):
            # If the residue is one of the main amino acids
            if a_residue_names[i] in elem_config.RES:

                # Hydrogen
                if a_atom_symbol[i] == "H":
                    s_custom_type = "H"

                # # If the atom is one of the main carbon chain
                # elif a_atom_name[i] in d_translate_custom.keys():
                #     s_custom_type = d_translate_custom[a_atom_name[i]]

                # Nitrogen in Arginine
                elif a_residue_names[i] == "ARG" and a_atom_name[i] in elem_config.NARG[a_residue_names[i]]:
                    s_custom_type = "NBAS"

                # Carbon SP2 in aromatic ring
                elif a_residue_names[i] in elem_config.CAR.keys() and a_atom_name[i] in elem_config.CAR[
                    a_residue_names[i]]:
                    s_custom_type = "CAR"

                # Oxygen in hydroxyl or phenol
                elif a_residue_names[i] in elem_config.OHY.keys() and a_atom_name[i] == elem_config.OHY[
                    a_residue_names[i]]:
                    s_custom_type = "OH"

                # Nitrogen in amide
                elif a_residue_names[i] in elem_config.NAM.keys() and a_atom_name[i] == elem_config.NAM[
                    a_residue_names[i]]:
                    s_custom_type = "NAM"

                # Nitrogen in Histidine
                elif a_residue_names[i] in elem_config.NHIS.keys() and a_atom_name[i] in elem_config.NHIS[
                    a_residue_names[i]]:
                    s_custom_type = "NBAS"

                # Central carbon from ARG, GLN, GLU, ASP, ASN
                elif a_residue_names[i] in elem_config.CE.keys() and elem_config.CE[a_residue_names[i]] == a_atom_name[
                    i]:
                    s_custom_type = "CAR"

                # Oxygen in carbonyl
                elif a_residue_names[i] in elem_config.OC.keys() and a_atom_name[i] == elem_config.OC[
                    a_residue_names[i]]:
                    s_custom_type = "OC"

                # Oxygen in carboxylate and oxygen in C-terminal
                elif a_residue_names[i] in elem_config.OOX.keys() and \
                        (a_atom_name[i] == elem_config.OOX[a_residue_names[i]][0] or
                         a_atom_name[i] == elem_config.OOX[a_residue_names[i]][1]):
                    s_custom_type = "OOX"

                # Nitrogen in Lysine
                elif a_residue_names[i] in elem_config.NLYS.keys() and a_atom_name[i] == elem_config.NLYS[
                    a_residue_names[i]]:
                    s_custom_type = "NBAS"

                # Unknown element within a amino acid
                else:
                    s_custom_type = "XOT"

            # If the element is a metallic atom
            elif a_atom_symbol[i] in elem_config.METAL:
                s_custom_type = "META"

            # # If the element is a halogen
            # elif a_atom_symbol[i] in elem_config.HALO:
            #     s_custom_type = "HALO"

            # If the element is a water molecule
            elif a_residue_names[i] == "HOH" and a_atom_name[i] == "O":
                s_custom_type = "Oow"

            # If the element is not known
            else:
                # # If the element can be converted
                #     if a_atom_symbol[i] in d_translate_custom.keys():
                #         s_custom_type = d_translate_custom[a_atom_symbol[i]]
                #     # If it cannot
                #     else:
                s_custom_type = "HETATM"

            l_s_custom_types.append(s_custom_type)  # Saves the new element type

        self.a_atoms["custom_type"] = l_s_custom_types  # Saves the list of custom types

    def retrieve_element_mass(self):
        """
        Retrieves the mass of each given element
        :param x_element_symbol: Array of element symbol or a single element symbol
        :param x_backup_symbol: Atom name in case of missing element symbol
        :return: The mass corresponding of the given element symbols
        """

        # STEP 0 : Preparing variables ---------------------- #
        x_element_symbol = self.a_atoms["element_symbol"]  # Element symbol
        x_backup_symbol = self.a_atoms["atom_name"]  # Element symbol in case of fail
        l_s_logs = []  # A list for log
        # END STEP 0 ---------------------------------------- #
        d_element_mass = {}  # Creates an empty dictionary for the elements mass
        for e in mendeleev.elements.__all__:
            mass = eval('mendeleev.' + e + '.mass')
            if mass is not None:
                d_element_mass[e.upper()] = mass
            else:
                d_element_mass[e.upper()] = 0
        # STEP 1 : Retrieving the element mass -------------- #
        if isinstance(x_element_symbol, np.ndarray):

            a_element_mass = np.zeros(len(x_element_symbol)).astype(
                np.float32)  # Creates an empty array for the elements mass
            x_element_symbol.tolist()  # Converts the numpy array into a Python list

            # For each element to process
            for i_element in range(len(x_element_symbol)):

                # Tries to retrieve the element mass
                try:
                    a_element_mass[i_element] = d_element_mass[
                        x_element_symbol[i_element]]  # Retrieves the mass of the element

                # If there is a symbol error
                except KeyError:
                    a_element_mass[i_element] = d_element_mass[
                        x_backup_symbol[i_element]]  # Retrieves the mass of the element

            return a_element_mass  # Returns the array of mass

        # If the element to convert is a string
        elif isinstance(x_element_symbol, str):

            # Tries to retrieve the element mass
            try:
                return d_element_mass[x_element_symbol]  # Retrieves the mass of the element

            # If there is a symbol error
            except KeyError:
                return d_element_mass[x_backup_symbol]  # Retrieves the mass of the element

        # If the argument type is wrong
        else:

            l_s_logs.append(
                "ERROR : Wrong element symbol type '{}'".format(
                    type(type(x_element_symbol))))  # Defines the error message
            terminate_program_process(  # Stops the program
                l_s_content=l_s_logs  # Content to save to logs
            )

# ---------------------------------------------------------------------------- #
