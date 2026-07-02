#!/usr/bin/env python3

##########
# Import #
##########

import csv
import datetime
import os
import tempfile
import time
import warnings

import numpy as np
from Bio.PDB import MMCIFIO
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from openbabel import openbabel as ob
from pymol import cmd, cgo
from sklearn.neighbors import KDTree
from chempy import cpv
from tqdm import tqdm
import shutil


########
# Main #
########
warnings.filterwarnings("ignore")
date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
cmd.feedback("disable", "all", "everything")
ob.obErrorLog.SetOutputLevel(0)


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
    # Nitrogen in Arginine
    Narg = {'ARG': ['NH1', 'NH2', 'NE']}
    # Carbon SP2 in aromatic ring
    Car = {'PHE': ['CG', 'CD1', 'CE2', 'CZ', 'CE1', 'CD2'],
           'TYR': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
           'TRP': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CE3',
                   'CZ3', 'CH2', 'CZ2'],
           'HIS': ['CG', 'CD2', 'CE1']}
    # Central carbon from ARG, GLN, GLU, ASP, ASN
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

    # Define atoms type considered as origin
    ori_custom = ('Xot', 'Car', 'Nbas', 'Nam', 'Oc', 'Oh', 'Oox', 'Oow')
    ori_sybyl = ("C.3", "C.2", "C.1", "C.ar", "C.cat", "N.3", "N.2", "N.1",
                 "N.ar", "N.am", "N.pl3", "N.4", "O.3.wat", "O.3", "O.2",
                 "O.co2", "S.3", "S.2", "S.o", "S.o2", "P.3", "Ti.th",
                 "Ti.oh", "Cr.th", "Cr.oh", "Co.oh", "Ru.oh", "Du")

    wat_type = ('Oow', 'O.3.wat')


CustomType = CustomAtomTypes()


def parse_parameter_file(file_path):
    parameters = {}
    with open(file_path, 'r') as file:
        for line in file:
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
        return [parse_value(item.strip()) for item in value.split(',')]
    else:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value


def translate_sybyl(pdb):
    obConversion = ob.OBConversion()
    obConversion.SetInFormat('pdb')
    ttab = ob.ttab
    ttab.SetFromType("INT")
    ttab.SetToType("SYB")
    l_syb = []
    mol = ob.OBMol()
    obConversion.ReadFile(mol, pdb)
    for obatom in ob.OBMolAtomIter(mol):
        if obatom.GetResidue().GetName() == 'HOH':
            l_syb.append('O.3.wat')
        else:
            l_syb.append(ttab.Translate(obatom.GetType()))
    return l_syb


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
        if atom_name in CustomType.MAINATOM:
            if res_num == last_resn:
                element_name = CustomType.trans_main_last[atom_name]
            else:
                element_name = CustomType.trans_main[atom_name]
        elif res_name == 'ARG' and atom_name in CustomType.Narg[res_name]:
            element_name = 'Nbas'
        elif res_name in CustomType.Car.keys() and atom_name in CustomType.Car[res_name]:
            element_name = 'Car'
        elif res_name in CustomType.OHY.keys() and atom_name == CustomType.OHY[res_name]:
            element_name = 'Oh'
        elif res_name in CustomType.Nam.keys() and atom_name == CustomType.Nam[res_name]:
            element_name = 'Nam'
        elif res_name in CustomType.Nhis.keys() and atom_name in CustomType.Nhis[res_name]:
            element_name = 'Nbas'
        elif res_name in CustomType.Ce.keys() and CustomType.Ce[res_name] == atom_name:
            element_name = 'Car'
        elif res_name in CustomType.Oc.keys() and atom_name == CustomType.Oc[res_name]:
            element_name = 'Oc'
        elif res_name in CustomType.Oox.keys() and \
                (atom_name == CustomType.Oox[res_name][0] or atom_name == CustomType.Oox[res_name][1]):
            element_name = 'Oox'
        elif res_name in CustomType.Nlys.keys() and atom_name == CustomType.Nlys[res_name]:
            element_name = 'Nbas'
        if element_name == 0:
            element_name = 'Xot'
    elif res_name in CustomType.METAL:
        element_name = "Meta"
    elif res_name == 'HOH' and atom_name == 'O':
        element_name = 'Oow'
    else:
        element_name = "Hetatm"
    return element_name


