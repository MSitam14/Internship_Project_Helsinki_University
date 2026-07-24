# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano, Samuel Besseau
# Contact : samuelbesseau77@gmail.com
# University of Helsinki
# Created : June 2020
# Updated : May 2023
# ---------------------------------------------------------------------------- #



# Importations --------------------------------------------------------------- #

# Universal modules
# Time manipulation
# Phylogenetic tree tool
from copy import deepcopy
# Allows the total copy of variables




# ---------------------------------------------------------------------------- #


# Class ---------------------------------------------------------------------- #

class TreePlot:
    """
	A class converting a matrix of scores into a phylogenetic tree
	"""

    def __init__(self):
        """
		Initializes the tree fields
		"""

        # Raw data fields
        self.d_nodes = {}  # The list of nodes registered
        self.l_s_nodes = []  # The list of nodes names
        self.l_l_distances = []  # The matrix of distances
        self.l_l_coverage = []  # The matrix of coverage for the first element
        self.i_node_index = 0  # The index of the last node registered

        # Computed fields
        self.s_tree = ""  # The tree as text, in newick format
        self.o_tree = None  # The tree object generated from the newick tree
        self.o_style = None  # The tree style to apply when rendered

    # End method ---------------------------------------- #

    def __repr__(self):
        """
		Displays the fields of the tree
		"""

        l_s_content = [  # List containing the content to print
            "> The tree's matrix :"
        ]
        s_line = " " * 8  # The first line indentation

        # For each node in the matrix
        for s_node in self.l_s_nodes:
            s_line += "{:<8}".format(s_node)  # Appends the name of each node

        l_s_content.append(s_line)  # Saves the first line

        # For each node in the matrix
        for i_node_index in range(len(self.l_l_distances)):
            s_line = "{:<8}".format(self.l_s_nodes[
                                        i_node_index])  # Starts the line with the name of the node

            # For each node within
            for f_node in self.l_l_distances[i_node_index]:

                # If the node value is None
                if f_node is None:
                    s_line += "{:<8}".format(str(f_node))  # Appends None

                # If the node value is valid
                else:
                    s_line += "{:<8.2f}".format(
                        f_node)  # Appends the score of the two concerned nodes
            # End for

            l_s_content.append(s_line)  # Appends each line
        # End for

        return "\n".join(l_s_content)  # Returns the content to show

    # End method ---------------------------------------- #
    # Data gathering

    def add_score(self, s_first_node, s_second_node, d_comparison):
        """
		Adds a score and it's nodes, if necessary, to the matrix of scores
		:param s_first_node: The first element
		:param s_second_node: The second element
		:param d_comparison: The dictionary containing the scores of the comparison between the two elements
		"""

        # For each node to actualize
        for s_node in [s_first_node, s_second_node]:

            # If the node is not registered in the dictionary
            if s_node not in self.d_nodes.keys():

                self.d_nodes[s_node] = self.i_node_index  # Registers the node in the dictionary
                self.l_s_nodes.append(s_node)  # Saves the node name
                self.l_l_distances.append([0.0] * self.i_node_index)  # Creates a place for each missing score
                self.l_l_coverage.append([1.0] * self.i_node_index)  # Creates a place for each missing coverage
                self.i_node_index += 1  # Adds one to the number of registered nodes

                # Grow ALL existing rows to keep matrices square (distances + coverage)
                for l_node in self.l_l_distances:
                    if len(l_node) < self.i_node_index:
                        l_node.append(0.0)  # Appends an empty item to the list
                for l_node in self.l_l_coverage:
                    if len(l_node) < self.i_node_index:
                        l_node.append(1.0)

            # End for
        # End if
        # End for

        i_first_index = self.d_nodes[
            s_first_node]  # Loads the index of the first node
        i_second_index = self.d_nodes[
            s_second_node]  # Loads the index of the second node
        self.l_l_distances[i_first_index][
            i_second_index] = 1-d_comparison['tanimoto']  # Saves the score in the symmetrical matrix
        self.l_l_distances[i_second_index][
            i_first_index] = 1-d_comparison['tanimoto']  # Saves the score in the symmetrical matrix
        self.l_l_coverage[i_first_index][
            i_second_index] = d_comparison['coverage_A_by_B']  # Saves the coverage in the upper part of the matrix
        self.l_l_coverage[i_second_index][
            i_first_index] = d_comparison['coverage_B_by_A']  # Saves the

    # End method ---------------------------------------- #

    # Tree generation

    def compute_tree(self, d_parameters):
        """
		Computes the tree topology and saves it into a newick format
		:param d_parameters: Parameters used for the tree computation
		"""

        # Preparing variables
        l_l_distances = deepcopy(self.l_l_distances)  # Copies the matrix of scores
        l_s_nodes = deepcopy(self.l_s_nodes)  # Copies the list of leaf names
        f_max = 0  # Maximal score buffer
        i_max_first = 0  # X coordinates of the maximal score
        i_max_second = 0  # Y coordinates of the maximal score

        # Sorting the matrix
        # For each node merging needed
        for i_loop in range(len(self.l_s_nodes) - 1):
            # For each node in the matrix
            for i_first_node in range(len(l_l_distances)):

                # For each node in the matrix
                for i_second_node in range(len(l_l_distances)):

                    # If the score is actually the best
                    if l_l_distances[i_first_node][i_second_node] > f_max:
                        f_max = l_l_distances[i_first_node][
                            i_second_node]  # Saves the maximal score
                        i_max_first = i_first_node  # Saves the x coordinates of the maximal score
                        i_max_second = i_second_node  # Saves the y coordinates of the maximal score
            # End for

            # If the tree only needs topology
            if d_parameters["b_only_topology"]:
                f_max = 1  # Defines the branch length as 1
                d_parameters[
                    "b_branch_length"] = False  # Do not display the branch lengths

            l_s_nodes[i_max_first] = "({}:{}, {}:{})".format(
                # Formats the tree as text
                l_s_nodes[i_max_first],
                f_max,
                l_s_nodes[i_max_second],
                f_max,
            )

            # For each element, computes the mean scores
            for i_node in range(len(l_l_distances)):
                l_l_distances[i_max_first][i_node] = (l_l_distances[i_max_first][
                                                       i_node] +
                                                   l_l_distances[i_max_second][
                                                       i_node]) / 2  # New average score
                l_l_distances[i_node][i_max_first] = (l_l_distances[i_node][
                                                       i_max_first] +
                                                   l_l_distances[i_node][
                                                       i_max_second]) / 2  # New average score

            l_l_distances[i_max_first][i_max_first] = 0 # Sets the score of an element with itself to 0

            # For each element, deletes the merged elements (row and column)
            for i_node in range(len(l_l_distances)):
                l_l_distances[i_node].pop(
                    i_max_second)  # Deletes the row of the merged elements

            l_s_nodes.pop(
                i_max_second)  # Deletes the name of the merged element
            l_l_distances.pop(
                i_max_second)  # Deletes the column of the merged element

            # For each element, resets the score of an element compared with itself
            for i_node in range(len(l_l_distances)):
                l_l_distances[i_node][
                    i_node] = -1.0  # Sets to -1 the score of an element with itself

            f_max = 0.0  # Resets the maximum score comparator
            i_max_first = 0  # Resets the x index of the maximum score
            i_max_second = 0  # Resets the y index of the maximum score
        # End for

        self.s_tree = l_s_nodes[0] + ';'  # Saves the tree

    # End method ---------------------------------------- #


# End method ---------------------------------------- #

# ---------------------------------------------------------------------------- #


# Reference ------------------------------------------------------------------ #

# from tree_plot import TreePlot
# Generates, renders and saves trees

# ---------------------------------------------------------------------------- #
#
# t.d_nodes = {'4zj8': 0, '4s0v': 1, '4grv': 2}
# t.l_s_nodes = ['4zj8', '4s0v', '4grv']
# t.l_l_distances = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.07762442946388846], [0.0, 0.07762442946388846, 0.0]]
# t.i_node_index = 3
#
# t.s_tree = '4zj8:0.0,4s0v:0.0,4grv:0.0;'


# Display tree

# generate a tree from lower triangular using neighbor joining




