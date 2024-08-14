import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)
from pathlib import Path
path = Path(myDir)
a=str(path.parent.absolute())
sys.path.append(a)
import os.path
import random
import argparse
from CoWC.Experiments.dbquery import perform_query

#IMPORTANT: download the csv files for the UCI datasets from their site
def read_combine(line):
    line=line[1:-1]
    combines=[]
    while line.count("{")>0:
        beg=line.find("{")
        end=line.find("}")
        sub=line[beg+1:end]
        line=line[end+1:]
        combines.append({int(x) for x in sub.split(",")})
    return combines


def generate_random_query(name):
    csv_file="DS/Data/"+name+".csv"
    with open(csv_file) as f:
        columns=f.readline().split(",")[1:]
        data_size = len(list(f.readlines()))-1
    combine_file="DS/Data/"+name+".combines"
    with open(combine_file) as f:
        combines=read_combine(f.readline())
    queries=[]
    success_counter=1
    while success_counter<11:
        clauses=[]
        for x in range(1,random.randint(5,25)):
            clause=[]
            subs=random.sample(combines, random.randint(1,len(combines)))
            for combo in subs:
                subclause=random.sample(combo, random.randint(0,len(combo)))
                subclause=[(-1)**random.randint(1,2)*lit for lit in subclause]
                if len([x for x in subclause if x<0])<2:
                    if len([x for x in subclause if x < 0])==1:
                        clause+=[x for x in subclause if x < 0]
                    else:
                        clause+=subclause
            if len(clause)>0:
                clauses.append(clause)
        ids=perform_query(clauses,0, csv_file,columns, name, "id")
        if len(ids)>0.1*data_size and len(ids)<0.25*data_size:
            queries.append(clauses)
            success_counter+=1
            # print(0.1*data_size,"<",len(ids), "<", 0.25*data_size)
    return queries
def experiment(name, i):
    if not os.path.isfile("DS/Data/random_theories/" + name + "_" + str(i) + ".theories"):
        qs = generate_random_query(name)
        with open("DS/Data/random_theories/" + name + "_" + str(i) + ".theories", "w") as f:
            f.write(str(qs))
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name")
    parser.add_argument("--i")
    args = parser.parse_args()
    experiment(str(args.name), int(args.i))

  # # # #
if __name__ == "__main__":
    main()
