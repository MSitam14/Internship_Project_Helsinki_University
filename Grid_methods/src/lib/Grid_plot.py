
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm,Normalize,LinearSegmentedColormap
from Grid_methods.src.lib.progress_bar_color import create_color_mapping,create_custom_color_mapping

def plot_grid_3D(a_grid):
    # Assuming a_grid is a 3D numpy array
    # a_grid = a_grid['element_symbol']
    # Get the dimensions of the grid
    x_dim, y_dim, z_dim = a_grid.shape

    # Create a list of corner points
    corners = [(0, 0, 0), (x_dim, 0, 0), (0, y_dim, 0), (0, 0, z_dim),
               (x_dim, y_dim, 0), (x_dim, 0, z_dim), (0, y_dim, z_dim),
               (x_dim, y_dim, z_dim)]

    # Create a figure
    fig = plt.figure()

    # Create 3D subplot
    ax = fig.add_subplot(111, projection='3d')
    x, y, z = a_grid.nonzero()

    # Plot the corner points
    for corner in corners:
        ax.scatter(*corner, color='blue')  # Plot corner points in blue for visibility

    # Get the values at these coordinates
    values = a_grid[x, y, z]

    # Determine unique values and assign discrete colors
    unique_values = np.unique(values)
    palette = sns.color_palette("Set2", len(unique_values))  # "Set2" is good for discrete colors

    # Create a mapping from values to colors
    value_to_color = {val: palette[i] for i, val in enumerate(unique_values)}

    # Get colors for each point based on their value
    point_colors = [value_to_color[val] for val in values]

    # Plot the points, colored by their mapped values
    scatter = ax.scatter(x, y, z, color=point_colors)

    # Add a colorbar with mappings
    sc_map = sns.color_palette("Set2", len(unique_values), as_cmap=True)
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=sc_map, norm=plt.Normalize(vmin=min(unique_values), vmax=max(unique_values))), ax=ax)
    cbar.set_label('Element Symbol Value')

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.axis('equal')

    plt.show()
    return 0
def plot_grid_2D(a_grid):
    ### create a 2D plot of the grid

    # Create a figure
    fig = plt.figure()
    x_dim, y_dim, z_dim = a_grid.shape

    # Create 2D subplot
    ax = fig.add_subplot(111)
    x, y, z = a_grid.nonzero()
    # Create a list of corner points
    corners = [(0, 0, 0), (x_dim, 0, 0), (0, y_dim, 0), (0, 0, z_dim),
               (x_dim, y_dim, 0), (x_dim, 0, z_dim), (0, y_dim, z_dim),
               (x_dim, y_dim, z_dim)]
    # Plot the corner points
    for corner in corners:
        ax.scatter(corner[0], corner[1], color='blue')  # Plot corner points in blue for visibility

    # Get the values at these coordinates
    values = a_grid[x, y, z]

    # Determine unique values and assign discrete colors
    unique_values = np.unique(values)
    palette = sns.color_palette("Set2", len(unique_values))  # "Set2" is good for discrete colors

    # Create a mapping from values to colors
    value_to_color = {val: palette[i] for i, val in enumerate(unique_values)}

    # Get colors for each point based on their value
    point_colors = [value_to_color[val] for val in values]

    # Plot the points, colored by their mapped values
    scatter = ax.scatter(x, y, color=point_colors)

    # Add a colorbar with mappings
    sc_map = sns.color_palette("Set2", len(unique_values), as_cmap=True)
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=sc_map, norm=plt.Normalize(vmin=min(unique_values), vmax=max(unique_values))), ax=ax)
    cbar.set_label('Element Symbol Value')

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('equal')

    plt.show()
    return 0


# Function to check neighbors for NaN

def check_nan_neighbors_and_create_lines(arr, e_color='red', lw=2):
    rows, cols = arr.shape
    lines = []

    for r in range(rows):
        for c in range(cols):
            current_val = arr[r, c]
            # Check if current cell is NaN, skip if it is
            if np.isnan(current_val):
                continue

            # Up
            if r > 0 and np.isnan(arr[r-1, c]):
                lines.append(plt.Line2D([c, c+1], [r, r], color=e_color, linewidth=lw))
            # Down
            if r < rows - 1 and np.isnan(arr[r+1, c]):
                lines.append(plt.Line2D([c, c+1], [r+1, r+1], color=e_color, linewidth=lw))
            # Left
            if c > 0 and np.isnan(arr[r, c-1]):
                lines.append(plt.Line2D([c, c], [r, r+1], color=e_color, linewidth=lw))
            # Right
            if c < cols - 1 and np.isnan(arr[r, c+1]):
                lines.append(plt.Line2D([c+1, c+1], [r, r+1], color=e_color, linewidth=lw))

    return lines

