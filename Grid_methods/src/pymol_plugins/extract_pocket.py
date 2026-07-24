import numpy as np
from pymol import cmd


# finish_launching()
def extract_pocket(l_res_name, res_id = False, chain_id = False, pdb_id = False, with_ligand = True, size = 4.5):

    if size == False:
        size = 4.5
    flag = False
    for res_name in l_res_name.split():
        pocket_name = 'Pocket_'+ res_name + '_' + pdb_id if pdb_id else res_name

        # Initialize the selection string with the residue name
        selection = 'byres resn ' + res_name

        # Append res_id, chain_id, and pdb_id to the selection string if they are not empty
        if res_id != '':
            selection += ' and resi ' + str(res_id)
        if chain_id != '':
            selection += ' and chain ' + chain_id
        # Add the expand size to the selection string

        selection += ' and ' + pdb_id + ' expand ' + str(size) + ' and ' + pdb_id

        # Now use the selection string in the cmd.select function
        # check if pocket_name exists in the session
        if pocket_name in cmd.get_names():
            pocket_name = pocket_name + '_1'
        if cmd.select(pocket_name, selection):
            flag = True
        else:
            print('Residue', res_name, 'NOT found in the ' + pdb_id + ' structure')
            cmd.delete(pocket_name)
            continue
        cmd.enable(pdb_id)
        if not with_ligand:
            # cmd.remove('byres resn ' + res_name + res_id + chain_id + ' expand 0.5 ' + pdb_id + ' and ' + pocket_name)
            cmd.remove('resn ' + res_name + ' and ' + pocket_name)
        cmd.hide('cartoon', pocket_name)
        cmd.delete(pocket_name)
        cmd.create(pocket_name, selection)
        cmd.show('sticks', pocket_name)
        cmd.show('surface', pocket_name)
        cmd.set("transparency", 0.5, pocket_name)
        cmd.color(cmd.get_object_color_index(pdb_id), pocket_name)
        # cmd.group('pockets',pocket_name)
        mdl = pocket_name
        # get all the residues ID in the pocket

    # if fold_out:
    #     cmd.save(fold_out + 'Pocket_' + pocket_name + '.pdb', pocket_name)
    if not flag:
        return []
    l_res = []
    for i in cmd.get_model(mdl).atom:  # get all residues
        l_res.append(int(i.resi))
    l_res = np.sort(np.unique(l_res))

    return l_res

cmd.extend('extract_pocket', extract_pocket)

def extract_pocket_global(l_res_name, res_id = False, chain_id = False, pdb_id = False, with_ligand = True, size = 4.5):

    if size == False:
        size = 4.5
    flag = False
    # create super_ligand that is the selection of all ligands
    res_name = l_res_name.replace(' ', '+')
    if not 'super_ligand' in cmd.get_names():
        cmd.create('super_ligand', 'resn ' + res_name)
    pocket_name = 'Pocket_' + pdb_id if pdb_id else res_name

    # Initialize the selection string with the residue name
    selection = 'byres (' + pdb_id

    # Append res_id, chain_id, and pdb_id to the selection string if they are not empty
    if res_id != '':
        selection += ' and resi ' + str(res_id)
    if chain_id != '':
        selection += ' and chain ' + chain_id

    selection += ' within ' + str(size) + ' of super_ligand)'
    # Now use the selection string in the cmd.select function
    # check if pocket_name exists in the session
    if pocket_name in cmd.get_names():
        pocket_name = pocket_name + '_1'
    if cmd.select(pocket_name, selection):
        flag = True
    else:
        print('Residue', res_name, 'NOT found in the ' + pdb_id + ' structure')
        cmd.delete(pocket_name)
    cmd.enable(pdb_id)
    if not with_ligand:
        cmd.remove('resn ' + res_name + ' and ' + pocket_name)
    cmd.hide('cartoon', pocket_name)
    cmd.delete(pocket_name)
    cmd.create(pocket_name, selection)
    cmd.show('sticks', pocket_name)
    cmd.show('surface', pocket_name)
    cmd.set("transparency", 0.5, pocket_name)
    cmd.color(cmd.get_object_color_index(pdb_id), pocket_name)
    # cmd.group('pockets',pocket_name)
    mdl = pocket_name
    # get all the residues ID in the pocket

    # if fold_out:
    #     cmd.save(fold_out + 'Pocket_' + pocket_name + '.pdb', pocket_name)
    if not flag:
        return []
    l_res = []
    for i in cmd.get_model(mdl).atom:  # get all residues
        l_res.append(int(i.resi))
    l_res = np.sort(np.unique(l_res))

    return l_res

cmd.extend('extract_pocket_global', extract_pocket)