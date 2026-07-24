# read all water_distance1.csv csv files in the subdirectory of /mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/test_set_hotspot/30_08_2024-17_11/
# and concatenate them to generate a figure of the hotspot analysis

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn
import numpy as np
import glob
from scipy.stats import gaussian_kde

from sklearn.neighbors import KDTree

# Change the current working directory
# Define the path to the directory containing the csv files
# path = '/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/test_set_hotspot/01_09_2024-19_10/'
# path_tag = '/home/dreano/Desktop/Grid_methods/data/output/hotspot/Score_test_set/19_09_2024-17_06/' # where we place hotspot based on tag position
path = '/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/test_set_hotspot/Water_prediction_test_set/'
path_random =  '/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/test_set_hotspot/Random_test_set/' # hotspot are place randomly in the box
matplotlib.use('Agg')

# List all the csv files in the directory
# all_files = glob.glob(path + "*/*/water_distance1.csv")
all_files_hot_to_wat = glob.glob(path + "*/*/hotspot_distance_1.csv")
all_files_wat_to_hot = glob.glob(path + "*/*/water_distance_1.csv")
# Create an empty list to store the dataframes
all_files_hot_to_wat_random = glob.glob(path_random +  "*/*water*full*.csv")
all_files_wat_to_hot_random = glob.glob(path_random +  "*/*spot*full*.csv")
all_files_hot_to_wat_clean = glob.glob(path_random +  "*/*water*clean*.csv")
all_files_wat_to_hot_clean = glob.glob(path_random +  "*/*spot*clean*.csv")


all_files_random_clean = glob.glob(path_random + "*/*clean*.csv")
all_files_full_random = glob.glob(path_random + "*/*full*.csv")

li = []
li_tag = []
li_wat_to_hot = []
li_hot_to_wat = []

# Loop through the csv files
for filename in all_files_wat_to_hot:
    # Read the csv file
    df = pd.read_csv(filename, index_col=None, header=0)
    # keep only the lines where the column 'step' is equal to 3
    # df = df[df['step'] == 3]
    # Append the dataframe to the list
    li_wat_to_hot.append(df)

for filename in all_files_hot_to_wat:
    # Read the csv file
    df = pd.read_csv(filename, index_col=None, header=0)
    # keep only the lines where the column 'step' is equal to 3
    # df = df[df['step'] == 3]
    # Append the dataframe to the list
    li_hot_to_wat.append(df)


li_full_hot_to_wat = []
for filename in all_files_hot_to_wat_random:
    df = pd.read_csv(filename, index_col=None, header=0)
    # add a column 'run' to the dataframe with the name of the run
    df['run'] = filename[-5]
    li_full_hot_to_wat.append(df)

li_full_wat_to_hot = []
for filename in all_files_wat_to_hot_random:
    df = pd.read_csv(filename, index_col=None, header=0)
    # add a column 'run' to the dataframe with the name of the run
    df['run'] = filename[-5]
    li_full_wat_to_hot.append(df)

li_clean_hot_to_wat = []
for filename in all_files_hot_to_wat_clean:
    df = pd.read_csv(filename, index_col=None, header=0)
    # add a column 'run' to the dataframe with the name of the run
    df['run'] = filename[-5]
    li_clean_hot_to_wat.append(df)

li_clean_wat_to_hot = []
for filename in all_files_wat_to_hot_clean:
    df = pd.read_csv(filename, index_col=None, header=0)
    # add a column 'run' to the dataframe with the name of the run
    df['run'] = filename[-5]
    li_clean_wat_to_hot.append(df)



# Concatenate all the dataframes in the list
frame_wat_to_hot = pd.concat(li_wat_to_hot, axis=0, ignore_index=True)
frame_hot_to_wat = pd.concat(li_hot_to_wat, axis=0, ignore_index=True)
# focus only on the step 3 hotspots
frame_hot_to_wat_s3 = frame_hot_to_wat[frame_hot_to_wat['Step'] == 3]
# concatenate all the dataframes in the list li_full only when column 'run' is equal to 4

frame_full_hot_to_wat = pd.concat(li_full_hot_to_wat, axis=0, ignore_index=True)
frame_full_hot_to_wat_0 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '0']
frame_full_hot_to_wat_1 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '1']
frame_full_hot_to_wat_2 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '2']
frame_full_hot_to_wat_3 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '3']
frame_full_hot_to_wat_4 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '4']
frame_full_hot_to_wat_5 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '5']
frame_full_hot_to_wat_6 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '6']
frame_full_hot_to_wat_7 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '7']
frame_full_hot_to_wat_8 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '8']
frame_full_hot_to_wat_9 = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == '9']

