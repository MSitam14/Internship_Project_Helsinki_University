# Information ---------------------------------------------------------------- #
# Author :	Loïc Dreano
# Github :	DreanoLoic
# Created : 2025
# Updated :
# ---------------------------------------------------------------------------- #

##### SCRIPT ROLE : generates PDBx/mmCIF output for the hotspot and comparison #####
##### pipelines instead of legacy fixed-column PDB.                           #####
#
# hotspot_cif()     - one combined CIF per structure : the real, scored atoms
#                      (_atom_site, with fitness score / atom type / grid position)
#                      plus every hotspot candidate point found across every round
#                      and every hotspot type (_hotspot, tagged by tier/gen_round),
#                      and the grid geometry used to place them (_grid, _grid_corner).
# comparison_cif()  - every already-parsed structure of a comparison dataset (i.e.
#                      gp.O_SYSTEM_COMPARISON.l_o_structures right after
#                      launch_structure_comparison() has parsed every cleaned .pdb
#                      into a PdbStructure - a_atoms is already typed by
#                      PdbStructure.load_structure(), no re-translation happens
#                      here) merged into a single CIF as one mmCIF "model"
#                      (pdbx_PDB_model_num) per structure, each keeping its own
#                      original chain(s) untouched (_atom_site, with the SYBYL/
#                      custom atom type already computed for that atom), with a
#                      small lookup table pairing model number <-> original pdb id
#                      (_dataset_structure) so a PyMOL script can split_states it
#                      back apart later, plus the grid footprint of the merged
#                      dataset (_grid, _grid_corner).  Structures are disambiguated
#                      by model rather than by remapping chains, since forcing a
#                      whole (possibly multi-chain) structure onto one new chain
#                      letter collides its residue numbering across the original
#                      chain boundary and breaks PyMOL's secondary-structure
#                      assignment after splitting.
#
# Both share a small mmCIF writer core ported from the augment_and_write_cif()
# technique used in Scoring_website_mmcif.py : build the _atom_site loop as a
# dict-of-lists and render it with Bio.PDB's MMCIFIO, then hand-write a comment
# header and any extra single-value/loop categories in front of it, so their
# ordering in the file is under our control instead of whatever MMCIFIO would
# otherwise pick.  Neither function needs a live PyMOL session - both build the
# _atom_site loop straight from already-parsed gp.a_atom_dtype arrays.

import os
import tempfile
import datetime

import numpy as np
from Bio.PDB import MMCIFIO

from Grid_methods.src.lib import global_parameters as gp


# ---------------------------------------------------------------------------- #
# Shared mmCIF writer core
# ---------------------------------------------------------------------------- #

def _format_cif_value(value):
    """Formats a single value for hand-written mmCIF text, quoting when needed."""
    if value is None:
        return '.'
    s = str(value)
    if s == '':
        return '.'
    if s in ('.', '?') or any(ch.isspace() for ch in s):
        return '"{}"'.format(s)
    return s


def _write_loop(f, category, columns, rows):
    """Writes one hand-formatted mmCIF loop_ block."""
    f.write('loop_\n')
    for col in columns:
        f.write('_{}.{}\n'.format(category, col))
    for row in rows:
        f.write(' '.join(_format_cif_value(v) for v in row) + '\n')


def _write_mmcif(cif_path, entry_id, atom_site_dict, header_lines=(), single_items=(), loops=()):
    """
    Writes a complete mmCIF file : data_ line, comment header, single-value
    categories, extra loop categories, then the _atom_site loop rendered by
    Bio.PDB's MMCIFIO from *atom_site_dict* (dict of '_atom_site.<col>' -> list
    of one string per row, all lists the same length).
    """
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.cif')
    os.close(tmp_fd)
    try:
        d = dict(atom_site_dict)
        d['data_'] = entry_id
        io = MMCIFIO()
        io.set_dict(d)
        io.save(tmp_path)
        with open(tmp_path, 'r') as f:
            body_lines = f.readlines()
    finally:
        os.remove(tmp_path)

    # MMCIFIO always starts a file with "data_<id>\n#\n" - drop that since the
    # data_ line and everything else above the _atom_site loop is written by hand.
    if body_lines and body_lines[0].startswith('data_'):
        body_lines = body_lines[1:]
    if body_lines and body_lines[0].strip() == '#':
        body_lines = body_lines[1:]

    with open(cif_path, 'w') as f:
        f.write('data_{}\n'.format(entry_id))
        f.write('#\n')
        for line in header_lines:
            f.write('# {}\n'.format(line))
        f.write('#\n')
        for key, value in single_items:
            f.write('{:<41} {}\n'.format(key, _format_cif_value(value)))
        if single_items:
            f.write('#\n')
        for category, columns, rows in loops:
            if not rows:
                continue
            _write_loop(f, category, columns, rows)
            f.write('#\n')
        f.writelines(body_lines)


