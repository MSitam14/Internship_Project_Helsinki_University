#!/usr/bin/env python3

##########
# Import #
##########

import csv
import datetime
import json
import os
import time
import warnings

import numpy as np
from openbabel import openbabel as ob
from pymol import cmd, cgo
from sklearn.neighbors import KDTree
from chempy import cpv
from tqdm import tqdm
from .tools import translate_path
import shutil

########
# Main #
########

# finish_launching()
class CustomAtomTypes:
    # Residue type
    MAINATOM = ['C', 'O', 'N', 'CA', 'OXT']
    RES = ['ALA', 'ILE', 'LEU', 'VAL', 'MET', 'CYS', 'PHE', 'TRP', 'TYR', 'HIS',
           'THR', 'SER', 'ASN', 'GLN', 'ASP',
           'GLU', 'ARG', 'LYS', 'PRO', 'GLY']
    WATER = ['HOH']
    # New Definition of Atom types:
    # Oxygen in carbonyl
    Oc = {'O': 'O', 'ASN': 'OD1', 'GLN': 'OE1'}
    # Nitrogen in amide
    Nam = {'N': 'N', 'ASN': 'ND2', 'GLN': 'NE2', 'TRP': 'NE1'}
    # Oxygen in carboxylate and oxygen in C-terminal
    Oox = {'GLU': ['OE1', 'OE2'], 'ASP': ['OD1', 'OD2'], 'OXT': 'OXT'}
    # Oxygen in hydroxyl or phenol
    OHY = {'THR': 'OG1', 'SER': 'OG', 'TYR': 'OH'}
    # Nitrogen in Lysine
    Nlys = {'LYS': 'NZ'}
    # Nitrogein in Arginine
    Narg = {'ARG': ['NH1', 'NH2', 'NE']}
    # Carbon SP2 in aromatic ring
    Car = {'PHE': ['CG', 'CD1', 'CE2', 'CZ', 'CE1', 'CD2'],
           'TYR': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
           'TRP': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CE3',
                   'CZ3', 'CH2', 'CZ2'],
           'HIS': ['CG', 'CD2', 'CE1']}
    # Centeral carbon from ARG, GLN, GLU, ASP, ASN
    CRES = ['ARG', 'GLN', 'GLU', 'ASP', 'ASN']
    Ce = {'ARG': 'CZ', 'GLN': 'CD', 'GLU': 'CD', 'ASP': 'CG', 'ASN': 'CG'}
    # Nitrogen in Histidine
    Nhis = {'HIS': ['NE2', 'ND1']}
    # Metal
    METAL = ['LI', 'BE', 'NA', 'MG', 'AL', 'K', 'CA', 'SC', 'TI', 'V', 'CR',
             'MN', 'FE', 'CO', 'NI', 'CU', 'ZN', 'GA', 'GE', 'RB', 'SR', 'Y',
             'ZR', 'NB', 'MO', 'TC', 'RU', 'RH', 'PD', 'AG', 'CD', 'IN', 'SN',
             'SB', 'CS', 'BA', 'LA', 'HF', 'TA', 'W', 'RE', 'OS', 'IR', 'PT',
             'AU', 'HG', 'TL', 'PB', 'BI', 'PO', 'FR', 'RA', 'AC', 'RF', 'DB',
             'SG', 'CE', 'PR', 'ND', 'PM', 'SM', 'EU', 'GD', 'TB', 'DY', 'HO',
             'ER', 'TM', 'YB', 'LU', 'TH', 'PA', 'U', 'NP', 'PU', 'AM', 'CM',
             'BK', 'CF', 'ES', 'FM', 'MD', 'NO', 'LR']

    trans_main = {'O': 'Oc', 'H': 'H', 'N': 'Nam', 'CA': 'Xot', 'C': 'Xot',
                  'OXT': 'Oox', 'CB': 'Xot'}
    trans_main_last = {'O': 'Oox', 'H': 'H', 'N': 'Nam', 'CA': 'Xot', 'C': 'Xot',
                       'OXT': 'Oox', 'CB': 'Xot'}
    trans_main_first = {'O': 'Oc', 'H': 'H', 'N': 'Nbas', 'CA': 'Xot',
                        'C': 'Xot', 'CB': 'Xot'}

    # Define atoms type consider as origin
    ori_custom = ('Xot', 'Car', 'Nbas', 'Nam', 'Oc', 'Oh', 'Oox', 'Oow')
    ori_sybyl = ("C.3", "C.2", "C.1", "C.ar", "C.cat", "N.3", "N.2", "N.1",
                 "N.ar", "N.am", "N.pl3", "N.4", "O.3.wat", "O.3", "O.2",
                 "O.co2", "S.3", "S.2", "S.o", "S.o2", "P.3", "Ti.th",
                 "Ti.oh", "Cr.th", "Cr.oh", "Co.oh", "Ru.oh", "Du")

    wat_type = ('Oow', 'O.3.wat')


