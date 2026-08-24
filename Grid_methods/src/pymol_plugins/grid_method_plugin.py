"""
grid_method_plugin.py  -  PyMOL plugin
=======================================
Reconstructs the comparison dataset view from a PDBx/mmCIF file produced by
cif_generation.py's comparison_cif() - the merged, cleaned/aligned dataset
clean_dataset.py builds during a comparison run, one mmCIF model per
structure with its original chain(s) untouched.  Splitting it back into one
named object per structure plus the same grid-box outline clean_dataset.py
draws around the whole dataset (drawgridbox('full_gridbox', '(all)', ...))
reproduces the view its .pse session would have shown.

Installation
------------
Copy this file to your PyMOL plugin directory, or load it at runtime with:

    Plugin > Plugin Manager > Install New Plugin > choose file

Or from the PyMOL command line:

    run /path/to/grid_method_plugin.py

Usage (PyMOL command line)
--------------------------
    visual_comparison_dataset  [cif_path]  [object_name]
        The one-command entry point: open a comparison_cif CIF in PyMOL the
        normal way (File > Open, drag-and-drop, or `load`), then just run

            visual_comparison_dataset

        with no arguments.  It splits the merged object back into one
        object per structure (named after the structure's original pdb id,
        via _dataset_structure), draws the same white grid-box outline
        clean_dataset.py draws around the whole dataset, and enables every
        object - i.e. load_comparison_dataset + draw_dataset_gridbox below,
        in one shot.  If the data can't be recovered (see "Recovering
        dataset data" below), it asks for the path explicitly instead -
        e.g. visual_comparison_dataset /path/to/cleaned_dataset.cif.

    load_comparison_dataset  [cif_path]  [object_name]
        Splits the merged object into one object per structure (named from
        _dataset_structure.name) and deletes the merged source object,
        without drawing the grid box.  cif_path is normally not needed -
        see below.  Returns the list of object names created.

    draw_dataset_gridbox  [name='full_gridbox']  [color='white']  [line_width=2.0]
        Draws a CGO wireframe box from the _grid_corner corners of the
        most recently loaded dataset, expanded by _grid.padding on every
        side - the same box clean_dataset.py draws with
        drawgridbox('full_gridbox', '(all)', padding=...) for a comparison
        run.  Can be called again after load_comparison_dataset/
        visual_comparison_dataset without arguments; only needs cif_path/
        object_name if called cold (nothing loaded yet this session).

    clear_dataset_gridbox  [name='full_gridbox']
        Deletes the CGO box object created by draw_dataset_gridbox.

    create_pocket_objects
        Creates one '<structure>_pocket' object per structure with pocket
        residues (from _dataset_pocket_residue), shown as sticks. Called
        automatically by visual_comparison_dataset.

    create_dataset_scenes
        Stores two named scenes: 'global_alignement' (every structure as
        cartoon, plus the dataset gridbox) and 'focus_pocket' (camera
        zoomed on the pocket gridbox, cartoon hidden, pocket residues as
        sticks - only stored when pocket data exists). Called automatically
        by visual_comparison_dataset, which then recalls 'global_alignement'.

    visual_hotspot_structure  [cif_path]  [object_name]
        The one-command entry point for a single hotspot_cif() output (one
        structure per file - no splitting needed). Loads/reuses the scored
        structure, draws its grid/pocket boxes, creates one spheres object
        per tier per hotspot type (all tiers of a given type share one
        color, cycling through _OBJECT_COLOR_PALETTE - see
        _create_hotspot_tier_objects()) from every accumulated hotspot
        candidate point and a sticks object from the pocket residues, then
        stores : 'global_view' (whole structure), 'focus_pocket' (pocket
        zoom, every type shown), one scene per hotspot type named after its
        group (only that type's tiers shown), and 'Fitness_scored' (same
        view as focus_pocket, hotspots colored by fitness score instead -
        see _color_hotspot_by_fitness()).

    Recovering dataset data without a file path
    ---------------------------------------------
    Same mechanism as cgo_from_cif.py : this plugin turns PyMOL's
    `cif_keepinmemory` setting on as soon as it is installed, so any .cif
    opened afterwards keeps its raw _dataset_structure/_grid/_grid_corner
    data queryable through PyMOL's own (experimental) cif_get_array(), with
    zero extra steps.  Failing that (e.g. the object was loaded before this
    plugin was installed, or cif_get_array isn't available), it falls back
    to a cmd.load() hook remembering the path of every .cif loaded while
    installed, and finally to re-parsing cif_path itself if given
    explicitly.

Implementation notes
---------------------
comparison_cif() (cif_generation.py) writes one mmCIF *model*
(pdbx_PDB_model_num) per structure rather than remapping chains, precisely
so each structure keeps its own original chain(s) - see that module's
docstring for why forcing everything onto one new chain id breaks PyMOL's
secondary-structure assignment once split.  Splitting here therefore uses
cmd.create(name, source, source_state, 1) per model (equivalent to
split_states but letting each split object be named straight from
_dataset_structure.name instead of PyMOL's default "<object>_0001" suffix).

_grid_corner stores the *raw* bounding box of the merged dataset's atoms
(unpadded); _grid.padding is applied here at draw time, matching how
drawgridbox() pads a selection's extent when clean_dataset.py calls it.
"""

from __future__ import print_function

import os

try:
    from pymol import cmd, cgo, util
    _PYMOL_AVAILABLE = True
except ImportError:
    _PYMOL_AVAILABLE = False
    print("grid_method_plugin: PyMOL not found - plugin loaded in standalone mode.")


# ---------------------------------------------------------------------------
# CIF parser  (verbatim from cgo_from_cif.py - generic dict-of-lists per
# loop_ category / flat key=value items, not tied to a specific schema)
# ---------------------------------------------------------------------------

