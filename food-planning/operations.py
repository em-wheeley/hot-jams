import math
import random
from gurobipy import *



# DATA---
WEIGHT =[70,90,100,110,120,130,150,180,210,220,250,280,340,350,400]
wMAX = 1000
Compartment = ['A','B','C','D']
m = Model("Space")

# SETS---

C=range(len(Compartment)) #4 compartments
P=range(15) #15 packages


# VARIABLES---
L = {(p, c) : m.addVar(vtype=GRB.BINARY) for p in P for c in C } #L[p,c]=1 if package p loaded into compartment c


# OBJECTIVE----
#no objective

# CONSTRAINTS---
#total mass in A= total mass in D
m.addConstr(quicksum(L[p,0]*WEIGHT[p] for p in P)==quicksum(L[p,3]*WEIGHT[p] for p in P))

#total mass in B= total mass in C
m.addConstr(quicksum(L[p,1]*WEIGHT[p] for p in P)==quicksum(L[p,2]*WEIGHT[p] for p in P))
    
#every package must be included once in the delivery
for p in P:
    m.addConstr(quicksum(L[p,c]for c in C) ==1.0)

#Each compartment must contain at least 3 packages
#No compartment can contains more than wMAX
for c in C:
    m.addConstr(quicksum(L[p,c]for p in P )>=3)
    m.addConstr(quicksum(L[p,c]*WEIGHT[p] for p in P)<=wMAX)

m.optimize()
for c in C:
    print("Compartment" , Compartment[c], "contains", [p for p in P if L[p,c].x==1.0], "weighing", quicksum(L[p,c].x*WEIGHT[p] for p in P).getValue() )

