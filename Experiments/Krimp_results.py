import os
import pandas as pd
import ast
from dbquery import perform_query
def krimp_result(name, db):
    if not os.path.isfile("DS/Results/Krimp/theories/"+name+"/"+name+".result"):
        ####START###
        # print("START: ", mode,x_id, i_id,recall_tresh, db, combines_file)
        with open(db) as f:
            columns = f.readline().split(",")
        print("Ground")
        with open("DS/Data/federated_theories/" + name + ".theories") as f:
            all_theories = ast.literal_eval(f.readline())
            ground = []
            for theo_id in range(0, len(all_theories)):
                theory = all_theories[theo_id]
                theo_ids = perform_query(theory, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id", negative=False)
                # print("Neg --> ",len(theo_ids))
                ground.append(theo_ids)
        results=set(ground.pop(0))
        while len(ground)>0:
            results=results.union(set(ground.pop(0)))
        ground=set(results)
        print("--> ", len(ground))
        theories=[]
        for file in os.listdir("DS/Results/Krimp/theories/"+name):
            with open("DS/Results/Krimp/theories/"+name+"/"+file,"r") as f:
                line=f.readlines()[0]
            theories.append(ast.literal_eval(line))
        results=[]
        todo=[x for x in theories if len(x)>0]
        for theory_id in range(0,len(todo)):
            print(theory_id,"/",len(todo))
            theory=todo[theory_id]
            print(theory)
            result=[]
            result.append(sum([len(x) for x in theory]))
            ids=set(perform_query(theory, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id", negative=False))
            TP=len(ids.intersection(ground))
            FP=len(ids-ground)
            FN=len(ground-ids)
            result.append(2*TP/(2*TP+FN+FP))
            result.append([TP,FP,FN])
            results.append(result)
        with open("DS/Results/Krimp/theories/"+name+"/"+name+".result","w") as f:
            f.write(str(results))

# for i in range(0,20):
#     for x in range(0,10):
#         print("------",i,x)
#         krimp_result(str(i)+"_"+str(x), "DS/Data/fma.csv")
for name in ["votes",'car',"ttt","flare","hayesroth"]:
    for i in range(1,10):
        print(name,i)
        krimp_result(name+"_"+str(i),"DS/Data/"+name+".csv")
