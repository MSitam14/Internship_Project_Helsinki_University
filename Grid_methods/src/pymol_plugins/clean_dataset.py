# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano, Samuel Besseau
# Contact : samuelbesseau77@gmail.com
# University of Helsinki
# Created : June 2020
# Updated : May 2023
# ---------------------------------------------------------------------------- #

import os
import time

import numpy as np
from pymol import cmd, finish_launching
from tqdm import tqdm

from lib import global_parameters as gp
from pymol_plugins.extract_pocket import extract_pocket, extract_pocket_global
from pymol_plugins.first_chains import first_chains
from pymol_plugins.gridbox import drawgridbox, align_principal_axes
from pymol_plugins.tmalign import tmalign
from lib.progress_bar_color import get_color

cmd.extend('extract_pocket', extract_pocket)
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
# color_scheme = {
#     "ADRB2_HU_i": "#1E90FF",  # DodgerBlue (distinct blue for ADRB2)
#     "EDNRB_HU_i": "#DAA520",  # GoldenRod (unchanged)
#     "HCRTR2_HU_a": "#800080",  # OrangeRed (bright orange-red for HCRTR2 active)
#     "HCRTR1_HU_i": "#9370DB",  # HotPink (soft pink for HCRTR1 inactive)
#     "HCRTR2_HU_i": "#E192BF",  # Pink (light pink for HCRTR2 inactive/5WQC)
#     "ADRB1_HU_a": "#32CD32",  # LimeGreen (bright green for ADRB1 active)
#     "ADRA2C_HU_i": "#A0522D",  # Sienna (unchanged, muted brown-red for ADRA2C)
#     "ADRB1_MG_a": "#4682B4",  # SteelBlue (soft blue for ADRB1 in mouse active)
#     "ADRB1_MG_u": "#5F9EA0",  # CadetBlue (muted teal for ADRB1 in mouse unknown)
#     "ADRB1_HU_i": "#2b8522",  # DodgerBlue (distinct blue for ADRB1 inactive)
#     "DRD2_HU_i": "#008B8B",  # DarkCyan (cyan for DRD2, distinct from others)
#     "OPRM_HU_u": "#B22222",  # FireBrick (dark red for OPRM, distinct and bold)
# }

color_scheme = {
    "HCRTR2": "#d184b0",  # DodgerBlue
    "HCRTR1": "#800080",  # Purple
    "ADRB1": "#264DFF",  # Purple
    "ADRB2": "#3FA0FF",  # OrangeRed
    "ADRA2C": "#1E8E99",  # Sienna
    "DRD2": "#009959",  # CadetBlue
    "EDNRB": "#888888",  # GoldenRod
    "OPRM": "#000000",  # DarkCyan
}


def lightning_rubber():
    cmd.bg_color("black")
    cmd.set('ambient', 0.05)
    cmd.set('direct', 0.2)  # diffuse
    cmd.set('spec_direct', 0)
    cmd.set('shininess', 10.)  # same as spec_power
    cmd.set('reflect', 0.3)  # diffuse
    cmd.set('spec_count', -1)
    cmd.set('spec_reflect', -1.)
    cmd.set('specular', 1)
    cmd.set('specular_intensity', 0.5)


