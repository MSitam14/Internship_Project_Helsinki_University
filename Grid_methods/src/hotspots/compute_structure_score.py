# Information ---------------------------------------------------------------- #
# Author :	Teemu Rönkkö
# Github :	teemuronkko
# Created : October 2021
# Updated :
# ---------------------------------------------------------------------------- #

import multiprocessing as mp
import time

import numpy as np
from tqdm import tqdm

from lib import global_parameters as gp  # Parameters
from lib.progress_bar_color import get_color

def write_pdb(filename, d_atoms,b_factor='score_total'):
    with open(filename, 'w') as f:
        for i in range(len(d_atoms["atom_serial"])):
            f.write(
                "{:6s}{:5d} {:^4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:>2s}{:2s}\n".format(
                    d_atoms["HetAtom"][i],
                    d_atoms["atom_serial"][i],
                    d_atoms["atom_name"][i],
                    d_atoms["alternative_location"][i],
                    d_atoms["residue_name"][i],
                    d_atoms["chain_id"][i],
                    d_atoms["residue_serial"][i],
                    d_atoms["residue_insertion"][i],
                    d_atoms["coord_x"][i],
                    d_atoms["coord_y"][i],
                    d_atoms["coord_z"][i],
                    d_atoms["occupancy"][i],
                    1 - d_atoms["score_total"][i],
                    d_atoms["element_symbol"][i],
                    d_atoms["element_charge"][i]
                ))


