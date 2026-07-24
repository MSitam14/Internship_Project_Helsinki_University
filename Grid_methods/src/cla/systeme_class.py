# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : July 2020
# Updated :
# ---------------------------------------------------------------------------- #


# Importations --------------------------------------------------------------- #

import sys

import mendeleev
import numpy as np

from lib import global_parameters as gp
from lib.read_file_content import read_file_content
from lib.retrieve_specific_files import retrieve_specific_files
from lib.terminate_program_process import terminate_program_process
from lib.Grid_plot  import plot_heatmap

# ---------------------------------------------------------------------------- #


# Class ---------------------------------------------------------------------- #

class System:
    """
    TODO
    """

    def __init__(self):
        """
        Initializes the fields
        """

        # Structure fields
        self.l_o_structures = []  # A list for structure objects
        self.a_offset = np.array((0, 0, 0))  # Coordinates offset compared to the original placement
        self.a_max_coord = None  # Maximal real coordinates for each axis
        self.a_min_coord = None  # Minimal real coordinates for each axis

        # Grid fields
        self.i_grid_bleeding = 0  # Number of extra points around the grids
        self.f_grid_spacing = 5.0  # Distance between two grid points in Angstroms
        self.f_grid_padding = 0.0  # Distance between the grid and the structure
        self.a_max_grid = None  # Maximal grid coordinates for each axis
        self.a_min_grid = None  # Minimal grid coordinates for each axis
        self.a_grid_size = None  # Size of the grid
        self.i_points_count = 0  # Number of points in the grid

        # Resources fields
        self.d_vdw_radius = {}  # Dictionary of VdW radius
        self.d_scaled_vdw = {}  # VdW radius scaled to the grid
        self.i_max_radius = 0  # The maximal VdW radius scaled to the grid
        self.d_d_distance_score = {}  # Dictionary containing the electronic densities

        # Progression fields
        self.i_current_structure = 0  # Keeps tacks of the structures being processed
        self.i_progress_length = 0  # The length of the progress bar
        self.l_l_tasks = []  # A list containing the tasks to process
        self.i_progress = 0  # The number of completed task

        # Hetero atom
        self.s_hetatm_name = "Oow"  # Name of the hetero atom/molecule to score - water is the default value
        self.s_atom_type = None  # Custom or Sybyl type - depends on the inputted density folder

    # End method ---------------------------------------- #

    def __repr__(self):
        """
        Creates a human friendly representation of the system and it's content
        """

        # Preparing variables
        l_s_content = ["> The hotspot system :",
                       # Structure fields
                       "l_o_structures : {}".format(len(self.l_o_structures)), "a_offset : {}".format(self.a_offset),
                       "a_max_coord : {}".format(self.a_max_coord), "a_min_coord : {}".format(self.a_min_coord),
                       # Grid fields
                       "i_grid_bleeding : {}".format(self.i_grid_bleeding),
                       "f_grid_spacing : {}".format(self.f_grid_spacing), "a_max_grid : {}".format(self.a_max_grid),
                       "a_min_grid : {}".format(self.a_min_grid), "a_grid_size : {}".format(self.a_grid_size),
                       # Resources fields
                       "d_d_distance_score : {} entries".format(len(self.d_d_distance_score.keys()))]
        return "\n".join(l_s_content)  # Returns the content to show

    # End method

    # System initialization

    def initialize_system(self, d_parameters):
        """
        Initializes the system base fields
        :param d_parameters: Dictionary of the system parameters
        """

        # Grid fields
        self.f_grid_spacing = gp.D_PARAMETERS_GLOBAL["f_grid_spacing"]  # The space between two grid points
        self.f_grid_padding = gp.D_PARAMETERS_GLOBAL["f_grid_padding"]  # The space between the grid and the structure
        # Resources fields
        self.load_vdw_radius()  # Retrieves the VdW radius of chemical elements
        self.scale_vdw_radius()  # Scales the radius to the grid spacing
        if gp.D_PARAMETERS_GLOBAL["run_hotspot"]:
            self.load_electronic_densities(  # Retrieves the electronic densities of each atom type
                d_parameters=d_parameters)

        # Adapting the grid size
        self.i_grid_bleeding = np.floor(  # Defines the number of points to add around the grids
            # self.i_max_radius * 2 + int(self.f_grid_padding / self.f_grid_spacing) * 2
            # self.i_max_radius + self.f_grid_padding / self.f_grid_spacing
            self.f_grid_padding / self.f_grid_spacing
        )

        self.a_offset = self.a_offset + self.i_grid_bleeding  # Records the scaled offset

    # End method ---------------------------------------- #

    def load_vdw_radius(self):
        """
        Extracts the values of VdW radius
        """

        # Preparing variables
        d_vdw_radius = {'Oow': 1.4}

        for e in mendeleev.elements.__all__:
            vdw_radius = eval('mendeleev.' + e + '.vdw_radius')
            if vdw_radius is not None:
                d_vdw_radius[e] = float(vdw_radius) / 100  # Saves the VdW radius of each chemical element
            else:
                d_vdw_radius[e] = 0

        self.d_vdw_radius = d_vdw_radius  # Saves the dictionary of VdW radius

    # End method ---------------------------------------- #

    def scale_vdw_radius(self):
        """
        Scales the VdW radius to the grid spacing, converting the radius from Angstroms to points
        """

        # Preparing variables
        i_max_radius = 0  # Stores the maximal radius encountered
        d_scaled_vdw = {}  # Dictionary of VdW radius per element scaled with the grid spacing

        # For each element in the dictionary
        for s_element in self.d_vdw_radius:
            d_scaled_vdw[s_element] = np.floor(  # Defines the VdW radius in points
                self.d_vdw_radius[s_element] / self.f_grid_spacing
            ).astype(np.int32)

            # If the radius is superior to the actual maximal
            if d_scaled_vdw[s_element] > i_max_radius:
                i_max_radius = d_scaled_vdw[s_element]  # Saves the actual radius
        # End for

        self.i_max_radius = i_max_radius  # Saves the maximal radius
        self.d_scaled_vdw = d_scaled_vdw  # Saves the scaled radius

    # End method ---------------------------------------- #

    def load_electronic_densities(self, d_parameters):
        """
        Retrieves the electronic densities of each atom type
        :param d_parameters: Dictionary of parameters containing the path to the density files
        """
        d_d_distance_score = {}  # Dictionary of scoring dictionaries

        if gp.D_PARAMETERS_GLOBAL['atom_type'].lower() == "sybyl":
            d_parameters["p_electronic_densities"] += '/sybyl/'
            if self.s_hetatm_name == "Oow":
                self.s_hetatm_name = "O.3.wat"
        elif gp.D_PARAMETERS_GLOBAL['atom_type'].lower() == "custom":
            d_parameters["p_electronic_densities"] += '/custom/'
        # Retrieving the density files considering the maximum number of neighbours to consider
        l_p_density_files = retrieve_specific_files(d_parameters["p_electronic_densities"], "*")
        l_p_density_files = [file for file in l_p_density_files
                             if int(file.split("_")[-1][:-4]) <= d_parameters["i_max_neighbor_number"]]
        max_scaled_dist = 0
        # For each density file
        for p_file in l_p_density_files:
            if 'empty' in p_file:
                continue
            d_score_rule_buffer = {}  # A temporary dictionary buffer
            a_distance = np.zeros(512).astype(np.float32)  # Array of distances
            a_distance_scaled = np.zeros(512).astype(np.float32)  # Array of scaled distances
            a_density = np.zeros(512).astype(np.float16)  # Array of densities
            l_s_content = read_file_content(p_file)[1:]  # Read file and skip first line
            s_file_name = p_file.split("/")[-1][:-4]  # Extracts the last string before the extension

            # For each line in the density file, retrieve distance and density
            for i_line in range(len(l_s_content)):
                a_distance[i_line] = l_s_content[i_line].split(' ')[1]
                a_density[i_line] = l_s_content[i_line].split(' ')[2]
                a_distance_scaled[i_line] = a_distance[i_line] / self.f_grid_spacing # rounding Method previously np.rint() np.floor()
            # Normalize the densities if necessary

            if d_parameters["b_normalize_densities"]:
                a_density = a_density / max(a_density)
            d_score_rule_buffer['distance'] = a_distance
            d_score_rule_buffer['distance_scaled'] = a_distance_scaled
            d_score_rule_buffer['density'] = a_density
            d_score_rule_buffer['optimal_distance'] = np.floor(a_distance_scaled[
                                                                   np.where(a_density == max(a_density))[0][0]]).astype(
                np.int32)
            origin = gp.D_ELEMENT_NUMBER[s_file_name.split("_")[0]]
            neighbour = gp.D_ELEMENT_NUMBER[s_file_name.split("_")[1]]
            rank = int(s_file_name.split("_")[2])
            d_d_distance_score.setdefault(origin, {}).setdefault(neighbour, {}).setdefault(rank, d_score_rule_buffer)
            max_scaled_dist = max(max_scaled_dist, max(a_distance_scaled))
        gp.I_MAX_SCALED_DIST = max_scaled_dist
        self.d_d_distance_score = d_d_distance_score  # Saves the electronic densities in the system object

    # Saves the electronic densities in the system object
    # End forw
    # End method ---------------------------------------- #

    def update_system_properties(self):
        """
        Actualizes the properties of the system
        """

        if gp.D_PARAMETERS_GLOBAL["run_comparison"]:
            self.a_max_coord = np.array((np.NaN, np.NaN, np.NaN))  # Maximal coordinates of the structure
            self.a_min_coord = np.array((np.NaN, np.NaN, np.NaN))  # Minimal coordinates of the structure

            for o_structure in self.l_o_structures:
                o_structure.update_extrema_coordinates()  # Updates the maximal and minimal coordinates

                # Loops over the structures to get the maximal and minimal coordinates
                # to generate the grid with the same dimensions for all structures

                self.a_max_coord = np.array((  # Computes the maximal coordinates
                     max(o_structure.a_max_coord[0], self.a_max_coord[0]),  # For the x axis
                     max(o_structure.a_max_coord[1], self.a_max_coord[1]),  # For the y axis
                     max(o_structure.a_max_coord[2], self.a_max_coord[2])  # For the z axis
                ))
                self.a_min_coord = np.array((  # Computes the minimal coordinates
                     min(o_structure.a_min_coord[0], self.a_min_coord[0]),  # For the x axis
                     min(o_structure.a_min_coord[1], self.a_min_coord[1]),  # For the y axis
                     min(o_structure.a_min_coord[2], self.a_min_coord[2])  # For the z axis
                ))
            # End for
            # Actualizing the grid properties
            self.a_max_grid = np.floor(self.a_max_coord / self.f_grid_spacing)  # Maximal coordinates in the grid
            self.a_min_grid = np.floor(self.a_min_coord / self.f_grid_spacing)  # Minimal coordinates in the grid

            # For each axis x, y and z
            for i_axis in range(3):
                self.a_offset[i_axis] -= self.a_min_grid[i_axis]  # Centers all the structures

            self.a_grid_size = np.array((  # Computes the number of points in each dimension of the grid
                (self.i_grid_bleeding * 2 + self.a_max_grid[0] - self.a_min_grid[0]),
                (self.i_grid_bleeding * 2 + self.a_max_grid[1] - self.a_min_grid[1]),
                (self.i_grid_bleeding * 2 + self.a_max_grid[2] - self.a_min_grid[2])
            )).astype(np.int64)
            self.i_points_count = (
                    self.a_grid_size[0] * self.a_grid_size[1] * self.a_grid_size[2])  # Number of points in the grid
        else:
            # For each registered structure
            for o_structure in self.l_o_structures:
                o_structure.update_extrema_coordinates()  # Updates the maximal and minimal coordinates

                # Actualizing the grid properties for each structure
                o_structure.a_max_grid = np.floor(
                    o_structure.a_max_coord / self.f_grid_spacing)  # Maximal coordinates in the grid
                o_structure.a_min_grid = np.floor(
                    o_structure.a_min_coord / self.f_grid_spacing)  # Minimal coordinates in the grid

                o_structure.a_offset = self.a_offset.copy()  # Copies the offset
                # For each axis x, y and z
                for i_axis in range(3):
                    o_structure.a_offset[i_axis] -= o_structure.a_min_grid[i_axis]  # Centers all the structures so that the minimal coordinates are at 0

                o_structure.a_grid_size = np.array((  # Computes the number of points in each dimension of the grid
                    (self.i_grid_bleeding * 2 + o_structure.a_max_grid[0] - o_structure.a_min_grid[0]),
                    (self.i_grid_bleeding * 2 + o_structure.a_max_grid[1] - o_structure.a_min_grid[1]),
                    (self.i_grid_bleeding * 2 + o_structure.a_max_grid[2] - o_structure.a_min_grid[2])
                )).astype(np.int64)
                o_structure.i_points_count = (
                        o_structure.a_grid_size[0] * o_structure.a_grid_size[1] * o_structure.a_grid_size[2])  # Number of points in the grid

    # End method ---------------------------------------- #

    # Grid management

    def generate_grid(self, o_structure, d_parameters):
        """
        Generates a grid for a given PDB structure
        :param o_structure: The structure to be loaded into a grid
        :param d_parameters: Dictionary of the program parameters
        """
        if o_structure.b_loaded is not True:

            # Creating the grid explicitly (not necessary for hotspots)
            if self.a_grid_size is not None:  # If system parameters are not None
                grid_src = self
            else:  # If system parameters are None
                grid_src = o_structure

            # Preparing variables
            l_l_elements = o_structure.l_l_elements  # Shortcut for the structure field containing sorted data for each element

            # Converting the structure real coordinates to grid coordinates
            o_structure.a_atoms["grid_x"] = np.floor(o_structure.a_atoms["coord_x"] / self.f_grid_spacing + grid_src.a_offset[0])
            o_structure.a_atoms["grid_y"] = np.floor(o_structure.a_atoms["coord_y"] / self.f_grid_spacing + grid_src.a_offset[1])
            o_structure.a_atoms["grid_z"] = np.floor(o_structure.a_atoms["coord_z"] / self.f_grid_spacing + grid_src.a_offset[2])

            # If the pocket indexes are defined initialize the pocket atoms
            if isinstance(o_structure.pocket_indexes, np.ndarray):
                o_structure.a_pocket_atoms = o_structure.a_atoms[o_structure.pocket_indexes]

            # For each chemical element in the structure
            for i_element in range(len(l_l_elements)):
                a_element_indexes = l_l_elements[i_element][2]  # Loads the indexes of the element
                l_l_elements[i_element][3] = (  # Retrieves the coordinates of the element
                    o_structure.a_atoms["grid_x"][a_element_indexes],
                    o_structure.a_atoms["grid_y"][a_element_indexes],
                    o_structure.a_atoms["grid_z"][a_element_indexes])

                # Formats and saves the atom coordinates
                o_structure.l_l_elements[i_element][3] = np.transpose(l_l_elements[i_element][3])

            # creating the grid explicitly
            if gp.D_PARAMETERS_GLOBAL["run_hotspot"] and gp.D_PARAMETERS_GLOBAL['explicit_grid']:
                # Creating the grid
                o_structure.a_grid = np.zeros(grid_src.i_points_count).reshape(  # Initializes the grid
                    grid_src.a_grid_size[0],
                    grid_src.a_grid_size[1],
                    grid_src.a_grid_size[2]
                ).astype(
                    np.dtype([  # Defines the content of each point
                        ("element_symbol", np.uint16, 1),  # The atom symbol
                        ("atom_serial", np.uint16, 1),  # The atom serial number
                        ("score_1", np.float16, 1),  # The atom score at position 1
                        ("score_2", np.float16, 1),  # The atom score at position 2
                        ("score_3", np.float16, 1)  # The atom score at position 3
                    ])
                )

                o_structure.a_grid["element_symbol"][  # Loads the elements symbols in the grid
                    o_structure.a_atoms["grid_x"],
                    o_structure.a_atoms["grid_y"],
                    o_structure.a_atoms["grid_z"]
                ] = o_structure.a_atoms["type_number"]
                o_structure.a_grid["atom_serial"][  # Loads the elements symbols in the grid
                    o_structure.a_atoms["grid_x"],
                    o_structure.a_atoms["grid_y"],
                    o_structure.a_atoms["grid_z"]
                ] = o_structure.a_atoms["atom_serial"]

                o_structure.b_loaded = True  # Sets the structure as loaded

            if gp.D_PARAMETERS_GLOBAL["run_comparison"]:
                if gp.D_PARAMETERS_GLOBAL['explicit_grid']:
                    o_structure.a_grid = np.zeros(self.i_points_count).reshape(  # Initializes the grid
                        self.a_grid_size[0],
                        self.a_grid_size[1],
                        self.a_grid_size[2]
                    ).astype(np.uint16)  # Stores values between 0 and 300
                    o_structure.a_grid[  # Loads the elements symbols in the grid
                        o_structure.a_atoms["grid_x"],
                        o_structure.a_atoms["grid_y"],
                        o_structure.a_atoms["grid_z"]
                    ] = o_structure.a_atoms["type_number"]
                    plot_heatmap(o_structure.a_grid, z=9, lab=False,palette=None,
                                 plot_name=gp.D_PARAMETERS_COMPARISON['p_output_comparison']+'/'+o_structure.s_name+'_grid_before_vdw.svg')
                self.generate_vdw_spheres(  # Generates the VdW volumes around each atom
                    o_structure=o_structure,  # The structure to be incorporated
                    d_parameters=d_parameters, # Dictionary of the program parameters
                )
                if gp.D_PARAMETERS_GLOBAL['explicit_grid']:
                    plot_heatmap(o_structure.a_grid, z=9, lab=False,palette=None,
                                plot_name=gp.D_PARAMETERS_COMPARISON['p_output_comparison']+'/'+o_structure.s_name+'_grid_after_vdw.svg')
                # Generating VDW volumes


    # End method ---------------------------------------- #

    def generate_vdw_spheres(self, o_structure, d_parameters):
        """
        Generates the VdW volumes around each atom in a specific grid
        :param o_structure: The structure to be incorporated with its VdW volume
        :param d_parameters: Dictionary of the program parameters
        """

        # Preparing variables
        l_l_elements = o_structure.l_l_elements  # Shortcut for the structure field containing sorted data for each element
        # If the VdW radius by element has not been already retrieved
        if o_structure.b_loaded is not True:
            o_structure.b_loaded = True  # Sets the structure as loaded
            o_structure.a_vdw = np.zeros(0, dtype=gp.a_vdw_dtype)
            # For each atom type in the structure
            for i_element in range(len(l_l_elements)):
                try:
                    i_radius = self.d_scaled_vdw[l_l_elements[i_element][0]]  # Retrieves the VdW radius of the element
                except:
                    i_radius = self.d_scaled_vdw[
                        gp.D_SYBYL_TYPE[l_l_elements[i_element][0]]]  # Retrieves the VdW radius of the element

                l_i_radius_range = list(
                    range(-i_radius, i_radius + 1))  # Builds a list of distances included in the sphere
                l_l_elements[i_element][4] = i_radius  # Saves the VdW radius
                l_l_elements[i_element][5] = self.create_vdw_sphere(
                    d_parameters=d_parameters,  # Dictionary of the program parameters
                    i_radius=i_radius,  # VdW radius of the element
                    l_i_radius_range=l_i_radius_range  # Range of radius around the element
                )


            # For each chemical element present
            # for i_element in range(len(l_l_elements)):

                # For each atom in the structure
                for a_atom in l_l_elements[i_element][3]:

                    a_sphere_coords = (  # Retrieves the coordinates of each point of the sphere
                        l_l_elements[i_element][5][0] + a_atom[0],  # X coordinates
                        l_l_elements[i_element][5][1] + a_atom[1],  # Y coordinates
                        l_l_elements[i_element][5][2] + a_atom[2]  # Z coordinates
                    )

                    new_vdw = np.zeros(a_sphere_coords[0].size, dtype=gp.a_vdw_dtype)
                    # Step 2: Modify the 'HetAtom' field
                    new_vdw['type_number'] = l_l_elements[i_element][1]

                    # Step 3: Create as many new_vdw elements as there are coordinates

                    # Step 4: Modify the 'grid_*' fields for each new_vdw element
                    new_vdw['grid_x'] = a_sphere_coords[0]
                    new_vdw['grid_y'] = a_sphere_coords[1]
                    new_vdw['grid_z'] = a_sphere_coords[2]

                    # Step 5: Add the new_vdw elements to the a_atoms array
                    # o_structure.a_atoms = np.concatenate((o_structure.a_atoms, new_vdw_elements))
                    o_structure.a_vdw = np.concatenate((o_structure.a_vdw, new_vdw))
                    # If the comparison uses the type of elements
                    if gp.D_PARAMETERS_GLOBAL['explicit_grid']:
                        # o_structure.a_grid[a_sphere_coords] = o_structure.a_grid[a_atom[0]][a_atom[1]][a_atom[2]]	# Fills the sphere with the element
                        o_structure.a_grid[a_sphere_coords] = l_l_elements[i_element][1]  # Fills the sphere with the element
                    #
                    #
                    # # If only the volume is considered
                    # else:
                        # o_structure.a_grid[a_sphere_coords] = 1  # Fills the sphere with the same element
        # End for
    # End method ---------------------------------------- #
    @staticmethod
    def create_vdw_sphere(d_parameters, i_radius, l_i_radius_range):
        """
        Defines a spherical array of points for a specific geometry
        :param d_parameters: Dictionary of the program parameters
        :param i_radius: The raw VdW radius of the element, in grid points
        :param l_i_radius_range: The list of points in the radius range
        :return: A spherical array of relative coordinates
        """

        # Preparing variables
        s_grid_geometry = d_parameters["s_grid_geometry"].upper()  # Converts to uppercase the grid geometry
        a_sphere = None  # Array of points coordinates for each grid point in the VdW range
        l_s_logs = []  # Creates an empty list for logs

        # If the grid geometry is a taxicab
        if s_grid_geometry == "TAXICAB":
            a_sphere = np.array(  # The taxicab sphere formula
                [
                    (x, y, z) for x in l_i_radius_range for y in l_i_radius_range for z in l_i_radius_range
                    if abs(x) + abs(y) + abs(z) <= i_radius
                ]
            ).astype(np.int32)

        # If the grid geometry is uniform
        elif s_grid_geometry == "UNIFORM":
            a_sphere = np.array(  # The uniform sphere formula
                [
                    (x, y, z) for x in l_i_radius_range for y in l_i_radius_range for z in l_i_radius_range
                ]
            ).astype(np.int32)

        # If the grid geometry is a classic sphere
        elif s_grid_geometry == "SPHERE":
            a_sphere = np.array(  # The classic sphere formula
                [
                    (x, y, z) for x in l_i_radius_range for y in l_i_radius_range for z in l_i_radius_range
                    if x ** 2 + y ** 2 + z ** 2 <= i_radius ** 2
                ]
            ).astype(np.int32)

        # If the geometry is unknown
        else:
            l_s_logs.append(
                "ERROR : Unknown sphere geometry '{}', known geometries are 'taxicab', 'uniform' and 'sphere'.".format(
                    s_grid_geometry))  # Defines the error message
            terminate_program_process(  # Stops the program
                l_s_content=l_s_logs  # Content to save in the logs
            )
        # End if
        return a_sphere.T  # Returns the spherical array of points

    # End method ---------------------------------------- #

    def retrieve_nearest_score(self, s_interaction, f_distance):
        """
        Retrieves the score corresponding to the closest distance to the query
        :param s_interaction: The atom_atom_neighbourindex interaction to analyse
        :param f_distance: The distance, in Angstroms, to compare
        :return: The score corresponding to the distance closest to the query
        """

        # If the interaction is present within the density files
        if s_interaction in self.d_d_distance_score:
            l_f_distances = list(
                self.d_d_distance_score[s_interaction].keys())  # Loads every distances recorded for this interaction
            i_nearest = l_f_distances[min(range(len(l_f_distances)), key=lambda i: abs(
                l_f_distances[i] - f_distance).any())]  # Retrieves the index of the nearest recorded distance

            return self.d_d_distance_score[s_interaction][
                i_nearest]  # Returns the score corresponding to the distance closest to the query

        # If this interaction does not exist
        else:
            return 0.0  # Returns a null score

    # End method ---------------------------------------- #

    # Progression

    def setup_progress(self, s_text=""):
        """
        Initializes a progression bar
        """

        # Preparing the toolbar

        # If the text field is not empty
        if s_text != "":
            s_header = "|{:^46}|".format(s_text)

        # If the text field is empty
        else:
            s_header = "|{:^46}|".format("Running structure comparison...")

        print(s_header)
        self.i_progress_length = 50  # Defines the length of the progression bar
        sys.stdout.write(  # Allocates space to the progression bar
            "|%s|" % (' ' * self.i_progress_length)
        )
        sys.stdout.flush()  # Do not resets the terminal
        sys.stdout.write(  # Writes the first char of the bar
            "\b" * (self.i_progress_length + 1)
        )

    # End method ---------------------------------------- #

    def update_progress(self):
        """
        Updates the progression bar
        """

        i_previous_percentage = int(  # Determines the "percentage" before the update
            self.i_progress * 50 / len(self.l_l_tasks)
        )
        self.i_progress += 1  # Updates the number of completed tasks
        i_current_percentage = int(  # Determines the percentage after the update
            self.i_progress * 50 / len(self.l_l_tasks)
        )

        # For each missing percentage since the last update
        for i in range((i_current_percentage - i_previous_percentage)):  # TODO
            sys.stdout.write("-")  # Displays the progression
            sys.stdout.flush()  # Without resetting the terminal

    # End method ---------------------------------------- #

    def close_progress(self):
        """
        Closes the progression bar
        """
        sys.stdout.write("|\n")  # Ending the progression bar
        self.i_progress = 0  # Resets the progress advancement
# End method ---------------------------------------- #

# ---------------------------------------------------------------------------- #


# Reference ------------------------------------------------------------------ #