frame_full_wat_to_hot = pd.concat(li_full_wat_to_hot, axis=0, ignore_index=True)
frame_full_wat_to_hot_0 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '0']
frame_full_wat_to_hot_1 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '1']
frame_full_wat_to_hot_2 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '2']
frame_full_wat_to_hot_3 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '3']
frame_full_wat_to_hot_4 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '4']
frame_full_wat_to_hot_5 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '5']
frame_full_wat_to_hot_6 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '6']
frame_full_wat_to_hot_7 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '7']
frame_full_wat_to_hot_8 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '8']
frame_full_wat_to_hot_9 = frame_full_wat_to_hot[frame_full_wat_to_hot['run'] == '9']

frame_clean_hot_to_wat = pd.concat(li_clean_hot_to_wat, axis=0, ignore_index=True)
frame_clean_hot_to_wat_0 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '0']
frame_clean_hot_to_wat_1 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '1']
frame_clean_hot_to_wat_2 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '2']
frame_clean_hot_to_wat_3 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '3']
frame_clean_hot_to_wat_4 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '4']
frame_clean_hot_to_wat_5 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '5']
frame_clean_hot_to_wat_6 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '6']
frame_clean_hot_to_wat_7 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '7']
frame_clean_hot_to_wat_8 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '8']
frame_clean_hot_to_wat_9 = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == '9']

frame_clean_wat_to_hot = pd.concat(li_clean_wat_to_hot, axis=0, ignore_index=True)
frame_clean_wat_to_hot_0 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '0']
frame_clean_wat_to_hot_1 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '1']
frame_clean_wat_to_hot_2 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '2']
frame_clean_wat_to_hot_3 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '3']
frame_clean_wat_to_hot_4 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '4']
frame_clean_wat_to_hot_5 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '5']
frame_clean_wat_to_hot_6 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '6']
frame_clean_wat_to_hot_7 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '7']
frame_clean_wat_to_hot_8 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '8']
frame_clean_wat_to_hot_9 = frame_clean_wat_to_hot[frame_clean_wat_to_hot['run'] == '9']

frame_hot_to_wat_s3['Distance'].describe().apply(lambda x: round(x, 3))
frame_full_hot_to_wat_0['distance'].describe().apply(lambda x: round(x, 3))
frame_clean_hot_to_wat_0['distance'].describe().apply(lambda x: round(x, 3))
# create the cumulative distribution function of the distance column
plt.figure(figsize=(12, 8))
seaborn.ecdfplot(frame_hot_to_wat_s3['Distance'], color=seaborn.color_palette("tab10")[0])
seaborn.ecdfplot(frame_full_hot_to_wat_0['distance'], color=seaborn.color_palette("tab10")[3])

