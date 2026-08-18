from dataclasses import dataclass
from typing import Optional
import json


# ==========================================================
# Base class
# ==========================================================

@dataclass
class RequestGridGlobalParameters:

    # ---------- Global parameters ----------
    run_comparison: str = "True"
    run_hotspot: str = "False"

    explicit_grid: str = "False"
    atom_type: str = "SYBYL"
    grid_spacing: str = "0.25"
    grid_padding: str = "3.0"
    align_principal_axes: str = "False"

    pocket_res_name: str = "False"
    pocket_res_id: str = "False"
    lig_chain: str = "False"
    pocket_size: str = "4.5"

    discard_hetatm: str = "False"
    discard_atom: str = "False"
    discard_hydrogen: str = "True"
    discard_water: str = "True"
    discard_alternative: str = "False"

    keep_chains: str = ""
    discard_chains: str = ""
    keep_residues: str = ""
    discard_residues: str = ""
    keep_residue_ids: str = ""
    discard_residue_ids: str = ""
    keep_atoms: str = ""
    discard_atoms: str = ""

    cpu_allocated: str = "None"

    path_to_comparison_parameters: str = "Grid_methods/config/comparison_parameters.txt"
    path_to_hotspot_parameters: str = "Grid_methods/config/hotspot_parameters.txt"

    watch_live: str = "False"
    create_pymol_session: str = "False"
    session_name: str = "None"


# ==========================================================
# Comparison
# ==========================================================

@dataclass
class RequestGridComparisonParameters(RequestGridGlobalParameters):

    # ---------- Comparison parameters ----------
    path_to_PDB_directory: str = "Grid_methods/data/input/structures_comparison/"
    path_to_output_directory: str = "Grid_methods/data/output/structures/"
    path_to_cleaned_directory: str = "Grid_methods/data/output/structures_comparison/cleaned_dataset/"

    consider_elements: str = "True"
    comparison_normalisation: str = "Max"
    grid_geometry: str = "Sphere"
    delete_grid: str = "True"

    save_parameters_files: str = "False"
    database: str = "False"

    dataset_status: str = "1"
    tmalign_reference: str = "None"

    tree: str = "structures"
    tree_name: str = "None"
    display_alignment: str = "False"            # don't modify this parameter
    node_name: str = "pdb"

    spheres_size: str = "5"
    sphere_color: str = "True"
    label_color: str = "True"
    show_distances: str = "True"
    line_width: str = "1"
    tree_scale: str = "80"

    save_structures_tree: str = "False"
    save_sequences_tree: str = "False"

    show_structures_tree: str = "False"         # don't modify this parameter
    show_sequences_tree: str = "False"          # don't modify this parameter

    save_newick_files: str = "True"

    tree_shape: str = "Linear"
    only_topology: str = "False"
    leaf_name: str = "True"
    branch_length: str = "True"

    # ---------- PDB ----------
    pdb1_name: str = ""
    pdb1_content: str = ""

    pdb2_name: str = ""
    pdb2_content: str = ""

    def toJson(self):

        global_parameters = {
            k: v
            for k, v in self.__dict__.items()
            if k
            in (
                "run_comparison",
                "run_hotspot",
                "explicit_grid",
                "atom_type",
                "grid_spacing",
                "grid_padding",
                "align_principal_axes",
                "pocket_res_name",
                "pocket_res_id",
                "lig_chain",
                "pocket_size",
                "discard_hetatm",
                "discard_atom",
                "discard_hydrogen",
                "discard_water",
                "discard_alternative",
                "keep_chains",
                "discard_chains",
                "keep_residues",
                "discard_residues",
                "keep_residue_ids",
                "discard_residue_ids",
                "keep_atoms",
                "discard_atoms",
                "cpu_allocated",
                "path_to_comparison_parameters",
                "path_to_hotspot_parameters",
                "watch_live",
                "create_pymol_session",
                "session_name",
            )
        }

        comparison_parameters = {
            k: v
            for k, v in self.__dict__.items()
            if k
            in (
                "path_to_PDB_directory",
                "path_to_output_directory",
                "path_to_cleaned_directory",
                "consider_elements",
                "comparison_normalisation",
                "grid_geometry",
                "delete_grid",
                "save_parameters_files",
                "database",
                "dataset_status",
                "tmalign_reference",
                "tree",
                "tree_name",
                "display_alignment",
                "node_name",
                "spheres_size",
                "sphere_color",
                "label_color",
                "show_distances",
                "line_width",
                "tree_scale",
                "save_structures_tree",
                "save_sequences_tree",
                "show_structures_tree",
                "show_sequences_tree",
                "save_newick_files",
                "tree_shape",
                "only_topology",
                "leaf_name",
                "branch_length",
            )
        }

        return json.dumps(
            {
                "params": {
                    "comparison_parameters": comparison_parameters,
                    "global_parameters": global_parameters,
                },
                "pdb1": {
                    "name": self.pdb1_name,
                    "content": self.pdb1_content
                },
                "pdb2": {
                    "name": self.pdb2_name,
                    "content": self.pdb2_content
                }
            },
            indent=4
        )


# ==========================================================
# Hotspot
# ==========================================================

@dataclass
class RequestGridHotspotParameters(RequestGridGlobalParameters):

    # ---------- Hotspot parameters ----------
    path_to_PDB_directory: str = "Grid_methods/data/input/hotspot_lig/"
    path_to_output_directory: str = "Grid_methods/data/output/hotspot/"

    grid_geometry: str = "Sphere"
    max_neighbor_number: str = "3"

    hotspot_type: str = "None"
    tag_threshold: str = "6"
    bad_score_threshold: str = "0.4"
    good_score_threshold: str = "0.6"
    number_of_rounds: str = "3"

    electronic_densities_folder: str = "Grid_methods/data/densities"
    normalize_electronic_densities: str = "False"

    # ---------- PDB ----------
    pdb_name: str = ""
    pdb_content: str = ""

    def toJson(self):

        global_parameters = {
            k: v
            for k, v in self.__dict__.items()
            if k
            in (
                "run_comparison",
                "run_hotspot",
                "explicit_grid",
                "atom_type",
                "grid_spacing",
                "grid_padding",
                "align_principal_axes",
                "pocket_res_name",
                "pocket_res_id",
                "lig_chain",
                "pocket_size",
                "discard_hetatm",
                "discard_atom",
                "discard_hydrogen",
                "discard_water",
                "discard_alternative",
                "keep_chains",
                "discard_chains",
                "keep_residues",
                "discard_residues",
                "keep_residue_ids",
                "discard_residue_ids",
                "keep_atoms",
                "discard_atoms",
                "cpu_allocated",
                "path_to_comparison_parameters",
                "path_to_hotspot_parameters",
                "watch_live",
                "create_pymol_session",
                "session_name",
            )
        }

        hotSpot_parameters = {
            k: v
            for k, v in self.__dict__.items()
            if k
            in (
                "path_to_PDB_directory",
                "path_to_output_directory",
                "grid_geometry",
                "max_neighbor_number",
                "hotspot_type",
                "tag_threshold",
                "bad_score_threshold",
                "good_score_threshold",
                "number_of_rounds",
                "electronic_densities_folder",
                "normalize_electronic_densities"
            )
        }

        return json.dumps(
            {
                "params": {
                    "hotspot_parameters": hotSpot_parameters,
                    "global_parameters": global_parameters,
                },
                "pdb": {
                    "name": self.pdb_name,
                    "content": self.pdb_content
                }
            },
            indent=4
        )