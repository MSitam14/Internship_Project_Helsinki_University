import ete3
from Bio import AlignIO
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

import lib.global_parameters as gp


def tree_sequences():

    try :
        alignment = AlignIO.read(gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + "/output_muscle.fasta", "fasta")
        calculator = DistanceCalculator('identity')
        dm = calculator.get_distance(alignment)
        constructor = DistanceTreeConstructor()
        tree = constructor.nj(dm)
        Phylo.write(tree, gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + "/tree_sequences.nwk", "newick")
        tree = ete3.PhyloTree(tree.format("newick"), format=1)

    except:
        pass
    return tree