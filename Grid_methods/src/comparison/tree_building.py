from Bio import SeqIO
from ete3 import Tree, SeqMotifFace, TextFace, TreeStyle, NodeStyle

from lib import global_parameters as gp


def read_multiple_alignement():
    sequences = {}
    try :
        for record in SeqIO.parse(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/output_muscle.fasta', "fasta"):
            sequences[record.id] = str(record.seq)
    except FileNotFoundError:
        pass
    return sequences


# create function that returns a face for mathc
def match_face(seq_start,seq_end):
    return [seq_start,seq_end, "()", None, 10, "lightblue", "lightblue", None]
def over80_face(seq_start,seq_end):
    return [seq_start,seq_end, "()", None, 15, "darkgreen", "darkgreen", None]
def over50_face(seq_start,seq_end):
    return [seq_start,seq_end, "()", None, 10, "yellowgreen", "yellowgreen", None]
def under50_face(seq_start,seq_end):
    return [seq_start,seq_end, "()", None, 5, "darkred", "darkred", None]
def gap_face(seq_start,seq_end):
    return [seq_start,seq_end, "line", None, 30, "black", "black", None]

def get_motifs(dict_seq):
    list_seq = []
    list_pdbs = []
    d_match = {}
    for k,v in dict_seq.items():
        list_seq.append(v)
        list_pdbs.append(k)
    pos = 0
    l = 0
    l_match = []
    d_motifs = {}
    for i in zip(*list_seq):
        pos += 1
        count = {}
        for j in i:
            if j in count:
                count[j] += 1
            else:
                count[j] = 1
        l_i = len(i)
        d_match[pos] = {i: count / l_i for i, count in count.items()}


    for seq in list_seq:
        motifs = []
        pdb_id = list_pdbs[l]
        l += 1
        flag = -1
        for j in range(len(seq)):
            freq = d_match[j + 1][seq[j]]
            if seq[j] == '-':
                if flag == 0:
                    continue
                if flag == 1:
                    motifs.append(over80_face(ind_08_start, j-1))
                elif flag == 2:
                    motifs.append(over50_face(ind_05_start, j-1))
                elif flag == 3:
                    motifs.append(under50_face(ind_unmatch_start, j-1))
                flag = 0
                ind_gap_start = j
            elif freq > 0.8:
                if flag == 1:
                    continue
                elif flag == 0:
                    motifs.append(gap_face(ind_gap_start,j-1))
                elif flag == 2:
                    motifs.append(over50_face(ind_05_start,j-1))
                elif flag == 3:
                    motifs.append(under50_face(ind_unmatch_start,j-1))
                ind_08_start = j
                flag = 1
            elif freq > 0.5:
                if flag == 2:
                    continue
                elif flag == 0:
                    motifs.append(gap_face(ind_gap_start, j-1))
                elif flag == 1:
                    motifs.append(over80_face(ind_08_start,j-1))
                elif flag == 3:
                    motifs.append(under50_face(ind_unmatch_start,j-1))
                flag = 2
                ind_05_start = j
            else:
                if flag == 3:
                    continue
                elif flag == 0:
                    motifs.append(gap_face(ind_gap_start, j-1))
                elif flag == 1:
                    motifs.append(over80_face(ind_08_start,j-1))
                elif flag == 2:
                    motifs.append(over50_face(ind_05_start,j-1))
                flag = 3
                ind_unmatch_start = j
        if flag == 0:
            motifs.append(gap_face(ind_gap_start,j))
        elif flag == 1:
            motifs.append(over80_face(ind_08_start,j))
        elif flag == 2:
            motifs.append(over50_face(ind_05_start,j))
        elif flag == 3:
            motifs.append(under50_face(ind_unmatch_start,j))
        d_motifs[pdb_id] = {"motifs":motifs,"seq":seq}

    return d_motifs


def create_tree_style( d_parameters, scale_factor=1):
    ts = TreeStyle()
    ts.show_leaf_name = False
    ts.scale_length = 0.1
    ts.force_topology = False
    ts.scale = d_parameters['tree_scale']

    if d_parameters['show_distances']:
        ts.show_branch_length = True
    else:
        ts.show_branch_length = False

    if d_parameters['tree_shape'] == 'Circular':
        ts.mode = "c"

    elif d_parameters['tree_shape'] == 'Semicircular':
        ts.mode = "c"
        ts.arc_start = -179
        ts.arc_span = 180


    elif d_parameters['tree_shape'] == 'Linear':
        ts.mode = "r"

    return ts

def plot_tree(d_parameters, t1, t2, scale_factor=1):
    if d_parameters["display_alignment"] == True:
        try:
            sequences = read_multiple_alignement()
            seq_motif = get_motifs(sequences)
        except:
            print("Error in the multiple alignement")

    try:
        if d_parameters["tree"] == 'both':
            t1 = Tree(t1.write())
            t2 = Tree(t2.write())
        elif d_parameters["tree"] == 'structures':
            t1 = Tree(t1.write())
        elif d_parameters["tree"] == 'sequences':
            t2 = Tree(t2.write())
    except:
        pass

    # t = Tree("( (A, B, C, D, E, F, G), H, I);")
    #t = Tree("(((5t04_neurotensin_aligned_super_4s0v:0.31949,5wqc_orexin_aligned_super_4s0v:0.28828)1:0.03607,(6k1q_endothelin_aligned_super_4s0v:0.22776,5x93_endothelin_aligned_super_4s0v:0.2265)1:0.05497)1:0.0344,6lry_endothelin_aligned_super_4s0v:0.28618,5glh_endothelin_aligned_super_4s0v:0.2131);")
    D_leaf_color = {"ADRB2_HU_i": "#7CFC00",
                    "EDNRB_HU_i":"yellowgreen",
                    "HCRTR2_HU_a": "olivedrab",
                    "HCRTR1_HU_i": "darkseagreen",
                    "HCRTR2_HU_i": "springgreen",
                    "ADRB1_HU_a": "darkolivegreen",
                    "ADRA2C_HU_i": "mediumseagreen",
                    "ADRB1_MG_a": "mediumseagreen",
                    "ADRB1_MG_u": "mediumseagreen",
                    "ADRB1_HU_i": "mediumseagreen",
                    "DRD2_HU_i": "mediumseagreen",
                    "OPRM_HU_u": "mediumseagreen",
                    "-B-": "blue",
                    "-C-": "purple",
                    "-F-": "red"}
    D_leaf_color = {
        "ADRB2_HU_i": "#FF4500",  # OrangeRed (distinct for ADRB2)
        "EDNRB_HU_i": "#DAA520",  # GoldenRod (darker gold for EDNRB)
        "HCRTR2_HU_a": "#1E90FF",  # DodgerBlue (bright blue for HCRTR2 active)
        "HCRTR1_HU_i": "#32CD32",  # LimeGreen (bright green for HCRTR1)
        "HCRTR2_HU_i": "#4682B4",  # SteelBlue (muted blue for HCRTR2 inactive)
        "ADRB1_HU_a": "#800080",  # Purple (bright purple for ADRB1 active)
        "ADRA2C_HU_i": "#A0522D",  # Sienna (muted brown-red for ADRA2C)
        "ADRB1_MG_a": "#E9967A",  # DarkSalmon (soft red for ADRB1 in mouse active)
        "ADRB1_MG_u": "#B22222",  # FireBrick (strong red for ADRB1 in mouse unknown)
        "ADRB1_HU_i": "#9370DB",  # MediumPurple (lighter purple for ADRB1 inactive)
        "DRD2_HU_i": "#5F9EA0",  # CadetBlue (muted teal for DRD2, replacing BlueViolet)
        "OPRM_HU_u": "#008B8B",  # DarkCyan (cyan for OPRM, distinct from others)
    }
    D_leaf_color = {
        "ADRB2_HU_i": "#1E90FF",  # DodgerBlue (distinct blue for ADRB2)
        "EDNRB_HU_i": "#DAA520",  # GoldenRod (unchanged)
        "HCRTR2_HU_a": "#800080",  # OrangeRed (bright orange-red for HCRTR2 active)
        "HCRTR1_HU_i": "#9370DB",  # HotPink (soft pink for HCRTR1 inactive)
        "HCRTR2_HU_i": "#E192BF",  # Pink (light pink for HCRTR2 inactive/5WQC)
        "ADRB1_HU_a": "#32CD32",  # LimeGreen (bright green for ADRB1 active)
        "ADRA2C_HU_i": "#A0522D",  # Sienna (unchanged, muted brown-red for ADRA2C)
        "ADRB1_MG_a": "#4682B4",  # SteelBlue (soft blue for ADRB1 in mouse active)
        "ADRB1_MG_u": "#5F9EA0",  # CadetBlue (muted teal for ADRB1 in mouse unknown)
        "ADRB1_HU_i": "#2b8522",  # DodgerBlue (distinct blue for ADRB1 inactive)
        "DRD2_HU_i": "#008B8B",  # DarkCyan (cyan for DRD2, distinct from others)
        "OPRM_HU_u": "#B22222",  # FireBrick (dark red for OPRM, distinct and bold)
    }
    D_leaf_color = {
        "HCRTR2": "#d184b0",  # DodgerBlue
        "HCRTR1": "#800080",  # Purple
        "ADRB1": "#264DFF",  # Purple
        "ADRB2": "#3FA0FF",  # OrangeRed
        "ADRA2C": "#1E8E99",  # Sienna
        "DRD2": "#009959",  # CadetBlue
        "EDNRB": "#888888",  # GoldenRod
        "OPRM": "#000000",  # DarkCyan
    }

    # D_leaf_color = {
    #     #blue for adrenoreceptor
    #     "ADR": "#1277b5",
    #     # Green for orexin
    #     "HCRT": "#2b8522",
    # }
    # D_leaf_color = {
    #     "7MA": "#FF4500",  # OrangeRed (distinct for ADRB2)
    #     "NRZ": "#DAA520",  # GoldenRod (darker gold for EDNRB)
    #     "7V7": "#1E90FF",  # DodgerBlue (bright blue for HCRTR2 active)
    #     "CVD": "#32CD32",  # LimeGreen (bright green for HCRTR1)
    #     "E5E": "#4682B4",  # SteelBlue (muted blue for HCRTR2 inactive)
    #     "5FW": "#800080",  # Purple (bright purple for ADRB1 active)
    #     "E33": "#A0522D",  # Sienna (muted brown-red for ADRA2C)
    #     "CAU": "#E9967A",  # DarkSalmon (soft red for ADRB1 in mouse active)
    #     "8NU": "#B22222",  # FireBrick (strong red for ADRB1 in mouse unknown)
    #     "A6F": "#9370DB",  # MediumPurple (lighter purple for ADRB1 inactive)
    #     "SUV": "#5F9EA0",  # CadetBlue (muted teal for DRD2, replacing BlueViolet)
    #     "4OT": "#008B8B",  # DarkCyan (cyan for OPRM, distinct from others)
    #     'XGD': "#FF4500",
    #     'D2D': "#DAA520",
    # }
    if d_parameters['tree'] == 'structures' or d_parameters['tree'] == 'both':
        for node in t1.traverse():
            # Hide node circles
            node.img_style['size'] = 0
            if node.dist:
                node.dist = round(node.dist, 2)
            nstyle = NodeStyle()
            nstyle["vt_line_width"] = d_parameters['line_width']
            nstyle["hz_line_width"] = d_parameters['line_width']
            if node.is_leaf():
                try :
                    color = [val for key, val in D_leaf_color.items() if key in node.name][0]
                except:
                    color = 'black'
                if d_parameters['display_alignment'] == True:
                    motif, seq = [(val['motifs'], val['seq']) for key, val in seq_motif.items() if key in node.name][0]
                # color = D_leaf_color.get(node.name, None)
                # color = D_leaf_color.get(node.name, None)
                if d_parameters['node_name'] == 'pdb':
                    node.name = node.name.split('_')[0]
                elif d_parameters['node_name'] == 'ligand':
                    node.name = node.name.split('_')[0] + '_' + node.name.split('_')[4]
                elif d_parameters['node_name'] == 'protein':
                    node.name = "_".join(node.name.split('_')[1:4])
                elif d_parameters['node_name'] == 'pdb_protein':
                    node.name = "_".join(node.name.split('_')[0:4])
                elif d_parameters['node_name'] == 'pdb_organism':
                    node.name = node.name.split('_')[0] +'_' + "_".join(node.name.split('_')[2:4])
                if d_parameters['label_color'] == True and d_parameters['leaf_name'] == True:
                    name_face = TextFace(' ' + node.name + ' ', fgcolor=color, fsize=0.001 * scale_factor)
                    node.add_face(name_face, column=2, position='branch-right')
                else:
                    name_face = TextFace(' ' + node.name + ' ', fgcolor='black', fsize=0.001 * scale_factor)
                    node.add_face(name_face, column=2, position='branch-right')
                # if color:
                #     if d_parameters['leaf_name'] == True:
                #         name_face = TextFace(' ' + node.name + ' ', fgcolor=color, fsize=0.001*scale_factor)
                #         node.add_face(name_face, column=2, position='branch-right')
                    # seqFace = SeqMotifFace(seq, seq_format="compactseq", height=10, scale_factor=0.5)
                    # seqFace = SeqMotifFace(seq, seq_format="()", height=10, scale_factor=0.5, fgcolor=color, bgcolor=color)
                if d_parameters['display_alignment'] == True:
                    seqFace = SeqMotifFace(seq, motifs=motif)
                    node.add_face(seqFace, column=1, position='aligned')
                    # node.add_face(image, column=2, position='aligned')
                nstyle["shape"] = "sphere"
                if d_parameters['sphere_color'] == True:
                    nstyle["fgcolor"] = color
                else:

                    nstyle["fgcolor"] = "black"
                    # nstyle["hz_line_color"] = color
                    # nstyle["vt_line_color"] = color
                    # nstyle["size"] = d_parameters['spheres_size']
                nstyle["size"] = d_parameters['spheres_size']
                nstyle["hz_line_type"] = 0  # 0 solid, 1 dashed, 2 dotted
                    # nstyle["bgcolor"] = color
            node.set_style(nstyle)

    if d_parameters['tree'] == 'sequences' or d_parameters['tree'] == 'both':
        for node in t2.traverse():
            # Hide node circles
            node.img_style['size'] = 0
            if node.is_leaf():
                try:
                    color = [val for key, val in D_leaf_color.items() if key in node.name][0]
                except:
                    color = 'black'
                if d_parameters['display_alignment'] == True:
                    motif, seq = [(val['motifs'], val['seq']) for key, val in seq_motif.items() if key in node.name][0]
                # color = D_leaf_color.get(node.name, None)
                # color = D_leaf_color.get(node.name, None)

                if color:
                    if d_parameters['leaf_name'] == True:
                        name_face = TextFace(node.name, fgcolor=color, fsize=12)
                        node.add_face(name_face, column=2, position='branch-right')
                    # seqFace = SeqMotifFace(seq, seq_format="compactseq", height=10, scale_factor=0.5)
                    # seqFace = SeqMotifFace(seq, seq_format="()", height=10, scale_factor=0.5, fgcolor=color, bgcolor=color)
                    if d_parameters['display_alignment'] == True:
                        seqFace = SeqMotifFace(seq, motifs=motif)
                        node.add_face(seqFace, column=1, position='aligned')
                    # node.add_face(image, column=2, position='aligned')
                    nstyle = NodeStyle()
                    nstyle["shape"] = "sphere"
                    nstyle["fgcolor"] = color
                    nstyle["hz_line_color"] = color
                    nstyle["vt_line_color"] = color
                    nstyle["size"] = d_parameters['spheres_size']
                    nstyle["vt_line_width"] = 2
                    nstyle["hz_line_width"] = 5
                    nstyle["hz_line_type"] = 0  # 0 solid, 1 dashed, 2 dotted
                    # nstyle["bgcolor"] = color
                    node.set_style(nstyle)

    ts = create_tree_style(d_parameters)
    # Add legend to the tree style
### Save structures tree output ###

    if (d_parameters['tree'] == 'structures' or d_parameters['tree'] == 'both') and d_parameters['save_structures_tree'] == True :
        f_tree_out = d_parameters['p_output_comparison'] + '/' + d_parameters['tree_shape'] + '_tree_' +  gp.D_PARAMETERS_GLOBAL['atom_type'].lower() + '_structures.svg'
        t1.render(f_tree_out, tree_style=ts, dpi=2000)

    if (d_parameters['tree'] == 'sequences' or d_parameters['tree'] == 'both') and d_parameters['save_sequences_tree'] == True:
        f_seq_tree_out = d_parameters['p_output_comparison'] + '/' + d_parameters['tree_shape'] + '_tree_' + gp.D_PARAMETERS_GLOBAL['atom_type'].lower() + '_sequences.svg'
        t2.render(f_seq_tree_out, tree_style=ts, dpi=2000)

### Show structures tree output ###
    if (d_parameters['tree'] == 'structures' or d_parameters['tree'] == 'both') and d_parameters['show_structures_tree'] == True :
        t1.show(tree_style=ts)
    if (d_parameters['tree'] == 'sequences' or d_parameters['tree'] == 'both') and d_parameters['show_sequences_tree'] == True :
        t2.show(tree_style=ts)
    return t1, t2



