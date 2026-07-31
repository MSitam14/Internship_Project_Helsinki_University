from matplotlib.colors import Normalize
import numpy as np
import seaborn as sns
from Grid_methods.src.lib import global_parameters as gp


def get_color(progress):
    """Return color as per progress with a matte transition from red to green through yellow and orange."""
    if progress < 0.1:
        return '\033[38;2;139;0;0m'  # Dark Red
    elif progress < 0.2:
        return '\033[38;2;205;55;0m'  # Dark Orange Red
    elif progress < 0.3:
        return '\033[38;2;205;102;0m'  # Darker Orange
    elif progress < 0.4:
        return '\033[38;2;205;139;0m'  # Orange
    elif progress < 0.5:
        return '\033[38;2;205;173;0m'  # Gold
    elif progress < 0.6:
        return '\033[38;2;238;220;130m'  # Light Goldenrod
    elif progress < 0.7:
        return '\033[38;2;188;238;104m'  # Yellowish Green
    elif progress < 0.8:
        return '\033[38;2;154;205;50m'  # Yellow Green
    elif progress < 0.9:
        return '\033[38;2;107;142;35m'  # Olive Drab
    else:
        return '\033[38;2;34;139;34m'  # Forest Green


def create_color_mapping(palette='Spectral'):
    # Initialize an empty list to store all unique values
    all_unique_values = []

    try:
        l_structures = gp.O_SYSTEM_COMPARISON.l_o_structures
    except AttributeError:
        l_structures = gp.O_SYSTEM_HOTSPOT.l_o_structures
    # Iterate over all structures in the list
    for structure in l_structures:
        # Get unique values from the current structure's grid and extend the global list
        all_unique_values.extend(np.unique(structure.a_atoms['type_number']))

    # Get unique values from the global list
    unique_values = np.unique(all_unique_values)
    # remove 0
    unique_values = unique_values[unique_values != 0]

    # Determine unique values and assign discrete colors
    l_color = len(unique_values)

    # Create a list of colors
    colors = sns.color_palette(palette, l_color)

    # add the color grey for 0
    unique_values = np.append(unique_values, 0)
    colors.append((0.90, 0.90, 0.90))

    # Create a mapping from values to colors
    value_to_color = {val: color for val, color in zip(unique_values, colors)}

    return value_to_color

def create_custom_color_mapping():
    # Define the ranges
    negative_values = np.array([-4, -3, -2, -1])
    non_negative_values = [0, 0.29,0.30, 1]  # Just the key points

    # Define the colormaps
    neg_cmap = sns.color_palette("Blues_r", as_cmap=True)

    # Normalize the negative values from 0 to 1 for mapping
    norm_neg = Normalize(vmin=-4, vmax=0.5)
    negative_colors = [neg_cmap(norm_neg(value)) for value in negative_values]

    # Assign colors for non-negative values directly
    non_negative_colors = ['red', 'red', 'green','green']  # Red up to 0.5, green above 0.5

    # Create a dictionary mapping each value to a color
    value_to_color = {}
    for val, color in zip(negative_values, negative_colors):
        value_to_color[val] = color
    for val, color in zip(non_negative_values, non_negative_colors):
        value_to_color[val] = color

    return value_to_color