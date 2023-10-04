from  gurobipy import *

Probs = [0.95,0.975,0.99,0.995]

ECost = [
[51000,113000,202000,462000],
[62000,105000,243000,405000],
[55000,134000,256000,436000],
[55000,126000,232000,442000],
[70000,128000,222000,405000],
[58000,101000,258000,448000],
[59000,100000,206000,427000],
[61000,129000,223000,419000],
[54000,104000,240000,478000],
[62000,108000,258000,468000],
[50000,100000,201000,403000],
[56000,116000,247000,422000],
[62000,111000,213000,422000],
[58000,100000,248000,466000],
[51000,102000,227000,423000],
[64000,119000,204000,410000],
[70000,139000,218000,456000],
[57000,106000,245000,433000],
[59000,135000,226000,435000],
[53000,130000,246000,426000],
[66000,118000,247000,424000],
[50000,113000,249000,420000],
[63000,130000,215000,461000],
[55000,122000,231000,408000],
[59000,137000,244000,416000]
]

C=range(25)
P=range(4)

m=Model("Vaccine Distribution Options")

#X[c,p] defines CCD and probability column
X={ (c,p): m.addVar(vtype=GRB.BINARY) for c in C for p in P}


m.setObjective(quicksum((X[c,p]*ECost[c][p])for c in C for p in P),GRB.MINIMIZE)

for c in C:
    m.addConstr(quicksum(X[c,p] for p in P)==1)



m.addConstr(quicksum(quicksum(X[c,p]*math.log(Probs[p]) for p in P) for c in C)>=math.log(0.8))
    
m.optimize()
print(m.objVal)