def dist_score_prot(l_atom, l_atom_num, dist, nb_contact, pdb, run_fobs, density_fold, fobs_fexp_fold):
    """
    Compute the per-contact fitness score and (optionally) Fobs/Fexp preference score
    for an origin atom and its nb_contact nearest neighbours.

    Returns
    -------
    dict_detail : dict
        Full detail record (written to CSV and embedded in mmCIF).
    ori_type : str
        Custom / SYBYL type of the origin atom.
    score_tot_mean : float
        Mean fitness score across neighbours (used for B-factor coloring).
    """
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
            if i == nb_contact + 1:
                dict_detail['Score_total'] = "%.3f" % (score_tot / nb_contact)
            else:
                continue
        if run_fobs:
            with open(fobs_fexp_fold + 'Env_score_' + l_atom[0] + '_' + str(
                    i) + '_prim.txt', 'r') as src:
                reader = csv.reader(src, quotechar="\"", delimiter=' ')
                next(reader, None)
                for row in reader:
                    if row[1] == l_atom[i]:
                        fobs_fexp = row[5]
            dict_detail['Fobs_Fexp_' + str(i)] = "%.3f" % (float(fobs_fexp))

        try:
            log_file = '../logs/logfile_' + pdb + '.txt'
            with open(density_fold + l_atom[0] + '_' +
                      l_atom[i] + '_' + str(i) + '.txt', 'r') as src:
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
                append_write = 'a'
            else:
                append_write = 'w'
            with open(log_file, append_write) as out:
                out.write(l_atom_num[0] + ' ' + l_atom[0] + '_' +
                          l_atom[i] + '_' + str(i) + ' no density\n')
            dict_detail['Score_' + str(i)] = -1.00
            score_tot = score_tot + 0.5
            dict_detail['Score_total'] = "%.3f" % (score_tot / nb_contact)
    return dict_detail, l_atom[0], round(score_tot / nb_contact, 3)


# ---------------------------------------------------------------------------
# mmCIF input/output
#
# Reading and writing both go through a plain dict-of-lists in the same
# shape Bio.PDB.MMCIF2Dict produces (key "_category.item" -> list of one
# string per row; single key/value items -> single-element list; the data
# block name itself under the special key "data_").  That shape is also
# exactly what Bio.PDB.MMCIFIO consumes via set_dict(), so the two are a
# matched read/write pair: reading a real input CIF this way and writing it
# back after only adding new keys keeps every original category/column
# (including ones we don't understand, e.g. _struct_conn) byte-for-byte
# intact - which is what lets us "just add fields" instead of rebuilding
# the file from scratch and losing information.
#
# For .pdb input there is no such generic reader, so _pdb_lines_to_
# atom_site_dict() builds the equivalent dict directly from the fixed-
# column ATOM/HETATM text, one row per line.  Deliberately not going
# through Bio.PDB's Structure/Atom object model here: that model collapses
# alternate conformations into a single "disordered atom" by default
# (confirmed empirically - a real structure with extensive altloc A/B
# pairs lost ~25% of its atom records on a naive Structure round-trip),
# which would silently throw away exactly the information this is meant
# to preserve.
# ---------------------------------------------------------------------------

def _format_pdb_atom_line(group_pdb, serial, name, altloc, resname, chain, resseq, icode,
                          x, y, z, occ, bfac, element):
    """
    Format one standard fixed-column PDB ATOM/HETATM line.  Validated to
    round-trip exactly through every column slice used elsewhere in this
    module (write_mmcif's old parsing, translate_custom(), including its
    off-by-one atom-name slice) against a real multi-altloc structure.
    """
    name = (name or '').strip()
    name_field = ((' ' + name) if len(name) <= 3 else name).ljust(4)[:4]
    altloc_c = (altloc or '.').strip()
    altloc_c = '' if altloc_c in ('', '.') else altloc_c[:1]
    chain_c = (chain or 'A').strip()[:1] or 'A'
    icode_c = (icode or '').strip()
    icode_c = '' if icode_c in ('', '.') else icode_c[:1]
    element_s = (element or '').strip()[:2].rjust(2)
    resname_s = (resname or '').strip()[:3].rjust(3)
    resseq_s = str(resseq).strip()[:4].rjust(4)
    return "{:<6}{:>5} {}{}{:>3} {}{}{}   {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {}  \n".format(
        group_pdb, str(serial).strip(), name_field, altloc_c or ' ', resname_s,
        chain_c, resseq_s, icode_c or ' ',
        x, y, z, occ, bfac, element_s)


