import os
import json
modes = ["_weighted", "_unweighted", "_pmc","_uncompressed"]
tresholds=["0.8","0.85","0.9","0.95","0.97","0.99","0.999"]
correct=[]
for i in range(0,20):
    for x in range(0,10):
        all_true=True
        for mode in modes:
            if mode=="_weighted" or mode=="_unweighted":
                todo=tresholds
            else:
                todo=["0.0"]
            for tresh in todo:
                if not os.path.isfile("../Results/"+str(i)+"_"+str(x)+"_"+tresh+mode+".json"):
                    all_true=False
        if all_true:
            correct.append((i,x))
f1={}
DL={}
new_f1={}
new_DL={}
failure={}
for mode in modes:
    if mode == "_weighted" or mode=="_unweighted":
        todo = tresholds
    else:
        todo = ["0.0"]
    for tresh in todo:
        f1[mode+"_"+tresh]=[]
        DL[mode+"_"+tresh]=[]
        new_f1[mode + "_" + tresh] = []
        new_DL[mode + "_" + tresh] = []
        failure[mode+"_"+tresh]=0
print("Full experiments: ", len(correct))

for i,x in correct:

    for mode in modes:
        if mode == "_weighted"  or mode=="_unweighted":
            todo = tresholds
        else:
            todo = ["0.0"]
        for tresh in todo:
            with open("../Results/" + str(i) + "_" + str(x) + "_" + tresh + mode + ".json") as f:
                subr=json.load(f)
            if subr[tresh]=="SKIPPED":
                failure[mode+"_"+tresh]+=1
            else:
                Init_positives=set([z for y in subr[tresh]["Positives"][0] for z in y])
                last_positives=set(subr[tresh]["Positives"][-1][0])
                TP=len(last_positives.intersection(Init_positives))
                FP=len(last_positives-Init_positives)
                FN=len(Init_positives-last_positives)
                if mode=="_pmc":
                    print(i, x, TP, FP, FN)
                f1[mode+"_"+tresh].append(2*TP/(2*TP+FP+FN))
                DL[mode+"_"+tresh].append(sum([len(x) for x in subr[tresh]["Theories"][-1]]))
results=[]
print("---FAILURES---")
for x in failure:
    results.append((x, failure[x]))
print("---F1---")
for x in f1:
    results.append((x, sum(f1[x])/len(f1[x])))
print("---DL---")
for z in DL:
    results.append((z, sum(DL[z])/len(DL[z])))


print("############### NO FAILURES")

for i,x in correct:
    todo=tresholds
    for tresh in todo:
        with open("../Results/" + str(i) + "_" + str(x) + "_" + tresh + "_weighted" + ".json") as f:
            weighted_subr=json.load(f)
        with open("../Results/" + str(i) + "_" + str(x) + "_" + tresh + "_unweighted" + ".json") as f:
            unweighted_subr = json.load(f)
        if weighted_subr[tresh]!="SKIPPED" and unweighted_subr[tresh]!="SKIPPED":
                for subr in [weighted_subr, unweighted_subr]:
                    Init_positives=set([z for y in subr[tresh]["Positives"][0] for z in y])
                    last_positives=set(subr[tresh]["Positives"][-1][0])
                    TP=len(last_positives.intersection(Init_positives))
                    FP=len(last_positives-Init_positives)
                    FN=len(Init_positives-last_positives)
                    if subr==weighted_subr:
                        new_f1["_weighted"+"_"+tresh].append(2*TP/(2*TP+FP+FN))
                        new_DL["_weighted"+"_"+tresh].append(sum([len(x) for x in subr[tresh]["Theories"][-1]]))
                    else:
                        new_f1["_unweighted" + "_" + tresh].append(2 * TP / (2 * TP + FP + FN))
                        new_DL["_unweighted" + "_" + tresh].append(sum([len(x) for x in subr[tresh]["Theories"][-1]]))
all_results=[]
print("---F1---")
for x in new_f1:
    if len(new_f1[x])>0:
        all_results.append((x, sum(new_f1[x])/len(new_f1[x])))
print("---DL---")
for z in new_DL:
    if len(new_DL[z])>0:
        all_results.append((z, sum(new_DL[z])/len(new_DL[z])))

print(all_results)
print(results)


