import subprocess
from time import time
import os
def perform_query(clauses,counter, db=None, columns=None, name=None, id=None, negative=False):
    clauses=list(clauses)
    cut=int(len(clauses)//10)
    result=[]
    for i in range(0,cut):
        ids = perform_internal_query(clauses[10*i:10*(i+1)], counter, db, columns, name, id, negative)
        if ids!=[-1]:
            result.append(ids)
    ids = perform_internal_query(clauses[(cut)*10:], counter, db, columns, name, id, negative)
    if ids != [-1]:
        result.append(ids)
    final=set(result.pop())
    while len(result)>0:
        if not negative:
            final=final.intersection(set(result.pop()))
        else:
            final=final.union(set(result.pop()))
    return list(final)
def perform_internal_query(clauses,counter, db=None, columns=None, name=None, id=None, negative=False):
    if len(clauses)==0:
        return [-1]
    command = "python3 DS/Resources/querycsv-0.3.0.0/querycsv/querycsv.py"
    command+=" -i "+db

    query="Select "+id+" from "+name+" where "
    for clause in clauses:
        subq=""
        for element in clause:
            if element>0:
                if negative:
                    subq += columns[element - 1] + "='0'"
                else:
                    subq+=columns[element-1]+"='1'"
            else:
                if negative:
                    subq += columns[abs(element) - 1] + "='1'"
                else:
                    subq+=columns[abs(element)-1]+"='0'"
            if len(clause)>1:
                if negative:
                    subq+=" and "
                else:
                    subq+=" or "
        if len(clause)>1:
            if negative:
                query += "(" + subq[:-5] + ")"
            else:
                query+="("+subq[:-4]+")"
        else:
            query+=subq
        if len(clauses)>1:
            if negative:
                query+=" or "
            else:
                query+=" and "
    if "and" in query[-5:]:
        query=query[:-5]+";"
    elif "or" in query[-4:]:
        query=query[:-4]+";"
    else:
        query+=";"
    # print(query)
    name="DS/Temp/query"+str(time())+".sql"
    with open(name, "w") as f:
        f.write(query)
    # print("Query", query)
    # command+=" -o "
    # command+=output
    command += " -s "
    command += name

    process = subprocess.Popen(command,shell=True,
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
    result=process.stdout.readlines()
    os.remove(name)
    if 'No results\n' not in result:
        return [int(x) for x in result[2:]]
    else:
        print(result)
        print("No results from database")
        return []
