import math
from copy import copy
from DS.Src.WMC.get_wmc import get_wmc


def W_possible(num_lit, clauses, Frequent, Residues, others, dl, new_operators):
    for i in new_operators:
        if i in Frequent or -i in Frequent:
            return False
    new_clauses = [frozenset(x) for x in list(others) + [Frequent + [num_lit + 1]] + [
        x + [-(num_lit + 1)] if isinstance(x, list) else [x, -(num_lit + 1)] for x in Residues]+[[-x,-(num_lit + 1)] for x in Frequent]]


    dl_diff= sum([len(x) for x in new_clauses])-sum([len(x) for x in clauses])
    # print("W DL diff: ", dl_diff)
    return len(Frequent)>1 and dl_diff<0

def joint_prob(x):
    return 1-math.prod([1-z for z in x])

def W_operator(frequent, residues, weights):
    """
    Inter construction operator
    1 2 3
    1 2 4
    1 2 5 6
    ------->
    1 2 7
    -1 -7
    -2 -7
    3 -7
    4 -7
    5 6 -7

    p(7) = (WMC(T) - WMC(frequent)) / (WMC(Residues) - WMC(Frequent))


    :param frequent: a list of the frequent items
    :param residues: a list of the residues for each clause eg. [[3],[4],[5,6]]
    :param weights: a dictionary of the weights of the literals
    :return: the resulting clauses and a new weights dictionary
    """
    # print("W",frequent,residues, weights)
    max_literal = max(weights)
    weights[max_literal+1]=1
    weights[-(max_literal+1)]=1
    return [frequent + [max_literal+1]] +[x+[-(max_literal+1)] if isinstance(x,list) else [x,-(max_literal+1)] for x in residues]+[[-x,-(max_literal+1)] for x in frequent], weights, max_literal+1


def find_new_prob(frequent,others, residue,weights,new_literal):
    original_wmc=get_wmc(others+[frozenset(frequent + x) for x in residue],weights,abs(new_literal)-1)
    res = get_wmc(others+[frozenset(x) for x in residue], weights, abs(new_literal) - 1)
    freq = get_wmc(others + [frozenset(frequent)], weights, abs(new_literal) - 1)
    try:
        new_weight=(original_wmc-freq)/(res-freq)
        return new_weight
    except:
        return False