def prepare_dataset(d_parameters):
    dir = d_parameters['p_input_pdb']
    d_parameters["p_unprocessed_pdb"] = d_parameters["p_input_pdb"]
    pdbs = os.listdir(dir)
    pymol_time = time.time()
    glob_parameters = gp.D_PARAMETERS_GLOBAL
    global_pocket = False
    print('')
    print('')
    if glob_parameters['watch_live']:
        finish_launching()
    if glob_parameters['choice'] in ['comparison', 'both']:
        folder_out = d_parameters['p_output_comparison']
        l_align = ['all']
    if glob_parameters['choice'] in ['hotspot']:
        folder_out = d_parameters['p_output_hotspot']
        l_align = [pdb.replace('.pdb', '') for pdb in pdbs]
        # set grid mode to 1
        cmd.set('grid_mode', 1)

    folder_cleaned = folder_out + '/cleaned_dataset/'
    if not os.path.exists(folder_cleaned):
        os.mkdir(folder_cleaned)
    # print('')
    with tqdm(total=len(pdbs), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
        for index, pdb in enumerate(pdbs):
            if len(pdbs) > 1:
                pbar.set_description(get_color(index / (len(pdbs) - 1)) + f"Processing PDB files loading")
            else:
                pbar.set_description(get_color(1)+"Processing PDB files loading")
            cmd.load(dir + '/' + pdb)
            pbar.update()
    print(get_color(1)+"PDB import done in {:.1f} seconds".format(time.time() - pymol_time))
    print('')

    # lightning_rubber()
    # cmd.color('white', 'all')
    if glob_parameters['choice'] in ['comparison']:
        if d_parameters['database'] == 'GPCRs':
            first_chains()
        if d_parameters['dataset_status'] == 0:
            cmd.remove('hetatm or byres z<-15 or z>15')
            cmd.remove('resn dum')
            pdbs = cmd.get_names()
            cleaning_time = time.time()
            with tqdm(total=len(pdbs), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
                pbar.set_description('\033[38;2;250;241;168m' + f"Processing PDB files cleaning")
                for pdb in pdbs:
                    l_res = []
                    for i in cmd.get_model(pdb).atom:  # get all residues
                        l_res.append(int(i.resi))
                    l_res = np.sort(np.unique(l_res))
                    res_remove = []
                    for res in l_res:
                        res_env = np.in1d([res - 3, res - 2, res - 1, res + 1, res + 2, res + 3], l_res)
                        if res_env.sum() < 2:
                            res_remove.append(res)
                    if len(res_remove) > 0:
                        selection = 'resi ' + '+'.join(str(x) for x in res_remove)
                        cmd.remove(selection + ' and ' + pdb)
                    pbar.update(1)
            print("\033[1;38;2;250;241;168mPDBs cleaning done in {:.1f} seconds".format(time.time() - cleaning_time))
            print('')

        pdbs = [pdb.replace('.pdb', '') for pdb in pdbs]
        t_start = time.time()
        if d_parameters['dataset_status'] == 0 or d_parameters['dataset_status'] == 1:
            if d_parameters['tmalign_reference'] is None:
                pdb_ref = pdbs[0]
            else:
                for pdb in pdbs:
                    if pdb.startswith('2rh1'):
                        pdb_ref = pdb
            with tqdm(total=len(pdbs), bar_format='{l_bar}{bar:80}{r_bar}', ncols=180, smoothing=1) as pbar:
                pbar.set_description('\033[38;2;250;231;104m' + f"Processing tmalign structural alignment")
                for pdb in pdbs:
                    if pdb != pdb_ref or pdb != pdb_ref + '*':
                        tmalign(pdb, pdb_ref, quiet=1)
                        pbar.update(1)
            print(
                "\033[1;38;2;250;231;104mTmalign alignment done in {:.1f} seconds\033[0m".format(time.time() - t_start))
            print('')

    if glob_parameters['align_principal_axes']:
        for select in l_align:
            align_principal_axes(select)
    pdbs = cmd.get_names()
    if glob_parameters['pocket_res_name'] != 'False':
        res_name = glob_parameters['pocket_res_name'] if glob_parameters['pocket_res_name'] != 'False' else ''
        res_id = glob_parameters['pocket_res_id'] if glob_parameters['pocket_res_id'] != 'False' else ''
        chain_id = glob_parameters['lig_chain'] if glob_parameters['lig_chain'] != 'False' else ''
        pocket_size = glob_parameters['pocket_size'] if glob_parameters['pocket_size'] != 'False' else ''
        global_pocket = glob_parameters["run_comparison"]
        for pdb in pdbs:
            # cmd.group('structures', pdb)
            if global_pocket:
                l_res = extract_pocket_global(res_name, res_id, chain_id, pdb, True, pocket_size)
            else:
                l_res = extract_pocket(res_name, res_id, chain_id, pdb, True, pocket_size)
            if len(l_res) > 0:
                gp.D_POCKET_RES_ID[pdb] = l_res
        # cmd.color('marine', 'all')
        # cmd.color('cyan', 'pockets')
        #color the protein based on the color_scheme dictionary
        # for pdb in pdbs:
        #     if pdb.split('_')[1] in color_scheme.keys():
        #         cmd.set_color(color_scheme[pdb.split('_')[1]],hex_to_rgb(color_scheme[pdb.split('_')[1]]))
        #         cmd.color(color_scheme[pdb.split('_')[1]], '*'+pdb)



        # cmd.color('yellow', 'hetatm')
        # if res_name != '' and res_id != '':
        #     cmd.color("red", "resi " + res_id + " and resname " + res_name)
        # elif res_id == '':
        #     cmd.color("red", 'resn ' + ' or resn '.join(res_name.split()))
        # if 'super_ligand' in cmd.get_names():
        #     cmd.color('orange', 'super_ligand')
        if not global_pocket:
            for name in res_name.split():
                try:
                    pkt_name = [pkt for pkt in cmd.get_names('objects') if name in pkt]
                    for pkt in pkt_name:
                        drawgridbox('Pockets_gridbox_' + pkt, pkt, padding=glob_parameters['f_grid_padding'], group=False)
                except:
                    continue
        # cmd.group('pockets','*gridbox*')
    # apply filers
    if glob_parameters["b_discard_hetatm"]:  # Discards hetero atoms
        cmd.remove('hetatm and not resn HOH')
    if glob_parameters["b_discard_atom"]:
        cmd.remove('not hetatm')
    if glob_parameters["b_discard_hydrogen"]:  # Discards Hydrogen atoms
        cmd.remove('elem H')
    if glob_parameters["b_discard_water"]:  # Discards water molecules
        cmd.remove('resn HOH')
    if glob_parameters["b_discard_alternative"]:  # Discards alternative positions
        cmd.remove('not alt ''+A')
    if len(glob_parameters["l_keep_chain"]) > 0:  # List of chains to keep, discards others
        cmd.remove('not chain ' + '+'.join(glob_parameters["l_keep_chain"]))
    if len(glob_parameters["l_chain_discard"]) > 0:  # List of chains to discard
        cmd.remove('chain ' + '+'.join(glob_parameters["l_chain_discard"]))
    if len(glob_parameters["l_keep_residues"]) > 0:  # List of residues to keep, discards others
        cmd.remove('resn ' + '+'.join(glob_parameters["l_keep_residues"]))
    if len(glob_parameters["l_discard_residues"]) > 0:  # List of residues to discard
        cmd.remove('resn ' + '+'.join(glob_parameters["l_discard_residues"]))
    if len(glob_parameters["l_keep_res_ids"]) > 0:  # List of residues ID to keep, discards others
        cmd.remove('not resi ' + '+'.join(glob_parameters["l_keep_res_ids"]))
    if len(glob_parameters["l_discard_res_ids"]) > 0:  # List of residues ID to discard
        cmd.remove('resi ' + '+'.join(glob_parameters["l_discard_res_ids"]))
    if len(glob_parameters["l_keep_atoms"]) > 0:  # List of atom type to keep, discards others
        cmd.remove('elem ' + '+'.join(glob_parameters["l_keep_atoms"]))
    if len(glob_parameters["l_discard_atoms"]) > 0:  # List of atom type to discard
        cmd.remove('elem ' + '+'.join(glob_parameters["l_discard_atoms"]))

    # update input pdb folder
    d_parameters['p_input_pdb'] = folder_cleaned
    if global_pocket:
        for pdb in pdbs:
            cmd.save(folder_cleaned + pdb + '.pdb', 'Pocket*'+pdb)
        drawgridbox('Pockets_gridbox', 'Pocket*', padding=glob_parameters['f_grid_padding'], group=False)
    else:
        for pdb in pdbs:
            cmd.save(folder_cleaned + pdb + '.pdb', pdb)
        for select in l_align:
            if select == 'all':
                drawgridbox('full_gridbox','(all)',padding=glob_parameters['f_grid_padding'])
            else:
                drawgridbox(select + '_gridbox', select, padding=glob_parameters['f_grid_padding'])
    cmd.delete('pockets')
    cmd.enable('all')

    if glob_parameters['session_name'] is None:
        name = 'cleaned_dataset'
    else:
        name = glob_parameters['session_name']
    if glob_parameters['pymol_session']:
        cmd.save(folder_out + '/cleaned_dataset/' + name + '.pse')
    if glob_parameters['watch_live']:
        cmd.quit()
