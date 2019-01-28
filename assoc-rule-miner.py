import sys
import os
import math
import itertools
from collections import Counter


def read_csv(filepath):
    '''Read transactions from csv_file specified by filepath
    Args:
        filepath (str): the path to the file to be read

    Returns:
        list: a list of lists, where each component list is a list of string representing a transaction

    '''

    transactions = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            transactions.append(line.strip().split(',')[:-1])
    return transactions

class Hash_Node:
    """
    Class which represents node in a hash tree.
    """

    def __init__(self):
        self.children = {}
        self.isLeaf = True
        self.container = {}


class Hash_Tree:
    """
    Class for Hash_Tree
    """

    def __init__(self, max_leaf, max_child):
        self.root = Hash_Node()
        self.max_leaf = max_leaf
        self.max_child = max_child
        self.frequent_itemsets = []
        
    def insert(self, itemset):
        # convert list to tuple for itemset
        itemset = tuple(itemset)
        self.recur_insert(self.root, itemset, 0, 0)

    def recur_insert(self, node, itemset, count, index):
        #Recursively add nodes to the hash tree.

        if index == len(itemset):
            if itemset in node.container:
                node.container[itemset] += count
            else:
                node.container[itemset] = count
            return

        if node.isLeaf:

            if itemset in node.container:
                node.container[itemset] += count
            else:
                node.container[itemset] = count
            if len(node.container) == self.max_leaf:
                # container has reached its maximum capacity and its intermediate node so split and redistribute entries.
                for old_itemset, old_cnt in node.container.items():
                    hash_key = self.hash(old_itemset[index])
                    if hash_key not in node.children:
                        node.children[hash_key] = Hash_Node()
                    self.recur_insert(node.children[hash_key], old_itemset, old_cnt, index + 1)

                del node.container
                node.isLeaf = False
        else:
            hash_key = self.hash(itemset[index])
            if hash_key not in node.children:
                node.children[hash_key] = Hash_Node()
            self.recur_insert(node.children[hash_key], itemset, count, index + 1)

    def add_support(self, itemset):
        #increase support count of the itemset by 1 inside hash tree 

        temp_root = self.root
        itemset = tuple(itemset)
        index = 0
        while True:
            if temp_root.isLeaf:
                if itemset in temp_root.container:
                    temp_root.container[itemset] += 1
                break
            key = self.hash(itemset[index])
            if key in temp_root.children:
                temp_root = temp_root.children[key]
            else:
                break
            index += 1

    def get_frequent_itemsets(self, minsup):
        self.frequent_itemsets = []
        self.dfs(self.root, minsup)
        return self.frequent_itemsets
        
    def dfs(self, node, minsup):
        if node.isLeaf:
            for key, value in node.container.items():
                if value >= minsup:
#                     self.frequent_itemsets.append(list(key))
                    self.frequent_itemsets.append((list(key),value))
                    # print key, value, minsup
            return

        for child in node.children.values():
            self.dfs(child, minsup)    

    def hash(self, val):
#         print("value:",val)
        return val % self.max_child

# To be implemented
def generate_frequent_itemset(transactions, minsup):
    '''Generate the frequent itemsets from transactions
    Args:
        transactions (list): a list of lists, where each component list is a list of string representing a transaction
        minsup (float): specifies the minsup for mining

    Returns:
        list: a list of frequent itemsets and each itemset is represented as a list string

    Example:
        Output: [['margarine'], ['ready soups'], ['citrus fruit','semi-finished bread'], ['tropical fruit','yogurt','coffee'], ['whole milk']]
        The meaning of the output is as follows: itemset {margarine}, {ready soups}, {citrus fruit, semi-finished bread}, {tropical fruit, yogurt, coffee}, {whole milk} are all frequent itemset

    '''
    # generate frequent itemset of single items
    
    print("transaction:",len(transactions))
    items = []
    support_count = []
    unique_items = []
    frequent_k = []
    transactions_index = []
    frequent_itemsets = [[]]
    unique_items_map = {} 
    
    for transaction in transactions:
        for item in transaction:
            items.append(item)
    
    num_transactions = len(transactions)
      
    for item in items:
        if not (item in unique_items):
            unique_items.append(item)
            
    unique_items = sorted(unique_items)
    unique_items_index = list(range(1,len(unique_items)+1))
 
    i = 1
    
    for item in unique_items:
        unique_items_map[item] = i
        i += 1    
    
    #get frequent items of k=1, convert unique items to integers
    frequent_items = Counter(x for sublist in transactions for x in sublist)
    for name, freq in frequent_items.items():
        if freq/num_transactions >= minsup:
            templist = []
            templist.append(unique_items_map.get(name))
            if not len(templist) == 0:
                frequent_k.append(templist)
                support_count.append((templist, freq))
    
    #print("frequent_k:",frequent_k)
    
    unique_items_map_inversed = dict((v,k) for k, v in unique_items_map.items())   #number, item
    
    #convert all items in transactions to integers
    for transaction in transactions:
        templist = []
        for item in transaction:  
            templist.append(unique_items_map.get(item))
        transactions_index.append(templist)

    frequent_itemsets = frequent_k