CustomType = CustomAtomTypes()


def parse_parameter_file(file_path):
    parameters = {}
    with open(translate_path(file_path), 'r') as file:
        for line in file:
            # Skip comments and empty lines
            if '=' in line:
                key, value = line.split('=', 1)
                parameters[key.strip()] = parse_value(value.strip())
    return parameters


def parse_value(value):
    # Handles booleans, integers, floats, and comma-separated lists.
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    elif value.lower() == 'none':
        return None
    elif ',' in value:
        # Splits the value at commas and recursively parses each item.
        return [parse_value(item.strip()) for item in value.split(',')]
    else:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value


# translate sybyl type

### update
def translate_sybyl(pdb):
    obConversion = ob.OBConversion()
    obConversion.SetInFormat('pdb')

    ttab = ob.ttab
    ttab.SetFromType("INT")
    ttab.SetToType("SYB")

    l_syb = []
    mol = ob.OBMol()
    obConversion.ReadFile(mol, str(translate_path(pdb)))
    for obatom in ob.OBMolAtomIter(mol):
        if obatom.GetResidue().GetName() == 'HOH':
            l_syb.append('O.3.wat')
        else:
            l_syb.append(ttab.Translate(obatom.GetType()))
    return l_syb


# translate atom type


def translate_custom(line, last_resn):
    if line[0:6].strip() not in ["ATOM", "HETATM"]:
        return None
    atom_name = line[13:16].strip()
    res_name = line[17:20].strip()
    res_num = line[22:27].strip()
    element_name = 0
    if line[76:78].strip() == 'H':
        element_name = 'H'
    elif res_name in CustomType.RES:
        # Protein main chain N, O ,CA, C
        # Nitrogen in amide

        if atom_name in CustomType.MAINATOM:
            if res_num == last_resn:
                element_name = CustomType.trans_main_last[atom_name]
            else:
                element_name = CustomType.trans_main[atom_name]
        # Nitrogen in Arginine
        elif res_name == 'ARG' and atom_name in CustomType.Narg[res_name]:
            # element_name = 'Narg'
            element_name = 'Nbas'
        # Carbon SP2 in aromatic ring
        elif res_name in CustomType.Car.keys() and atom_name in CustomType.Car[res_name]:
            element_name = 'Car'

        elif res_name in CustomType.OHY.keys() and atom_name == CustomType.OHY[res_name]:
            element_name = 'Oh'

        elif res_name in CustomType.Nam.keys() and atom_name == CustomType.Nam[res_name]:
            element_name = 'Nam'

        elif res_name in CustomType.Nhis.keys() and atom_name in CustomType.Nhis[res_name]:
            # element_name = 'Nhis'
            element_name = 'Nbas'

        elif res_name in CustomType.Ce.keys() and CustomType.Ce[res_name] == atom_name:
            element_name = 'Car'  # 'Ce'

        elif res_name in CustomType.Oc.keys() and atom_name == CustomType.Oc[res_name]:
            element_name = 'Oc'

        elif res_name in CustomType.Oox.keys() and \
                (atom_name == CustomType.Oox[res_name][0] or atom_name == CustomType.Oox[res_name][1]):
            element_name = 'Oox'

        elif res_name in CustomType.Nlys.keys() and atom_name == CustomType.Nlys[res_name]:
            # element_name = 'Nlys'
            element_name = 'Nbas'
        if element_name == 0:
            element_name = 'Xot'

    elif res_name in CustomType.METAL:
        # element_name = 'Meta'
        element_name = "Meta"

    elif res_name == 'HOH' and atom_name == 'O':
        element_name = 'Oow'

    else:
        # element_name = 'Lig'
        element_name = "Hetatm"
    return element_name


# apply scoring



