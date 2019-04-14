# Import Regular Expression
import re
from time import gmtime, strftime
import timeit

#**********************************************************************************
# read_input: function to read input file containing transactions and returns
# entire transaction set, list of unique items and count of each items 
#**********************************************************************************
def read_input(in_file):
    file = open(in_file, "r")
    transaction_database = []
    items=[]
    per_item_count={}

    for line in file:                                     # For every line in transactions file
        transaction = re.findall(r"\d+", line)            # digits
        transaction = [ int(z) for z in transaction ]     # Convert strings to int and create list
        if len(transaction)==0:
            continue                                      # Empty line
        for i in transaction:                             # For every item in single transaction
            if i in per_item_count.keys():
                per_item_count[i]=per_item_count[i]+1     # increment item count
            else:
                per_item_count[i]=1
                items.append(i)
        transaction_database += [transaction]             # Add trasaction to database

    file.close()
    return transaction_database, items, per_item_count

#**********************************************************************************
# MSApriori: function to read input file containing transactions and returns
# entire transaction set, list of unique items and count of each items 
#**********************************************************************************
def MSApriori(transaction_db, items, mis, sdc, must_have, cannot_be_togethor):
    F = [[]] * ( 20 )       # As per a look at input file, we will surely not get itemset with more than 19 items
    C = [[]] * ( 20 )       # As per a look at input file, we will surely not get itemset with more than 19 items
    
    count = {}                    # count of k-itemsets. k=1,2,3 etc.
    n = len(transaction_db)       # number of transactions
    
    len_cannot_be_togethor = len(cannot_be_togethor[0])   # Calculate the length of 1 set of cannot_be_togethor sets

    # Sort the items in list by its MIS values
    M = sorted(items, key = lambda i : mis[i])
    
    # Init pass:
    # 1.
    # Step is done in Main program by statement support_count[item]=float(per_item_count[item]/len_transaction_db)
    # I am calculating MIS values there so took care of support count part as well to avoid 1 for for loop
    
    # 2.
    L = [ M[0] ]
    for j in range(1, len(M)):
        if support_count[ M[j] ]  >= mis[ M[0] ] :   
            L.append( M[j] )
            count[ tuple( [M[j]] )] = support_count[ M[j] ] * n  

    # Calculate F1:
    F[1] = []
    for item in L:
        if (support_count[item]) >= mis[item]:  
            F[1].append(item)
            count[ tuple( [item] )] = support_count[item] * n

    # Generate candidates set and count them:
    k = 2
    while k <= n and len( F[k-1] ) > 0:
        F[k] = []
        
        # Create candidate set 2:
        if k == 2:                                             
            C[2] = level2_candidate_gen(L, sdc, n)
            for c in C[2]:                 # Initialize counts of each itemset. Will be used to filter C[k] to F[k]
                d = tuple(sorted(c, key = lambda i : mis[i]))
                count[d] = 0
                
        # Create candidate set  >  2:
        if k > 2:                                              
            C[k] = MScandidate_gen(F[k-1], sdc)
            for c in C[k]:                  # Initialize counts of each itemset. Will be used to filter C[k] to F[k]
                d = tuple(sorted(c, key = lambda i : mis[i]))
                count[d] = 0
        
        # Apply can not be togethor constraint
        if k >= len_cannot_be_togethor:
            for c in C[k]:
                for t in cannot_be_togethor:
                    if set(t).issubset(set(c)):     # if can not be togethor is subset of itemset
                        C[k].remove(c)              # Remove 
                        break;                      # Break and go for next itemset in C[k]
      
        # Calculate counts of each itemset. Will be used to filter C[k] to F[k]:
        for t in transaction_db:
            txn_set=set(t)
            for c in C[k]:                 
                if set(c).issubset(txn_set):
                    d = tuple(sorted(c, key = lambda i : mis[i]))
                    count[d] += 1
        
        # Filter C[k] to F[k]:
        for c in C[k]:
            d = tuple(sorted(c, key = lambda i : mis[i]))

            if (count[d]) >= (n * mis[ c[0] ]):
                F[k].append(c)

        k += 1

    # return F containing k-itemsets
    return F

