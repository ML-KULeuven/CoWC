import os
import subprocess
import uuid
import time
def compute_itemsets(
        transactions,
        support=0.00001,
        algo="LCM",
        spmf_path="DS/Resources/spmf.jar",
        suppress_output=False,
        show_transaction_ids=False,
):
    """
    Computes itemsets from a set of clauses. Depending on the algorithm, itemsets can be closed, maximal or only frequent
    :param support: Support of the itemset, between 0 and 1. It is relative support.
    :param transactions: A list of clauses. Clauses are represented by a list of literals. This is like the DIMACS format
    :param algo: Name of the algorithm (see spmf doc for more details). LCM is for closed itemsets, FPMax for maximal, Eclat for frequent, DCI_CLosed.
    :param spmf_path: path to the spmf.jar file
    :return: a list of patterns as a list of tuples. First element of the tuple is the items of the patterns, second element is the support.
    """
    transactions=[list(x) for x in transactions]
    working_dir = os.getcwd()
    rand_id = uuid.uuid4()
    time_set=int(time.time()*100000)
    dataset_base_name = "DS/Temp/temp_spmf_dataset_" + str(rand_id)+str(time_set)
    dataset_name = os.path.join(working_dir, dataset_base_name)
    output_base_name = "DS/Temp/temp_spmf_dataset_res_" + str(rand_id)+str(time_set)
    output_name = os.path.join(working_dir, output_base_name)

    encoding_dict = {}

    encoded_transactions = []
    for transaction in transactions:
        encoded_transaction = []
        for item in transaction:
            if item not in encoding_dict:
                encoding_dict[item] = len(encoding_dict) + 1
            encoded_transaction.append(encoding_dict[item])
        encoded_transactions.append(sorted(encoded_transaction))
    inverse_token_dict = {v: k for k, v in encoding_dict.items()}
    with open(dataset_name, "w+") as db_file:
        db_file.write(
            "\n".join(
                [
                    " ".join([str(item) for item in transaction])
                    for transaction in encoded_transactions
                ]
            )
        )

    if suppress_output:
        stdout = open(os.devnull, "w")
    else:
        stdout = None
    if algo != "DCI_Closed":
        test=subprocess.Popen(
            [
                "java",
            "-jar",
                spmf_path,
                "run",
                algo,
                dataset_name,
                output_name,
                str(support),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        test=subprocess.Popen(
            [
                'java',
            "-jar",
                spmf_path,
                "run",
                algo,
                dataset_name,
                output_name,
                str(support),
                str(show_transaction_ids).lower(),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    test.communicate()

    result_patterns = []
    if algo == "DCI_Closed" and show_transaction_ids:
        parent_pattern = None
        parent_support = 0
        parent_t_ids = None

        with open(output_name,"w") as output:
            for l in output:
                pattern, support_t_ids = l.split("#SUP:")
                items = pattern.split()
                decoded_pattern = [inverse_token_dict[int(i)] for i in items]

                support, t_ids = support_t_ids.split("#TID:")
                support = int(support.strip())
                t_ids = t_ids.strip().split(" ")

                if support >= parent_support:
                    parent_pattern = pattern
                    parent_support = support
                    parent_t_ids = t_ids
                    decoded_t_ids = t_ids
                else:
                    assert parent_pattern.strip() in pattern.strip()
                    decoded_t_ids = []
                    for id in t_ids:
                        decoded_t_ids.append(parent_t_ids[int(id)])

                decoded_t_ids = [int(t_id) for t_id in decoded_t_ids]
                result_patterns.append((decoded_pattern, support, decoded_t_ids))
    else:
        with open(output_name,"r") as output:
            for l in output:
                pattern, support = l.split("#SUP:")
                support = int(support.strip())
                items = pattern.split()
                decoded_pattern = [inverse_token_dict[int(i)] for i in items]
                result_patterns.append((decoded_pattern, support))
    os.remove(dataset_name)
    os.remove(output_name)
    return result_patterns