def dist_score_prot(l_atom, l_atom_num, dist, nb_contact, pdb, run_fobs, density_fold, fobs_fexp_fold):
    score_tot = 0
    dict_detail = {}
    dict_detail["Origin"] = l_atom[0] + " " + str(l_atom_num[0])
    for i in range(1, nb_contact + 1):
        try:
            dict_detail["Neighbor_" + str(i)] = l_atom[i] + " " + l_atom_num[i]
        except:
            dict_detail["Neighbor_" + str(i)] = "None"
            dict_detail["Score_" + str(i)] = -1.00
            if run_fobs:
                dict_detail['Fobs_Fexp_' + str(i)] = -1.00
            if i == nb_contact+1:
                dict_detail['Score_total'] = "%.3f" % (score_tot / nb_contact)
            else:
                continue
        if run_fobs:
            # Fobs_Fexp
            with open(translate_path(fobs_fexp_fold + 'Env_score_' + l_atom[0] + '_' + str(
                    i) + '_prim.txt'), 'r') as src:
                reader = csv.reader(src, quotechar="\"", delimiter=' ')
                next(reader, None)
                for row in reader:
                    if row[1] == l_atom[i]:
                        fobs_fexp = row[5]

            dict_detail['Fobs_Fexp_' + str(i)] = "%.3f" % (float(fobs_fexp))

        try:
            # Fitness score
            log_file = '../logs/logfile_' + pdb + '.txt'
            with open(translate_path(density_fold + l_atom[0] + '_' +
                      l_atom[i] + '_' + str(i) + '.txt'), 'r') as src:
                reader = csv.reader(src, quotechar="\"", delimiter=' ')
                next(reader, None)
                x = []
                y = []
                for row in reader:
                    x.append(float(row[1]))
                    y.append(float(row[2]))
                score = float(
                    y[x.index(min(x, key=lambda j: abs(j - dist[i])))] / max(y))
            dict_detail['Score_' + str(i)] = "%.3f" % (score)
            score_tot = score_tot + score
            dict_detail['Score_total'] = "%.3f" % (score_tot / nb_contact)
        except:
            if os.path.exists(log_file):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not
            with open(translate_path(log_file), append_write) as out:
                out.write(l_atom_num[0] + ' ' + l_atom[0] + '_' +
                          l_atom[i] + '_' + str(i) + ' no density\n')
            dict_detail['Score_' + str(i)] = -1.00
            score_tot = score_tot + 0.5
            dict_detail['Score_total'] = "%.3f" % (score_tot / nb_contact)
    return dict_detail, l_atom[0], round(score_tot / nb_contact, 3)

def cgo_arrow(atom1='pk1', atom2='pk2', radius=0.5, gap=0.0, hlength=-1,
              hradius=-1, color='blue red', name='', name_prefix=''):
    '''
DESCRIPTION

    Create a CGO arrow between two picked atoms.

ARGUMENTS

    atom1 = string: single atom selection or list of 3 floats {default: pk1}

    atom2 = string: single atom selection or list of 3 floats {default: pk2}

    radius = float: arrow radius {default: 0.5}

    gap = float: gap between arrow tips and the two atoms {default: 0.0}

    hlength = float: length of head

    hradius = float: radius of head

    color = string: one or two color names {default: blue red}

    name = string: name of CGO object
    '''

    radius, gap = float(radius), float(gap)
    hlength, hradius = float(hlength), float(hradius)

    try:
        color1, color2 = color.split()
    except ValueError as e:
        color1 = color2 = color

    color1 = list(cmd.get_color_tuple(color1))
    color2 = list(cmd.get_color_tuple(color2))

    def get_coord(v):
        if not isinstance(v, str):
            return v
        if v.startswith('['):
            return cmd.safe_list_eval(v)
        coords = cmd.get_atom_coords(v)
        return coords

    try:

        xyz1 = get_coord(atom1)
        xyz2 = get_coord(atom2)
        normal = cpv.normalize(cpv.sub(xyz1, xyz2))

        if hlength < 0:
            hlength = radius * 3.0
        if hradius < 0:
            hradius = hlength * 0.6

        if gap:
            diff = cpv.scale(normal, gap)
            xyz1 = cpv.sub(xyz1, diff)
            xyz2 = cpv.add(xyz2, diff)

        xyz3 = cpv.add(cpv.scale(normal, hlength), xyz2)

        obj = [cgo.CYLINDER] + xyz1 + xyz3 + [radius] + color1 + color2 + \
              [cgo.CONE] + xyz3 + xyz2 + [hradius, 0.0] + color2 + color2 + \
              [1.0, 0.0]

        if not name:
            name = cmd.get_unused_name(name_prefix + 'arrow')


        cmd.load_cgo(obj, name)

    except Exception:
        pass


