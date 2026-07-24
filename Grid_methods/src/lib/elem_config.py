
# Residue type
RES = ['ALA', 'ILE', 'LEU', 'VAL', 'MET', 'CYS', 'PHE', 'TRP', 'TYR', 'HIS', 'THR', 'SER', 'ASN', 'GLN', 'ASP',
       'GLU', 'ARG', 'LYS', 'PRO', 'GLY']
WATER = ['HOH']

# New Definition of Atom types:
# Atom grouped in the highest level
GROUP = ['Mc', 'Sc', 'Met', 'Lgd', 'Ow']

# Oxygen in carbonyl
OC = {'O': 'O', 'ASN': 'OD1', 'GLN': 'OE1'}
# Nitrogen in amide
NAM = {'N': 'N', 'ASN': 'ND2', 'GLN': 'NE2', 'TRP': 'NE1'}
# Oxygen in carboxylate and oxygen in C-terminal
ORES = ['GLU', 'ASP']
OOX = {'GLU': ['OE1', 'OE2'], 'ASP': ['OD1', 'OD2'], 'OXT': 'OXT'}
OHRES = ['THR', 'SER', 'TYR']
# Oxygen in hydroxyl or phenol
OHY = {'THR': 'OG1', 'SER': 'OG', 'TYR': 'OH'}
# Nitrogen in Lysine
NLYS = {'LYS': 'NZ'}
# Nitrogen in Arginine
NARG = {'ARG': ['NH1', 'NH2', 'NE']}
# Carbon SP2 in aromatic ring
CAR = {'PHE': ['CG', 'CD1', 'CE2', 'CZ', 'CE1', 'CD2'], 'TYR': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
       'TRP': ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CE3', 'CZ3', 'CH2', 'CZ2'], 'HIS': ['CG', 'CD2', 'CE1']}
# Central carbon from ARG, GLN, GLU, ASP, ASN
CRES = ['ARG', 'GLN', 'GLU', 'ASP', 'ASN']
CE = {'ARG': 'CZ', 'GLN': 'CD', 'GLU': 'CD', 'ASP': 'CG', 'ASN': 'CG'}
# XOt
# Xot= {'VAL':'', ''}

# Nitrogen in Histidine
NHIS = {'HIS': ['NE2', 'ND1']}
# Metal
METAL = ['LI', 'BE', 'NA', 'MG', 'AL', 'K', 'CA', 'SC', 'TI', 'V', 'CR', 'MN',
         'FE', 'CO', 'NI', 'CU', 'ZN', 'GA', 'GE', 'RB', 'SR', 'Y', 'ZR', 'NB',
         'MO', 'TC', 'RU', 'RH', 'PD', 'AG', 'CD', 'IN', 'SN', 'SB', 'CS', 'BA',
         'LA', 'HF', 'TA', 'W', 'RE', 'OS', 'IR', 'PT', 'AU', 'HG', 'TL', 'PB',
         'BI', 'PO', 'FR', 'RA', 'AC', 'RF', 'DB', 'SG', 'CE', 'PR', 'ND', 'PM',
         'SM', 'EU', 'GD', 'TB', 'DY', 'HO', 'ER', 'TM', 'YB', 'LU', 'TH', 'PA',
         'U', 'NP', 'PU', 'AM', 'CM', 'BK', 'CF', 'ES', 'FM', 'MD', 'NO', 'LR']
# Halogenx
# HALO = ['F', 'CL', 'BR', 'I']

#  Ligand
LGD = ['O', 'C', 'N', 'S', 'B', 'F']
# Water
OW = {'HOH': 'O'}

#####################
# Functional groups #
#####################
# alcholic oH group in serine and threonine
# phenolic OH groups in tyrosine
# SH group in cysteine and methionine
# Narg group in Arginine
# Nhis group in His
# COO groups in asparatic and glutamic acids
# NH2 groups in lysine
# CONH2 groups in asparagine and glutamine
# NH3+ N-terminus
# ONH ---peptide
# OXT
# Functional group -> all atom in functional group should be present
#####################################################################
FUNCTIONALGROUP = ['GUI', 'IMD', 'I', 'COO_ASP', 'COO', 'OH', 'CONH2', 'SH', 'TRP_RING', 'TRP_N', 'PHENOL', 'PHE']

# A) Amino acids elecrically charged side chains
# I) Positive charged
# Arginine(ARG-R) - guanidinium group

GUI = ['CD', 'NE', 'CZ', 'NH1', 'NH2']

# Histidine(His-H) -imidazole functional group

IMD = ['CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2']

# Lysine(Lys-L) -amino group (a primary amine)

I = ['CE', 'NZ']

#################################################
# II) negatively charged
#
#################################################
# Asparatic Acid (ASP-D) ---Carboxylate functional group

COO_ASP = ['CG', 'OD1', 'OD2']

# Glutamic Acid (GLU-E)

COO_GLU = ['CD', 'OE1', 'OE2']

# B) Amino acids with polar uncharged side chains
###################################################
# Serine
OH_SER = ['CB', 'OG']

# Threonine
OH_THR = ['CB', 'OG1']
# Asparagine -AMIDE GROUP
CONH2_ASN = ['CG', 'OD1', 'ND2']
# Glutamine -AMIDE GROUP
CONH2_GLN = ['CD', 'OE1', 'NE2']

# C Special cases
# Cystene  - SH group
SH_CYS = ['CB', 'S']

# Selenocystine
# Glycine
# Proline
# D Amino acids with hydrophobic side chains

# Alanine
# Valine
# isoleucine
# Leucine
# Methionine
SH = ['CG', 'SD', 'CE']
# Phenylalanine
PHE = ['CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CEZ']
# Tyrosine
HYDORXYL = ['CZ', 'OH']  # HYDROXYL
PHENOL = ['CB', 'CG', 'CD1', 'CE1', 'CE2', 'CZ', 'OH']

# Tryptophan
TRP_RING = ['CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2']
TRP_N = ['CD2', 'NE1', 'CE2']

# Main chain

NH3 = ['N', 'CA']
peptide = ['C', 'O', 'N']
CO = ['C', 'O']
OXT = ['C', 'O', 'OXT']
