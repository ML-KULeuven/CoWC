
def theory2cnf(clauses, weights, num_literals, destination):
    num_clauses=len(clauses)
    if len(weights)>num_literals:
        for i in range(num_literals+1,int(len(weights)/2)+1):
            weights.pop(i)
            weights.pop(-i)
    with open(destination,"w") as f:
        f.write("p cnf "+str(num_literals)+" "+str(num_clauses)+"\n")
        f.write("c weights "+str(list(weights.values()))[1:-1].replace(",","")+"\n")
        clauses=list(clauses)
        for clause in clauses[:-1]:
            if len(clause)>0:
                f.write(str(sorted(list(clause),key=abs))[1:-1].replace(",","")+" 0\n")
        if len(clauses)>0:
            if len(clauses[-1])>0:
                f.write(str(sorted(list(clauses[-1]),key=abs))[1:-1].replace(",","")+" 0")