def fobs_pymol(csv_in, pdb_in, pdb_ses, atom_type='custom', p_min=-1, p_max=100,
               res_num=None, res_name=None, alt_pos=None, focus_res_num=-1,focus_dist=5):
    ''' Description:
    This function is used to visualize the Fobs_Fexp score in pymol session using color cgo arrow
    Args:'''
    if res_num is None:
        res_num = []
    if res_name is None:
        res_name = []
    if alt_pos is None:
        alt_pos = ['A']
    if atom_type == 'custom':
        tail = '_Cust'
    elif atom_type == 'sybyl':
        tail = '_Syb'
    res_num = [str(x) for x in res_num]
    arrow_length = 0.45
    arrow_radius = 0.1
    alt_pos.append('')
    pdb_name = pdb_in.split('/')[-1].split('.')[0]
    cmd.delete('*')
    cmd.load(str(translate_path(pdb_in)))
    cmd.hide('cartoon')
    cmd.show('stick')
    cmd.hide('stick', 'hydro')
    cmd.hide("(not alt '', and not alt " + alt_pos[0] + ")")
    cmd.set('dash_gap', 0.5)
    cmd.set('dash_radius', 0.05)
    cmd.spectrum('b', minimum=0, maximum=1)
    if focus_res_num != -1:
        cmd.select('Focus', 'resi ' + str(focus_res_num) + ' expand ' + str(focus_dist))
    else:
        cmd.select('Focus', '*')
    header = []
    l_id = []
    l_grp = []
    with open(translate_path(pdb_in)) as pdb_f:
        for line in pdb_f:
            if len(res_num) == len(res_name) == 0 and line[16:17].strip() in alt_pos:
                l_id.append(line[6:11].strip())
                if line[13:16].strip() in CustomType.MAINATOM:
                    l_grp.append('Main_')
                else:
                    l_grp.append('Side_')
            if (line[22:27].strip() in res_num or
                line[17:20].strip() in res_name) and \
                    line[16:17].strip() in alt_pos:
                l_id.append(line[6:11].strip())
                if line[13:16].strip() in CustomType.MAINATOM:
                    l_grp.append('Main_')
                else:
                    l_grp.append('Side_')

    with open(translate_path(csv_in)) as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        id_neighs = [i for i, col_name in enumerate(header) if 'Neighbor' in col_name]
        id_fobs = [i for i, col_name in enumerate(header) if 'Fobs_Fexp' in col_name]
        for row in csv_reader:
            id_ori = row[0].split(' ')[1]
            if id_ori not in l_id:
                continue
            for i in range(len(id_neighs)):
                p_value = float(row[id_fobs[i]])
                if p_max > p_value > p_min:
                    id_nei = row[id_neighs[i]].split(' ')[1]
                    try:
                        cmd.get_distance('id ' + id_ori + ' and Focus',
                                         'id ' + id_nei + ' and Focus')
                    except:
                        continue
                    if p_value < 0.5:

                        cmd.pseudoatom(l_grp[l_id.index(id_ori)] + 'Label_low_' + str(1 + i) +
                                       tail, '(id ' + id_ori + ', or id ' +
                                       id_nei + ') and Focus',
                                       resn=str(p_value))
                        cgo_arrow('id ' + id_ori + ' and Focus',
                                  'id ' + id_nei + ' and Focus',
                                  0.0, 0.3, arrow_length, arrow_radius, 'red',
                                  l_grp[l_id.index(id_ori)] + 'Dir_low' + str(1 + i) + tail)
                        cmd.distance(l_grp[l_id.index(id_ori)] + 'Fobs_Fexp_low_' + str(i + 1) + tail,
                                     'id ' + id_ori + ' and Focus',
                                     'id ' + id_nei + ' and Focus')
                    elif p_value > 1.5:

                        cmd.pseudoatom(l_grp[l_id.index(id_ori)] + 'Label_high_' + str(1 + i) + tail,
                                       '(id ' + id_ori + ', or id ' + id_nei + ') and Focus', resn=str(p_value))
                        cgo_arrow('id ' + id_ori + ' and Focus', 'id ' + id_nei + ' and Focus',
                                  0.0, 0.3, arrow_length, arrow_radius, 'marine',
                                  l_grp[l_id.index(id_ori)] + 'Dir_high_' + str(1 + i) + tail)
                        cmd.distance(l_grp[l_id.index(id_ori)] + 'Fobs_Fexp_high_' + str(i + 1) + tail,
                                     'id ' + id_ori + ' and Focus', 'id ' + id_nei + ' and Focus')
                    else:
                        cmd.pseudoatom(l_grp[l_id.index(id_ori)] + 'Label_mid_' + str(1 + i) + tail,
                                       '(id ' + id_ori + ', or id ' + id_nei + ') and Focus', resn=str(p_value))
                        cgo_arrow('id ' + id_ori + ' and Focus', 'id ' + id_nei + ' and Focus',
                                  0.0, 0.3, arrow_length, arrow_radius, 'green',
                                  l_grp[l_id.index(id_ori)] + 'Dir_mid' + str(1 + i) + tail)
                        cmd.distance(l_grp[l_id.index(id_ori)] + 'Fobs_Fexp_mid_' + str(i + 1) + tail,
                                     'id ' + id_ori + ' and Focus',
                                     'id ' + id_nei + ' and Focus')
    cmd.hide('label')
    cmd.delete('Focus')
    cmd.hide('nonbonded', '*Label*')
    cmd.group('Fitness_score' + tail, pdb_name)
    cmd.color('red', '*Fobs_Fexp_low*')
    cmd.color('green', '*Fobs_Fexp_mid*')
    cmd.color('marine', '*Fobs_Fexp_high*')
    cmd.label('*Label*', 'resn')
    cmd.copy('Protein_low' + tail, pdb_name)
    cmd.copy('Protein_mid' + tail, pdb_name)
    cmd.copy('Protein_high' + tail, pdb_name)
    cmd.group('Contact_low' + tail, '*low*')
    cmd.group('Contact_mid' + tail, '*mid*')
    cmd.group('Contact_high' + tail, '*high*')
    cmd.disable('*Label*')
    cmd.order('*Label*', 'yes', 'bottom')
    cmd.order('*Dir*', 'yes', 'top')
    cmd.order('*Fobs*', 'yes', 'top')
    cmd.order('*Protein*', 'yes', 'top')
    cmd.set('orthoscopic', 1)
    cmd.set('grid_mode', 1)
    cmd.util.cbaw('Protein_*')
    cmd.set('all_states', 1)
    cmd.save(translate_path(pdb_ses))