# ---------------------------------------------------------------------------- #
# Small shared helpers
# ---------------------------------------------------------------------------- #

def _now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def _yes_no(value):
    return 'yes' if bool(value) else 'no'


def _str_col(values, default='.'):
    """Converts a numpy string column to a plain list, replacing blanks with '.'."""
    out = []
    for v in values:
        s = str(v).strip()
        out.append(s if s else default)
    return out


def _num_col(values, fmt):
    return [fmt.format(float(v)) for v in values]


def _identity_axis_items():
    """
    Placeholder principal-axes rotation, written as an identity matrix.  The real
    rotation applied by align_principal_axes() (src/pymol_plugins/gridbox.py) is
    derived from the live PyMOL camera view and isn't persisted anywhere once
    applied to the coordinates, so it can't be recovered here.
    """
    return [
        ('_grid.axis_x_x', '1.0'), ('_grid.axis_x_y', '0.0'), ('_grid.axis_x_z', '0.0'),
        ('_grid.axis_y_x', '0.0'), ('_grid.axis_y_y', '1.0'), ('_grid.axis_y_z', '0.0'),
        ('_grid.axis_z_x', '0.0'), ('_grid.axis_z_y', '0.0'), ('_grid.axis_z_z', '1.0'),
    ]


def _corner_rows(a_min, a_max):
    """The 8 corners of a real-coordinate bounding box, flagged by ix/iy/iz (0=min, 1=max)."""
    rows = []
    cid = 1
    for ix, x in enumerate((a_min[0], a_max[0])):
        for iy, y in enumerate((a_min[1], a_max[1])):
            for iz, z in enumerate((a_min[2], a_max[2])):
                rows.append((cid, '{:.3f}'.format(x), '{:.3f}'.format(y), '{:.3f}'.format(z), ix, iy, iz))
                cid += 1
    return rows


def _pocket_view_loops(d_view_meta):
    """
    Builds the _pocket_corner / _dataset_pocket_residue / _dataset_scene_view
    loops shared by comparison_cif() and hotspot_cif(), from the PyMOL-side
    view metadata dict captured in clean_dataset.py's prepare_dataset()
    (pocket box corners, pocket residue ids per structure, camera view).
    """
    d_view_meta = d_view_meta or {}
    loops = []

    pocket_residues = d_view_meta.get('pocket_residues') or {}
    pocket_rows = []
    i_res_id = 1
    for s_name, l_res_ids in pocket_residues.items():
        for i_res in l_res_ids:
            pocket_rows.append((i_res_id, s_name, int(i_res)))
            i_res_id += 1
    if pocket_rows:
        loops.append(('dataset_pocket_residue', ['id', 'structure_name', 'residue_serial'], pocket_rows))

    pocket_corners = d_view_meta.get('pocket_corners')
    if pocket_corners:
        loops.append(('pocket_corner', ['id', 'Cartn_x', 'Cartn_y', 'Cartn_z', 'ix', 'iy', 'iz'], [
            (
                int(c['id']),
                '{:.3f}'.format(float(c['Cartn_x'])),
                '{:.3f}'.format(float(c['Cartn_y'])),
                '{:.3f}'.format(float(c['Cartn_z'])),
                int(c['ix']),
                int(c['iy']),
                int(c['iz']),
            )
            for c in pocket_corners
        ]))

    l_view = d_view_meta.get('dataset_view') or []
    if len(l_view) == 18:
        loops.append(('dataset_scene_view', ['id', 'value'], [
            (i + 1, '{:.8f}'.format(float(v))) for i, v in enumerate(l_view)
        ]))

    return loops