def _parse_cif(cif_path):
    """
    Parse a PDBx/mmCIF file and return a dict of all data items.

    Simple loop_ blocks are returned as  dict[category] = {col: [values...]}.
    Single key=value pairs are returned as  dict[key] = value.
    """
    data = {}

    with open(cif_path, 'r') as f:
        lines = f.readlines()

    i = 0
    n = len(lines)

    def next_token(line):
        """Split a CIF line into tokens, respecting quoted strings."""
        tokens = []
        pos = 0
        while pos < len(line):
            ch = line[pos]
            if ch in (' ', '\t', '\n', '\r'):
                pos += 1
                continue
            if ch == '#':
                break
            if ch == '"':
                end = line.find('"', pos + 1)
                if end == -1:
                    end = len(line) - 1
                tokens.append(line[pos + 1:end])
                pos = end + 1
            elif ch == "'":
                end = line.find("'", pos + 1)
                if end == -1:
                    end = len(line) - 1
                tokens.append(line[pos + 1:end])
                pos = end + 1
            else:
                end = pos
                while end < len(line) and line[end] not in (' ', '\t', '\n', '\r'):
                    end += 1
                tokens.append(line[pos:end])
                pos = end
        return tokens

    while i < n:
        line = lines[i].rstrip('\n')
        stripped = line.strip()

        if stripped == '' or stripped.startswith('#'):
            i += 1
            continue

        if stripped.startswith('data_'):
            data['_entry_id'] = stripped[5:]
            i += 1
            continue

        if stripped == 'loop_':
            i += 1
            col_names = []
            while i < n and lines[i].strip().startswith('_'):
                col_names.append(lines[i].strip())
                i += 1
            if col_names:
                cat = col_names[0].rsplit('.', 1)[0]
                short_cols = [c.rsplit('.', 1)[1] for c in col_names]
                table = {c: [] for c in short_cols}
                ncols = len(short_cols)
                row_tokens = []
                while i < n:
                    row_line = lines[i].rstrip('\n')
                    rs = row_line.strip()
                    if rs.startswith('_') or rs == 'loop_' or rs.startswith('data_') or rs == '#':
                        break
                    if rs == '' or rs.startswith('#'):
                        i += 1
                        continue
                    row_tokens.extend(next_token(row_line))
                    i += 1
                for k in range(0, len(row_tokens), ncols):
                    chunk = row_tokens[k:k + ncols]
                    if len(chunk) != ncols:
                        break
                    for col, val in zip(short_cols, chunk):
                        table[col].append(val)
                data[cat] = table
            continue

        tokens = next_token(stripped)
        if tokens and tokens[0].startswith('_'):
            key = tokens[0]
            if len(tokens) >= 2:
                data[key] = tokens[1]
            else:
                i += 1
                if i < n:
                    data[key] = lines[i].strip()
            i += 1
            continue

        i += 1

    return data


# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_cif_data     = {}   # last-resolved raw CIF data, see _load_from_memory() / _parse_cif()
_grid_data    = {}   # {'padding': float, 'corners': {...}} - what draw_dataset_gridbox() draws
_pocket_data  = {}   # {'corners': {...}, 'residues': {...}} - pocket metadata from CIF
_scene_data   = {}   # {'view': [18 floats]} - camera/view metadata from CIF
_last_objects = []   # object names created by the last load_comparison_dataset() call
_pocket_objects = [] # per-structure pocket object names created by create_pocket_objects()
_name_to_target = {} # original _dataset_structure.name -> actual split object name

# object_name (str) -> absolute .cif path, populated by the cmd.load() hook further down
_cif_path_by_object = {}

# Per-object carbon color cycle, matching PyMOL's own default per-object coloring
_OBJECT_COLOR_PALETTE = [
    'white', 'green', 'cyan', 'magenta', 'yellow', 'salmon', 'slate', 'orange', 'lime',
    'deepteal', 'hotpink', 'yelloworange', 'violetpurple', 'grey70', 'marine',
    'olive', 'smudge', 'teal', 'dirtyviolet', 'wheat', 'deepsalmon',
]


try:
    from pymol.querying import cif_get_array as _cif_get_array_fn
except ImportError:
    _cif_get_array_fn = None


def _find_active_object():
    """Best-effort guess at "the merged dataset object the user just loaded"."""
    objs = cmd.get_object_list()
    if not objs:
        return None
    if len(objs) == 1:
        return objs[0]
    enabled = cmd.get_names('objects', 1)
    if len(enabled) == 1:
        return enabled[0]
    for name in reversed(list(_cif_path_by_object.keys())):
        if name in objs:
            return name
    return objs[-1]


def _cif_array(object_name, key, dtype='s'):
    """Thin, never-raising wrapper around PyMOL's (experimental) cif_get_array."""
    if _cif_get_array_fn is None:
        return None
    try:
        return _cif_get_array_fn(object_name, key, dtype=dtype, quiet=1)
    except Exception:
        return None