def element_prot_dist_score(pdb, fold_out, size, date, wat_env, atom_type, l_ori, pocket_num,
                            model_num, run_fobs, density_fold, fobs_fexp_fold):
    # Score and color protein atoms
    # Initialize variables and lists needed
    dict_detail_keys = ['Origin']
    for i in range(size):  # create keys for the dictionary
        dict_detail_keys.extend(['Neighbor_' + str(i + 1)])
        dict_detail_keys.extend(['Score_' + str(i + 1)])
    dict_detail_keys.append('Score_total')
    if run_fobs:
        for i in range(size):
            dict_detail_keys.extend(['Fobs_Fexp_' + str(i + 1)])

    l_res_pocket, max_bfac = 0, 0

    l_res_num, l_dict, pdb_score, prot, p_coord, o_coord, origin, l_ele_name, l_atom_num, l_alt_pos, l_score_wat,\
    l_score_prot, l_res_alt = ([] for _ in range(13))

    if l_ori is None and atom_type == 'custom':
        l_ori = ('Xot', 'Car', 'Nbas', 'Nam', 'Oc', 'Oh', 'Oox', 'Oow')
        basename = 'cust_' + pdb.split("/")[-1][:-4]
    elif l_ori is None and atom_type == 'sybyl':
        l_ori = ("C.3", "C.2", "C.1", "C.ar", "C.cat", "N.3", "N.2", "N.1",
                 "N.ar", "N.am", "N.pl3", "N.4", "O.3.wat", "O.3", "O.2",
                 "O.co2", "S.3", "S.2", "S.o", "S.o2", "P.3", "Ti.th",
                 "Ti.oh", "Cr.th", "Cr.oh", "Co.oh", "Ru.oh", "Du")
    if atom_type == 'sybyl':
        l_syb = translate_sybyl(pdb)
        idx_syb = 0
        basename = 'syb_' + pdb.split("/")[-1][:-4]
    # Read pdb file to find the last residue number
    with open(translate_path(pdb), 'r') as src:
        mdl_flag = 1
        if atom_type == 'custom':
            for line in src:
                if line.split()[0] == 'MODEL':
                    if line.split()[1] == str(model_num):
                        mdl_flag = 1
                    else:
                        mdl_flag = 0
                if mdl_flag == 0:
                    continue
                if mdl_flag == 1 and line[0:6].strip() == 'ENDMDL':
                    break
                if line[0:6].strip() == "ATOM":
                    last_resn = line[22:27].strip()
    # Read pdb file
    with open(translate_path(pdb), 'r') as src:
        mdl_flag = 1
        for line in src:
            if line.split()[0] == 'MODEL':  # select model
                if line.split()[1] == str(model_num):
                    mdl_flag = 1
                else:
                    mdl_flag = 0
            if mdl_flag == 0:  # skip if not the selected model
                continue
            if mdl_flag == 1 and line[0:6].strip() == 'ENDMDL':  # stop reading if end of model
                break
            if line[0:6].strip() not in ["ATOM", "HETATM"]:  # skip if not atom
                continue
            if atom_type == 'custom':  # translate into element name
                element_name = translate_custom(line, last_resn)
            elif atom_type == 'sybyl':
                element_name = l_syb[idx_syb]
                idx_syb += 1
            if element_name is None:  # skip if not in the list
                continue
            max_bfac = max(max_bfac, float(line[60:66]))  # get max bfactor
            atom_num = line[6:11].strip()
            res_num = line[22:27].strip()
            alt_pos = line[16:17].strip()
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            if element_name == 'H':
                pdb_score.append(line)
                continue
            if element_name in l_ori:
                # if the atom is in the list of origin atoms
                # add to origin list
                origin.append([atom_num,
                               element_name,
                               res_num,
                               alt_pos,
                               x,
                               y,
                               z])
                pdb_score.append(line[:56] + line[66:])
            else:
                # if the atom is not in the list of origin atoms
                # keep the line unchanged and add to prot list
                pdb_score.append(line)
            if wat_env or element_name not in CustomType.wat_type:
                prot.append([atom_num,
                             element_name,
                             res_num,
                             alt_pos,
                             x,
                             y,
                             z])
            # add needed info to lists
            l_res_num.append(res_num)
            l_atom_num.append(atom_num)
            l_ele_name.append(element_name)
            l_alt_pos.append(alt_pos)
            l_res_alt.append(res_num + '_' + alt_pos)
    for p in prot:  # get coordinates of protein atoms
        p_coord.append(p[4:])
    for o in origin:  # get coordinates of origin atoms
        o_coord.append(o[4:])
    if len(o_coord) == 0:
        print("No residus in " + pdb)
        return
    # Create KDTree based on protein atoms
    tree = KDTree(p_coord, leaf_size=500000, metric='euclidean')
    # Find neighbors of origin atoms within 10A radius and sort them
    ind, dist = tree.query_radius(o_coord, 10, return_distance=True,
                                  sort_results=True)
    start = time.time()
    l_res_uniq = np.take(l_res_num,
                         np.sort(np.unique(l_res_num, return_index=True)[1]))
    if (pocket_num != None):
        ind_pocket = np.where(np.array(l_res_num) == pocket_num)[0]
        l_res_pocket = []
    for i in range(len(ind)):
        if (pocket_num != None and i in ind_pocket):
            l_res_pocket = np.unique(np.append(l_res_pocket, np.take(l_res_num,
                                                                     np.take(
                                                                         ind[i],
                                                                         np.where(
                                                                             dist[
                                                                                 i] < 4)))))
        if len(dist[i]) == 0:
            dict_default = {}
            for l in range(size):
                dict_default['Neighbor_' + str(l + 1)] = 'None'
                dict_default['Score_' + str(l + 1)] = '0.500'
            dict_default['Score_total'] = '0.500'
            dict_default['Origin'] = l_ele_name[i]
            l_dict.append(dict_default)
            continue
        if dist[i][0] != 0.0:
            ori_id = [k for k, x in enumerate(l_atom_num) if x == origin[i][0]][0]  # get index of origin atom
            ind[i] = np.append(ori_id, ind[i])
            dist[i] = np.append(0, dist[i])

        ind_unique = np.sort(np.unique(np.take(l_res_alt, ind[i]),
                                       return_index=True)[1])
        # remove alt position
        l_alt_tmp = np.array(l_alt_pos)[np.take(ind[i], ind_unique)]
        # remove self : residus +1 and -1
        l_res_tmp = np.array(l_res_num)[np.take(ind[i], ind_unique)]

        if np.array(l_ele_name)[np.take(ind[i], ind_unique[0])] not in \
                CustomType.wat_type:
            res_idx = np.where(l_res_uniq == l_res_tmp[0])[0][0]
            if res_idx == len(l_res_uniq) - 1:
                l_res_up = None
            else:
                res_idx_up = res_idx + 1
                l_res_up = l_res_uniq[res_idx_up]
            if res_idx == 0:
                l_res_prev = None
            else:
                res_idx_prev = res_idx - 1
                l_res_prev = l_res_uniq[res_idx_prev]
            # if origin alt pos = '' have neighbors with different alt to update
            if len(np.unique(l_alt_tmp)) > 1 and l_alt_tmp[0] == '':
                l_alt_ori = np.unique(l_alt_tmp)[1]  # take the first alt pos
            else:
                l_alt_ori = l_alt_tmp[0]
            ind_unique = ind_unique[np.where(
                ((l_alt_tmp == l_alt_ori) | (l_alt_tmp == '')) &
                (l_res_tmp != l_res_up) &
                (l_res_tmp != l_res_prev)
            )][0:size + 1]
        else:
            ind_unique = ind_unique[np.where(
                (l_alt_tmp == l_alt_tmp[0]) | (l_alt_tmp == ''))][0:size + 1]

        # if len(ind_unique) == size + 1:
        l_dist = np.take(dist[i], ind_unique).tolist()
        l_atom = np.array(l_ele_name)[np.take(ind[i], ind_unique)].tolist()
        l_atom_num_env = np.array(l_atom_num)[
            np.take(ind[i], ind_unique)].tolist()
        dict_tmp, ori_tmp, score_tmp = dist_score_prot(l_atom,
                                                       l_atom_num_env,
                                                       l_dist, size,
                                                       basename,
                                                       run_fobs,
                                                       density_fold,
                                                       fobs_fexp_fold)
        l_dict.append(dict_tmp)
        # list score prot, wat and tot
        if ori_tmp in CustomType.wat_type:
            l_score_wat.append(score_tmp)
        else:
            l_score_prot.append(score_tmp)

        # else:
        #     dict_default = {}
        #     for l in range(size):
        #         dict_default['Neighbor_' + str(l + 1)] = 'None'
        #         dict_default['Score_' + str(l + 1)] = '0.500'
        #     dict_default['Score_total'] = '0.500'
        #     dict_default['Origin'] = np.array(l_ele_name)[np.take(ind[i], 0)]
        #     l_dict.append(dict_default)
    if wat_env:
        basename = basename + '_wat'
    pdb_fold = fold_out + date + '/pdb_color_' + atom_type + '/'
    pdb_ses_fold = fold_out + date + '/pdb_session_' + atom_type + '/'
    score_fold = fold_out + date + '/detail_score_' + atom_type + '/'
    try:
        os.makedirs(translate_path(pdb_ses_fold))
        os.makedirs(translate_path(pdb_fold))
        os.makedirs(translate_path(score_fold))
    except:
        pass

    pdb_name = basename + '_' + str(size) + "_score_" + date + ".pdb"
    csv_name = basename + "_" + str(size) + "_prot_score_" + date + ".csv"
    pdb_ses = basename + '_' + str(size) + "_score_" + date + ".pse"
    pdb_path = pdb_fold + pdb_name
    csv_path = score_fold + csv_name
    pdb_ses_path = pdb_ses_fold + pdb_ses

    try:
        print("\nWriting output files...")
        print("PDB file")
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        with open(translate_path(pdb_path), 'w') as out:
            out.write('REMARK   1 SCORE PROTEIN ' +
                    str(round(np.mean(l_score_prot), 3))
                    + '                                                  \n')
            out.write('REMARK   1 SCORE WATERS  ' +
                    str(round(np.mean(l_score_wat), 3))
                    + '                                                  \n')
            out.write('REMARK   1 SCORE TOTAL   ' +
                    str(round(np.mean(l_score_wat + l_score_prot), 3))
                    + '                                                  \n')
            l = 0
            for line in pdb_score:
                if len(line) <= 71:
                    line_out = line[:56] + '1.00 ' + "%.3f" % (
                            1 - float(l_dict[l]['Score_total'])) + line[56:]
                    l += 1
                else:
                    line_out = line[0:56] + "1.00 0.500" + line[66:]
                out.write(line_out)

        print("CSV file")
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        with open(translate_path(csv_path), 'w') as outcsv:
            writer = csv.DictWriter(outcsv, fieldnames=dict_detail_keys)
            writer.writeheader()
            for line in l_dict:
                writer.writerow(line)

        if run_fobs:
            print("Pymol session")
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            fobs_pymol(csv_path, pdb_path, pdb_ses_path, atom_type=atom_type)
        
        print("Done writing output files")
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
    except Exception as e:
        try: shutil.rmtree(translate_path(fold_out + date))
        except: pass
        raise Exception("Error in creating output files: " + str(e))

    
    pdb_content = ''
    csv_content = ''
    pdb_ses_content = ''

    with open(translate_path(pdb_path), 'r') as src:
        pdb_content = src.read()
    with open(translate_path(csv_path), 'r') as src:
        csv_content = src.read()
    if run_fobs:
        with open(translate_path(pdb_ses_path), 'rb') as src:
            pdb_ses_content = src.read()

    out = {
        "pdb_file": {
            "file_name": pdb_name,
            "file_content": pdb_content
        },
        "csv_file": {
            "file_name": csv_name,
            "file_content": csv_content
        },
        "pdb_session": {
            "file_name": pdb_ses,
            "file_content": pdb_ses_content
        }
    }

    try: 
        shutil.rmtree(translate_path(fold_out + date))
    except Exception as e: 
        print("Error in cleaning up temporary files: " + str(e))
    
    return out


