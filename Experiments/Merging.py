import json
import math
import itertools
import os.path
import random
from copy import deepcopy
import numpy as np
from DS.Experiments.dbquery import  perform_query
from DS.Src.Main.Prob_Mistle import Prob_Mistle
from DS.Src.File_Manipulation.theory2cnf import theory2cnf
import sqlite3
from tqdm import tqdm
def postprocess(c, combines):

    singles=[list(x)[0] for x in c if len(x)==1]
    buckets=[[] for _ in range(0,len(combines))]
    for element in singles:
        for combo in range(0,len(combines)):
            if abs(element) in combines[combo]:
                buckets[combo].append(element)
    result_buckets=[]
    for combo in range(0,len(combines)):
        if len(buckets[combo])>0:
            if len([x for x in buckets[combo] if x>0])==1:
                result_buckets.append([x for x in buckets[combo] if x>0])
            else:
                res=[]
                for element in combines[combo]:
                    if -element not in buckets[combo]:
                        res.append(element)
                result_buckets.append(res)
    final_clauses=[]
    all_clauses=[x for x in c if len(x)>1]+[x for x in result_buckets]

    # print("ALL:",len(all_clauses), "vs", len([x for x in all_clauses if len(x)>1]))
    for clause_id in tqdm(range(0,len(all_clauses))):
        issuper = False
        for other_id in range(0, len(all_clauses)):
            # print(all_clauses[clause_id])
            if set(all_clauses[other_id]).issubset(set(all_clauses[clause_id])) and  len(all_clauses[other_id])!=len(all_clauses[clause_id]):
                issuper=True
                break;
        if not issuper and all_clauses[clause_id] not in final_clauses:
            final_clauses.append(all_clauses[clause_id])
    final_clauses=[x for x in final_clauses if len(x)>1 or x[0]>0]
    result=list(set([frozenset(x) for x in final_clauses]))
    return result

def find_best(list, indices=[]):
    max_score = math.inf
    max_result = []
    if len(list) == 0:
        return 0, []
    if len(list)==1:
        return list[0][1], [list[0][0]]
    for element in list:
        new_list = [x for x in list if len(set(x[0]).intersection(set(element[0]))) == 0]
        # print("Result: ", find_best(new_list, False))
        new_score, result = find_best(new_list)
        if element[1] + new_score < max_score:
            max_score = new_score + element[1]
            max_result = [element[0]] + result

    for i in indices:
        present=False
        for x in max_result:
            if i in x:
                present=True
                break;
        if not present:
            max_result.append((i,))
    return max_score, max_result

import math

import pandas as pd

def merge_theories(theories, combines):
    a=theories[0]
    b=theories[1]
    print("Input Theory size: ", len(a), len(b), len(a)*len(b))
    new=[]
    for x in a:
        for y in b:
            final_clause=[]
            to_add=True
            new_clause=set(list(x)+list(y))
            inter_count=0
            for combo in combines:
                inter={abs(x) for x in new_clause}.intersection(combo)
                inter_count+=len(inter)
                if len(inter)>0:
                    lits=[x for x in new_clause if abs(x) in combo]
                    neg_lits=[x for x in lits if x<0]
                    if len(neg_lits)>1:
                        to_add=False
                        break;
                    elif len(neg_lits)==1:
                        final_clause+=neg_lits
                    else:
                        final_clause+=lits

            if to_add and inter_count==len(new_clause):
                new.append(final_clause)
    print("Theory size: ",len(new))
    return new
def idstoweights(ids, vals, id=False, tunify=False):

    if id:
        if tunify:
            positives=[x[3:] for x in vals if x[0] in ids]
        else:
            positives = [x[1:] for x in vals if x[0] in ids]

        final_ids=ids
        # print("IDS2WEIGHTS: ", len(ids), len(positives))
    else:
        positives = [vals[x][3:] for x in ids]
        final_ids=[vals[x][0] for x in ids]
    new_pos = []
    for x in positives:
        new_pos += [[y if x[y - 1] == 1 else -y for y in range(1, len(x) + 1)]]
    positives = new_pos
    weights = [[0, 0] for x in range(0, len(positives[0]))]
    for i in positives:
        for ele in i:
            weights[abs(ele) - 1][ele < 0] += 1
    weights=[[x[0]/sum(x), x[1]/sum(x)] for x in weights]
    return weights, positives, final_ids

import ast


####START###

#NOTE: for the correct DB, download the csv files at the source
# FMA: https://github.com/mdeff/fma
#
# Congressional voting: https://archive.ics.uci.edu/dataset/105/congressional+voting+records
# 
# Car evaluation :https://archive.ics.uci.edu/dataset/19/car+evaluation
#
# Soybean:https://archive.ics.uci.edu/dataset/90/soybean+large
#
# Tic-tac-toe: https://archive.ics.uci.edu/dataset/101/tic+tac+toe+endgame
#
# Hayes-roth:https://archive.ics.uci.edu/dataset/44/hayes+roth
db="../Data/music_playlists/fma.csv"
combines_file= "../Data/fma.combines"
temp_file="../Temp/todo.cnf"
with open(db) as f:
    columns = f.readline().split(",")
df = pd.read_csv(db) # can also index sheet by name or fetch all sheets
vals=df.values
extra="_unweighted"
with open(combines_file) as f:
    combines=ast.literal_eval(f.readline())