def _load_from_memory(object_name):
    """
    Recover _dataset_structure/_grid/_grid_corner straight out of PyMOL's own
    in-memory CIF cache - no .cif file path needed at all.  Returns None if
    PyMOL has no cached raw CIF data for this object.
    """
    def col(key, length, default='.'):
        vals = _cif_array(object_name, key)
        if not vals:
            return [default] * length
        return [default if v is None else v for v in vals]

    names = _cif_array(object_name, '_dataset_structure.name')
    if not names:
        return None

    data = {
        '_dataset_structure': {
            'id':        col('_dataset_structure.id', len(names)),
            'name':      names,
            'model_num': col('_dataset_structure.model_num', len(names)),
            'chain_ids': col('_dataset_structure.chain_ids', len(names)),
        }
    }

    # PyMOL memory-backed CIF arrays are sometimes incomplete for custom loops
    # (notably Cartn_x/y/z for *_corner categories) - queried here anyway as a
    # fallback since _resolve_dataset_data can only merge full loop tables from
    # file when a .cif path is actually known (e.g. not for File > Open/drag-
    # and-drop loads that happened before this plugin's cmd.load hook was
    # installed).
    corner_ids = _cif_array(object_name, '_grid_corner.id')
    if corner_ids:
        data['_grid_corner'] = {
            'id': corner_ids,
            'Cartn_x': col('_grid_corner.Cartn_x', len(corner_ids)),
            'Cartn_y': col('_grid_corner.Cartn_y', len(corner_ids)),
            'Cartn_z': col('_grid_corner.Cartn_z', len(corner_ids)),
            'ix': col('_grid_corner.ix', len(corner_ids)),
            'iy': col('_grid_corner.iy', len(corner_ids)),
            'iz': col('_grid_corner.iz', len(corner_ids)),
        }

    padding = _cif_array(object_name, '_grid.padding')
    if padding:
        data['_grid.padding'] = padding[0]

    p_ids = _cif_array(object_name, '_dataset_pocket_residue.id')
    if p_ids:
        data['_dataset_pocket_residue'] = {
            'id': p_ids,
            'structure_name': col('_dataset_pocket_residue.structure_name', len(p_ids)),
            'residue_serial': col('_dataset_pocket_residue.residue_serial', len(p_ids)),
        }

    pocket_corner_ids = _cif_array(object_name, '_pocket_corner.id')
    if pocket_corner_ids:
        data['_pocket_corner'] = {
            'id': pocket_corner_ids,
            'Cartn_x': col('_pocket_corner.Cartn_x', len(pocket_corner_ids)),
            'Cartn_y': col('_pocket_corner.Cartn_y', len(pocket_corner_ids)),
            'Cartn_z': col('_pocket_corner.Cartn_z', len(pocket_corner_ids)),
            'ix': col('_pocket_corner.ix', len(pocket_corner_ids)),
            'iy': col('_pocket_corner.iy', len(pocket_corner_ids)),
            'iz': col('_pocket_corner.iz', len(pocket_corner_ids)),
        }

    view_vals = _cif_array(object_name, '_dataset_scene_view.value')
    if view_vals:
        data['_dataset_scene_view'] = {
            'value': view_vals,
        }

    return data


def _corner_data_ok(grid_corner):
    """True if *grid_corner* (a _grid_corner table dict) has usable coordinates."""
    if not grid_corner:
        return False
    xs = grid_corner.get('Cartn_x')
    if not xs:
        return False
    try:
        [float(v) for v in xs]
    except (TypeError, ValueError):
        return False
    return True


def _loop_has_xyz(loop_table):
    """True if a loop table contains numeric Cartn_x/Cartn_y/Cartn_z columns."""
    if not loop_table:
        return False
    for axis in ('Cartn_x', 'Cartn_y', 'Cartn_z'):
        vals = loop_table.get(axis)
        if not vals:
            return False
        try:
            [float(v) for v in vals]
        except (TypeError, ValueError):
            return False
    return True


def _resolve_dataset_data(cif_path, object_name):
    """
    Find _dataset_structure/_grid/_grid_corner for *object_name* (or the
    active object, or a file at *cif_path*), preferring PyMOL's own
    in-memory CIF cache over re-parsing a file from disk.

    Returns (struct_name, cif_data) or (None, None).
    """
    loaded_objs = cmd.get_object_list()

    if not object_name:
        object_name = _find_active_object() or ''

    data = None
    if object_name and object_name in loaded_objs:
        data = _load_from_memory(object_name)
        if data and cif_path:
            _cif_path_by_object[object_name] = os.path.abspath(os.path.expanduser(cif_path))

    path = cif_path or (_cif_path_by_object.get(object_name) if object_name else None)

    # PyMOL's in-memory CIF cache may omit custom loop columns; when a file path is
    # known, merge authoritative loop data from disk.
    if data and path and os.path.isfile(os.path.expanduser(path)):
        file_data = _parse_cif(os.path.expanduser(path))
        if not _loop_has_xyz(data.get('_grid_corner')) and _loop_has_xyz(file_data.get('_grid_corner')):
            data['_grid_corner'] = file_data['_grid_corner']
        if not _loop_has_xyz(data.get('_pocket_corner')) and _loop_has_xyz(file_data.get('_pocket_corner')):
            data['_pocket_corner'] = file_data['_pocket_corner']
        if '_dataset_scene_view' not in data and '_dataset_scene_view' in file_data:
            data['_dataset_scene_view'] = file_data['_dataset_scene_view']
        if '_dataset_pocket_residue' not in data and '_dataset_pocket_residue' in file_data:
            data['_dataset_pocket_residue'] = file_data['_dataset_pocket_residue']
        if '_grid.padding' in file_data:
            data['_grid.padding'] = file_data['_grid.padding']

    if data:
        return object_name, data

    if not path:
        return None, None
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        print("load_comparison_dataset: file not found: {}".format(path))
        return None, None

    print("load_comparison_dataset: parsing {}".format(os.path.basename(path)))
    data = _parse_cif(path)

    stem = os.path.basename(path).replace('.cif', '')
    if object_name and object_name in loaded_objs:
        struct_name = object_name
    elif not object_name and stem in loaded_objs:
        struct_name = stem
    elif not object_name and len(loaded_objs) == 1:
        struct_name = loaded_objs[0]
    else:
        struct_name = object_name if object_name else cmd.get_unused_name(stem)
        cmd.load(path, struct_name)

    _cif_path_by_object[struct_name] = os.path.abspath(path)
    return struct_name, data


_NO_DATA_MSG = (
    "no dataset data found. Open a comparison_cif CIF while this plugin is "
    "installed, or run load_comparison_dataset('/path/to/cleaned_dataset.cif') first."
)