def score(parameter_json, pdb_path):
    warnings.filterwarnings("ignore")
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    cmd.feedback("disable", "all", "everything")
    ob.obErrorLog.SetOutputLevel(0)
    # params = parse_parameter_file('../data/input/Scoring_parameters.txt') 

    params = parameter_json
    params['atom_type'] = str(params['atom_type']).lower()
    fold_out = '../data/output/api_score/'

    out = element_prot_dist_score(pdb_path, fold_out, params['environment_size'], date,
                                    params['water_env'], params['atom_type'], params['l_ori'],
                                    params['pocket_num'], params['model_num'], params['run_frequencies'],
                                    params['densities_fold'], params['frequencies_fold'])

    return out
    # with tqdm(total=len(os.listdir(params['fold_in']))) as pbar:
    #     pbar.set_description('Score proteins')
    #     for pdb in os.listdir(params['fold_in']):
    #         element_prot_dist_score(params['fold_in'] + pdb, params['environment_size'], date,
    #                                 params['fold_out'], params['water_env'], params['atom_type'], params['l_ori'],
    #                                 params['pocket_num'], params['model_num'], params['run_frequencies'],
    #                                 params['densities_fold'], params['frequencies_fold'])
    #         pbar.update(1)


    # fobs_pymol(csv_in='./Demo_comitee/output/Score_111123/detail_score_sybyl/syb_4eiy_3_prot_score_111123.csv',
    #            pdb_in='./Demo_comitee/output/Score_111123/pdb_color_sybyl/syb_4eiy_3_score_111123.pdb',
    #            pdb_ses='./Demo_comitee/output/Score_111123/pdb_session_sybyl/syb_4eiy_3_score_111123_FOCUS.pse',
    #            atom_type='sybyl',res_name=['ZMA'],focus_dist=4)

    # element_prot_dist_score('./structures_to_score/4eiy_round_1_step_2.pdb', 3, wat_env=False, atom_type='custom',
    #                         Fobs=False, fold_out='./Demo_comitee/output/')



