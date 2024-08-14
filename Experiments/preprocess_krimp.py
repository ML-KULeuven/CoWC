import pandas as pd
import os
import ast
from DS.Experiments.dbquery import  perform_query
def pre_krimp(name, db):
    ####START###
    # print("START: ", mode,x_id, i_id,recall_tresh, db, combines_file)
    with open(db) as f:
        columns = f.readline().split(",")
    df = pd.read_csv(db)  # can also index sheet by name or fetch all sheets
    vals = df.values
    with open("DS/Data/random_theories/" + name + ".theories") as f:
        all_theories = ast.literal_eval(f.readline())
        negative_ids = []
        for theo_id in range(0, len(all_theories)):
            theory = all_theories[theo_id]
            # theo_ids = perform_query(theory, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id", negative=False)
            # print("Normal --> ", len(theo_ids))
            theo_ids = perform_query(theory, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id", negative=True)
            # print("Neg --> ",len(theo_ids))
            negative_ids.append(theo_ids)
    results=set(negative_ids.pop(0))
    while len(negative_ids)>0:
        results=results.intersection(set(negative_ids.pop(0)))


    negatives = [list(x[1:])+[1,0] for x in vals if x[0] in results]
    positives=[list(x[1:])+[0,1] for x in vals if x[0] not in results]

    db_string=""
    for x in negatives+positives:
        line=""
        for i in range(1,len(x)+1):
            if x[i-1]==1:
                line+=str(i)+" "
        db_string+=line[:-1]+"\n"
    with open("DS/Data/Krimp/"+name+".dat","w") as f:
        f.write(db_string[:-1])

for name in ["flare","hayesroth","ttt","votes","car"]:
    for id in range(1,10):
        print(name, id)
        pre_krimp(name+"_"+str(id), "DS/Data/"+name+".csv")
# for i in range(0,20):
#     for x in range(0,10):
#         print(i,x)
#         pre_krimp(str(i)+"_"+str(x),"DS/Data/fma.csv")