def _pdb_lines_to_atom_site_dict(pdb_lines):
    """Build an _atom_site.* dict-of-lists directly from PDB ATOM/HETATM text, one row per line."""
    cols = {k: [] for k in (
        'group_PDB', 'id', 'type_symbol', 'label_atom_id', 'label_alt_id',
        'label_comp_id', 'label_asym_id', 'label_seq_id', 'pdbx_PDB_ins_code',
        'Cartn_x', 'Cartn_y', 'Cartn_z', 'occupancy', 'B_iso_or_equiv',
    )}
    for line in pdb_lines:
        rec = line[0:6].strip()
        if rec not in ("ATOM", "HETATM"):
            continue
        name = line[12:16].strip()
        try:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
        except ValueError:
            continue
        try:
            occ = float(line[54:60])
        except ValueError:
            occ = 1.0
        try:
            bfac = float(line[60:66])
        except ValueError:
            bfac = 0.0
        element = line[76:78].strip() if len(line) > 77 else (name[0] if name else '')
        cols['group_PDB'].append('HETATM' if rec == 'HETATM' else 'ATOM')
        cols['id'].append(line[6:11].strip())
        cols['type_symbol'].append(element if element else (name[0] if name else '.'))
        cols['label_atom_id'].append(name)
        cols['label_alt_id'].append(line[16:17].strip() or '.')
        cols['label_comp_id'].append(line[17:20].strip())
        cols['label_asym_id'].append(line[21:22].strip() or 'A')
        cols['label_seq_id'].append(line[22:26].strip())
        cols['pdbx_PDB_ins_code'].append(line[26:27].strip() or '.')
        cols['Cartn_x'].append('{:.3f}'.format(x))
        cols['Cartn_y'].append('{:.3f}'.format(y))
        cols['Cartn_z'].append('{:.3f}'.format(z))
        cols['occupancy'].append('{:.2f}'.format(occ))
        cols['B_iso_or_equiv'].append('{:.3f}'.format(bfac))
    return {'_atom_site.' + k: v for k, v in cols.items()}


def _atom_site_to_pdb_lines(cif_dict):
    """
    Synthesize standard fixed-column PDB ATOM/HETATM lines from a generic
    mmCIF's _atom_site loop, so the text-based scoring logic below can run
    unchanged regardless of whether the original input was a .pdb or a
    .cif file.  Prefers auth_* columns (matching conventional PDB chain
    IDs/residue numbering) and falls back to label_* when absent (e.g. for
    a CIF previously written by this same script).
    """
    def col(*keys):
        for k in keys:
            v = cif_dict.get('_atom_site.' + k)
            if v:
                return v
        return None

    ids = col('id')
    if not ids:
        raise ValueError("No _atom_site.id found - not a valid mmCIF structure file.")
    n = len(ids)
    group   = col('group_PDB') or ['ATOM'] * n
    names   = col('auth_atom_id', 'label_atom_id') or [''] * n
    alts    = col('label_alt_id') or ['.'] * n
    resname = col('auth_comp_id', 'label_comp_id') or [''] * n
    chain   = col('auth_asym_id', 'label_asym_id') or ['A'] * n
    resseq  = col('auth_seq_id', 'label_seq_id') or ['1'] * n
    icode   = col('pdbx_PDB_ins_code') or ['.'] * n
    xs      = col('Cartn_x')
    ys      = col('Cartn_y')
    zs      = col('Cartn_z')
    occs    = col('occupancy') or ['1.00'] * n
    bfacs   = col('B_iso_or_equiv') or ['0.00'] * n
    elems   = col('type_symbol') or [''] * n
    models  = col('pdbx_PDB_model_num')

    lines = []
    cur_model = None
    multi_model = bool(models) and len(set(models)) > 1
    for i in range(n):
        if multi_model and models[i] != cur_model:
            if cur_model is not None:
                lines.append('ENDMDL\n')
            cur_model = models[i]
            lines.append('MODEL     {:>4}\n'.format(str(cur_model)))
        try:
            x, y, z = float(xs[i]), float(ys[i]), float(zs[i])
        except (TypeError, ValueError):
            continue
        try:
            occ = float(occs[i])
        except (TypeError, ValueError):
            occ = 1.0
        try:
            bfac = float(bfacs[i])
        except (TypeError, ValueError):
            bfac = 0.0
        lines.append(_format_pdb_atom_line(
            'HETATM' if str(group[i]).upper() == 'HETATM' else 'ATOM',
            ids[i], names[i], alts[i], resname[i], chain[i], resseq[i], icode[i],
            x, y, z, occ, bfac, elems[i]))
    if multi_model and cur_model is not None:
        lines.append('ENDMDL\n')
    return lines