# Add horizontal line at 80% of the Y-axis
plt.axhline(y=0.75, color='grey', linestyle='--')
# Add vertical line at the corresponding X-axis value
plt.axvline(x=frame_hot_to_wat_s3['Distance'].quantile(0.75), color='grey', linestyle='--')
plt.axvline(x=frame_full_hot_to_wat_0['distance'].quantile(0.75), color='grey', linestyle='--')
plt.axvline(x=frame_clean_hot_to_wat_0['distance'].quantile(0.75), color='grey', linestyle='--')
seaborn.ecdfplot(frame_full_hot_to_wat_1['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_2['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_3['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_4['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_5['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_6['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_7['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_8['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_hot_to_wat_9['distance'], color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_clean_hot_to_wat_0['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_1['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_2['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_3['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_4['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_5['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_6['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_7['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_8['distance'], color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_hot_to_wat_9['distance'], color=seaborn.color_palette("tab10")[2])

# add legend
plt.legend(['grid','full_0','full_1','full_2','full_3','full_4','full_5','full_6','full_7','full_8','full_9','clean_0','clean_1','clean_2','clean_3','clean_4','clean_5','clean_6','clean_7','clean_8','clean_9'])
# fix the x-axis limits
plt.xlim(0,30)
# fix ticks on the x-axis
plt.xticks(np.arange(0, 30, 1))
#fix ticks on the y-axis
plt.yticks(np.arange(0, 1.1, 0.1))
plt.xlabel('Distance')
plt.ylabel('Cumulative Probability')
plt.title('Cumulative Distribution Function of the closest distance between hotspot_step3 and water')
plt.savefig('cdf_hot_to_wat_3.svg')

#plot the distance line of the hotspot to water distance, and the two conctatened line off the 10 run of random and clean

plt.figure(figsize=(12, 8))

# Plot grid ECDF
seaborn.ecdfplot(frame_hot_to_wat_s3['Distance'], color=seaborn.color_palette("tab10")[0], label='grid')

# Compute mean/min/max ECDF for full
distance_grid = np.linspace(0, 30, 301)
ecdf_matrix_full = []
for run in range(10):
    subset = frame_full_hot_to_wat[frame_full_hot_to_wat['run'] == str(run)]['distance'].dropna()
    ecdf = [np.mean(subset <= d) for d in distance_grid]
    ecdf_matrix_full.append(ecdf)
ecdf_matrix_full = np.array(ecdf_matrix_full)
mean_full = ecdf_matrix_full.mean(axis=0)
min_full = ecdf_matrix_full.min(axis=0)
max_full = ecdf_matrix_full.max(axis=0)

# Compute mean/min/max ECDF for clean
ecdf_matrix_clean = []
for run in range(10):
    subset = frame_clean_hot_to_wat[frame_clean_hot_to_wat['run'] == str(run)]['distance'].dropna()
    ecdf = [np.mean(subset <= d) for d in distance_grid]
    ecdf_matrix_clean.append(ecdf)
ecdf_matrix_clean = np.array(ecdf_matrix_clean)
mean_clean = ecdf_matrix_clean.mean(axis=0)
min_clean = ecdf_matrix_clean.min(axis=0)
max_clean = ecdf_matrix_clean.max(axis=0)

# Plot mean ECDF lines
plt.plot(distance_grid, mean_full, color='red', label='mean_full')
plt.plot(distance_grid, mean_clean, color='green', label='mean_clean')

# Add min/max bars every 1 Å
angstroms = np.arange(0, 31, 1)
indices = [np.abs(distance_grid - x).argmin() for x in angstroms]
for idx in indices:
    plt.vlines(distance_grid[idx], min_full[idx], max_full[idx], color='red', linewidth=2, label='_nolegend_')
    plt.vlines(distance_grid[idx], min_clean[idx], max_clean[idx], color='green', linewidth=2, label='_nolegend_')

# Add horizontal and vertical lines
plt.axhline(y=0.75, color='grey', linestyle='--')
plt.axvline(x=frame_hot_to_wat_s3['Distance'].quantile(0.75), color='grey', linestyle='--')

# Find the distance where mean ECDF crosses 0.75
full_075_idx = np.abs(mean_full - 0.75).argmin()
clean_075_idx = np.abs(mean_clean - 0.75).argmin()
full_075_dist = distance_grid[full_075_idx]
clean_075_dist = distance_grid[clean_075_idx]
# Plot vertical lines at these quantiles
plt.axvline(x=full_075_dist, color='red', linestyle='--')
plt.axvline(x=clean_075_dist, color='green', linestyle='--')

# Custom legend for bars
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color=seaborn.color_palette("tab10")[0], label='grid'),
    Line2D([0], [0], color='red', label='mean_full'),
    Line2D([0], [0], color='green', label='mean_clean'),
    Line2D([0], [0], color='red', linewidth=2, label='min/max full'),
    Line2D([0], [0], color='green', linewidth=2, label='min/max clean'),
    Line2D([0], [0], color='grey', linestyle='--', label='0.75 quantile')
]
plt.legend(handles=legend_elements)

plt.xlim(0, 30)
plt.xticks(np.arange(0, 31, 1))
plt.yticks(np.arange(0, 1.1, 0.1))
plt.xlabel('Distance')
plt.ylabel('Cumulative Probability')
plt.title('Cumulative Distribution Function of the closest distance between hotspot_step3 and water')
plt.savefig('cdf_hot_to_wat_3.svg')


d1_hot =frame_hot_to_wat['Distance'].describe().apply(lambda x: round(x, 2))
d1_rand=frame_full_hot_to_wat['distance'].describe().apply(lambda x: round(x, 2))
d1_clean=frame_clean_hot_to_wat['distance'].describe().apply(lambda x: round(x, 2))

plt.figure(figsize=(12, 8))
seaborn.ecdfplot(frame_wat_to_hot['Distance_s3'], color=seaborn.color_palette("tab10")[0])

# Add horizontal line at 80% of the Y-axis
plt.axhline(y=0.75, color='grey', linestyle='--')
# Add vertical line at the corresponding X-axis value
x_value = frame_wat_to_hot['Distance_s3'].quantile(0.75)
plt.axvline(x=x_value, color='grey', linestyle='--')
x_value_2 = frame_full_wat_to_hot_0['distance'].quantile(0.75)
plt.axvline(x=x_value_2, color='grey', linestyle='--')
x_value_3 = frame_clean_wat_to_hot_0['distance'].quantile(0.75)
plt.axvline(x=x_value_3, color='grey', linestyle='--')
seaborn.ecdfplot(frame_full_wat_to_hot_0['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_1['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_2['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_3['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_4['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_5['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_6['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_7['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_8['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_full_wat_to_hot_9['distance'],color=seaborn.color_palette("tab10")[3])
seaborn.ecdfplot(frame_clean_wat_to_hot_0['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_1['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_2['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_3['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_4['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_5['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_6['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_7['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_8['distance'],color=seaborn.color_palette("tab10")[2])
seaborn.ecdfplot(frame_clean_wat_to_hot_9['distance'],color=seaborn.color_palette("tab10")[2])


plt.xlim(0,30)
plt.xticks(np.arange(0, 30, 1))
plt.yticks(np.arange(0, 1.1, 0.1))
plt.xlabel('Distance')
plt.ylabel('Cumulative Probability')
plt.title('Cumulative Distribution Function of the closest distance between water and hotspot_step3')
plt.savefig('cdf_wat_to_hot.svg')


# plot density of 'score_water' column

plt.figure(figsize=(12, 8))
seaborn.kdeplot(frame_hot_to_wat_s3['Score_water'], fill=True)
plt.xlabel('Score Water')
plt.ylabel('Density')
plt.title('Density Plot of the Score Water')
plt.savefig('density_plot_score_water.png')


# Plot a density plot of the distance column colored by the score_water column values
plt.figure(figsize=(12, 8))

# Plot a density plot of the distance column colored by the score_water column values

bins = [0, 0.25, 0.5, 0.75, 1]
labels = ['0-0.25', '0.25-0.5', '0.5-0.75', '0.75-1']

bins = [0,0.1,0.2,0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1]
labels = ['0-0.10','0.10-0.20', '0.20-0.30','0.30-0.40', '0.40-0.50', '0.50-0.60', '0.60-0.70', '0.70-0.80', '0.80-0.90', '0.90-1']

# create bin that go from 0 to 1 with 5 bins
# bins = [0, 0.2, 0.4, 0.6, 0.8, 1]
# labels = ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1']
# frame_hot_to_wat_s3['score_water_category'] = pd.cut(frame_hot_to_wat_s3['Score_water'], bins=bins, labels=labels, include_lowest=True)
# Add labels and title
# seaborn.kdeplot(data=frame_wat_to_hot, x='Distance_s3', fill=True, hue='score_water_category', levels=4)
#
# plt.xlabel('Distance')
# plt.ylabel('Density')
# plt.title('Density Plot of the closest distance between hotspot and water_step3')
# plt.savefig('density_plot_color_water_step3_HOT_colored.png')

# Plot a density plot of the distance column colored by the new categorized score_water column


plt.figure(figsize=(12, 8))
frame_hot_to_wat_s3['score_water_category'] = pd.cut(frame_hot_to_wat_s3['Score_water'], bins=bins, labels=labels, include_lowest=True)
seaborn.kdeplot(data=frame_hot_to_wat_s3, x='Distance', fill=False, hue='score_water_category', levels=4)
for cat, color in zip(labels, seaborn.color_palette("tab10", len(labels))):
    subset = frame_hot_to_wat_s3[frame_hot_to_wat_s3['score_water_category'] == cat]['Distance'].dropna()
    if len(subset) > 1:
        kde = gaussian_kde(subset)
        x_grid = np.linspace(subset.min(), subset.max(), 1000)
        y_kde = kde(x_grid)
        max_idx = np.argmax(y_kde)
        max_x = x_grid[max_idx]
        plt.axvline(x=max_x, color=color, linestyle='--', alpha=0.7, label=f'Peak {cat}')
#x lim 0 to 10 Angstrom
plt.xlim(0, 8)
plt.xlabel('Distance')
plt.ylabel('Density')
plt.title('Density Plot of the closest distance between hotspot and water_step3')
plt.savefig('density_plot_color_step3_HOT_to_wat_colored_score_wat_line.svg')

#create a custom color palette
frame_hot_to_wat_s3['score_hotspot_category'] = pd.cut(frame_hot_to_wat_s3['Score_spot'], bins=bins, labels=labels, include_lowest=True)

plt.figure(figsize=(12, 8))
seaborn.kdeplot(data=frame_hot_to_wat_s3, x='Distance', fill=False, hue='score_hotspot_category',
                palette=[(0,0,0),(0,0,0)]+seaborn.color_palette("plasma", n_colors=len(labels)-2),
                # palette=seaborn.diverging_palette(220, 20, n=len(labels)),
                levels=4)
ax = plt.gca()
for line, cat, color in zip(ax.get_lines(), labels, seaborn.color_palette("tab20c", len(labels))):
    x_data = line.get_xdata()
    y_data = line.get_ydata()
    max_idx = np.argmax(y_data)
    max_x = x_data[max_idx]
    max_y = y_data[max_idx]
    plt.vlines(x=max_x, ymin=0, ymax=max_y, color=color, linestyle='--', alpha=0.7, label=f'Peak {cat}')
plt.xlim(0, 8)
plt.xlabel('Distance')
plt.ylabel('Density')
plt.title('Density Plot of the closest distance between hotspot and water_step3')
plt.savefig('density_plot_color_step3_HOT_to_wat_colored_score_hot_line.svg')

#close the figure
plt.close('all')
plt.figure(figsize=(12, 8))
frame_wat_to_hot['score_hotspot_category'] = pd.cut(frame_wat_to_hot['Score_spot_s3'], bins=bins, labels=labels, include_lowest=True)
seaborn.kdeplot(data=frame_wat_to_hot, x='Distance_s3', fill=False, hue='score_hotspot_category')
plt.xlabel('Distance')
plt.ylabel('Density')
plt.title('Density Plot of the closest distance between hotspot and water_step3')
plt.savefig('density_plot_color_step3_wat_to_hot_colored_score_hot.svg')


plt.figure(figsize=(12, 8))
frame_wat_to_hot['score_water_category'] = pd.cut(frame_wat_to_hot['Score_water'], bins=bins, labels=labels, include_lowest=True)
seaborn.kdeplot(data=frame_wat_to_hot, x='Distance_s3', fill=False, hue='score_water_category')
plt.xlabel('Distance')
plt.ylabel('Density')
plt.title('Density Plot of the closest distance between hotspot and water_step3')
plt.savefig('density_plot_color_step3_wat_to_hot_colored_score_wat.svg')


# old dist calculation

#
# os.chdir(path)
# l_prot = list(os.listdir())[list(os.listdir()).index('selected_parameters.txt')+1:]
# for prot in l_prot:
#     print(prot)
#     if prot == 'cleaned_dataset':
#         continue
#     os.chdir(prot + '/O_3_wat')
#     # open the file containing step1 in the name
#     f_step_1 = [f for f in os.listdir() if 'step_1' in f][0]
#     f_step_2 = [f for f in os.listdir() if 'step_2' in f][0]
#     f_step_3 = [f for f in os.listdir() if 'step_3' in f][0]
#
#     # read the file
#     l_coord_step1 = []
#     l_coord_step2 = []
#     l_coord_step3 = []
#     l_wat_coord = []
#     with open(f_step_1, 'r') as f:
#         for line in f:
#             if 'O3w' in line:
#                 # l_coord_step1= np.append(l_coord_step1, [float(line[30:38]), float(line[39:47]), float(line[48:56])])
#                 l_coord_step1.append([float(line[30:38]), float(line[39:46]), float(line[47:56])])
#
#     with open(f_step_2, 'r') as f:
#         for line in f:
#             if 'O3w' in line:
#                 # np.append(l_coord_step2, [float(line[30:38]), float(line[39:47]), float(line[48:56])])
#                 l_coord_step2.append([float(line[30:38]), float(line[39:46]), float(line[46:55])])
#     with open(f_step_3, 'r') as f:
#         for line in f:
#             if 'O3w' in line:
#                 # np.append(l_coord_step3, [float(line[30:38]), float(line[39:47]), float(line[48:56])])
#                 l_coord_step3.append([float(line[30:38]), float(line[39:46]), float(line[46:55])])
#
#     # read coordinate of water in reference protein
#     with open('aligned_ref.pdb', 'r') as f:
#         for line in f:
#             if 'HOH' in line:
#                 l_wat_coord.append([float(line[30:38]), float(line[39:46]), float(line[46:55])])
#             if 'DOD' in line:
#                 l_wat_coord.append([float(line[30:38]), float(line[39:46]), float(line[46:55])])
#     if len(l_wat_coord) == 0:
#         'No water molecule found in the reference protein'
#         continue
#
#     l_coord_step1 = np.array(l_coord_step1)
#     l_coord_step2 = np.array(l_coord_step2)
#     l_coord_step3 = np.array(l_coord_step3)
#     l_wat_coord = np.array(l_wat_coord)
#     # create a KDTree object with the coordinates of the water molecules
#     o_water_tree = KDTree(l_wat_coord,metric='euclidean')
#     # create a KDTree object with the coordinates of the hotspots in step 1
#     o_step1_tree = KDTree(l_coord_step1,metric='euclidean')
#     # create a KDTree object with the coordinates of the hotspots in step 2
#     o_step2_tree = KDTree(l_coord_step2,metric='euclidean')
#     # create a KDTree object with the coordinates of the hotspots in step 3
#     o_step3_tree = KDTree(l_coord_step3,metric='euclidean')
#
#     # calculate the distance between each hotspot in step 1 and the closest water molecule
#     l_hotspot_dist ,wat_index = o_water_tree.query(l_coord_step1, k=1)
#
#     # caluculate the distance between each water molecule and the closest hotspot in step 1
#     l_wat_dist, hotspot_index = o_step1_tree.query(l_wat_coord, k=1)
#
#     # caluculate the distance between each water molecule and the closest hotspot in step 2
#     l_wat_dist2, hotspot_index2 = o_step2_tree.query(l_wat_coord, k=1)
#
#     # caluculate the distance between each water molecule and the closest hotspot in step 3
#     l_wat_dist3, hotspot_index3 = o_step3_tree.query(l_wat_coord, k=1)
#
#
#
#
#     # generate a dataframe with the coordinates step_1 called 'hotspot_coord', 'step'
#     df_step1 = pd.DataFrame(l_coord_step1, columns=['hots_x', 'hots_y', 'hots_z'])
#     df_step_2 = pd.DataFrame(l_coord_step2, columns=['hots_x', 'hots_y', 'hots_z'])
#     df_step_3 = pd.DataFrame(l_coord_step3, columns=['hots_x', 'hots_y', 'hots_z'])
#
#     # generate a dataframe for the distance between each hotspot and the closest water molecule
#     df_hotspots = pd.DataFrame(l_coord_step1, columns=['hots_x', 'hots_y', 'hots_z'])
#     df_hotspots['step'] = 1
#     df_hotspots['HOH_x'] = l_wat_coord[wat_index,0]
#     df_hotspots['HOH_y'] = l_wat_coord[wat_index, 1]
#     df_hotspots['HOH_z'] = l_wat_coord[wat_index, 2]
#     df_hotspots['distance_water'] = l_hotspot_dist
#     # update 'step' value to 2 in the dataframe for coordinates in l_coord_step_2
#     df_hotspots.loc[df_hotspots[['hots_x', 'hots_y', 'hots_z']].apply(tuple, 1).isin(df_step_2.apply(tuple, 1)), 'step'] = 2
#     # update 'step' value to 3 in the dataframe for coordinates in l_coord_step_3
#     df_hotspots.loc[df_hotspots[['hots_x', 'hots_y', 'hots_z']].apply(tuple, 1).isin(df_step_3.apply(tuple, 1)), 'step'] = 3
#     # save the dataframe to a csv file
#     df_hotspots.to_csv('closest_water_to_hotspots.csv', index=False)
#     # print number of hotspots in each step
#     # generate a dataframe for the distance between each water molecule and the closest hotspot in step 1
#     df_water = pd.DataFrame(l_wat_coord, columns=['HOH_x', 'HOH_y', 'HOH_z'])
#     df_water['step'] = 1
#     df_water['hots_x_step1'] = l_coord_step1[hotspot_index, 0]
#     df_water['hots_y_step1'] = l_coord_step1[hotspot_index, 1]
#     df_water['hots_z_step1'] = l_coord_step1[hotspot_index, 2]
#     df_water['distance_step_1'] = l_wat_dist
#     df_water['hots_x_step2'] = l_coord_step2[hotspot_index2, 0]
#     df_water['hots_y_step2'] = l_coord_step2[hotspot_index2, 1]
#     df_water['hots_z_step2'] = l_coord_step2[hotspot_index2, 2]
#     df_water['distance_step_2'] = l_wat_dist2
#     df_water['hots_x_step3'] = l_coord_step3[hotspot_index3, 0]
#     df_water['hots_y_step3'] = l_coord_step3[hotspot_index3, 1]
#     df_water['hots_z_step3'] = l_coord_step3[hotspot_index3, 2]
#     df_water['distance_step_3'] = l_wat_dist3
#     df_water.loc[df_water[['hots_x_step1', 'hots_x_step1', 'hots_x_step1']].apply(tuple, 1).isin(df_step_2.apply(tuple, 1)), 'step'] = 2
#     df_water.loc[df_water[['hots_x_step1', 'hots_x_step1', 'hots_x_step1']].apply(tuple, 1).isin(df_step_3.apply(tuple, 1)), 'step'] = 3
#     df_water.to_csv('closest_hotspot_to_water.csv', index=False)
#
#     os.chdir('../..')

#
# all_files_tag = [path_tag + "4ayp/O_3_wat/Closest_hotspot_distance_1.csv",
#                  path_tag + "1gvu/O_3_wat/Closest_hotspot_distance_1.csv",
#                  path_tag + "1k5c/O_3_wat/Closest_hotspot_distance_1.csv",
#                  path_tag + "3w8f/O_3_wat/Closest_hotspot_distance_1.csv"]
# all_files_score = [path + "4ayp/O_3_wat/Closest_hotspot_distance_1.csv",
#                      path + "1gvu/O_3_wat/Closest_hotspot_distance_1.csv",
#                      path + "1k5c/O_3_wat/Closest_hotspot_distance_1.csv",
#                      path + "3w8f/O_3_wat/Closest_hotspot_distance_1.csv"]

#
#
# frame_full_hot_to_wat_0['distance'].describe()
#
# frame_wat_to_hot['Distance_s3'].describe()
# frame_hot_to_wat_s3['Distance'].describe()
#
#
# # draw a density plot of the distance column
# plt.figure(figsize=(12, 8))
# seaborn.kdeplot(frame_full_0['distance'], fill=True)
# plt.xlabel('Distance')
# plt.ylabel('Density')
# plt.title('Density Plot of the closest distance between hotspot and run0')
# plt.savefig('density_plotwater_RANDOM0.png')
#
# # create a density plot of the distance column colored by the score_water column values (with 4 levels of color
# # 0 to 0.25, 0.25 to 0.5, 0.5 to 0.75, 0.75 to 1)
#
# # Create a figure
#
#
# # Plot a density plot of the distance column colored by the score_water column values
# plt.figure(figsize=(12, 8))
#
# # Plot a density plot of the distance column colored by the score_water column values
#
# bins = [0, 0.25, 0.5, 0.75, 1]
# labels = ['0-0.25', '0.25-0.5', '0.5-0.75', '0.75-1']
# frame_wat_to_hot['score_water_category'] = pd.cut(frame_wat_to_hot['Score_water'], bins=bins, labels=labels, include_lowest=True)
# # Add labels and title
# plt.xlabel('Distance')
# plt.ylabel('Density')
# plt.title('Density Plot of the closest distance between hotspot and water_step3')
# plt.savefig('density_plot_color_water_step3_HOT_colored.png')
#
# # Plot a density plot of the distance column colored by the new categorized score_water column
# seaborn.kdeplot(data=frame_wat_to_hot, x='Distance_s3', fill=True, hue='score_water_category', levels=4)
#
# plt.figure(figsize=(12, 8))
# frame_hot_to_wat_s3['score_water_category'] = pd.cut(frame_hot_to_wat_s3['Score_water'], bins=bins, labels=labels, include_lowest=True)
# seaborn.kdeplot(data=frame_hot_to_wat_s3, x='Distance', fill=True, hue='score_water_category', levels=4)
# plt.xlabel('Distance')
# plt.ylabel('Density')
# plt.title('Density Plot of the closest distance between hotspot and water_step3')
# plt.savefig('density_plot_color_step3_HOT_to_wat_colored_s3.png')
#
#
# # Create a figure
# plt.figure(figsize=(12, 8))
#
# # plot a histogram of the distance column
# seaborn.histplot(frame_wat_to_hot['Distance_s3'], bins=1000)
# plt.savefig('histogram_water_step3_HOT.png')
#
# # Plot a scatter of the score_water column against the distance column
#
# seaborn.scatterplot(x='distance', y='score_water', data=frame)
#
# # Add labels and title
# plt.xlabel('Distance')
# plt.ylabel('Score Water')
# plt.title('Hotspot Analysis')
#
# # save the figure
# plt.savefig('hotspot_analysis.png')
#
# #check max distance
# max_distance = frame['distance'].max()
#
# # second figure
# # # making a histogram of the distance column of the
#
# # find the file with minimum distance
#
# min_distance = frame['distance'].min()
# print(min_distance)
# print(frame[frame['distance'] == min_distance])
#
# # percentage of distances < 1 Å in
# # §the dataset
# c_1 = frame['distance'] <= 1
# c_1 = frame['distance'] <= 1
# p_1 = c_1.sum() / len(frame) * 100
# print(f'Percentage of distances < 1 Å: {p_1:.2f}%')

#
# # check the distribution of the distance in the set
# df_h_full = pd.DataFrame()
# df_p_wat_to_hot = pd.DataFrame()
# df_p_hot_to_wat = pd.DataFrame()
#
#
# for df in li_full:
#     # Count the number of files with a distance < 1
#     c_1 = df['distance'] <= 1
#     # calculate the percentage of files with a distance < 1
#
#     # Calculate the percentage of files with a distance < 1
#     p_1 = c_1.sum() / len(df) * 100
#     print(f'Percentage of files with a distance < 1: {p_1:.2f}%')
#     C_2 = (df['distance'] <= 2) & (df['distance'] > 1)
#     p_2 = C_2.sum() / len(df) * 100
#
#     C_3 = (df['distance'] <= 3) & (df['distance'] > 2)
#     p_3 = C_3.sum() / len(df) * 100
#     C_4 = (df['distance'] <= 4) & (df['distance'] > 3)
#     p_4 = C_4.sum() / len(df) * 100
#     C_5 = (df['distance'] <= 5) & (df['distance'] > 4)
#     p_5 = C_5.sum() / len(df) * 100
#     C_6 = (df['distance'] <= 6) & (df['distance'] > 5)
#     p_6 = C_6.sum() / len(df) * 100
#
#     # Append the percentage to the dataframe
#     df_h_full = df_h_full.append({'1Å': p_1, '2Å': p_2, '3Å': p_3, '4Å': p_4, '5Å': p_5, '6Å': p_6,'run': df['run']}, ignore_index=True)
#
# for df in li_wat_to_hot:
#     for step in range(1,4):
#         d_name = f'Distance_s{step}'
#         d_col = df[d_name]
#         # df_step = df[df['Step'] == step]
#         # calculate the percentage of distance in every range of 1 Å from 1 to 10 Å
#         p_1 = ((d_col <= 1)).sum() / len(df) * 100
#         p_2 = ((d_col <= 2) & (d_col > 1)).sum() / len(df) * 100
#         p_3 = ((d_col <= 3) & (d_col > 2)).sum() / len(df) * 100
#         p_4 = ((d_col <= 4) & (d_col > 3)).sum() / len(df) * 100
#         p_5 = ((d_col <= 5) & (d_col > 4)).sum() / len(df) * 100
#         p_6 = ((d_col <= 6) & (d_col > 5)).sum() / len(df) * 100
#         p_7 = ((d_col <= 7) & (d_col > 6)).sum() / len(df) * 100
#         p_8 = ((d_col <= 8) & (d_col > 7)).sum() / len(df) * 100
#         p_9 = ((d_col <= 9) & (d_col > 8)).sum() / len(df) * 100
#         p_10 = ((d_col <= 10) & (d_col > 9)).sum() / len(df) * 100
#         p_11 = ((d_col > 10)).sum() / len(df) * 100
#
#         # Append the percentage to the dataframe
#         df_p_wat_to_hot = df_p_wat_to_hot.append({'1Å': p_1, '2Å': p_2, '3Å': p_3, '4Å': p_4, '5Å': p_5, '6Å': p_6,
#                                                   '7Å': p_7, '8Å': p_8, '9Å': p_9, '10Å': p_10, '11Å': p_11, 'step': step}, ignore_index=True)
#
# for df in li_hot_to_wat:
#     for step in range(1,4):
#         df_step = df[df['Step'] == step]
#         # calculate the percentage of distance in every range of 1 Å from 1 to 10 Å
#         p_1 = ((df_step['Distance'] <= 1)).sum() / len(df) * 100
#         p_2 = ((df_step['Distance'] <= 2) & (df_step['Distance'] > 1)).sum() / len(df) * 100
#         p_3 = ((df_step['Distance'] <= 3) & (df_step['Distance'] > 2)).sum() / len(df) * 100
#         p_4 = ((df_step['Distance'] <= 4) & (df_step['Distance'] > 3)).sum() / len(df) * 100
#         p_5 = ((df_step['Distance'] <= 5) & (df_step['Distance'] > 4)).sum() / len(df) * 100
#         p_6 = ((df_step['Distance'] <= 6) & (df_step['Distance'] > 5)).sum() / len(df) * 100
#         p_7 = ((df_step['Distance'] <= 7) & (df_step['Distance'] > 6)).sum() / len(df) * 100
#         p_8 = ((df_step['Distance'] <= 8) & (df_step['Distance'] > 7)).sum() / len(df) * 100
#         p_9 = ((df_step['Distance'] <= 9) & (df_step['Distance'] > 8)).sum() / len(df) * 100
#         p_10 = ((df_step['Distance'] <= 10) & (df_step['Distance'] > 9)).sum() / len(df) * 100
#         p_11 = ((df_step['Distance'] > 10)).sum() / len(df) * 100
#         df_p_hot_to_wat = df_p_hot_to_wat.append({'1Å': p_1, '2Å': p_2, '3Å': p_3, '4Å': p_4, '5Å': p_5, '6Å': p_6,
#                                                   '7Å': p_7, '8Å': p_8, '9Å': p_9, '10Å': p_10, '11Å': p_11, 'step': step}, ignore_index=True)
#
# # extracting caracteristics of the dataframe df_hits
# df_p_wat_to_hot.describe()
# df_hits_tag = pd.DataFrame()
# df_p_hot_to_wat.describe()
# for df in li_tag:
#     # Count the number of files with a distance < 1
#     c_1 = df['distance'] <= 1
#     # calculate the percentage of files with a distance < 1
#
#     # Calculate the percentage of files with a distance < 1
#     p_1 = c_1.sum() / len(df) * 100
#     print(f'Percentage of files with a distance < 1: {p_1:.2f}%')
#     C_2 = (df['distance'] <= 2) & (df['distance'] > 1)
#     p_2 = C_2.sum() / len(df) * 100
#     p_2 = C_2.sum() / len(df) * 100
#
#     C_3 = (df['distance'] <= 3) & (df['distance'] > 2)
#     p_3 = C_3.sum() / len(df) * 100
#     C_4 = (df['distance'] <= 4) & (df['distance'] > 3)
#     p_4 = C_4.sum() / len(df) * 100
#     C_5 = (df['distance'] <= 5) & (df['distance'] > 4)
#     p_5 = C_5.sum() / len(df) * 100
#     C_6 = (df['distance'] <= 6) & (df['distance'] > 5)
#     p_6 = C_6.sum() / len(df) * 100
#
#     # Append the percentage to the dataframe
#     df_hits_tag = df_hits_tag.append({'1Å': p_1, '2Å': p_2, '3Å': p_3, '4Å': p_4, '5Å': p_5, '6Å': p_6}, ignore_index=True)
#
# df_hits_tag.describe()
#
# os.chdir('/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/Grid_methods/plot_test_set')
#
# # Plot the histogram
# plt.figure(figsize=(12, 8))
#
# colors = [seaborn.color_palette("tab10")[0], seaborn.color_palette("tab10")[3], seaborn.color_palette("tab10")[2], 'purple', 'orange', 'black', 'pink', 'brown', 'grey', 'yellow','cyan']
# for i, column in enumerate(df_p_wat_to_hot.columns):
#     if column == 'step':
#         print('continue')
#         continue
#     plt.hist(df_p_wat_to_hot[column], bins=20, alpha=0.5, label=column, color=colors[i])
#
# # Add labels and title
# plt.xlabel('Percentage')
# plt.ylabel('Frequency')
# plt.title('Histogram with Different Bin Colors by Column')
# plt.legend()
#
# # Show the plot
# plt.show()
#
# # Create a histogram of the percentage of files with a distance < 1
# # plt.figure(figsize=(12, 8))
# # plt.hist(df_hits['percentage'], bins=10,c)
# # save the figure
# plt.savefig('percentage_histogram_HOT_070225.png')