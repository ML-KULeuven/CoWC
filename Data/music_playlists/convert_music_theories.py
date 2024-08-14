import os

def convert_music_theories():
    music = [list(range(1, 34)), list(range(34, 44)), list(range(44, 54)), list(range(54, 64)), list(range(64, 73)),
             list(range(73, 83)), list(range(83, 93)), list(range(93, 99)), list(range(99, 107)), list(range(107, 117)),
             list(range(117, 127)), list(range(127, 134)), list(range(134, 146)), list(range(146, 158))]
    for i in range(0,20):
        for x in range(0,10):
            with open("merging_theories_raw/"+str(i)+"_"+str(x)+".txt", "r") as f:
                lines=f.readlines()
            theories=[]
            sharp_counted=False
            theory=[]
            for line in [z.strip().replace("'","") for z in lines if len(z.strip())>0]:
                if line.startswith("-") or (line.startswith("#") and sharp_counted):
                    theories.append(theory)
                    theory=[]
                elif line.startswith("#") and not sharp_counted:
                    sharp_counted=True
                elif not line.startswith("{"):
                    variable=int(line[1:line.find('=')].strip())
                    values=[int(x) for x in line[line.find('=')+2:-1].split(",")]
                    clause=[]
                    for v in values:
                        clause.append(music[variable-1][v])
                    theory.append(clause)
            with open("merging_theories/"+str(i)+"_"+str(x)+".theories","w") as f:
                f.write(str(theories))

convert_music_theories()