def comparaison_pocket(l_pdb, csv_out="Score_pocket_target_1.csv"):
    l_tmp = []
    l_score = []
    l_res_pocket = []
    pdb_fold = './structures_to_score/Target_1_min/'
    score_fold = './prot_score/Score_121521/pdb_color_sybyl/'
    for pdb in l_pdb:
        l_res_pocket = np.unique(np.append(l_res_pocket,
                                           element_prot_dist_score(pdb_fold + pdb, wat_env=True, atom_type='sybyl',
                                                                   pocket_num='1')))
        print(pdb)
    l_pdb_scored = os.listdir(score_fold)
    for pdb_scored in l_pdb_scored:
        score = 0
        nb_atm = 0
        nb_atm_lig = 0
        score_lig = 0
        with open(translate_path(score_fold + pdb_scored), 'r') as src:
            for line in src:
                if line[22:26].strip() in l_res_pocket and line[0:6].strip() == 'ATOM':
                    score = score + (1 - float(line[60:66]))
                    nb_atm += 1
                    l_tmp.append(line)
                if line[22:26].strip() == '999' and line[76:78].strip() != 'H':
                    nb_atm_lig += 1
                    score_lig = score_lig + (1 - float(line[60:66]))
        l_tmp.append('/n')
        l_score.append({'pdb': pdb_scored, 'score_pocket': score, 'mean_score': score / nb_atm, 'nb_atom': nb_atm,
                        'score_ligand': score_lig / nb_atm_lig, 'nb_atom_lig': nb_atm_lig})
    csv_columns = ['pdb', 'score_pocket', 'mean_score', 'nb_atom', 'score_ligand', 'nb_atom_lig']
    csv_file = csv_out
    try:
        with open(translate_path(csv_file), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in l_score:
                writer.writerow(data)
    except IOError:
        print("I/O error")
    return l_tmp