# ---------------------------------------------------------------------------
# Public commands
# ---------------------------------------------------------------------------

def load_comparison_dataset(cif_path=None, object_name=''):
    """
    Splits the merged comparison_cif object into one object per structure -
    named from _dataset_structure.name, via cmd.create(name, source,
    source_state=model_num, target_state=1) - and deletes the merged source
    object.  Also caches the dataset's grid corners/padding so
    draw_dataset_gridbox() can be called afterward with no arguments.

    Parameters
    ----------
    cif_path    : path to the .cif file written by comparison_cif().
                  Optional if the active object's data can be recovered
                  from PyMOL's in-memory CIF cache or a previous
                  load_comparison_dataset()/cmd.load() call.
    object_name : optional PyMOL object name of the merged dataset
                  (default: the active/sole already-loaded object)

    Returns
    -------
    list[str] : names of the objects created, or [] on failure.
    """
    global _cif_data, _grid_data, _pocket_data, _scene_data, _last_objects, _pocket_objects, _name_to_target

    struct_name, data = _resolve_dataset_data(cif_path, object_name)
    if not struct_name:
        print("load_comparison_dataset: " + _NO_DATA_MSG)
        return []

    _cif_data = data
    dataset = data.get('_dataset_structure', {})
    names = dataset.get('name', [])
    model_nums = dataset.get('model_num', [])
    if not names:
        print("load_comparison_dataset: no _dataset_structure data found in the CIF.")
        return []

    n_states = cmd.count_states(struct_name)
    used_names = set(cmd.get_names())
    used_names.discard(struct_name)
    created = []
    _pocket_objects = []
    _name_to_target = {}

    for i, (nm, mn) in enumerate(zip(names, model_nums)):
        try:
            state = int(mn)
        except (TypeError, ValueError):
            continue
        if state < 1 or state > n_states:
            print("load_comparison_dataset: skipping '{}', model {} out of range (1..{}).".format(
                nm, state, n_states))
            continue
        target = nm if nm not in used_names else cmd.get_unused_name(nm + '_')
        # Round-trip through a real PDB block (rather than cmd.create) so PyMOL
        # re-guesses bonds and secondary structure for this state on its own -
        # cmd.create only copies coordinates from the merged/discrete source
        # object, which otherwise leaves every state but the first without the
        # bond connectivity dss needs to detect helices/sheets.
        cmd.read_pdbstr(cmd.get_pdbstr(struct_name, state), target)
        cmd.dss(target)
        cmd.color(_OBJECT_COLOR_PALETTE[i % len(_OBJECT_COLOR_PALETTE)], target + ' and elem C')
        used_names.add(target)
        created.append(target)
        _name_to_target[nm] = target

    cmd.delete(struct_name)
    _last_objects = created

    corners = data.get('_grid_corner')
    if corners:
        _grid_data = {
            'padding': data.get('_grid.padding', '0'),
            'corners': corners,
        }
    else:
        _grid_data = {}

    pocket_corners = data.get('_pocket_corner')
    pocket_residues = data.get('_dataset_pocket_residue', {})
    if pocket_corners or pocket_residues:
        _pocket_data = {
            'corners': pocket_corners,
            'residues': pocket_residues,
        }
    else:
        _pocket_data = {}

    scene_view = data.get('_dataset_scene_view', {}).get('value', [])
    if scene_view:
        _scene_data = {'view': scene_view}
    else:
        _scene_data = {}

    print("load_comparison_dataset: split into {} object(s) : {}".format(
        len(created), ', '.join(created)))
    return created


def visual_comparison_dataset(cif_path=None, object_name=''):
    """
    One-shot command: split the merged object back into one object per
    structure, draw the pocket box (or the dataset box when there is no
    pocket) and per-structure pocket objects, and store two scenes
    reproducing the .pse session's views - 'global_alignement' (zoom on
    every structure, shown as cartoon) and 'focus_pocket' (zoom on the
    pocket gridbox, cartoon hidden, pocket residues as sticks) - recalling
    'global_alignement' as the initial view.

    Equivalent to running load_comparison_dataset(), draw_pocket_gridbox(),
    draw_dataset_gridbox() (only when there is no pocket box),
    create_pocket_objects(), create_dataset_scenes(), then recalling the
    'global_alignement' scene.
    """
    created = load_comparison_dataset(cif_path, object_name)
    if not created:
        return
    draw_pocket_gridbox()
    # Only one box at a time: the pocket box takes precedence over the full
    # dataset box when pocket data is available.
    if not _pocket_data or not _pocket_data.get('corners'):
        draw_dataset_gridbox()
    create_pocket_objects()
    create_dataset_scenes()
    cmd.scene('global_alignement', 'recall')