# ---------------------------------------------------------------------------- #
# hotspot_cif
# ---------------------------------------------------------------------------- #

def build_hotspot_rows(p_atoms, residue_serial, gen_round, resn_spot, hotspot_type):
    """
    Builds one _hotspot loop row per pseudo-atom in *p_atoms* (a gp.p_atom_dtype
    array - the step_1/step_2/step_3 candidate points from launch_structure_hotspot()).
    Returns a list of plain dicts ready for hotspot_cif()'s l_hotspot_rows.
    """
    rows = []
    #D_TIER_NAME = {1: 'selected_voxel', 2: 'hotspot', 3: 'final_hotspot'}
    for i in range(len(p_atoms)):
        residue_serial = int(residue_serial)+1
        rows.append({
            'type_symbol': gp.D_SYBYL_TYPE[hotspot_type],
            'sybyl_type': hotspot_type,
            'label_comp_id': resn_spot,
            'auth_seq_id': residue_serial,
            'Cartn_x': float(p_atoms['coord_x'][i]),
            'Cartn_y': float(p_atoms['coord_y'][i]),
            'Cartn_z': float(p_atoms['coord_z'][i]),
            'grid_x': int(p_atoms['grid_x'][i]),
            'grid_y': int(p_atoms['grid_y'][i]),
            'grid_z': int(p_atoms['grid_z'][i]),
            'fitness_score': float(p_atoms['score_total'][i]),
            'score_rank1': float(p_atoms['score_1'][i]),
            'score_rank2': float(p_atoms['score_2'][i]),
            'score_rank3': float(p_atoms['score_3'][i]),
            'tag_total': float(p_atoms['tag_total'][i]),
            'tier': p_atoms['generation'][i],
            #'tier_name': D_TIER_NAME[p_atoms['generation'][i]],
            'gen_round': gen_round,
        })
    return rows


