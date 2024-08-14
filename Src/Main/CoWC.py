from DS.Src.File_Manipulation.cnf2theory import cnf2theory
from DS.Src.File_Manipulation.theory2cnf import theory2cnf
from DS.Src.Main.pattern_mining import compute_itemsets
from DS.Src.Operators.S_operator import S_operator, S_possible
from DS.Src.Operators.R_operator import R_operator, R_possible
from DS.Src.Operators.W_operator import W_operator, W_possible
from DS.Src.Operators.T_operator import T_operator
from DS.Src.Operators.V_operator import V_operator
from DS.Src.Operators.F_operator import F_operator
from DS.Src.WMC.get_wmc import get_wmc
import multiprocessing
import math
import time
from tqdm import tqdm

class CoWC:
    def __init__(self, cnf_file, description_length,skipped_operators=3, combines=[]):
        """
        The constructor of the CoWC object.
        It converts the given cnf_file to seperate clauses, weights and the amount of literals.
        It calculates the base weighted model count, used win the calculation of the accuracy.
        The last init calculates the base global criterion, which is the one that needs to be minimized.

        """
        self.path=[(0,1)]
        self.start_time=time.time()
        self.dl=description_length
        self.filename=cnf_file
        self.clauses, self.weights, self.num_literals=cnf2theory(cnf_file)
        self.original_cnf=self.clauses.copy()
        self.original_num_literals=int(self.num_literals)
        self.skipped_operators=skipped_operators
        self.resolved_literals=0
        self.guarded_clauses=dict()
        self.definitions=dict()
        self.support=2/len(self.clauses)
        self.original_dl=self.get_dl()
        self.current_global_criterion=(1,1,0)
        self.checked_sets=set()
        self.combines=comb_theory(combines)
        self.original_wmc = get_wmc(self.clauses.union(set(self.combines)), self.weights, self.num_literals)
        print("Original_WMC: ", self.original_wmc)

    def compress(self ,permitted_operators={"S":True, "W":True, "R": True, "T":True, "V":True,"F":True}, recall_tresh=0):
        """
        The main function of CoWC.
        Summarized:
            1) find all frequent sets
            2) Order the sets and select the best sets to use for compression
            3) Find the operator that optimizes the global criterion the most
            4) Apply that operator
            5) See if there is a new predicate that needs to be resolved

        Ends if there are no more frequent sets or if no operators can be applied for 5 times
        """

        #If recall tresh = 1.0, only lossless compression is allowed
        if recall_tresh==1.0:
            permitted_operators = {"S": True, "W": True, "R": True, "T": False, "V": False, "F": False}
        counts={"W":0, "V":0, "R":0, "T":0, "S":0,"F":0}
        # print("Start compression")
        skip_counter=0
        freq_count=0
        while skip_counter<self.skipped_operators:
            change_made=False
            frequent_items=self.find_all_frequent_sets()
            freq_count+=1
            if len(frequent_items)==0:
                break
            else:
                frequent, count, residues=self.best_frequent_set(frequent_items)
                if not frequent:
                    break
                self.checked_sets.add(frozenset(frequent))
                other_clauses={x for x in self.clauses if not frozenset(frequent).issubset(x)}.union(get_set_from_values(self.guarded_clauses.values()))
                operator_done, op=self.apply_operator(permitted_operators,frequent,residues,other_clauses,counts, recall_tresh)

                if operator_done:
                    path_accuracy=self.current_global_criterion[1]
                    O_countlit=self.get_dl(self.dl, self.get_original_cnf(),
                                                        self.original_num_literals)
                    path_compression=(O_countlit-self.get_dl(self.dl))/O_countlit
                    self.path.append((path_compression, path_accuracy))
                    change_made=True
                    self.resolve_clauses(counts)
                    self.clauses,self.weights,self.num_literals=preprocess(self.clauses, self.weights, self.num_literals)
            if not change_made:
                skip_counter+=1

        output={}
        output["GlobalCriterion"]=self.current_global_criterion[0]
        output["Accuracy"]=self.current_global_criterion[1]
        output["OriginalDL"]={}
        output["OriginalDL"]["count_lit"] = self.get_dl("count_lit", self.get_original_cnf(),
                                                        self.original_num_literals)
        output["DL"]={}
        output["DL"]["count_lit"] = self.get_dl("count_lit", self.get_clauses(),
                                                        self.num_literals)
        output["Compression"]=self.current_global_criterion[2]
        output["FrequentCount"]=freq_count
        output["Operators"]=counts
        output["Time"]=time.time()-self.start_time
        output["Resolved"]=self.resolved_literals

        return output



    def get_global_criterion(self, clauses=None, weights=None, num_literals=None, tresh=0):
        """
        The objective function that needs to be minimized.
        In an ideal situation, CoWC compresses 100%, whilst keeping a 100% accuracy
        The global criterion is the euclidean distance between the accuracy and compression of the cnf and the ideal point
        """
        if clauses == None and weights == None and num_literals == None:
            clauses = self.get_clauses()
            weights = self.get_weights()
            num_literals = self.get_num_literals()
        compression=(self.original_dl-self.get_dl(self.dl,clauses, num_literals ))/self.original_dl

        accuracy=self.get_accuracy(clauses=clauses, weights=weights, num_literals=num_literals)
        if accuracy<tresh:
            return math.inf, accuracy, compression
        accuracy=2*accuracy/(1+accuracy)
        global_criterion=math.sqrt((accuracy-1)**2+(compression-1)**2)
        return global_criterion,accuracy,compression

    def get_dl(self, dl=None, clauses=None, num_literals=None):
        """
        Calculate the Description Length of some clauses.
        """
        if dl==None:
            dl=self.dl
        if clauses==None:
            clauses=self.clauses
        if num_literals==None:
            num_literals=self.num_literals
        if dl=="count_lit":
            return sum([len(x) for x in clauses])
        else:
            raise Exception
    def find_all_frequent_sets(self):
        """
        Iteratively try to mine all frequent sets, if it does not work, try with a 10x higher support
        """
        debug=False
        if not debug:
            not_found=True
            manager = multiprocessing.Manager()
            while not_found:
                frequent_items = manager.list()
                # print("Sup = ",self.support)
                p = multiprocessing.Process(target=mine_freq_itemsets, args=(self.clauses,self.support, frequent_items))
                p.start()
                # Cleanup
                p.join(60)
                if p.is_alive() or len(frequent_items)>100:
                    # print("#freq items", len(frequent_items))
                    # Terminate foo
                    p.terminate()
                    p.join()

                    if 1.5*self.support>=1:
                        # print("Supp --> 0.9")
                        frequent_items = []
                        mine_freq_itemsets(
                            self.clauses - get_set_from_values(get_set_from_values(self.guarded_clauses.values())),
                            max(self.support, 0.9), frequent_items)
                        not_found=False
                    else:
                        self.support*=1.5
                else:
                    not_found = False
        else:
            frequent_items = []
            mine_freq_itemsets(self.clauses-get_set_from_values(get_set_from_values(self.guarded_clauses.values())), self.support, frequent_items)
        return frequent_items
    def best_frequent_set(self,frequent_items):
        """
        Order the frequent sets by approximating the effect of predicate invention
        Example:
            Frequent set is [1 2 3] and the count is 3
            Dummy_Before = [1 2 3] v [1 2 3] v [1 2 3]
            Dummy_After = [1 2 3 4] v [-1 -4] v [-2 -4] v [-3 -4] v [-4] v [-4] v [-4]
            The approximation is then DL(Dummy_After)-(Dummy_Before)


        """
        best=math.inf
        best_clause=[]
        still_possible=False
        # print(frequent_items)
        for fset, count in frequent_items:
            if frozenset(fset) not in self.checked_sets and (len(fset)>1 or count>1):
                still_possible=True
                base=self.get_dl(clauses=Base_dummy(fset,count))
                w_estimate=self.get_dl(clauses=W_dummy(self.get_num_literals(), fset, count), num_literals=self.get_num_literals()+1)
                t_estimate=self.get_dl(clauses=T_dummy(fset))
                if (w_estimate+t_estimate)/2-base < best:
                    best_clause=(fset, count)
                    best=(w_estimate+t_estimate)/2-base
        if not still_possible:
            return (False, False, False)
        residue= [list(x - frozenset(best_clause[0])) for x in self.clauses if frozenset(best_clause[0]).issubset(x)]
        return best_clause[0],best_clause[1],residue




    def resolve_clauses(self, counts):
        """
        Loop over all definitions and check if resolving them (replacing all new literals with the original definition)
        gives a better global criterion.
        """
        current_full_gc=self.get_global_criterion()
        current_gc = current_full_gc[0]
        resolved=len(self.definitions)!=0
        did_resolve=False
        while resolved and len(self.definitions)>0:
            resolved = False

            if len(self.definitions)>0:
                max_lit = max(self.definitions)

                for added in self.definitions:

                    resolved_clauses = self.clauses.copy()-self.guarded_clauses[added]
                    result_clauses=set()
                    result_weights=self.weights.copy()

                    if added==max_lit:

                        for clause in resolved_clauses:
                            if -added in clause:
                                result_clauses.add(clause.difference(frozenset([-added])).union(frozenset(self.definitions[added])))
                            elif added in clause:
                                result_clauses.add(clause.difference(frozenset([added])).union(frozenset(self.definitions[added])))

                            else:
                                result_clauses.add(clause)
                        result_weights.pop(added)
                        result_weights.pop(-added)


                    else:
                        result_weights[added]=result_weights.pop(max_lit)
                        result_weights[-added]=result_weights.pop(-max_lit)
                        for clause in resolved_clauses:
                            if -added in clause:
                                new_clause=clause.difference(frozenset([-added])).union(frozenset(self.definitions[added]))
                            elif added in clause:
                                new_clause=clause.difference(frozenset([added])).union(frozenset(self.definitions[added]))
                            else:
                                new_clause=clause
                            if max_lit in new_clause:
                                result_clauses.add((new_clause-{max_lit}).union({added}))
                            elif -max_lit in new_clause:
                                result_clauses.add((new_clause-{-max_lit}).union({-added}))
                            else:
                                result_clauses.add(new_clause)

                    new_full_gc = self.get_global_criterion(weights=result_weights,clauses=result_clauses, num_literals=self.num_literals - 1)

                    new_gc=new_full_gc[0]
                    if new_gc < current_gc:

                        resolved=True
                        did_resolve=True
                        self.resolved_literals += 1
                        self.num_literals -= 1
                        self.current_global_criterion = new_full_gc
                        self.weights=result_weights
                        self.clauses=result_clauses
                        counts["W"] -= 1
                        if added==max_lit:
                            self.definitions.pop(added)
                            self.guarded_clauses.pop(added)
                            new_seen_clauses = set()
                            for old in self.checked_sets:
                                if max_lit not in old and -max_lit not in old:
                                    new_seen_clauses.add(old)
                            self.checked_sets = new_seen_clauses
                        else:
                            self.definitions[added]=self.definitions.pop(max_lit)
                            new_guarded_clauses=set()
                            for old in self.guarded_clauses.pop(max_lit):
                                if max_lit in old:
                                    new_guarded_clauses.add((old-{max_lit}).union({added}))
                                else:
                                    new_guarded_clauses.add((old - {-max_lit}).union({-added}))
                            self.guarded_clauses[added]=new_guarded_clauses
                            new_seen_clauses = set()
                            for old in self.checked_sets:
                                if max_lit in old:
                                    new_seen_clauses.add((old - {max_lit}).union({added}))
                                elif -max_lit in old:
                                    new_seen_clauses.add((old - {-max_lit}).union({-added}))
                                else:
                                    new_seen_clauses.add(old)
                            self.checked_sets = new_seen_clauses

                        break

        return did_resolve


    def apply_operator(self, permitted_operators, frequent,residues, other_clauses, counts, recall_tresh):
        """
        Find the operator that minimizes the global criterion the most.
        If the S- or R-operator are possible, apply them, as they are lossless (Accuracy stays the same, compression rises)
        Otherwise, try the 3 other operators and see which one is best.
        """
        # print(frequent)
        operator_done=False
        best_operator=""
        if permitted_operators["S"] and S_possible(residues):
            # print("S")
            best_operator="S"
            new_clauses = S_operator(frequent, residues)
            self.clauses = {frozenset(x) for x in new_clauses}.union(other_clauses)
            counts["S"] += 1
            operator_done = True
            self.current_global_criterion=self.get_global_criterion()
        elif permitted_operators["R"] and R_possible(residues):
            # print("R")
            best_operator = "R"
            new_clauses = R_operator(frequent, residues)
            self.clauses = {frozenset(x) for x in new_clauses}.union(other_clauses)
            counts["R"] += 1
            operator_done = True
            self.current_global_criterion = self.get_global_criterion()
        else:
            operator_options=[]
            if permitted_operators["T"]:

                T_gc = self.get_global_criterion(clauses=other_clauses.union(set([frozenset(frequent)])),
                                          weights=self.get_weights(),
                                          num_literals=self.get_num_literals(), tresh=recall_tresh)
                # print("T", self.current_global_criterion[1], T_gc[1])
                T_clauses = {frozenset(x) for x in T_operator(frequent)}.union(other_clauses)
                operator_options.append((T_gc,T_clauses, "T"))
            if permitted_operators["F"]:
                # print("F")
                # print("Residues: ", residues)
                F_gc = self.get_global_criterion(clauses=other_clauses.union({frozenset(x) for x in residues}),
                                          weights=self.get_weights(),
                                          num_literals=self.get_num_literals(), tresh=recall_tresh)

                F_clauses = {frozenset(x) for x in F_operator(residues)}.union(other_clauses)
                operator_options.append((F_gc,F_clauses, "F"))
            if permitted_operators["V"]:
                # print("V")
                V_options = V_operator(frequent, residues, self.definitions.keys())
                V_gc=(math.inf,)
                V_clauses=[]
                for new_clauses in V_options:
                    new_V_clauses = {frozenset(x) for x in new_clauses}.union(other_clauses)
                    new_v_gc = self.get_global_criterion(clauses=new_V_clauses, weights=self.get_weights(),
                                                num_literals=self.get_num_literals(), tresh=recall_tresh)
                    if new_v_gc[0] < V_gc[0]:
                        V_gc=new_v_gc
                        V_clauses=new_V_clauses
                operator_options.append((V_gc, V_clauses, "V"))
            if permitted_operators["W"] and W_possible(self.num_literals , self.clauses,
                                                             frequent, residues,
                                                             other_clauses, self.dl, self.definitions.keys()):
                # print("W")
                new_clauses, new_weights, new_literal = W_operator(frequent, residues, self.weights.copy())

                W_clauses={frozenset(x) for x in new_clauses}.union(other_clauses)

                W_gc=self.get_global_criterion(clauses=W_clauses, weights=new_weights, num_literals=self.num_literals+1, tresh=recall_tresh)
                operator_options.append((W_gc, W_clauses, "W"))
            operator_options.append((self.current_global_criterion,set(),""))
            # print("Operator options: ", [(x[0],x[2]) for x  in operator_options])
            best_gc, best_clauses, best_operator=min(operator_options)
            # print("best_operator:", best_operator)
            if best_gc[0]<self.current_global_criterion[0]:
                self.current_global_criterion=best_gc
                operator_done=True
                counts[best_operator]+=1
                self.clauses=best_clauses
                if best_operator=="W":
                    self.weights=new_weights
                    self.definitions[new_literal] = frequent
                    self.guarded_clauses[new_literal]={frozenset(frequent + [new_literal])}
                    for i in frequent:
                        self.guarded_clauses[new_literal].add(frozenset([-i, -new_literal]))
                    self.num_literals += 1

        return operator_done, best_operator



    def get_original_wmc(self):
        return self.original_wmc

    def get_num_literals(self):
        return self.num_literals

    def get_clauses(self):
        return self.clauses

    def get_original_cnf(self):
        return self.original_cnf

    def get_weights(self):
        return self.weights

    def get_num_clauses(self):
        return len(self.clauses)

    def get_example_weight(self,example):
        return math.prod([self.weights[x] for x in example])

    def get_accuracy(self,test_clauses=None, clauses=None, weights=None, num_literals=None):
        """
        __________________
        |       |   -O   | FP = WMC(cnf) - TN
        | cnf   |--------|
        |       |    O   | TP  = WMC(cnf & O) = WMC(cnf)
        _________________|
        |       |   -O   | TN = 1 - TN - FN - FP
        | -cnf  |--------|
        |       |    O   | FN = WMC(O) - TP
        ___________________

        Accuracy = TP / TP + FN
        """

        if clauses==None and weights==None and num_literals==None:
            clauses=self.get_clauses()
            weights=self.get_weights()
            num_literals=self.get_num_literals()
        if test_clauses == None:
            test_clauses = self.get_original_cnf()
            original_wmc = self.get_original_wmc()
        else:
            original_wmc = get_wmc(test_clauses.union(set(self.combines)), weights, num_literals)
        # print("Combines: ", len(self.clauses),"+",len(self.combines),"=",len(clauses.union(set(self.combines))))
        WMC_cnf = get_wmc(clauses.union(set(self.combines)), weights, num_literals)
        return WMC_cnf/original_wmc