for x_id in range(0,10):
    for i_id in range(0,20):
        name=str(i_id)+"_"+str(x_id)
        exists=os.path.isfile("../Results/" + name + extra+".json")
        if exists:
            with open("../Results/" + name +extra+ ".json") as f:
                results=json.load(f)
        else:
            results={}
        if (not exists) or (exists and len(results)<10):
            for recall_tresh in [float(y) for y in ["0.8","0.85","0.9","0.95","0.97","0.99","0.999"] if not y in results]:
                print("_+_+_+_+",name," RECALL TRESH: ", recall_tresh, "_+_+_+_+")
                with open("../Data/merging_theories/" + name + ".theories") as f:
                    all_theories = ast.literal_eval(f.readline())
                print("#Theories: ", len(all_theories))
                query_counter = 0
                positive_tracker = []
                operator_tracker=[]
                weight_tracker = []
                positive_ids = []
                theory_tracker=[all_theories]
                for theo_id in range(0,len(all_theories)):
                    theory=all_theories[theo_id]
                    theo_ids=perform_query(theory,0, db,columns[1:], db[db.rfind("/")+1:-4], "id")
                    positive_ids.append(theo_ids)
                print("Positives:", [len(x) for x in positive_ids])
                all_weights=[]
                all_positives=[]
                all_ids=[]
                for positive in positive_ids:
                    weights, new_pos, final_ids=idstoweights(positive, vals, True)
                    all_weights.append(weights)
                    all_positives.append(new_pos)
                    all_ids.append(final_ids)

                positive_tracker.append(deepcopy(all_ids))
                weight_tracker.append(deepcopy(all_weights))
                indices=list(range(0,len(all_weights)))
                early_stop=False
                while len(all_theories)>1 and not early_stop:
                    print("++++++",len(all_theories))
                    t1=all_theories.pop(0)
                    t2=all_theories.pop(0)
                    p1=all_positives.pop(0)
                    p2=all_positives.pop(0)
                    i1=all_ids.pop(0)
                    i2=all_ids.pop(0)
                    merged_theory = merge_theories([t1,t2], combines)
                    if len(merged_theory) < 15000:
                        merged_ids = perform_query(merged_theory, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id")

                        merged_theory = postprocess(merged_theory, combines)
                        print("POSTPROCESSED: ", len(merged_theory))

                        postprocessed_ids=perform_query(merged_theory, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id")
                        assert set(merged_ids)==set(postprocessed_ids)
                        print("Before: ", len(merged_ids))
                        resulting_string = ""
                        for i in merged_theory:
                            for ele in i:
                                resulting_string += str(ele) + " "
                            resulting_string += "0\n"

                        weights = [[0, 0] for x in range(0, len(p1[0]))]
                        full_positives = p1+p2
                        for i in full_positives:
                            for ele in i:
                                weights[abs(ele) - 1][ele < 0] += 1
                        print(weights)
                        weight_string = "c weights"
                        for weight in weights:
                            if extra == "_unweighted":
                                weight_string += " " + str(1) + " " + str(1)
                            elif 0 in weight:
                                weight_string += " " + str(float(min(1.0, weight[0]))) + " " + str(float(min(weight[1], 1.0)))

                            else:
                                weight_string += " " + str(weight[0] / sum(weight)) + " " + str(weight[1] / sum(weight))

                        resulting_string = "p cnf " + str(len(weights)) + " " + str(
                            resulting_string.count("\n")) + "\n" + weight_string + "\n" + resulting_string
                        with open(temp_file, "w") as f:
                            f.write(resulting_string)

                        pm = Prob_Mistle(temp_file, "count_lit", skipped_operators=10, combines=combines)
                        res=pm.compress(recall_tresh=recall_tresh)
                        compressed_ids = perform_query(pm.clauses, 0, db, columns[1:], db[db.rfind("/") + 1:-4], "id")

                        print("Operators", res["Operators"])
                        print("GC: ", res["GlobalCriterion"])
                        print("Recall: ", res["Accuracy"])
                        print("Compression: ", res["Compression"])
                        postprocessed=postprocess(pm.clauses, combines)

                        theory2cnf(postprocessed, pm.weights, pm.num_literals, temp_file.replace(".cnf", "_compressed.cnf"))
                        try:
                            post_compressed_ids=perform_query(postprocessed, 0,db,columns[1:], db[db.rfind("/")+1:-4], "id")
                            print("--> postprocessed clauses & ids: ", len(postprocessed), len(post_compressed_ids))
                        except(sqlite3.OperationalError):
                            print("QUERY TOO BIG")
                            post_compressed_ids = []
                        assert set(compressed_ids)==set(post_compressed_ids)

                        if len(post_compressed_ids)>0:
                            new_weights, positives, final_ids=idstoweights(post_compressed_ids,vals, True)
                            all_positives = [positives] + all_positives
                            all_theories = [postprocessed] + all_theories
                            all_ids = [final_ids] + all_ids
                            operator_tracker.append(deepcopy(res["Operators"]))
                            positive_tracker.append(deepcopy(all_ids))
                            theory_tracker.append(deepcopy(all_theories))
                    else:
                        early_stop=True
                if not early_stop:
                    subres={}
                    subres["Positives"]=positive_tracker
                    subres["Theories"]=[[[list(x) for x in y] for y in z] for z in theory_tracker]
                    subres["Operators"]=operator_tracker
                else:
                    subres="SKIPPED"
                    print("EARLY STOPPED")
                results[recall_tresh]=subres
                with open("../Results/"+name+extra+".json","w") as f:
                    json.dump(results, f)

