def V_operator(frequent, residues, definitions):
    """
   V- operator
   1 2 3
   1 2 4 5
   1 2 6 7
   ------->
   1 2 3
   -3 4 5
   -3 6 7

   :param frequent: a list of the frequent items
   :param residues: a list of the residues for each clause eg. [[3],[4,5],[6,7]]
   :return: a list of possible resulting clauses in case of multiple single-literal residues
   eg.
   1 2 3
   1 2 4 5
   1 2 6

   -------->
   1 2 3
   -3 4 5
   -3 6

   OR

    1 2 6
    -6 3
    -6 4 5
   """
    new_clauses=[]
    for res_id in range(0,len(residues)):
        if len(residues[res_id])==1 and -residues[res_id][0] not in definitions:
            chosen_lit=residues[res_id][0]
            new_clause=[]
            new_clause.append(frequent+residues[res_id])
            for other_res in residues[0:res_id]+residues[res_id+1:]:
                if chosen_lit in other_res:
                    new_clause.append(other_res)
                elif -chosen_lit in other_res:
                    rem_res=other_res.copy()
                    rem_res.remove(-chosen_lit)
                    new_clause.append(rem_res)
                else:
                    new_clause.append(other_res+[-chosen_lit])
            new_clauses.append(new_clause)
            
    #Here is the possibility to choose one of the different options
    return new_clauses
