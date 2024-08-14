import subprocess
import platform
import math
import os
import pycosat
from time import time
from pathlib import Path
import math
from contextlib import contextmanager
import sys, os
from DS.Src.File_Manipulation.theory2cnf import theory2cnf
import subprocess
# from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout



def get_wmc(clauses=None, weights=None,num_literals=None, file=None):

    while True:
        try:
            if file==None:
                file="DS/Temp/addmc_file"+"_"+str(time())+".cnf"
                theory2cnf(clauses, weights, num_literals, file)
            process = subprocess.Popen(["DS/Resources/ADDMC-master/addmc", "--cf",file,"--wf","2"],
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True)
            wmc=0
            total=""
            while True:
                output = process.stdout.readline()
                # print("OUTPUT: ", output)
                total+=output+"\n"
                if output.strip().startswith("s wmc"):
                    wmc=float(output.strip()[5:])
                    os.remove(file)
                    return wmc
                # Do something else
                return_code = process.poll()
                if return_code is not None:
                    if return_code!=0:
                        print('RETURN CODE', return_code)
                        # Process has finished, read rest of the output
                        for output in process.stdout.readlines():
                            print(output.strip())
                    break
        except Exception as e:
            print("Again:",e)


### IMPLEMENTATION WITH PYSDD
# print(funct("Data/wcnfs/connect4_3.cnf"))
# def get_wmc2(clauses=None, weights=None,num_literals=None, file=None):
#
#     if clauses==None and weights==None and file==None and num_literals==None:
#         raise Exception("Not all WMC parameters can be none")
#     if platform.system()=="Linux":
#
#         if file!=None:
#             lines = open(file).readlines()
#             if len(lines)<3 or len(lines[1].split(" "))<4:
#                 raise Exception(file+"\n"+"".join(lines))
#             cnf_string = "".join(lines)
#
#         else:
#             cnf_string="p cnf "+str(num_literals)+" "+str(len(clauses))+"\n"
#             cnf_string+="c weights"
#             for i in range(1,int(len(weights)/2)+1):
#                 cnf_string+=" "+str(weights[i])+" "+str(weights[-i])
#             cnf_string+="\n"
#             clauses = list(clauses)
#             for clause in clauses[:-1]:
#                 cnf_string+=str(sorted(list(clause), key=abs))[1:-1].replace(",", "") + " 0\n"
#             if len(clauses) > 0:
#                 cnf_string+=str(sorted(list(clauses[-1]), key=abs))[1:-1].replace(",", "") + " 0"
#         print("SDD MANAGER")
#         with suppress_stdout():
#             line_weights = cnf_string.split("\n")[1].split(" ")[2:]
#
#             mgr, f = SddManager.from_cnf_string(cnf_string)
#             wmc = f.wmc(log_mode=False)
#             for i in mgr.vars:
#                 wmc.set_literal_weight(i.literal, float(line_weights.pop(0)))
#                 wmc.set_literal_weight(-i.literal, float(line_weights.pop(0)))
#             print("Start propagation")
#             returnval=wmc.propagate()
#
#         return returnval
#     elif platform.system()=="Windows":
#         print("WINDOWS")
#         lines=open(file).read().split("\n")[1:]
#         if len(lines)==1:
#             return 0
#         weights_line=lines.pop(0).split(" ")[2:]
#         weights=dict()
#         for i in range(1,len(weights_line)//2+1):
#             weights[i]=float(weights_line.pop(0))
#             weights[-i]=float(weights_line.pop(0))
#         all_lines=[]
#         for line in lines:
#             all_lines.append([int(x) for x in line.split(" ")][:-1])
#         solutions=list(pycosat.itersolve(all_lines))
#         return sum([math.prod([weights[x] for x in z]) for z in solutions])