#     print("frequent_itemsets:",frequent_itemsets)

    k = 2
    while len(frequent_k) > 0:
#         print("")
#         print("loop ",k," start")

        # 1 - candidate generation
        candidates = []
        
        for i in range (0,len(frequent_k)):
            item_to_merge_1 = frequent_k[i]
            
            for j in range (i+1,len(frequent_k)):
                item_to_merge_2 = frequent_k[j]
                new_itemset = []      
                if(k <= 2):
                    new_itemset.extend(item_to_merge_1)
                    new_itemset.extend(item_to_merge_2)
                else:
                    #Combine (k-1) Itemset to (k-1) Itemset 
                    if check_same_array(item_to_merge_1[0:k-2],item_to_merge_2[0:k-2]):
                        new_itemset = [x for x in item_to_merge_1]
                        new_itemset.extend(item_to_merge_2[k-2:k-1]) 
                        
                if new_itemset:
                    new_itemset = sorted(new_itemset) 
                    out_list = []
                    candidate_not_prune = True
                    
                    # 2 - candidate_pruning
                    #generate all subsets of the new itemset
                    out_list_temp = sum([list(itertools.combinations(new_itemset, i)) for i in range(len(new_itemset))],[])
                    out_list = [list(p) for p in out_list_temp if list(p) != []]
                      
                    #if any subset is not in existing frequent itemsets, prune the candidate
                    for element in out_list:
                        if not (element in frequent_itemsets):
                            candidate_not_prune = False
                            break
                    
                    if candidate_not_prune:
                        #print("prune result: True")
                        candidates.append(new_itemset)                   
            
        #3 support counting and candidate elimination
        
        #print("candidates:",candidates)
        #count occurence of k-itemsets in the transactions
        k_subsets = []
        for itemset in transactions_index:
            k_subsets.extend(map(list, itertools.combinations(itemset, k)))
            
        #generate hash tree
        hash_tree = Hash_Tree(max_child=4, max_leaf=5)
        
        # add candidates to hashtree
        #items in candidates have been sorted already
        for itemset in candidates:
            hash_tree.insert(itemset)
        
        #use hash tree to count support of k-itemsets
        for subset in k_subsets:
            subset = sorted(subset)
            hash_tree.add_support(subset)
        
        #get frequent itemsets from hash tree
        new_frequent = hash_tree.get_frequent_itemsets(math.ceil(minsup*num_transactions))
        
        frequent_k = [list(x[0]) for x in new_frequent]
        frequent_k.sort()
        frequent_itemsets.extend(frequent_k)

        k += 1
        
        support_count.extend(new_frequent)
    
    frequent_itemset_string = []
    for itemset in frequent_itemsets:
        item_string = []
        for item in itemset:
            item_string.append(unique_items_map_inversed.get(item))
        frequent_itemset_string.append(item_string)
        
    support_count_string = []
    for support in support_count:
        support_string = []
        for x in support[0]:
            support_string.append(unique_items_map_inversed.get(x))
        support_count_string.append((support_string, support[1]))

    #return frequent itemsets and support count of them
    
    return frequent_itemset_string, support_count_string

def check_same_array(list_1, list_2):
    """
    Check if two arrays have exactly the same elements
    """
    for i in range(0,len(list_1)):
        if list_1[i] != list_2[i]:
            return False
    return True


def generate_association_rules(transactions, minsup, minconf):
    '''Mine the association rules from transactions
    Args:
        transactions (list): a list of lists, where each component list is a list of string representing a transaction
        minsup (float): specifies the minsup for mining
        minconf (float): specifies the minconf for mining

    Returns:
        list: a list of association rule, each rule is represented as a list of string

    Example:
        Output: [['root vegetables', 'rolls/buns','=>', 'other vegetables'],['root vegetables', 'yogurt','=>','other vegetables']]
        The meaning of the output is as follows: {root vegetables, rolls/buns} => {other vegetables} and {root vegetables, yogurt} => {other vegetables} are the two associated rules found by the algorithm
    

    '''
    rules = []

    frequent_itemsets, support_count = generate_frequent_itemset(transactions, minsup)
