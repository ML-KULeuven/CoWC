def S_operator(frequent, residues):
    """
    Subsumption operator
    1 2 3
    1 2 5
    1 2
    ------->
    1 2
    :param frequent: the frequent itemset
    :param residues: a list of the residues (if no residue -> empty list) eg. [[3],[5],[]]
    :return: the resulting clauses
    """
    assert 0 in [len(x) for x in residues]
    return [frequent]

def S_possible(residues):
    return 0 in [len(x) for x in residues] and len(residues)>1
