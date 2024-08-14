import pycosat

def R_operator(frequent, residues):
    """
    Resolution operator, happens when the residues are unsatisfiable
    1 2 3 4
    1 2 -3
    1 2 -4
    -------->
    1 2
    :param frequent: The frequent itemset
    :param residues: List of the residues
    :return: resulting clauses
    """
    assert pycosat.solve(residues)=='UNSAT'
    return [frequent]

def R_possible(residues):
    return pycosat.solve(residues)=='UNSAT' and len(residues)>1