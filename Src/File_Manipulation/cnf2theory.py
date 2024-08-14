def cnf2theory(file):
    with open(file,"r") as open_file:
        lines=open_file.readlines()
        clauses=[]
        weights={}
        num_variables=0
        for line in [l for l in lines if len(l.strip())>0]:
            line=line.strip()
            if line.startswith("p cnf"):
                splitted=[x for x in line.split(" ") if x!=" "]
                num_variables=int(splitted[2])
            elif line.startswith("c weights"):
                splitted = [float(w) for w in [x for x in line.split(" ") if x != " "][2:]]
                for lit in range(0,num_variables):
                    weights[lit+1]=splitted[2*lit]
                    weights[-(lit+1)]=splitted[2*lit+1]
            elif not line.startswith("c"):
                clauses.append(
                    frozenset([int(x) for x in line.replace("\t"," ").split(" ") if x!=""][:-1] ))
    return set(clauses),weights, num_variables