def plot_heatmap(a_grid, x1=0, x2=0, y1=0, y2=0, z=50, lab=False,palette=None,plot_name=False,neg=False,fmt=".0f"):
    # plt.switch_backend('Agg')
    if x1 == 0 and x2 == 0 and y1 == 0 and y2 == 0:
        x1, x2, y1, y2 = 0, a_grid.shape[1], 0, a_grid.shape[0]
    layer = a_grid[y1:y2,x1:x2, z]
    layer = np.where(layer==0, np.nan, layer)
    # Create the color mapping
    if neg:
        value_to_color = create_custom_color_mapping()
    else:
        value_to_color = create_color_mapping(palette)
    # Create a figure
    # Sort the dictionary by keys (which represent the values)
    sorted_keys = sorted(value_to_color.keys())
    sorted_colors = [value_to_color[key] for key in sorted_keys]
    # Create the colormap
    cmap = ListedColormap(sorted_colors)
    # Normalize the data to match the colormap range
    bounds = sorted_keys + [max(sorted_keys) + 1]  # Add an upper bound
    norm = BoundaryNorm(bounds, cmap.N)
    # cmap = LinearSegmentedColormap.from_list("custom_cmap", sorted_colors, N=len(sorted_colors))
    fig, ax = plt.subplots()
    # Create a heatmap
    heatmap = sns.heatmap(layer, cmap=cmap, ax=ax, linewidths=0.5, linecolor='lightgrey', annot=lab, fmt=fmt,norm=norm,
                          cbar=False, annot_kws={'size': 9})

    heatmap.set_facecolor((1,1,1))  # Set background color for NaN entries
    # Hide x and y axis labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])

    # Add colorbar to the figure
    cbar = fig.colorbar(mappable=plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, orientation='vertical')
    cbar.set_label('Element Symbol Value', rotation=270, labelpad=15)  # Title for the colorbar

    # Set the ticks at the center of each color, using the midpoints between the bounds
    tick_locs = [bounds[i] + 0.5 for i in range(len(bounds) - 1)]
    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels(sorted_keys)

    # Show the plot
    plt.tight_layout()
    if plot_name:
        plt.savefig(plot_name,format='svg',bbox_inches='tight',dpi=300)
    # # Show the plot
    plt.show()
    return 0



def plot_comparison_heatmap(a_grid, b_grid, x1=0, x2=0, y1=0, y2=0, z=50, lab=False,palette='Spectral',plot_name=False):

    grid_comp = np.where(a_grid == b_grid, a_grid, 0)

    if x1 == 0 and x2 == 0 and y1 == 0 and y2 == 0:
        x1, x2, y1, y2 = 0, grid_comp.shape[1], 0, grid_comp.shape[0]
    layer_a = a_grid[y1:y2,x1:x2, z]
    layer_a = np.where(layer_a==0, -1, layer_a)
    layer_b = b_grid[y1:y2,x1:x2, z]
    layer_b = np.where(layer_b==0, -1, layer_b)
    layer = np.where(layer_a==layer_b, layer_a, 0)
    layer = np.where(layer==-1, np.nan, layer)
    # layer = np.where(layer==0, np.nan, layer)
    layer_a = np.where(layer_a==-1, np.nan, layer_a)
    layer_b = np.where(layer_b==-1, np.nan, layer_b)
    # Create the color mapping
    value_to_color = create_color_mapping(palette)
    # Create a figure
    # Sort the dictionary by keys (which represent the values)
    sorted_keys = sorted(value_to_color.keys())
    sorted_colors = [value_to_color[key] for key in sorted_keys]
    # Create the colormap
    cmap = ListedColormap(sorted_colors)
    # Normalize the data to match the colormap range
    bounds = sorted_keys + [max(sorted_keys) + 1]  # Add an upper bound
    norm = BoundaryNorm(bounds, cmap.N)
    # cmap = LinearSegmentedColormap.from_list("custom_cmap", sorted_colors, N=len(sorted_colors))
    fig, ax = plt.subplots()

    # Create the ouline of the two original grids
    outl_a = check_nan_neighbors_and_create_lines(layer_a, e_color='Navy', lw=3)
    outl_b = check_nan_neighbors_and_create_lines(layer_b, e_color='Crimson',lw=3)
    # Create a heatmap
    heatmap = sns.heatmap(layer, cmap=cmap, ax=ax, linewidths=0.5, linecolor='grey', annot=lab, fmt=".0f",norm=norm,
                          cbar=False)

    heatmap.set_facecolor((1,1,1))  # Set background color for NaN entries
    for line in outl_a:
        ax.add_line(line)
    for line in outl_b:
        ax.add_line(line)
    # Hide x and y axis labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])

    # Add colorbar to the figure
    cbar = fig.colorbar(mappable=plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, orientation='vertical')
    cbar.set_label('Element Symbol Value', rotation=270, labelpad=15)  # Title for the colorbar

    # Set the ticks at the center of each color, using the midpoints between the bounds
    tick_locs = [bounds[i] + 0.5 for i in range(len(bounds) - 1)]
    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels(sorted_keys)

    # Show the plot
    plt.tight_layout()
    # save the plot
    if plot_name:
        plt.savefig(plot_name,format='svg')
    # Show the plot
    # plt.show()
    return 0
