import os

def krimp_dict(file):
    with open(file, 'r') as f:
        lines=f.readlines()
    filtered_lines=[x[:x.find('\t')] for x in lines if "=>" in x and not " => " in x]
    result={}
    for x in filtered_lines:
        result[int(x[:x.find("=")])]=int(x[x.find(">")+1:])
    return result

def krimp2theory(file, dict):
    with open(file, 'r') as f:
        lines=f.readlines()
    lines=lines[2:-len(dict)]
    #convert krimp lits to normal lits, negate to go from dnf to cnf
    #Krinp line = conjunction,  theory = disjunction
    theory=[[-dict[int(z)] for z in x[:x.find("(")].strip().split(" ")] for x in lines]
    return theory
failed=[]
for file in [x for x in os.listdir("DS/Resources/KrimpBinSource_win,lin/data_class/datasets") if x.endswith(".txt")]:
    try:
        name=file[:-16]
        print(name)
        dict=krimp_dict("DS/Resources/KrimpBinSource_win,lin/data_class/datasets/"+file)
        with open("DS/Resources/KrimpBinSource_win,lin/data_class/datasets/"+name+".classes") as f:
            cls=int(f.readlines()[0].split(" ")[0])


        result_folders=[x for x in os.listdir("DS/Resources/KrimpBinSource_win,lin/xps/classify/") if x[:x.find("-")]==name]
        print(result_folders)
        result_folder=None
        for test in result_folders:
            files=os.listdir("DS/Resources/KrimpBinSource_win,lin/xps/classify/"+test)
            if "f1" in files and len([x for x in os.listdir("DS/Resources/KrimpBinSource_win,lin/xps/classify/"+test+"/"+"f1") if x=="train"+str(cls)])>0:
                result_folder=test
                print(result_folder)
                break;



        os.makedirs("DS/Results/Krimp/theories/"+name,exist_ok=True)
        counter=0
        for result in [x for x in os.listdir("DS/Resources/KrimpBinSource_win,lin/xps/classify/"+result_folder+"/f1/train"+str(cls)+"/") if x.endswith(".ct")]:
           theory=krimp2theory("DS/Resources/KrimpBinSource_win,lin/xps/classify/"+result_folder+"/f1/train"+str(cls)+"/"+result, dict)
           with open("DS/Results/Krimp/theories/"+name+"/"+name+"_"+str(counter)+".theory","w") as f:
               f.write(str(theory))
           counter+=1
    except Exception as e:
        print(e)
        failed.append(name)
print(failed)