def augment_and_write_cif(atom_site_dict, cif_path, l_dict, l_score_prot, l_score_wat,
                          size, atom_type, run_fobs, entry_id, source_path):
    """
    Add this run's score data to *atom_site_dict* - either the full
    original CIF read verbatim (every other category/column untouched), or
    one freshly built from a scored PDB's atom lines - and write the
    result to *cif_path*:

    * ``_atom_site.pdbx_fitness_score`` / ``_atom_site.pdbx_custom_type``
      added (or overwritten) on the existing _atom_site loop, matched by
      _atom_site.id.
    * ``_pdbx_preference_score`` : one row per (origin_atom, neighbour)
      pair - origin_atom_id, origin_atom_type, neighbor_rank,
      neighbor_atom_id, neighbor_atom_type, contribution_score,
      fobs_fexp_score.
    * ``_pdbx_scoring_summary`` : global summary key/value items.

    Bio.PDB.MMCIFIO writes _atom_site/_pdbx_preference_score/any other
    original categories, but doesn't let us control where a given category
    ends up in the file or add free-form comments, so the run summary
    (comment header + _pdbx_scoring_summary) is written by hand straight
    after the data_ line and the rest is spliced in after it - giving a
    short, human-readable summary at the top of every file.
    """
    serial_to_fitness = {}
    serial_to_custom_type = {}
    for d in l_dict:
        parts = d.get("Origin", "").split()
        if len(parts) == 2:
            atype, serial = parts[0], parts[1]
            serial_to_fitness[serial] = float(d.get("Score_total", 0.5))
            serial_to_custom_type[serial] = atype

    ids = atom_site_dict['_atom_site.id']
    atom_site_dict['_atom_site.pdbx_fitness_score'] = [
        "{:.3f}".format(serial_to_fitness[sid]) if sid in serial_to_fitness else '.'
        for sid in ids
    ]
    atom_site_dict['_atom_site.pdbx_custom_type'] = [
        serial_to_custom_type.get(sid, '.') for sid in ids
    ]

    pref_rows = []
    for d in l_dict:
        parts = d.get("Origin", "").split()
        if len(parts) < 2:
            continue
        ori_type, ori_id = parts[0], parts[1]
        for rank in range(1, size + 1):
            nei_val = d.get("Neighbor_" + str(rank), "None")
            if nei_val == "None":
                continue
            nei_parts = nei_val.split()
            if len(nei_parts) < 2:
                continue
            nei_type, nei_id = nei_parts[0], nei_parts[1]
            # Score_<rank> is the per-contact density-lookup score that
            # contributes to this origin atom's averaged Score_total (the
            # latter is what ends up in _atom_site.pdbx_fitness_score) -
            # distinct from the fobs/fexp ratio, hence its own column.
            contrib = d.get("Score_" + str(rank), '.')
            contrib_str = "{:.3f}".format(float(contrib)) \
                          if str(contrib) not in ('.', '-1.0', '-1') else '.'
            fobs = d.get("Fobs_Fexp_" + str(rank), '.') if run_fobs else '.'
            fobs_str = "{:.3f}".format(float(fobs)) \
                       if str(fobs) not in ('.', '-1.0', '-1') else '.'
            pref_rows.append((ori_id, ori_type, str(rank), nei_id, nei_type,
                              contrib_str, fobs_str))

    atom_site_dict['_pdbx_preference_score.origin_atom_id']       = [r[0] for r in pref_rows]
    atom_site_dict['_pdbx_preference_score.origin_atom_type']     = [r[1] for r in pref_rows]
    atom_site_dict['_pdbx_preference_score.neighbor_rank']        = [r[2] for r in pref_rows]
    atom_site_dict['_pdbx_preference_score.neighbor_atom_id']     = [r[3] for r in pref_rows]
    atom_site_dict['_pdbx_preference_score.neighbor_atom_type']   = [r[4] for r in pref_rows]
    atom_site_dict['_pdbx_preference_score.contribution_score']   = [r[5] for r in pref_rows]
    atom_site_dict['_pdbx_preference_score.fobs_fexp_score']      = [r[6] for r in pref_rows]
    # drop the stale, ambiguously-named fitness_score column if re-scoring
    # a CIF written before it was renamed to contribution_score
    atom_site_dict.pop('_pdbx_preference_score.fitness_score', None)

    score_prot_mean = round(np.mean(l_score_prot), 3) if l_score_prot else '.'
    score_wat_mean  = round(np.mean(l_score_wat),  3) if l_score_wat  else '.'
    score_tot_mean  = round(np.mean(l_score_prot + l_score_wat), 3) \
                      if (l_score_prot or l_score_wat) else '.'
    summary_items = (
        ('_pdbx_scoring_summary.entry_id',         str(entry_id)),
        ('_pdbx_scoring_summary.score_protein',    str(score_prot_mean)),
        ('_pdbx_scoring_summary.score_waters',     str(score_wat_mean)),
        ('_pdbx_scoring_summary.score_total',      str(score_tot_mean)),
        ('_pdbx_scoring_summary.atom_type_scheme', atom_type),
        ('_pdbx_scoring_summary.environment_size', str(size)),
    )
    # Keep these out of atom_site_dict - they're written by hand below so
    # they land right after the comment header instead of wherever MMCIFIO
    # would otherwise place them.
    for key, _ in summary_items:
        atom_site_dict.pop(key, None)

    if 'data_' not in atom_site_dict:
        atom_site_dict['data_'] = entry_id

    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.cif')
    os.close(tmp_fd)
    try:
        io = MMCIFIO()
        io.set_dict(atom_site_dict)
        io.save(tmp_path)
        with open(tmp_path, 'r') as f:
            body_lines = f.readlines()
    finally:
        os.remove(tmp_path)

    # MMCIFIO always starts a file with "data_<id>\n#\n" - drop that since
    # the data_ line and a matching summary block are written by hand below.
    if body_lines and body_lines[0].startswith('data_'):
        body_lines = body_lines[1:]
    if body_lines and body_lines[0].strip() == '#':
        body_lines = body_lines[1:]

    with open(cif_path, 'w') as f:
        f.write("data_{}\n".format(entry_id))
        f.write("#\n")
        f.write("# PDBx/mmCIF file generated by Scoring_website\n")
        f.write("# Atom-type scheme : {}\n".format(atom_type))
        f.write("# Source PDB       : {}\n".format(os.path.basename(source_path)))
        f.write("# Date             : {}\n".format(date))
        f.write("#\n")
        for key, value in summary_items:
            f.write("{:<41} {}\n".format(key, value))
        f.write("#\n")
        f.writelines(body_lines)