def check_for_superset(input,clauses):
    for cl in clauses:
        if input.issuperset(cl):
            return True
    return False


def mine_freq_itemsets(clauses, support, result):
    result += compute_itemsets(clauses, support=support, algo="LCM")
def comb_theory(combines):
    clauses=[]
    for comb in [list(x) for x in combines]:
        for i in range(0,len(comb)-1):
            for x in range(i+1, len(comb)):
                clauses.append(frozenset([-comb[i],-comb[x]]))
    return clauses
def get_set_from_values(values):
    result=set()
    for x in values:
        result=result.union(x)
    return result

def W_dummy(num_literals, frequent, count):
    return [frozenset([-(num_literals+ 1)]) for _ in range(0, count)] \
    + [frozenset(frequent + [num_literals + 1])] \
    + [frozenset([w, -(num_literals+ 1)]) for w in frequent]

def T_dummy(frequent):
    return [frozenset(frequent)]

def Base_dummy(frequent, count):
    return [frozenset(frequent) for _ in range(0,count)]
def preprocess(clauses, weights, num_literals):
    return clauses, weights, num_literals
    truths=[]
    tresh=0
    for i in range(1,num_literals+1):
        if weights[i]==weights[-i] and weights[i]==1:
            pass
        elif weights[i]<=tresh:
            truths.append(-i)
        elif weights[i]>=1-tresh:
            truths.append(i)
    change=True
    while change:
        change=False
        new_clauses=[]
        # print("Preprocess")
        for clause in tqdm(iterable=clauses):
            new_clause=[]
            cont=True
            for element in clause:
                if cont:
                    if element in truths:
                        cont=False
                    elif -element not in truths:
                        new_clause.append(element)
            if len(new_clause)>0 and cont:
                new_clauses.append(new_clause)
        for clause in new_clauses:
            if len(clause)==1 and clause[0] not in truths:
                truths.append(clause[0])
                change=True
    for i in truths:
        if [i] not in new_clauses:
            new_clauses.append([i])
    result=list(set([frozenset(x) for x in new_clauses]))
    return result, weights, num_literals