def draw_dataset_gridbox(name='Full_gridbox', color='white', line_width=0.3):
    """
    Draws a CGO wireframe box (cylinder edges, matching gridbox.py's
    drawgridbox() edge style) from the corners of the most recently loaded
    dataset's bounding box (see load_comparison_dataset), expanded by
    _grid.padding on every side - the same plain box
    drawgridbox('full_gridbox', '(all)', padding=...) draws in
    clean_dataset.py for a comparison run (no sub-grid divisions, no axes).

    Parameters
    ----------
    name       : CGO object name  [default: 'full_gridbox', matching
                 clean_dataset.py's own name for this box]
    color      : any PyMOL colour name  [default: 'white']
    line_width : cylinder edge diameter, in Angstrom  [default: 0.3,
                 matching gridbox.py's own edge_width default]
    """
    if not _grid_data or not _grid_data.get('corners'):
        print("draw_dataset_gridbox: " + _NO_DATA_MSG)
        return

    corners = _grid_data['corners']
    try:
        xs = [float(v) for v in corners['Cartn_x']]
        ys = [float(v) for v in corners['Cartn_y']]
        zs = [float(v) for v in corners['Cartn_z']]
        ix = [int(v) for v in corners['ix']]
        iy = [int(v) for v in corners['iy']]
        iz = [int(v) for v in corners['iz']]
    except (KeyError, ValueError):
        print("draw_dataset_gridbox: malformed _grid_corner data.")
        return

    try:
        x_min = min(x for x, f in zip(xs, ix) if f == 0)
        x_max = max(x for x, f in zip(xs, ix) if f == 1)
        y_min = min(y for y, f in zip(ys, iy) if f == 0)
        y_max = max(y for y, f in zip(ys, iy) if f == 1)
        z_min = min(z for z, f in zip(zs, iz) if f == 0)
        z_max = max(z for z, f in zip(zs, iz) if f == 1)
    except ValueError:
        print("draw_dataset_gridbox: incomplete _grid_corner data.")
        return

    try:
        padding = float(_grid_data.get('padding', 0) or 0)
    except (TypeError, ValueError):
        padding = 0.0
    x_min, x_max = x_min - padding, x_max + padding
    y_min, y_max = y_min - padding, y_max + padding
    z_min, z_max = z_min - padding, z_max + padding

    box_corners = [
        (x_min, y_min, z_min), (x_min, y_min, z_max),
        (x_min, y_max, z_min), (x_min, y_max, z_max),
        (x_max, y_min, z_min), (x_max, y_min, z_max),
        (x_max, y_max, z_min), (x_max, y_max, z_max),
    ]
    # 12 edges of the box, indexing into box_corners above
    edges = (
        (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
        (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7),
    )

    r, g, b = cmd.get_color_tuple(color)
    radius = float(line_width) / 2.0
    obj = []
    for i, j in edges:
        x1, y1, z1 = box_corners[i]
        x2, y2, z2 = box_corners[j]
        obj += [cgo.CYLINDER, x1, y1, z1, x2, y2, z2, radius, r, g, b, r, g, b]

    cmd.delete(name)
    cmd.load_cgo(obj, name)
    print("draw_dataset_gridbox: drew '{}' (padding {:.3f}).".format(name, padding))


def clear_dataset_gridbox(name='full_gridbox'):
    """Deletes the CGO box object created by draw_dataset_gridbox."""
    cmd.delete(name)
    print("clear_dataset_gridbox: deleted '{}'.".format(name))


def draw_pocket_gridbox(name='Pocket_gridbox', color='white', line_width=0.3):
    """
    Draws a pocket CGO wireframe box (cylinder edges, matching gridbox.py's
    drawgridbox() edge style) from _pocket_corner metadata when present.
    """
    if not _pocket_data or not _pocket_data.get('corners'):
        print("draw_pocket_gridbox: no pocket corner data available.")
        return

    corners = _pocket_data['corners']
    try:
        xs = [float(v) for v in corners['Cartn_x']]
        ys = [float(v) for v in corners['Cartn_y']]
        zs = [float(v) for v in corners['Cartn_z']]
        ix = [int(v) for v in corners['ix']]
        iy = [int(v) for v in corners['iy']]
        iz = [int(v) for v in corners['iz']]
    except (KeyError, ValueError):
        print("draw_pocket_gridbox: malformed _pocket_corner data.")
        return

    try:
        x_min = min(x for x, f in zip(xs, ix) if f == 0)
        x_max = max(x for x, f in zip(xs, ix) if f == 1)
        y_min = min(y for y, f in zip(ys, iy) if f == 0)
        y_max = max(y for y, f in zip(ys, iy) if f == 1)
        z_min = min(z for z, f in zip(zs, iz) if f == 0)
        z_max = max(z for z, f in zip(zs, iz) if f == 1)
    except ValueError:
        print("draw_pocket_gridbox: incomplete _pocket_corner data.")
        return

    box_corners = [
        (x_min, y_min, z_min), (x_min, y_min, z_max),
        (x_min, y_max, z_min), (x_min, y_max, z_max),
        (x_max, y_min, z_min), (x_max, y_min, z_max),
        (x_max, y_max, z_min), (x_max, y_max, z_max),
    ]
    edges = (
        (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
        (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7),
    )

    r, g, b = cmd.get_color_tuple(color)
    radius = float(line_width) / 2.0
    obj = []
    for i, j in edges:
        x1, y1, z1 = box_corners[i]
        x2, y2, z2 = box_corners[j]
        obj += [cgo.CYLINDER, x1, y1, z1, x2, y2, z2, radius, r, g, b, r, g, b]

    cmd.delete(name)
    cmd.load_cgo(obj, name)
    print("draw_pocket_gridbox: drew '{}'.".format(name))


def apply_dataset_scene():
    """
    Applies the camera view saved in _dataset_scene_view when available.
    """
    if not _scene_data or not _scene_data.get('view'):
        return
    try:
        view = tuple(float(v) for v in _scene_data['view'])
        if len(view) == 18:
            cmd.set_view(view)
            print("apply_dataset_scene: camera view restored.")
    except Exception as e:
        print("apply_dataset_scene: could not restore view ({})".format(e))


def create_pocket_objects():
    """
    Creates one '<structure>_pocket' object per structure that has pocket
    residues in _dataset_pocket_residue, shown as sticks - the residues
    extract_pocket()/extract_pocket_global() (pymol_plugins/extract_pocket.py)
    originally selected around the ligand during dataset preparation.

    Returns
    -------
    list[str] : names of the pocket objects created.
    """
    global _pocket_objects

    _pocket_objects = []
    residues = _pocket_data.get('residues') if _pocket_data else None
    if not residues or not residues.get('structure_name'):
        return _pocket_objects

    grouped = {}
    for s_name, resi in zip(residues['structure_name'], residues['residue_serial']):
        grouped.setdefault(s_name, []).append(str(resi))

    loaded_objs = set(cmd.get_object_list())
    for s_name, l_resi in grouped.items():
        target = _name_to_target.get(s_name, s_name)
        if target not in loaded_objs:
            continue
        pocket_obj = target + '_pocket'
        cmd.create(pocket_obj, '{} and resi {}'.format(target, '+'.join(l_resi)))
        cmd.hide('everything', pocket_obj)
        cmd.show('sticks', pocket_obj)
        _pocket_objects.append(pocket_obj)

    print("create_pocket_objects: created {} pocket object(s).".format(len(_pocket_objects)))
    return _pocket_objects


def create_dataset_scenes():
    """
    Stores the two scenes reproducing the original .pse session's views :
      - 'global_alignement' : zoom on every structure, shown as cartoon.
      - 'focus_pocket'      : zoom on the pocket gridbox (see
        draw_pocket_gridbox()), cartoon hidden, pocket residues as sticks
        (see create_pocket_objects()) - only stored when pocket data exists.
    The gridbox itself (whichever of full_gridbox/Pocket_gridbox exists) is
    left enabled throughout - only the cartoon/sticks representations are
    toggled between scenes, so the box stays visible when switching scenes.
    """
    if not _last_objects:
        print("create_dataset_scenes: " + _NO_DATA_MSG)
        return

    loaded_objs = cmd.get_object_list()
    box_name = 'Pocket_gridbox' if 'Pocket_gridbox' in loaded_objs else (
        'full_gridbox' if 'full_gridbox' in loaded_objs else None)
    if box_name:
        cmd.enable(box_name)
        cmd.show('cgo', box_name)

    for target in _last_objects:
        cmd.enable(target)
    for pocket_obj in _pocket_objects:
        cmd.enable(pocket_obj)
        cmd.hide('sticks', pocket_obj)

    # Scene 1 : every structure as cartoon, zoomed to fit
    for target in _last_objects:
        cmd.show('cartoon', target)
    cmd.zoom(' '.join(_last_objects), buffer=2)
    cmd.scene('global_alignement', 'store')
    print("create_dataset_scenes: stored scene 'global_alignement'.")

    # Scene 2 : pocket-focused view, only when pocket data is available
    if not _pocket_objects:
        print("create_dataset_scenes: no pocket data available, skipping 'focus_pocket'.")
        return

    for target in _last_objects:
        cmd.hide('everything', target)
    for pocket_obj in _pocket_objects:
        cmd.show('sticks', pocket_obj)   


    zoom_target = 'Pocket_gridbox' if 'Pocket_gridbox' in loaded_objs else ' '.join(_pocket_objects)
    cmd.zoom(zoom_target, buffer=2)
    cmd.scene('focus_pocket', 'store')
    print("create_dataset_scenes: stored scene 'focus_pocket'.")


# Per-tier sphere scale, matching launch_structure_hotspots.py's own step 1/2/3 CGO sizing.
_TIER_SPHERE_SCALE = {1: 0.05, 2: 0.2, 3: 0.5}
_TIER_SPHERE_TRANSPARENCY = {1: 0.0, 2: 0.3, 3: 0.5}

def _hotspot_pdb_block(hotspot_table, indices=None):
    """Builds a HETATM-only PDB block from a _hotspot loop table (see hotspot_cif()),
    restricted to *indices* if given, so the candidate points can be loaded as a
    real object and shown as spheres. Each atom's fitness_score is embedded in the
    B-factor column, so cmd.spectrum('b', ...) can color by it directly (see
    _color_hotspot_by_fitness()), the same way cgo_from_cif.py colors by
    pdbx_fitness_score."""
    xs = hotspot_table.get('Cartn_x', [])
    ys = hotspot_table.get('Cartn_y', [])
    zs = hotspot_table.get('Cartn_z', [])
    types = hotspot_table.get('type_symbol', [])
    comps = hotspot_table.get('label_comp_id', [])
    scores = hotspot_table.get('fitness_score', [])
    lines = []
    for i in (indices if indices is not None else range(len(xs))):
        try:
            x, y, z = float(xs[i]), float(ys[i]), float(zs[i])
        except (TypeError, ValueError):
            continue
        elem = (types[i] if i < len(types) else 'O').strip() or 'O'
        comp = (comps[i] if i < len(comps) else 'HOT').strip() or 'HOT'
        try:
            score = float(scores[i]) if i < len(scores) else 0.5
        except (TypeError, ValueError):
            score = 0.5
        lines.append(
            "HETATM{:>5d} {:<4s} {:<3s} A{:>4d}    {:>8.3f}{:>8.3f}{:>8.3f}{:>6.2f}{:>6.2f}          {:>2s}\n".format(
                i + 1, elem[:1].upper(), comp[:3].upper(), (i % 9999) + 1, x, y, z, 1.0, score, elem[:2].upper()))
    lines.append("END\n")
    return ''.join(lines)


def _color_hotspot_by_fitness(hotspot_objs, palette='rainbow_rev'):
    """Colors each hotspot tier object by its embedded fitness-score B-factor,
    matching cgo_from_cif.py's fitness-score spectrum (bad score = 0 -> red,
    good score = 1 -> blue)."""
    for obj in hotspot_objs:
        try:
            cmd.spectrum('b', palette, obj, minimum=0, maximum=1)
        except Exception:
            pass


def _create_hotspot_tier_objects(object_name, hotspot_table):
    """
    Creates one '<label_comp_id>_<tier_name>' object per (comp_id, tier) found
    in the _hotspot loop, shown as spheres with a tier-specific sphere_scale
    (see _TIER_SPHERE_SCALE), colors every tier object sharing a given
    label_comp_id with the same color (one color per hotspot type, cycling
    through _OBJECT_COLOR_PALETTE), then groups them together
    (cmd.group(comp_id, ...)).

    Returns
    -------
    (list[str], dict[str, list[str]]) : names of every tier object created,
    and the label_comp_id -> tier object names mapping (== the group
    contents), so callers can store one scene per hotspot type.
    """
    D_TIER_NAME = {1: 'selected_voxel', 2: 'hotspot', 3: 'final_hotspot'}   
    comps = hotspot_table.get('label_comp_id', [])
    tiers = hotspot_table.get('tier', [])
    grouped = {}
    for i in range(len(comps)):
        comp = (comps[i] or 'HOT').strip() or 'HOT'
        tier_name = D_TIER_NAME.get(int(tiers[i]), 'hotspot')
        try:
            tier = int(tiers[i]) 
        except (TypeError, ValueError):
            tier = 0
        grouped.setdefault((comp, tier, tier_name), []).append(i)

    hotspot_objs = []
    comp_to_objs = {}
    for (comp, tier, tier_name), indices in grouped.items():
        obj_name = '{}_{}'.format(comp, tier_name)
        cmd.read_pdbstr(_hotspot_pdb_block(hotspot_table, indices), obj_name)
        cmd.hide('everything', obj_name)
        cmd.show('spheres', obj_name)
        cmd.set('sphere_scale', _TIER_SPHERE_SCALE.get(tier, 0.3), obj_name)
        cmd.set('sphere_transparency', _TIER_SPHERE_TRANSPARENCY.get(tier, 0.3), obj_name)
        hotspot_objs.append(obj_name)
        comp_to_objs.setdefault(comp, []).append(obj_name)
    ind_color = 0
    for comp, objs in comp_to_objs.items():
        print("objs are {}, comp is {}".format(objs, comp))
        # if type of atom is carbon use color 
        if comp[0] == 'C':
            ind_color += 1
            comp_color = _OBJECT_COLOR_PALETTE[ind_color % len(_OBJECT_COLOR_PALETTE)]
            for obj in objs:
                print("coloring {} with {}".format(obj, comp_color))
                cmd.color(comp_color, obj)
        else:
            for obj in objs:
                util.cbag(obj)
        cmd.group(comp, ' '.join(objs))

    return hotspot_objs, comp_to_objs


def visual_hotspot_structure(cif_path=None, object_name=''):
    """
    One-shot command for a single hotspot_cif() output (one structure per
    file, no _dataset_structure splitting needed - see visual_comparison_dataset
    for the multi-structure comparison_cif equivalent). Loads/reuses the scored
    structure object, draws its grid/pocket boxes, creates one
    '<label_comp_id>_<tier_name>' spheres object per tier found in _hotspot
    (grouped by label_comp_id - see _create_hotspot_tier_objects()) and a
    '<structure>_pocket' object from _dataset_pocket_residue (sticks), then
    stores the same 'global_alignement' / 'focus_pocket' scenes as
    visual_comparison_dataset(), reproducing the hotspot workflow's .pse view.

    Parameters
    ----------
    cif_path    : path to the .cif file written by hotspot_cif(). Optional if
                  the structure was already loaded (via load/File > Open) while
                  this plugin was installed.
    object_name : optional PyMOL object name of the structure (default: the
                  active/sole already-loaded object)
    """
    global _grid_data, _pocket_data, _scene_data

    loaded_objs = cmd.get_object_list()
    if not object_name:
        object_name = _find_active_object() or ''

    data = None
    path = os.path.expanduser(cif_path) if cif_path else _cif_path_by_object.get(object_name)
    if path:
        if not os.path.isfile(path):
            print("visual_hotspot_structure: file not found: {}".format(path))
            return
        data = _parse_cif(path)
        stem = os.path.basename(path).replace('.cif', '')
        if object_name and object_name in loaded_objs:
            struct_name = object_name
        elif stem in loaded_objs:
            struct_name = stem
        else:
            struct_name = object_name if object_name else cmd.get_unused_name(stem)
            cmd.load(path, struct_name)
        object_name = struct_name
        _cif_path_by_object[object_name] = path
    elif object_name and object_name in loaded_objs:
        data = _load_from_memory(object_name)

    if not data or not object_name:
        print("visual_hotspot_structure: " + _NO_DATA_MSG)
        return

    corners = data.get('_grid_corner')
    _grid_data = {'padding': data.get('_grid.padding', '0'), 'corners': corners} if corners else {}

    pocket_corners = data.get('_pocket_corner')
    pocket_residues = data.get('_dataset_pocket_residue')
    _pocket_data = {'corners': pocket_corners, 'residues': pocket_residues} if (pocket_corners or pocket_residues) else {}

    scene_view = (data.get('_dataset_scene_view') or {}).get('value', [])
    _scene_data = {'view': scene_view} if scene_view else {}

    cmd.dss(object_name)
    util.cbaw(object_name)

    pocket_obj = None
    if pocket_residues and pocket_residues.get('residue_serial'):
        l_resi = sorted(set(str(r) for r in pocket_residues['residue_serial']))
        pocket_obj = object_name + '_pocket'
        cmd.create(pocket_obj, '{} and resi {}'.format(object_name, '+'.join(l_resi)))
        cmd.hide('everything', pocket_obj)
        cmd.show('sticks', pocket_obj)

    hotspot_objs = []
    comp_to_objs = {}
    hotspot_table = data.get('_hotspot')
    if hotspot_table and hotspot_table.get('Cartn_x'):
        hotspot_objs, comp_to_objs = _create_hotspot_tier_objects(object_name, hotspot_table)

    draw_dataset_gridbox(name='full_gridbox')
    draw_pocket_gridbox()

    # Scene 1 : whole structure as cartoon, zoomed to fit
    cmd.set('orthoscopic', 1)
    cmd.enable(object_name)
    if pocket_obj:
        cmd.disable(pocket_obj)
    for obj in hotspot_objs:
        cmd.disable(obj)
    cmd.show('cartoon', object_name)
    cmd.zoom(object_name, buffer=2)
    cmd.scene('global_view', 'store')
    print("visual_hotspot_structure: stored scene 'global_view'.")

    # Scene 2 : pocket-focused view, only when pocket/hotspot data is available
    if pocket_obj or hotspot_objs:
        cmd.set('grid_mode', 0)
        cmd.hide('cartoon', object_name)
        l_zoom_target = []
        if pocket_obj:
            cmd.disable('full_gridbox')
            cmd.enable(pocket_obj)
            cmd.show('sticks', pocket_obj)
            l_zoom_target.append(pocket_obj)
        for obj in hotspot_objs:
            cmd.enable(obj)
            cmd.show('spheres', obj)
            l_zoom_target.append(obj)
        zoom_target = 'Pocket_gridbox' if 'Pocket_gridbox' in cmd.get_object_list() else ' '.join(l_zoom_target)
        cmd.zoom(zoom_target, buffer=2)
        cmd.disable('*voxel')
        cmd.scene('All_hotspot', 'store')
        print("visual_hotspot_structure: stored scene 'All_hotspot'.")

        # One scene per hotspot type (group), named after the group, showing
        # only that type's tier objects (with their own type color) - all
        # other hotspot types disabled, same pocket zoom/visibility otherwise.
        cmd.disable('Pocket_gridbox')
        cmd.enable('*voxel')
        for comp, objs in comp_to_objs.items():
            for other_comp, other_objs in comp_to_objs.items():
                for obj in other_objs:
                    if other_comp == comp:
                        cmd.enable(obj)
                        cmd.show('spheres', obj)
                    else:
                        cmd.disable(obj)
            cmd.zoom(' '.join(objs), buffer=2)
            cmd.scene(comp, 'store')
            print("visual_hotspot_structure: stored scene '{}'.".format(comp))
            
        # Same view/visibility as focus_pocket, but hotspots colored by their
        # fitness score (see _color_hotspot_by_fitness()) instead of the
        # per-type color.
        _color_hotspot_by_fitness(hotspot_objs)
        for comp, objs in comp_to_objs.items():
            for other_comp, other_objs in comp_to_objs.items():
                for obj in other_objs:
                    if other_comp == comp:
                        cmd.enable(obj)
                        cmd.show('spheres', obj)
                    else:
                        cmd.disable(obj)
                        cmd.zoom(' '.join(objs), buffer=2)
            cmd.scene(comp+'_fitness', 'store')
            print("visual_hotspot_structure: stored scene '{}_fitness'.".format(comp))

    cmd.scene('global_view', 'recall')


# ---------------------------------------------------------------------------
# PyMOL plugin registration
# ---------------------------------------------------------------------------

def __init_plugin__(app=None):
    """Called by PyMOL when the plugin is installed via the Plugin Manager."""
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Load Comparison Dataset CIF', _gui_load)


def _gui_load():
    """Simple Qt file-dialog launcher so users can pick a CIF via the GUI."""
    try:
        from pymol.Qt import QtWidgets
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open comparison dataset CIF', '', 'CIF files (*.cif);;All files (*)')
        if fname:
            visual_comparison_dataset(fname)
    except Exception as e:
        print("GUI error: {}".format(e))


# ---------------------------------------------------------------------------
# cmd.load() hook - remembers which .cif file produced which object, so the
# zero-argument commands above can recover the path for an object the user
# opened through PyMOL's own load / File > Open / drag-and-drop, on PyMOL
# builds where cif_get_array / cif_keepinmemory (above) aren't available.
# ---------------------------------------------------------------------------

def _install_load_hook():
    if getattr(cmd.load, '_grid_method_plugin_hook', False):
        return  # already hooked (e.g. plugin file `run` twice in one session)

    _orig_load = cmd.load

    def _hooked_load(filename='', object='', *args, **kwargs):
        before = set(cmd.get_object_list())
        ret = _orig_load(filename, object, *args, **kwargs)
        try:
            if isinstance(filename, str) and filename.lower().endswith('.cif'):
                after = set(cmd.get_object_list())
                new_objs = after - before
                target = object or (new_objs.pop() if len(new_objs) == 1 else None)
                if target:
                    _cif_path_by_object[target] = os.path.abspath(os.path.expanduser(filename))
        except Exception:
            pass
        return ret

    _hooked_load._grid_method_plugin_hook = True
    cmd.load = _hooked_load


# ---------------------------------------------------------------------------
# Register commands so they are available in the PyMOL command line
# ---------------------------------------------------------------------------

if _PYMOL_AVAILABLE:
    # Must be set *before* a .cif is loaded for PyMOL to retain the raw
    # data - see _load_from_memory() above.
    cmd.set('cif_keepinmemory', 1)
    _install_load_hook()
    cmd.extend('visual_comparison_dataset', visual_comparison_dataset)
    cmd.extend('load_comparison_dataset',   load_comparison_dataset)
    cmd.extend('draw_dataset_gridbox',      draw_dataset_gridbox)
    cmd.extend('draw_pocket_gridbox',       draw_pocket_gridbox)
    cmd.extend('apply_dataset_scene',       apply_dataset_scene)
    cmd.extend('create_pocket_objects',     create_pocket_objects)
    cmd.extend('create_dataset_scenes',     create_dataset_scenes)
    cmd.extend('visual_hotspot_structure',  visual_hotspot_structure)
    cmd.extend('clear_dataset_gridbox',     clear_dataset_gridbox)
    print("grid_method_plugin loaded.")
    print("  Commands: visual_comparison_dataset | load_comparison_dataset"
            " | draw_dataset_gridbox | draw_pocket_gridbox | apply_dataset_scene"
            " | create_pocket_objects | create_dataset_scenes | visual_hotspot_structure"
            " | clear_dataset_gridbox")