# ---------------------------------------------------------------------------
# CGO arrow helper (unchanged – also used by the standalone plugin)
# ---------------------------------------------------------------------------

def cgo_arrow(atom1='pk1', atom2='pk2', radius=0.5, gap=0.0, hlength=-1,
              hradius=-1, color='blue red', name='', name_prefix=''):
    """Create a CGO arrow between two picked atoms."""
    radius, gap = float(radius), float(gap)
    hlength, hradius = float(hlength), float(hradius)
    try:
        color1, color2 = color.split()
    except ValueError:
        color1 = color2 = color
    color1 = list(cmd.get_color_tuple(color1))
    color2 = list(cmd.get_color_tuple(color2))

    def get_coord(v):
        if not isinstance(v, str):
            return v
        if v.startswith('['):
            return cmd.safe_list_eval(v)
        return cmd.get_atom_coords(v)

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


# ---------------------------------------------------------------------------
# Core scoring function  (replaces element_prot_dist_score)
# ---------------------------------------------------------------------------

def element_prot_dist_score(struct_path, size, date, fold_out, wat_env, atom_type, l_ori, pocket_num,
                            model_num, run_fobs, density_fold, fobs_fexp_fold):
    """
    Score all protein/water/hetatm origin atoms in *struct_path* (a .pdb or
    .cif file) and write:

    * ``<fold_out>/<date>/mmcif_<atom_type>/<basename>_<size>_score_<date>.cif``
      Full PDBx/mmCIF file with both per-atom fitness scores embedded in
      _atom_site and all directional preference scores in
      _pdbx_preference_score.  If the input was itself a .cif, every other
      category/column from it is carried over untouched (see
      augment_and_write_cif()); if it was a .pdb, only the _atom_site loop
      can be reconstructed (no HEADER/CONECT/etc. equivalent exists there).

    * ``<fold_out>/<date>/detail_score_<atom_type>/<basename>_<size>_prot_score_<date>.csv``
      Legacy CSV (kept for backward compatibility / downstream analysis).

    The heavy PSE session file is no longer generated by default; users can
    recreate the CGO visualization at any time from the CIF file using the
    accompanying PyMOL plugin  ``cgo_from_cif.py``.
    """
    # ------------------------------------------------------------------ #
    # Initialise                                                          #
    # ------------------------------------------------------------------ #
    dict_detail_keys = ['Origin']
    for i in range(size):
        dict_detail_keys.extend(['Neighbor_' + str(i + 1)])
        dict_detail_keys.extend(['Score_' + str(i + 1)])
    dict_detail_keys.append('Score_total')
    if run_fobs:
        for i in range(size):
            dict_detail_keys.extend(['Fobs_Fexp_' + str(i + 1)])

    l_res_pocket, max_bfac = 0, 0
    l_res_num, l_dict, pdb_score, prot, p_coord, o_coord, origin, \
    l_ele_name, l_atom_num, l_alt_pos, l_score_wat, \
    l_score_prot, l_res_alt = ([] for _ in range(13))

    # ------------------------------------------------------------------ #
    # Read the input structure (.pdb or .cif) into a uniform list of      #
    # standard-format PDB text lines, so every pass below this point      #
    # works identically regardless of the original file format.  For      #
    # .cif input, orig_cif_dict keeps the full original file content so   #
    # the final output can carry it all over untouched.                  #
    # ------------------------------------------------------------------ #
    orig_cif_dict = None
    if struct_path.lower().endswith('.cif'):
        orig_cif_dict = dict(MMCIF2Dict(struct_path))
        pdb_lines = _atom_site_to_pdb_lines(orig_cif_dict)
    else:
        with open(struct_path, 'r') as f:
            pdb_lines = f.readlines()

    # Determine basename and default l_ori
    if l_ori is None and atom_type == 'custom':
        l_ori = ('Xot', 'Car', 'Nbas', 'Nam', 'Oc', 'Oh', 'Oox', 'Oow')
        basename = 'cust_' + struct_path.split("/")[-1][:-4]
    elif l_ori is None and atom_type == 'sybyl':
        l_ori = ("C.3", "C.2", "C.1", "C.ar", "C.cat", "N.3", "N.2", "N.1",
                 "N.ar", "N.am", "N.pl3", "N.4", "O.3.wat", "O.3", "O.2",
                 "O.co2", "S.3", "S.2", "S.o", "S.o2", "P.3", "Ti.th",
                 "Ti.oh", "Cr.th", "Cr.oh", "Co.oh", "Ru.oh", "Du")
    if atom_type == 'sybyl':
        if orig_cif_dict is not None:
            # translate_sybyl() needs a real PDB file path for openbabel
            tmp_fd, tmp_pdb_path = tempfile.mkstemp(suffix='.pdb')
            try:
                with os.fdopen(tmp_fd, 'w') as f:
                    f.writelines(pdb_lines)
                l_syb = translate_sybyl(tmp_pdb_path)
            finally:
                os.remove(tmp_pdb_path)
        else:
            l_syb = translate_sybyl(struct_path)
        idx_syb = 0
        basename = 'syb_' + struct_path.split("/")[-1][:-4]

    # ------------------------------------------------------------------ #
    # First pass: find the last residue number (for C-terminal typing)   #
    # ------------------------------------------------------------------ #
    mdl_flag = 1
    if atom_type == 'custom':
        for line in pdb_lines:
            if line.split()[0] == 'MODEL':
                mdl_flag = 1 if line.split()[1] == str(model_num) else 0
            if mdl_flag == 0:
                continue
            if mdl_flag == 1 and line[0:6].strip() == 'ENDMDL':
                break
            if line[0:6].strip() == "ATOM":
                last_resn = line[22:27].strip()

    # ------------------------------------------------------------------ #
    # Second pass: read atoms                                             #
    # ------------------------------------------------------------------ #
    mdl_flag = 1
    for line in pdb_lines:
        if line.split()[0] == 'MODEL':
            mdl_flag = 1 if line.split()[1] == str(model_num) else 0
        if mdl_flag == 0:
            continue
        if mdl_flag == 1 and line[0:6].strip() == 'ENDMDL':
            break
        if line[0:6].strip() not in ["ATOM", "HETATM"]:
            continue
        if atom_type == 'custom':
            element_name = translate_custom(line, last_resn)
        elif atom_type == 'sybyl':
            element_name = l_syb[idx_syb]
            idx_syb += 1
        if element_name is None:
            continue
        max_bfac    = max(max_bfac, float(line[60:66]))
        atom_num    = line[6:11].strip()
        res_num     = line[22:27].strip()
        alt_pos     = line[16:17].strip()
        x           = float(line[30:38].strip())
        y           = float(line[38:46].strip())
        z           = float(line[46:54].strip())
        if element_name == 'H':
            pdb_score.append(line)
            continue
        if element_name in l_ori:
            origin.append([atom_num, element_name, res_num, alt_pos, x, y, z])
        pdb_score.append(line)
        if wat_env or element_name not in CustomType.wat_type:
            prot.append([atom_num, element_name, res_num, alt_pos, x, y, z])
        l_res_num.append(res_num)
        l_atom_num.append(atom_num)
        l_ele_name.append(element_name)
        l_alt_pos.append(alt_pos)
        l_res_alt.append(res_num + '_' + alt_pos)

    for p in prot:
        p_coord.append(p[4:])
    for o in origin:
        o_coord.append(o[4:])
    if len(o_coord) == 0:
        print("No residues in " + struct_path)
        return

    # ------------------------------------------------------------------ #
    # KDTree neighbour search                                             #
    # ------------------------------------------------------------------ #
    tree = KDTree(p_coord, leaf_size=500000, metric='euclidean')
    ind, dist = tree.query_radius(o_coord, 10, return_distance=True, sort_results=True)

    l_res_uniq = np.take(l_res_num, np.sort(np.unique(l_res_num, return_index=True)[1]))
    if pocket_num is not None:
        ind_pocket  = np.where(np.array(l_res_num) == pocket_num)[0]
        l_res_pocket = []

    for i in range(len(ind)):
        if pocket_num is not None and i in ind_pocket:
            l_res_pocket = np.unique(np.append(l_res_pocket,
                np.take(l_res_num, np.take(ind[i], np.where(dist[i] < 4)))))

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
            ori_id = [k for k, x in enumerate(l_atom_num) if x == origin[i][0]][0]
            ind[i]  = np.append(ori_id, ind[i])
            dist[i] = np.append(0, dist[i])

        ind_unique  = np.sort(np.unique(np.take(l_res_alt, ind[i]), return_index=True)[1])
        l_alt_tmp   = np.array(l_alt_pos)[np.take(ind[i], ind_unique)]
        l_res_tmp   = np.array(l_res_num)[np.take(ind[i], ind_unique)]

        if np.array(l_ele_name)[np.take(ind[i], ind_unique[0])] not in CustomType.wat_type:
            res_idx = np.where(l_res_uniq == l_res_tmp[0])[0][0]
            l_res_up   = l_res_uniq[res_idx + 1] if res_idx < len(l_res_uniq) - 1 else None
            l_res_prev = l_res_uniq[res_idx - 1] if res_idx > 0 else None
            if len(np.unique(l_alt_tmp)) > 1 and l_alt_tmp[0] == '':
                l_alt_ori = np.unique(l_alt_tmp)[1]
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

        l_dist          = np.take(dist[i], ind_unique).tolist()
        l_atom          = np.array(l_ele_name)[np.take(ind[i], ind_unique)].tolist()
        l_atom_num_env  = np.array(l_atom_num)[np.take(ind[i], ind_unique)].tolist()

        dict_tmp, ori_tmp, score_tmp = dist_score_prot(
            l_atom, l_atom_num_env, l_dist, size, basename,
            run_fobs, density_fold, fobs_fexp_fold)

        l_dict.append(dict_tmp)
        if ori_tmp in CustomType.wat_type:
            l_score_wat.append(score_tmp)
        else:
            l_score_prot.append(score_tmp)

    # ------------------------------------------------------------------ #
    # Build output paths                                                  #
    # ------------------------------------------------------------------ #
    if wat_env:
        basename = basename + '_wat'

    cif_fold   = fold_out + date + '/mmcif_' + atom_type + '/'
    score_fold = fold_out + date + '/detail_score_' + atom_type + '/'
    try:
        os.makedirs(cif_fold)
        os.makedirs(score_fold)
    except OSError:
        pass

    cif_name = cif_fold  + basename + '_' + str(size) + "_score_" + date + ".cif"
    csv_name = score_fold + basename + "_" + str(size) + "_prot_score_" + date + ".csv"
    entry_id = os.path.basename(cif_name).replace('.cif', '')

    # ------------------------------------------------------------------ #
    # Write mmCIF.  For .cif input, augment the original dict in place    #
    # (every other category/column kept byte-for-byte); for .pdb input,   #
    # build a fresh _atom_site dict from the scored atom lines.           #
    # ------------------------------------------------------------------ #

    print("Writing output files" )
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    out_dict = orig_cif_dict if orig_cif_dict is not None else _pdb_lines_to_atom_site_dict(pdb_score)
    augment_and_write_cif(out_dict, cif_name, l_dict, l_score_prot, l_score_wat,
                          size, atom_type, run_fobs, entry_id, struct_path)

    # ------------------------------------------------------------------ #
    # Write legacy CSV (kept for downstream analysis)                    #
    # ------------------------------------------------------------------ #
    with open(csv_name, 'w') as outcsv:
        writer = csv.DictWriter(outcsv, fieldnames=dict_detail_keys)
        writer.writeheader()
        for line in l_dict:
            writer.writerow(line)

    cif_content = ''
    csv_content = ''

    with open(cif_name, 'r') as src:
        cif_content = src.read()
    with open(csv_name, 'r') as src:
        csv_content = src.read()
    
    out = {
        "cif_file": {
            "file_name": basename + '_' + str(size) + "_score_" + date + ".cif",
            "file_content": cif_content
        },
        "csv_file": {
            "file_name": basename + "_" + str(size) + "_prot_score_" + date + ".csv",
            "file_content": csv_content
        }
    }

    try: 
        shutil.rmtree(fold_out + date)
    except Exception as e: 
        print("Error in cleaning up temporary files: " + str(e))

    return out