def score_environment(origin, o_structure, score_env=True, pseudo_type='O.3.wat'):
    # create global variables to be used in the compute_atom_score function
    global a_i_index
    global a_f_distance
    global score_atoms
    global type_pseudo

    a_i_index, a_f_distance = o_structure.o_tree.query_radius(origin, gp.I_MAX_SCALED_DIST, return_distance=True,
                                                              sort_results=True)
    type_pseudo = gp.D_ELEMENT_NUMBER[pseudo_type]

    if score_env:
        score_atoms = True
    else:
        # if we score hotspot, they are not part of the structure
        # a_f_distance, a_i_index = o_structure.o_tree.query(origin, k=1)
        score_atoms = False

    # Get the number of CPU
    if gp.D_PARAMETERS_GLOBAL["i_cpu_allocated"] is not None:
        i_cpu_count = gp.D_PARAMETERS_GLOBAL["i_cpu_allocated"]
    else:
        i_cpu_count = mp.cpu_count()

    # Compute the score for each atom
    l_score = []
    t_score = time.time()
    with mp.Pool(processes=i_cpu_count) as o_pool:
        with tqdm(total=len(a_i_index), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
            for i, result in enumerate(o_pool.imap(func=compute_atom_score,
                                                   iterable=range(len(a_i_index)),
                                                   chunksize=50)):
                l_score.append(result)
                progress = i / len(a_i_index)
                pbar.set_description(get_color(progress) + "Processing atom score")
                pbar.update()
        o_pool.close()  # Closes the pool of tasks
        o_pool.join()  # Waits for the results
        o_pool.terminate()  # Kills the pool of tasks
    # l_score = []
    # t_score = time.time()
    # with mp.Pool(processes=i_cpu_count) as o_pool:
    #     with tqdm(total=len(a_i_index), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
    #         pbar.set_description('\033[38;2;250;223;54m' + f"Processing atom score")
    #         for result in o_pool.imap(func=compute_atom_score,
    #                                   iterable=range(len(a_i_index)),
    #                                   chunksize=50):
    #             l_score.append(result)
    #             pbar.update()
    #     o_pool.close()  # Closes the pool of tasks
    #     o_pool.join()  # Waits for the results
    #     o_pool.terminate()  # Kills the pool of tasks
    print(get_color(progress)+"Atom Scored in {:.1f} seconds".format(time.time() - t_score))

    # delete global variables
    del a_i_index
    del a_f_distance
    del score_atoms
    del type_pseudo
    return l_score


def box_coordinates_to_euclidean_coordinates(grid_x, grid_y, grid_z):
    coord_x = (grid_x - gp.O_SYSTEM_HOTSPOT.a_offset[0]) * gp.O_SYSTEM_HOTSPOT.f_grid_spacing
    coord_y = (grid_y - gp.O_SYSTEM_HOTSPOT.a_offset[1]) * gp.O_SYSTEM_HOTSPOT.f_grid_spacing
    coord_z = (grid_z - gp.O_SYSTEM_HOTSPOT.a_offset[2]) * gp.O_SYSTEM_HOTSPOT.f_grid_spacing
    return coord_x, coord_y, coord_z


def update_atoms_and_write(a_atoms, pseudo_atoms, pdb_file, res_name='GAT', atom_name='O', sybyl_type='O.3.wat',
                           hotspot_type='Oow', res_number=None, atm_number=None, b_factor='score_total'):
    # convert back to atoms dtype to write it back to the a_atoms
    number_of_atoms = len(pseudo_atoms)
    new_atoms = np.zeros(number_of_atoms, dtype=gp.a_atom_dtype)
    for field in pseudo_atoms.dtype.names:
        try:
            new_atoms[field] = pseudo_atoms[field]
        except ValueError:
            continue
    last_atom = a_atoms[-1]
    if res_number is None:
        res_number = np.arange(last_atom['residue_serial'] + 1,
                               last_atom['residue_serial'] + number_of_atoms + 1)
    if atm_number is None:
        atm_number = np.arange(last_atom['atom_serial'] + 1, last_atom['atom_serial'] + number_of_atoms + 1)

    coord_x, coord_y, coord_z = box_coordinates_to_euclidean_coordinates(new_atoms['grid_x'], new_atoms['grid_y'],
                                                                         new_atoms['grid_z'])
    new_atoms['HetAtom'] = 'HETATM'
    new_atoms['atom_serial'] = atm_number
    new_atoms['atom_name'] = atom_name
    new_atoms['residue_name'] = res_name  # default is GAT standing for Grid Atom
    new_atoms['residue_serial'] = res_number
    new_atoms['coord_x'] = coord_x
    new_atoms['coord_y'] = coord_y
    new_atoms['coord_z'] = coord_z
    new_atoms['occupancy'] = 1
    new_atoms['temperature_factor'] = new_atoms[b_factor]
    new_atoms['custom_type'] = hotspot_type
    new_atoms['sybyl_type'] = sybyl_type
    new_atoms['type_number'] = gp.D_ELEMENT_NUMBER[hotspot_type]
    # add the new atoms to the a_atoms
    pdb_atoms = np.append(a_atoms, new_atoms)
    write_pdb(pdb_file, pdb_atoms,b_factor)
    return pdb_atoms


def compute_atom_score(index):
    o_structure = gp.O_FINAL_STRUCTURE
    a_atoms = o_structure.a_atoms
    d_distance_score = gp.O_SYSTEM_HOTSPOT.d_d_distance_score
    atm_ind = a_i_index[index]  # Index of the atom to score and its neighbours
    atm_dist = a_f_distance[index]  # Distance of the atom to score and its neighbours

    if not score_atoms:

        l_res_alt = [str(a_atoms[i]['residue_serial']) + '_' + a_atoms[i]['alternative_location']
                     for i in range(len(o_structure.a_atoms))]
        # index of the first atom of each residue_alternative position
        ind_unique = np.sort(np.unique(np.take(l_res_alt, atm_ind), return_index=True)[1])
        l_alt_tmp = np.array(a_atoms['alternative_location'])[np.take(atm_ind, ind_unique)]
        ind_unique_clean = ind_unique[np.where((l_alt_tmp == 'A') | (l_alt_tmp == ''))][0:3]
        l_dist = np.insert(np.take(atm_dist, ind_unique_clean), 0, 0)  # list of distance for the cleaned environment np.floor()
        l_atom_type = np.insert(a_atoms['type_number'][np.take(atm_ind, ind_unique_clean)], 0, type_pseudo)

    # residue_number = int([atm_ind[0]])
    else:
        # list of all residu concatenade with their alternative position to take alternative position into consideration
        l_res_alt = [str(a_atoms[i]['residue_serial']) + '_' + a_atoms[i]['alternative_location']
                     for i in range(len(o_structure.a_atoms))]

        # list of unique residue_alternative position in the structure
        l_res_uniq = np.take(a_atoms["residue_serial"],
                             np.sort(np.unique(a_atoms["residue_serial"], return_index=True)[1]))

        # index of the first atom of each residue_alternative position
        ind_unique = np.sort(np.unique(np.take(l_res_alt, atm_ind), return_index=True)[1])
        # remove alt position
        l_alt_tmp = np.array(a_atoms['alternative_location'])[np.take(atm_ind, ind_unique)]
        # remove self : residus +1 and -1
        l_res_tmp = np.array(a_atoms["residue_serial"])[np.take(atm_ind, ind_unique)]
        # when scoring external positions than the atoms from the structure
        res_ind = np.where(l_res_uniq == l_res_tmp[0])[0][0]
        ori_alt = l_alt_tmp[0]
        if a_atoms["HetAtom"][atm_ind[0]] == "HETATM": # add hotspot HERE
            res_up = None
            res_down = None
        else:
            if res_ind == len(l_res_uniq) - 1:
                res_up = None
            else:
                res_up = l_res_uniq[res_ind + 1]
            if res_ind == 0:
                res_down = None
            else:
                res_down = l_res_uniq[res_ind - 1]

        # if origin alt pos = '' have neighbors with different alt the score is based on the first alt pos
        if len(np.unique(l_alt_tmp)) > 1 and ori_alt == '':
            l_alt_ori = np.unique(l_alt_tmp)[1]  # take the first alt pos
        else:
            l_alt_ori = l_alt_tmp[0]
        # keep only the index of the 4 first atom with the same alt pos and different residue number
        ind_unique_clean = ind_unique[np.where(
            ((l_alt_tmp == l_alt_ori) | (l_alt_tmp == '')) &
            (l_res_tmp != res_up) &
            (l_res_tmp != res_down))][0:4]

        l_dist = np.take(atm_dist, ind_unique_clean)  # list of distance for the cleaned environment np.floor()
        # list of atom type for the cleaned environment
        l_atom_type = a_atoms['type_number'][np.take(atm_ind, ind_unique_clean)]

    # calculate the score for the 3 first neighbors around the atom
    l_score = []
    for j in range(1, len(l_dist)):
        if l_atom_type[0] not in d_distance_score:
            l_atom_type[0] = 260
        if l_atom_type[j] not in d_distance_score[l_atom_type[0]]:
            l_atom_type[j] = 260
        if l_atom_type[j] not in d_distance_score[l_atom_type[0]]:
            l_atom_type[0] = 260
        if j not in d_distance_score[l_atom_type[0]][l_atom_type[j]]:
            l_atom_type[j] = 260
        try:
            env_dict = d_distance_score[l_atom_type[0]][l_atom_type[j]][j]
        except KeyError:
            env_dict = d_distance_score[260][260][j]
        # find the index for which the distance is the distance in the list and take the mean of the corresponding density value
        # l_score.append(np.mean(env_dict['density'][np.where(l_dist[j] == env_dict['distance_scaled'])])) #old version with scaled_score rounded
        l_score.append(env_dict['density'][np.argmin(np.abs(l_dist[j] - env_dict['distance_scaled']))])

    while len(l_score) < 3:
        l_score.append(0)
    # replace Nan by 0 for distances that are not in the list so with 0 score value
    l_score = np.nan_to_num(l_score)
    # update a_grid in multiprocess
    return l_score

def compute_for_rank(args):
    rank, a_atoms, atom_type, score_lim = args
    return compute_optimal_distances_o(rank, a_atoms, atom_type, score_lim)


def multiprocess_over_ranks(a_atoms, atom_type, ranks=[1, 2, 3], score_lim=0.4):
    # Create data for compute_for_rank
    data = [(rank, a_atoms, atom_type, score_lim) for rank in ranks]
    l_p_atoms = np.zeros(0, dtype=gp.p_atom_dtype)
    with mp.Pool(processes=gp.D_PARAMETERS_GLOBAL["i_cpu_allocated"]) as o_pool:
        # with tqdm(total=len(data), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
        # pbar.set_description('\033[38;2;250;223;54m' + f"Processing optimal distance multiprocess")
        for results in o_pool.imap(func=compute_for_rank, iterable=data):
            l_p_atoms = np.append(l_p_atoms, results)
            # pbar.update()
    return l_p_atoms


def compute_optimal_distances_o(rank, a_atoms, atom_type, score_lim=0.4):
    atom_number = gp.D_ELEMENT_NUMBER[atom_type]
    d_distance_score = gp.O_SYSTEM_HOTSPOT.d_d_distance_score
    # keep atoms with lower score than the score limit
    a_atoms = a_atoms[np.where(a_atoms['score_' + str(rank)] <= score_lim)]
    l_p_atoms = np.zeros(0, dtype=gp.p_atom_dtype)
    with tqdm(total=len(a_atoms), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
        for index, atom in enumerate(a_atoms):
            pbar.set_description(get_color(index / (len(atom)-1)) + f"Processing optimal distance at rank " + str(rank))
            # distance corresponding to the optimal density value
            try:
                opti_dist = d_distance_score[atom['type_number']][atom_number][rank]['optimal_distance']
            except KeyError:
                try:
                    opti_dist = d_distance_score[atom['type_number']][260][rank]['optimal_distance']
                except KeyError:
                    opti_dist = d_distance_score[260][260][rank]['optimal_distance']

            # Fill all the grid point at the optimal around the atom distance with a -1
            origin = atom['grid_x'], atom['grid_y'], atom['grid_z'], atom['residue_serial']
            # fill the sphere around the origin with a radius of opti_dist with -1
            l_p_atoms = np.append(l_p_atoms, points_at_exact_distance(origin, opti_dist, rank))
            pbar.update()
    return l_p_atoms


# def points_at_exact_distance(origin, distance, rank):
#
#     distance = np.floor(distance).astype(int)
#     # Generate all points in a cube around the origin
#     x, y, z = np.indices([2 * distance + 1] * 3) - distance
#     # Shift by the origin
#     x, y, z = x + origin[0], y + origin[1], z + origin[2]
#     # Calculate euclidean distances
#     euclidean_distances = (np.sqrt((x - origin[0]) ** 2 + (y - origin[1]) ** 2 + (z - origin[2]) ** 2)) # np.floor()
#     # Get indices where manhattan_distances is exactly equal to distance
#     indices = np.where(euclidean_distances == distance)
#     # create pseudoatoms object like a_atoms
#     l_p_atoms = np.zeros((len(indices[0]),), dtype=gp.p_atom_dtype)
#     l_p_atoms['grid_x'] = x[indices]
#     l_p_atoms['grid_y'] = y[indices]
#     l_p_atoms['grid_z'] = z[indices]
#     l_p_atoms['tag_' + str(rank)] = -1
#     l_p_atoms['tag_total'] = -1
#     # l_p_atoms['score_' + str(rank)] = -1
#     # l_p_atoms['score_total'] = -1
#     l_p_atoms['residue_serial'] = origin[3]
#     return l_p_atoms


def points_at_exact_distance(origin, distance, rank):
    x0, y0, z0 = origin[:3]
    # rounded_distance = int(round(distance))  # Round the distance to the nearest integer
    squared_distance = distance ** 2  # Use the squared distance for comparison

    # Initialize list to store results
    results = []

    # Iterate over the bounding cube
    max_range = distance  # Limit the search space to ±rounded_distance
    for x in range(x0 - max_range, x0 + max_range + 1):
        for y in range(y0 - max_range, y0 + max_range + 1):
            for z in range(z0 - max_range, z0 + max_range + 1):
                # Calculate the squared distance to the origin
                current_squared_distance = (x - x0) ** 2 + (y - y0) ** 2 + (z - z0) ** 2

                # Check if the squared distance matches the rounded distance
                if current_squared_distance == squared_distance:
                    results.append((x, y, z))

    # Create pseudoatoms object like a_atoms
    l_p_atoms = np.zeros((len(results),), dtype=gp.p_atom_dtype)
    l_p_atoms['grid_x'] = [x for x, y, z in results]
    l_p_atoms['grid_y'] = [y for x, y, z in results]
    l_p_atoms['grid_z'] = [z for x, y, z in results]
    l_p_atoms['tag_' + str(rank)] = -1
    l_p_atoms['tag_total'] = -1
    l_p_atoms['residue_serial'] = origin[3]
    return l_p_atoms