#     print(frequent_itemsets)
    i = 0
    for itemset_k in frequent_itemsets:
#         print("check itemset:",i+1)
        i += 1 
        length = len(itemset_k)
        if length < 2:
            continue
        #find H_1
        consequence_1 = [''.join(x) for x in list(itertools.combinations(itemset_k, 1))]
#         print("consequence_1:",consequence_1)
        consequence_1, rules = prune(itemset_k, consequence_1,minconf,rules, support_count)
        if consequence_1:
            rules = apriori_genrules(itemset_k, consequence_1, minconf, rules, support_count)
          
#     print(rules)
    
    return rules

def prune(itemset_k, consequence_m, minconf, rules, support_count):
    """
    Generate rules by pruning
   """
    rules = [x for x in rules if x !=[]]
    templist_remove = []
    for consequence in consequence_m: 
        #generate the items in left side of the rule by removing consequence from itemset_k
        left = [x for x in itemset_k]
        if isinstance(consequence, list):
            for y in consequence:
                left.remove(y)
        else:
            left.remove(consequence)
#         print("left:",left, "  --  right:",consequence)
        conf = find_support(itemset_k, support_count) / find_support(left, support_count)
#         print("confidence level:",conf)
        if conf >= minconf:
            new_rule = []
            new_rule.extend(left)
            new_rule.append("=>")
            new_rule.append(consequence)
#             print("new_rule:",new_rule)
            rules.append(new_rule)
            
        else:
            templist_remove.append(consequence)
    
    for temp in templist_remove:
        consequence_m.remove(temp); 
#     print("after remove:",consequence_m)
    return consequence_m, rules


def apriori_genrules(itemset_k, consequence_m, minconf, rules, support_count):
    rules = [x for x in rules if x !=[]]
    k = len(itemset_k)
    
    if isinstance(consequence_m[0], list):
        m = len(consequence_m[0])
    else:
        m = 1
#     print("m:",m)
#     print("consequence_m",consequence_m)
    temp = [x for x in consequence_m]
    while (k >= m + 1 and temp):
        #generate H(m+1) from H(m)
        consequence_m_1 = apriori_gen(temp)
        temp = []
        temp,rules = prune(itemset_k, consequence_m_1, minconf, rules, support_count)
        m += 1
    return rules

def find_support(itemset_k, support_count):
    """
    Return the support count of the itemset_k
    """
    count = 0
    for x in support_count:
        if len(x[0])==len(itemset_k):
            if check_same_array(x[0], itemset_k):
                count = x[1]
    return count
    

def apriori_gen(consequence_m):
    """
    Generate H(m+1) given H(m)
    """
    templist = []
    if isinstance(consequence_m[0], list):
        m = len(consequence_m[0])
    else:
        m = 1
        
    for x in consequence_m:
        if m == 1:
            templist.append(x)
        else:
            for y in x:
                if not y in templist:
                    templist.append(y)
        
    consequence_m_1 = [list(x) for x in list(itertools.combinations(templist, m+1))]
    return consequence_m_1


def main():

    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Wrong command format, please follwoing the command format below:")
        print("python assoc-rule-miner-template.py csv_filepath minsup")
        print("python assoc-rule-miner-template.py csv_filepath minsup minconf")
        exit(0)

    
    if len(sys.argv) == 3:
        transactions = read_csv(sys.argv[1])
        result,_ = generate_frequent_itemset(transactions, float(sys.argv[2]))

        # store frequent itemsets found by your algorithm for automatic marking
        with open('.'+os.sep+'Output'+os.sep+'frequent_itemset_result.txt', 'w') as f:
            for items in result:
                output_str = '{'
                for e in items:
                    output_str += e
                    output_str += ','

                output_str = output_str[:-1]
                output_str += '}\n'
                f.write(output_str)

    elif len(sys.argv) == 4:
        transactions = read_csv(sys.argv[1])
        minsup = float(sys.argv[2])
        minconf = float(sys.argv[3])
        result = generate_association_rules(transactions, minsup, minconf)

        # store associative rule found by your algorithm for automatic marking
        with open('.'+os.sep+'Output'+os.sep+'assoc-rule-result.txt', 'w') as f:
            for items in result:
                output_str = '{'
                for e in items:
                    if e == '=>':
                        output_str = output_str[:-1]
                        output_str += '} => {'
                    else:
                        output_str += e
                        output_str += ','

                output_str = output_str[:-1]
                output_str += '}\n'
                f.write(output_str)


main()