def hotspot_cif(cif_path, o_structure, o_system=None, d_parameters=None, l_hotspot_rows=None, entry_id=None,
                d_view_meta=None):
    """
    Writes one combined mmCIF file for a scored hotspot structure : the real
    structure atoms (with fitness score, atom type and grid position) plus every
    hotspot candidate point accumulated in *l_hotspot_rows* (see
    build_hotspot_rows()), and the grid geometry used to place them.

    :param cif_path: Output .cif path
    :param o_structure: The scored PdbStructure (o_structure.a_atoms, a
        gp.a_atom_dtype array, must already carry score_1/2/3/score_total)
    :param o_system: The hotspot System object (gp.O_SYSTEM_HOTSPOT), used for the
        grid spacing/padding - optional, falls back to gp.D_PARAMETERS_GLOBAL
    :param d_parameters: The hotspot run parameters (gp.D_PARAMETERS_HOTSPOT)
    :param l_hotspot_rows: List of dict rows built by build_hotspot_rows(),
        accumulated across every round/type/tier - may be empty
    :param entry_id: Optional entry id, defaults to '<structure name>_combined'
    :param d_view_meta: Optional PyMOL-side metadata dict (see comparison_cif())
        carrying this structure's pocket corners, pocket residue ids and camera
        view, so the plugin can recreate the .pse-equivalent scene.
    """
    d_parameters = d_parameters or {}
    l_hotspot_rows = l_hotspot_rows or []
    d_view_meta = d_view_meta or {}
    entry_id = entry_id or '{}_combined'.format(o_structure.s_name)
    a_atoms = o_structure.a_atoms
    n = len(a_atoms)

    atom_site_dict = {
        '_atom_site.group_PDB': list(a_atoms['HetAtom']),
        '_atom_site.id': [str(v) for v in a_atoms['atom_serial']],
        '_atom_site.type_symbol': _str_col(a_atoms['element_symbol']),
        '_atom_site.label_atom_id': _str_col(a_atoms['atom_name']),
        '_atom_site.label_alt_id': _str_col(a_atoms['alternative_location']),
        '_atom_site.label_comp_id': _str_col(a_atoms['residue_name']),
        '_atom_site.label_asym_id': _str_col(a_atoms['chain_id'], default='A'),
        '_atom_site.label_seq_id': [str(v) for v in a_atoms['residue_serial']],
        '_atom_site.auth_seq_id': [str(v) for v in a_atoms['residue_serial']],
        '_atom_site.pdbx_PDB_ins_code': _str_col(a_atoms['residue_insertion']),
        '_atom_site.Cartn_x': _num_col(a_atoms['coord_x'], '{:.3f}'),
        '_atom_site.Cartn_y': _num_col(a_atoms['coord_y'], '{:.3f}'),
        '_atom_site.Cartn_z': _num_col(a_atoms['coord_z'], '{:.3f}'),
        '_atom_site.occupancy': _num_col(a_atoms['occupancy'], '{:.2f}'),
        '_atom_site.B_iso_or_equiv': _num_col(a_atoms['temperature_factor'], '{:.3f}'),
        '_atom_site.pdbx_PDB_model_num': ['1'] * n,
        '_atom_site.sybyl_type': _str_col(a_atoms['sybyl_type']),
        '_atom_site.custom_type': _str_col(a_atoms['custom_type']),
        '_atom_site.fitness_score': _num_col(a_atoms['score_total'], '{:.4f}'),
        '_atom_site.score_rank1': _num_col(a_atoms['score_1'], '{:.4f}'),
        '_atom_site.score_rank2': _num_col(a_atoms['score_2'], '{:.4f}'),
        '_atom_site.score_rank3': _num_col(a_atoms['score_3'], '{:.4f}'),
        '_atom_site.grid_x': [str(int(v)) for v in a_atoms['grid_x']],
        '_atom_site.grid_y': [str(int(v)) for v in a_atoms['grid_y']],
        '_atom_site.grid_z': [str(int(v)) for v in a_atoms['grid_z']],
    }

    header_lines = [
        'PDBx/mmCIF file generated by cif_generation.hotspot_cif',
        'Source structure : {}'.format(o_structure.s_name),
        'Atom-type scheme : {}'.format(gp.D_PARAMETERS_GLOBAL.get('atom_type', '.')),
        'Date             : {}'.format(_now_str()),
    ]

    single_items = [
        ('_entry.id', entry_id),
        ('_struct.title', 'GRID_hotspot combined output for {}'.format(o_structure.s_name)),
        ('_grid_hotspot.source_pdb', o_structure.s_name),
        ('_grid_hotspot.pipeline', 'launch_structure_hotspots'),
        ('_grid_hotspot.atom_type', gp.D_PARAMETERS_GLOBAL.get('atom_type', '.')),
        ('_grid_hotspot.number_of_rounds', d_parameters.get('i_number_of_rounds', '.')),
        ('_grid_hotspot.hotspot_type', d_parameters.get('s_hotspot_type', '.')),
        ('_grid_hotspot.discard_water', _yes_no(gp.D_PARAMETERS_GLOBAL.get('b_discard_water'))),
        ('_grid_hotspot.discard_hydrogen', _yes_no(gp.D_PARAMETERS_GLOBAL.get('b_discard_hydrogen'))),
        ('_grid_hotspot.discard_alternative', _yes_no(gp.D_PARAMETERS_GLOBAL.get('b_discard_alternative'))),
        ('_grid_hotspot.pocket_size', gp.D_PARAMETERS_GLOBAL.get('pocket_size', '.')),
    ]

    a_min = getattr(o_structure, 'a_min_coord', None)
    a_max = getattr(o_structure, 'a_max_coord', None)
    a_offset = getattr(o_structure, 'a_offset', None)
    a_size = getattr(o_structure, 'a_grid_size', None)
    spacing = getattr(o_system, 'f_grid_spacing', None) if o_system is not None else None
    spacing = spacing if spacing is not None else gp.D_PARAMETERS_GLOBAL.get('f_grid_spacing')
    padding = getattr(o_system, 'f_grid_padding', None) if o_system is not None else None
    padding = padding if padding is not None else gp.D_PARAMETERS_GLOBAL.get('f_grid_padding')

    if a_min is not None and a_max is not None:
        center = (np.asarray(a_min) + np.asarray(a_max)) / 2.0
        length = np.asarray(a_max) - np.asarray(a_min)
    else:
        center = np.zeros(3)
        length = np.zeros(3)

    single_items += [
        ('_grid.spacing', '{:.3f}'.format(spacing) if spacing is not None else '.'),
        ('_grid.padding', '{:.3f}'.format(padding) if padding is not None else '.'),
        ('_grid.geometry', d_parameters.get('s_grid_geometry', '.')),
        ('_grid.align_principal_axes', _yes_no(gp.D_PARAMETERS_GLOBAL.get('align_principal_axes'))),
        ('_grid.tag_threshold', d_parameters.get('f_tag_threshold', '.')),
        ('_grid.bad_score_threshold', d_parameters.get('f_bad_score_threshold', '.')),
        ('_grid.good_score_threshold', d_parameters.get('f_good_score_threshold', '.')),
        ('_grid.offset_x', int(a_offset[0]) if a_offset is not None else '.'),
        ('_grid.offset_y', int(a_offset[1]) if a_offset is not None else '.'),
        ('_grid.offset_z', int(a_offset[2]) if a_offset is not None else '.'),
        ('_grid.n_points_x', int(a_size[0]) if a_size is not None else '.'),
        ('_grid.n_points_y', int(a_size[1]) if a_size is not None else '.'),
        ('_grid.n_points_z', int(a_size[2]) if a_size is not None else '.'),
        ('_grid.center_x', '{:.3f}'.format(center[0])),
        ('_grid.center_y', '{:.3f}'.format(center[1])),
        ('_grid.center_z', '{:.3f}'.format(center[2])),
        ('_grid.length_x', '{:.3f}'.format(length[0])),
        ('_grid.length_y', '{:.3f}'.format(length[1])),
        ('_grid.length_z', '{:.3f}'.format(length[2])),
    ] + _identity_axis_items()

    loops = []
    if a_min is not None and a_max is not None:
        loops.append(('grid_corner', ['id', 'Cartn_x', 'Cartn_y', 'Cartn_z', 'ix', 'iy', 'iz'],
                      _corner_rows(a_min, a_max)))

    loops += _pocket_view_loops(d_view_meta)

    if l_hotspot_rows:
        columns = ['id', 'type_symbol', 'sybyl_type',  'label_comp_id', 'auth_seq_id',
                   'Cartn_x', 'Cartn_y', 'Cartn_z', 'grid_x', 'grid_y', 'grid_z', 'fitness_score',
                   'score_rank1', 'score_rank2', 'score_rank3', 'tag_total', 'tier', 'gen_round']
        rows = []
        for i, r in enumerate(l_hotspot_rows, start=1):
            rows.append((
                i, r['type_symbol'], r['sybyl_type'], r['label_comp_id'], r['auth_seq_id'],
                '{:.3f}'.format(r['Cartn_x']), '{:.3f}'.format(r['Cartn_y']), '{:.3f}'.format(r['Cartn_z']),
                r['grid_x'], r['grid_y'], r['grid_z'], '{:.4f}'.format(r['fitness_score']),
                '{:.4f}'.format(r['score_rank1']), '{:.4f}'.format(r['score_rank2']), '{:.4f}'.format(r['score_rank3']),
                '{:.4f}'.format(r['tag_total']), r['tier'], r['gen_round'],
            ))
        loops.append(('hotspot', columns, rows))

    _write_mmcif(cif_path, entry_id, atom_site_dict, header_lines, single_items, loops)