def main():
    params = parse_parameter_file('../data/input/Scoring_parameters.txt')
    structures = [f for f in os.listdir(params['fold_in'])
                  if f.lower().endswith('.pdb') or f.lower().endswith('.cif')]
    with tqdm(total=len(structures)) as pbar:
        pbar.set_description('Score proteins')
        for struct_file in structures:
            element_prot_dist_score(
                params['fold_in'] + struct_file,
                params['environment_size'],
                date,
                params['fold_out'],
                params['water_env'],
                params['atom_type'],
                params['l_ori'],
                params['pocket_num'],
                params['model_num'],
                params['run_frequencies'],
                params['densities_fold'],
                params['frequencies_fold'])
            pbar.update(1)

def apiMain(parameter_json, pdb_path, file_path):

    params = parameter_json
    params['atom_type'] = str(params['atom_type']).lower()
    fold_out = 'Fitness_score/data/output/api_score/'

    return_data = None


    return_data = element_prot_dist_score(
        pdb_path,
        params['environment_size'],
        date,
        fold_out,
        params['water_env'],
        params['atom_type'],
        params['l_ori'],
        params['pocket_num'],
        params['model_num'],
        params['run_frequencies'],
        params['densities_fold'],
        params['frequencies_fold'])

    return return_data

# if __name__ == "__main__":
    # main()