#*******************************************************************************************
# level2_candidate_gen:  Level 2 candidate-gen function
#*******************************************************************************************
def level2_candidate_gen(L, sdc, n):
    C2 = []    # initialize the set of candidates

    for i in range(0, len(L)-1):
        l_in_must_have = False
        l = L[i]
        
        if l in must_have:          # No need to serach l in must_have again in for loop.
            l_in_must_have = True
            
        if (support_count[l]) >= mis[l]:
            for j in range (i+1, len(L)):
                h = L[j]
                if l_in_must_have or (h in must_have):  # Apply Must have item constraint
                    if (support_count[h] >= mis[l]) and (abs(support_count[h] - support_count[l]) <= sdc):
                        C2.append([l, h])    # append the candidate [l, h] into C2
    return C2

#*******************************************************************************************
# level2_candidate_gen: Candidate-gen function for k > 2
#*******************************************************************************************
def MScandidate_gen(F_prev, sdc):
    Ck = []    # initialize the set of candidates

    for i in range(len(F_prev)):
        f1 = F_prev[i]
        f1.sort()
        j=0
        
        for j in range(len(F_prev)): 
            f2 = F_prev[j]
            f2.sort()

            if (f1[:len(f1)-1] == f2[:len(f2)-1]) and (f1[-1] < f2[-1]):
                if abs( support_count[f1[-1]]  - support_count[f2[-1]] ) <= sdc:
                    c=[]
                    c=f1.copy()              # Copy f1 to c so that we do not change original f1.
                    c.append(f2[-1])         # append item in c
                    Ck.append(c)             # insert the candidate itemset c into Ck

                    for idx in range(1, len(c)+1):
                        s = c[:idx-1] + c[idx:]    # (k-1)-subset of c
                        if (c[1] in s) or (mis[c[2]] == mis[c[1]]):
                            if s not in F_prev:
                                Ck.remove(c)       # delete c from the set of candidates
                                break; 

    return Ck


#*******************************************************************************************
# Main Program
#*******************************************************************************************

ls=.05
sdc = .05;
delta=.5
per_item_count={}
support_count={}
items=[]
must_have=[1534, 1816, 225, 1394]
cannot_be_togethor = [[1534, 1943, 1816, 1834], [1534, 1943, 225, 1215], [1534, 1943, 1394, 1989], 
                      [1534, 1943, 1534, 1582], [1816, 1834, 225, 1215], [1816, 1834, 1394, 1989],
                      [1816, 1834, 1534, 1582], [225, 1215, 1394, 1989], [225, 1215, 1534, 1582],
                      [1394, 1989, 1534, 1582]]

# Start time
start_time = timeit.default_timer()
print('start_time: ',start_time)

transaction_database, items, per_item_count = read_input(r'C:\Users\schopra\Desktop\test_files\retail1.txt')
#transaction_database, items, per_item_count = read_input(r'C:\Users\schopra\Desktop\test_files\retail1_testsmall.txt')

len_transaction_db = len(transaction_database)
mis={} 

# Calculate MIS of each item
for item in per_item_count:     
    mis[item] = max(float(delta*float(per_item_count[item]/len_transaction_db)),ls)
    support_count[item]=float(per_item_count[item]/len_transaction_db)
    

F = MSApriori(transaction_database, items, mis, sdc, must_have, cannot_be_togethor)

#End Time:
print('end_time: ',timeit.default_timer())
print('Total time taken by Python with IC while generating Itemsets in Seconds: ',timeit.default_timer() - start_time)

# Print Results
for i in F:
    total_no_of_itemsets = len(i)
    if total_no_of_itemsets > 0:
        if isinstance(i[0], int):
            size_of_1_itemset=1
        else:
            size_of_1_itemset=len(i[0])
        
        print('*********************************************************************************************')
        print('*********************************************************************************************')
        print(' ')
        print('Total number of itemsets of length '+ str(size_of_1_itemset) + ' are: ',total_no_of_itemsets)
        print('---------------------------------------------------------------------------------')
        print('Itemsets of length ' + str(size_of_1_itemset) + ' are as below: ')
        print(i)
        print(' ')
        print(' ')