# ---------------------------------------------------------------------------- #
# comparison_cif
# ---------------------------------------------------------------------------- #

def comparison_cif(l_o_structures, cif_path, d_parameters=None, entry_id='cleaned_dataset', d_view_meta=None):
    """
    Merges every already-parsed structure in *l_o_structures* into a single mmCIF
    file, giving each structure its own mmCIF model number (pdbx_PDB_model_num) while
    keeping its original chain id(s) untouched, plus a _dataset_structure loop
    pairing each model number with its original pdb name and chain(s), and a
    _grid/_grid_corner block describing the merged dataset's bounding box. Split it
    back apart later with PyMOL's split_states (not split_chains - see module
    docstring for why: collapsing a whole, possibly multi-chain, structure onto one
    new chain id collides residue numbering across the original chain boundary and
    breaks secondary-structure assignment on the split-out object).

    Call this once every structure has been parsed into a PdbStructure - i.e. right
    after the "STEP 2 : Extracts PDB structures" loop in launch_structure_comparison()
    has populated gp.O_SYSTEM_COMPARISON.l_o_structures - not any earlier. Atom
    typing (sybyl_type/custom_type) is read straight off each structure's a_atoms,
    already computed once by PdbStructure.load_structure(); this never re-runs
    OpenBabel or touches PyMOL.

    :param l_o_structures: List of parsed structures, each needing .s_name and
        .a_atoms (a gp.a_atom_dtype array) - e.g. gp.O_SYSTEM_COMPARISON.l_o_structures
    :param cif_path: Output .cif path
    :param d_parameters: The comparison run parameters (gp.D_PARAMETERS_COMPARISON)
    :param entry_id: Optional entry id, defaults to 'cleaned_dataset'
    :param d_view_meta: Optional PyMOL-side metadata dict carrying dataset/pocket
        corners, pocket residue ids and camera view to recreate the original scene.
    """
    d_parameters = d_parameters or {}
    d_view_meta = d_view_meta or {}
    columns = ('group_PDB', 'id', 'type_symbol', 'label_atom_id', 'label_alt_id', 'label_comp_id',
               'label_asym_id', 'auth_asym_id', 'label_seq_id', 'auth_seq_id', 'pdbx_PDB_ins_code',
               'Cartn_x', 'Cartn_y', 'Cartn_z', 'occupancy', 'B_iso_or_equiv', 'pdbx_PDB_model_num',
               'sybyl_type', 'custom_type')
    atom_site = {c: [] for c in columns}

    struct_rows = []
    a_min = None
    a_max = None
    serial = 0

    for i, o_structure in enumerate(l_o_structures):
        model_num = i + 1
        a_atoms = o_structure.a_atoms
        n = len(a_atoms)

        chain_col = _str_col(a_atoms['chain_id'], default='A')
        chains_seen = list(dict.fromkeys(chain_col))

        atom_site['group_PDB'].extend(list(a_atoms['HetAtom']))
        atom_site['id'].extend([str(v) for v in range(serial + 1, serial + n + 1)])
        atom_site['type_symbol'].extend(_str_col(a_atoms['element_symbol']))
        atom_site['label_atom_id'].extend(_str_col(a_atoms['atom_name']))
        atom_site['label_alt_id'].extend(_str_col(a_atoms['alternative_location']))
        atom_site['label_comp_id'].extend(_str_col(a_atoms['residue_name']))
        atom_site['label_asym_id'].extend(chain_col)
        atom_site['auth_asym_id'].extend(chain_col)
        atom_site['label_seq_id'].extend([str(v) for v in a_atoms['residue_serial']])
        atom_site['auth_seq_id'].extend([str(v) for v in a_atoms['residue_serial']])
        atom_site['pdbx_PDB_ins_code'].extend(_str_col(a_atoms['residue_insertion']))
        atom_site['Cartn_x'].extend(_num_col(a_atoms['coord_x'], '{:.3f}'))
        atom_site['Cartn_y'].extend(_num_col(a_atoms['coord_y'], '{:.3f}'))
        atom_site['Cartn_z'].extend(_num_col(a_atoms['coord_z'], '{:.3f}'))
        atom_site['occupancy'].extend(_num_col(a_atoms['occupancy'], '{:.2f}'))
        atom_site['B_iso_or_equiv'].extend(_num_col(a_atoms['temperature_factor'], '{:.3f}'))
        atom_site['pdbx_PDB_model_num'].extend([str(model_num)] * n)
        atom_site['sybyl_type'].extend(_str_col(a_atoms['sybyl_type']))
        atom_site['custom_type'].extend(_str_col(a_atoms['custom_type']))

        serial += n
        struct_rows.append((len(struct_rows) + 1, o_structure.s_name, model_num, ','.join(chains_seen), n))

        s_min = np.array([a_atoms['coord_x'].min(), a_atoms['coord_y'].min(), a_atoms['coord_z'].min()])
        s_max = np.array([a_atoms['coord_x'].max(), a_atoms['coord_y'].max(), a_atoms['coord_z'].max()])
        a_min = s_min if a_min is None else np.minimum(a_min, s_min)
        a_max = s_max if a_max is None else np.maximum(a_max, s_max)

    atom_site_dict = {'_atom_site.' + k: v for k, v in atom_site.items()}

    header_lines = [
        'PDBx/mmCIF file generated by cif_generation.comparison_cif',
        'Structures merged   : {}'.format(len(l_o_structures)),
        'Date                : {}'.format(_now_str()),
    ]

    spacing = gp.D_PARAMETERS_GLOBAL.get('f_grid_spacing')
    padding = gp.D_PARAMETERS_GLOBAL.get('f_grid_padding')
    geometry = d_parameters.get('s_grid_geometry', gp.D_PARAMETERS_GLOBAL.get('s_grid_geometry', '.'))

    if a_min is not None and a_max is not None:
        center = (a_min + a_max) / 2.0
        length = a_max - a_min
        if spacing:
            offset = np.floor(-a_min / spacing).astype(int)
            n_points = (np.floor(a_max / spacing) - np.floor(a_min / spacing) + 1).astype(int)
        else:
            offset = np.zeros(3, dtype=int)
            n_points = np.zeros(3, dtype=int)
    else:
        center = np.zeros(3)
        length = np.zeros(3)
        offset = np.zeros(3, dtype=int)
        n_points = np.zeros(3, dtype=int)

    single_items = [
        ('_entry.id', entry_id),
        ('_struct.title', 'Comparison cleaned dataset ({} structures)'.format(len(l_o_structures))),
        ('_grid.spacing', '{:.3f}'.format(spacing) if spacing else '.'),
        ('_grid.padding', '{:.3f}'.format(padding) if padding else '.'),
        ('_grid.geometry', geometry),
        ('_grid.align_principal_axes', _yes_no(gp.D_PARAMETERS_GLOBAL.get('align_principal_axes'))),
        ('_grid.offset_x', int(offset[0])),
        ('_grid.offset_y', int(offset[1])),
        ('_grid.offset_z', int(offset[2])),
        ('_grid.n_points_x', int(n_points[0])),
        ('_grid.n_points_y', int(n_points[1])),
        ('_grid.n_points_z', int(n_points[2])),
        ('_grid.center_x', '{:.3f}'.format(center[0])),
        ('_grid.center_y', '{:.3f}'.format(center[1])),
        ('_grid.center_z', '{:.3f}'.format(center[2])),
        ('_grid.length_x', '{:.3f}'.format(length[0])),
        ('_grid.length_y', '{:.3f}'.format(length[1])),
        ('_grid.length_z', '{:.3f}'.format(length[2])),
    ] + _identity_axis_items()

    loops = [('dataset_structure', ['id', 'name', 'model_num', 'chain_ids', 'atom_count'], struct_rows)]

    dataset_corners = d_view_meta.get('dataset_corners')
    if dataset_corners:
        loops.append(('grid_corner', ['id', 'Cartn_x', 'Cartn_y', 'Cartn_z', 'ix', 'iy', 'iz'], [
            (
                int(c['id']),
                '{:.3f}'.format(float(c['Cartn_x'])),
                '{:.3f}'.format(float(c['Cartn_y'])),
                '{:.3f}'.format(float(c['Cartn_z'])),
                int(c['ix']),
                int(c['iy']),
                int(c['iz']),
            )
            for c in dataset_corners
        ]))
    elif a_min is not None and a_max is not None:
        loops.append(('grid_corner', ['id', 'Cartn_x', 'Cartn_y', 'Cartn_z', 'ix', 'iy', 'iz'],
                      _corner_rows(a_min, a_max)))

    loops += _pocket_view_loops(d_view_meta)

    _write_mmcif(cif_path, entry_id, atom_site_dict, header_lines, single_items, loops)


# ---------------------------------------------------------------------------- #

# Reference ------------------------------------------------------------------ #

# Importation
# from lib.cif_generation import hotspot_cif, comparison_cif, build_hotspot_rows

# Usage
# hotspot_cif('out/1abc_combined.cif', o_structure, gp.O_SYSTEM_HOTSPOT, d_parameters, l_hotspot_rows)
# comparison_cif(gp.O_SYSTEM_COMPARISON.l_o_structures, 'out/cleaned_dataset.cif', gp.D_PARAMETERS_COMPARISON)

# ---------------------------------------------------------------------------- #