# ---------------------------------------------------------------------------
# Legacy pocket comparison  (kept, reads from the new mmCIF if needed)
# ---------------------------------------------------------------------------

# def comparaison_pocket(l_pdb, csv_out="Score_pocket_target_1.csv"):
#     l_tmp    = []
#     l_score  = []
#     l_res_pocket = []
#     pdb_fold   = './structures_to_score/Target_1_min/'
#     score_fold = './prot_score/Score_121521/pdb_color_sybyl/'
#     for pdb in l_pdb:
#         l_res_pocket = np.unique(np.append(l_res_pocket,
#             element_prot_dist_score(pdb_fold + pdb, wat_env=True, atom_type='sybyl',
#                                     pocket_num='1')))
#         print(pdb)
#     l_pdb_scored = os.listdir(score_fold)
#     for pdb_scored in l_pdb_scored:
#         score = nb_atm = nb_atm_lig = score_lig = 0
#         with open(score_fold + pdb_scored, 'r') as src:
#             for line in src:
#                 if line[22:26].strip() in l_res_pocket and line[0:6].strip() == 'ATOM':
#                     score    += (1 - float(line[60:66]))
#                     nb_atm   += 1
#                     l_tmp.append(line)
#                 if line[22:26].strip() == '999' and line[76:78].strip() != 'H':
#                     nb_atm_lig  += 1
#                     score_lig   += (1 - float(line[60:66]))
#         l_tmp.append('/n')
#         l_score.append({'pdb': pdb_scored, 'score_pocket': score,
#                         'mean_score': score / nb_atm, 'nb_atom': nb_atm,
#                         'score_ligand': score_lig / nb_atm_lig, 'nb_atom_lig': nb_atm_lig})
#     csv_columns = ['pdb', 'score_pocket', 'mean_score', 'nb_atom', 'score_ligand', 'nb_atom_lig']
#     try:
#         with open(csv_out, 'w') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#             writer.writeheader()
#             for data in l_score:
#                 writer.writerow(data)
#     except IOError:
#         print("I/O error")
#     return l_tmp
