import math
import os
import json
import ast


def mean(x):
    return sum(x)/len(x)
songs=False
dir=""
todo=[]

if songs:
    dir="music_playlists"
    res_dir=""
    for i in range(0,20):
        for x in range(0,10):
            todo.append(str(i)+"_"+str(x))
else:
    dir = "federated_theories"
    res_dir="federated_results/"
    for i in ["ttt","car","votes","hayesroth","flare"]:
        for x in range(1,10):
            todo.append(i + "_" + str(x))

results={}
modes=[]
for mode in ["_weighted", "_unweighted"]:
    for tresh in ["0.8","0.85","0.9","0.95","0.97","0.99","0.999"]:
        results[mode+"_"+tresh]=[]
        modes.append((mode, tresh))
for mode in ["_uncompressed","_pmc"]:
    results[mode]=[]
    modes.append((mode,"0.0"))
results["krimp"]=[]
# for file in todo:
#     with open("DS/Results/"+res_dir+file+"_0.0_uncompressed.json") as f:
#         uncompressed=json.load(f)
#     if uncompressed["0.0"]!="SKIPPED":
#         base_dl=sum([len(x) for x in uncompressed["0.0"]["Theories"][-1]])
#         for mode, tresh in modes:
#             with open("DS/Results/"+res_dir+file+"_"+tresh+mode+".json") as f:
#                 subr=json.load(f)
#
#             Init_positives = set([z for y in subr[tresh]["Positives"][0] for z in y])
#             last_positives = set(subr[tresh]["Positives"][-1][0])
#             TP = len(last_positives.intersection(Init_positives))
#             FP = len(last_positives - Init_positives)
#             FN = len(Init_positives - last_positives)
#             f1=2 * TP / (2 * TP + FP + FN)
#             dl=sum([len(x) for x in subr[tresh]["Theories"][-1]])
#             compression=(base_dl-dl)/base_dl
#             gc=math.sqrt((1-f1)**2+(1-compression)**2)
#             if tresh!="0.0":
#                 results[mode+"_"+tresh].append([[TP,FP,FN],f1,compression,gc])
#             else:
#                 results[mode].append([[TP, FP, FN], f1, compression, gc])
#         with open("DS/Results/Krimp/theories/"+file+"/"+file+".result") as f:
#             line=ast.literal_eval(f.readline())
#         best=[]
#         best_gc=math.inf
#         counter=0
#         bc=0
#         for i in line[:1]:
#             counter+=1
#             dl=i[0]
#             f1=i[1]
#             subs=i[2]
#             compression = max(0.0,(base_dl - dl) / base_dl)
#             gc = min(1.0,math.sqrt((1 - f1) ** 2 + (1 - compression) ** 2))
#             if gc<best_gc:
#                 bc=counter
#                 best_gc=gc
#                 best=[subs,f1,compression,gc]
#         if len(best)>0:
#             print(file,bc,"/",counter)
#             results["krimp"].append(best)
#         else:
#             print(file)
#
#
# for i in results:
#     f1=mean([x[1] for x in results[i]])
#     dl = mean([x[2] for x in results[i]])
#     gc = mean([x[3] for x in results[i]])
#     print(i, "GC: ", round(gc,2), "F1: ", round(f1,2), "DL: ", round(dl,2))
t="0.9"
print(modes)
for file in todo:
    with open("DS/Results/"+res_dir+file+"_"+t+"_unweighted.json") as f:
        unweighted=json.load(f)
    if unweighted[t]!="SKIPPED":
        for mode, tresh in [("_unweighted",t),("_weighted",t)]:
            with open("DS/Results/"+res_dir+file+"_"+tresh+mode+".json") as f:
                subr=json.load(f)

            Init_positives = set([z for y in subr[tresh]["Positives"][0] for z in y])
            last_positives = set(subr[tresh]["Positives"][-1][0])
            TP = len(last_positives.intersection(Init_positives))
            FP = len(last_positives - Init_positives)
            FN = len(Init_positives - last_positives)
            f1=2 * TP / (2 * TP + FP + FN)
            dl=sum([len(x) for x in subr[tresh]["Theories"][-1]])
            results[mode+"_"+tresh].append([[TP, FP, FN], f1, dl])
for i in ["_weighted_"+t,"_unweighted_"+t]:
    f1=mean([x[1] for x in results[i]])
    dl = mean([x[2] for x in results[i]])
    print(i, f1, dl)