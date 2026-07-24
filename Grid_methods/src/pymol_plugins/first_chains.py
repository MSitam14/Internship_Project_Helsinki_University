#!/usr/bin/env python3

#This program is a modification of a Pymol function program (split_chains.py) that splits a PDB file into multiple PDB files, one for each chain.
#There we want to generate only the first chain, to avoid any copy of the same protein in the dataset.

import pymol
def first_chains(selection='(all)', prefix=None):
    '''
DESCRIPTION

    Create a single object for each chain in selection

SEE ALSO

    split_states, http://pymolwiki.org/index.php/Split_object
    '''
    count = 0
    models = pymol.cmd.get_object_list('(' + selection + ')')
    chains_list =[]
    for model in models: #for each protein
        for chain in pymol.cmd.get_chains('(%s) and model %s' % (selection, model)): #for each chain of the protein
            if chain == '':
                chain = "''"
            count += 1
            if not prefix:
                name = '%s_%s' % (model, chain)
            else:
                name = '%s%04d' % (prefix, count)
            chains_list.append(name)
        #trouver l'id de la chaine la plus longue
        chain_length = []
        for chain in pymol.cmd.get_chains('(%s) and model %s' % (selection, model)):
            chain_length.append(len(pymol.cmd.get_fastastr('(%s) and model %s and chain %s' % (selection, model, chain))))
        longest_chain = chain_length.index(max(chain_length))
        chain = pymol.cmd.get_chains('(%s) and model %s' % (selection, model))[longest_chain]
        pymol.cmd.create(name, '(%s) and model %s and chain %s' % (selection, model, chain)) #create a new object with the chain
        pymol.cmd.delete(model) #delete the original object

pymol.cmd.extend('first_chains', first_chains)
