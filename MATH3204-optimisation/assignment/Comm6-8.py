from gurobipy import *

# Sets
I = range(3)
L = range(8)
C = range(25)

# Data
IDtoLVC = [
[42.9,16.2,72.0,79.2,27.6,68.9,60.0,63.7],
[69.8,60.0,76.2,58.2,35.6,89.2,29.6,10.3],
[30.7,52.0,9.2,24.1,50.3,28.1,38.7,77.3]
]

CCDPop = [3397,4841,4201,3432,4179,6042,3424,5150,3899,6322,6356,5824,3808,3859,4433,6187,4735,5729,6091,3469,6143,4418,3487,4413,3505]

CCDtoLVC = [
[0,23.7,0,0,36.6,0,0,0],
[0,29.6,0,0,22.1,0,0,0],
[0,0,0,0,20.3,0,0,34.7],
[0,0,0,0,31.4,0,0,10.7],
[0,0,0,0,0,0,36.5,5.6],
[0,13.9,0,0,33.8,0,0,0],
[0,9.8,0,0,19.1,0,0,0],
[0,0,0,0,9.4,0,24.4,0],
[0,0,0,0,29.4,0,16.7,23.4],
[0,0,0,0,0,0,28.4,13.4],
[15.0,19.0,0,0,0,0,0,0],
[16.7,11.3,0,0,24.4,0,0,0],
[31.1,0,0,0,25.1,0,18.9,0],
[0,0,0,23.8,0,0,5.5,0],
[0,0,0,27.1,0,0,14.1,0],
[11.5,0,0,0,0,19.6,0,0],
[5.7,30.4,26.8,0,0,24.0,0,0],
[23.6,0,20.3,28.2,0,0,0,0],
[0,0,0,12.3,0,0,18.4,0],
[0,0,0,17.5,0,0,23.9,0],
[32.3,0,0,0,0,18.0,0,0],
[20.9,0,20.8,0,0,5.4,0,0],
[0,0,7.4,29.9,0,26.0,0,0],
[0,0,27.0,15.1,0,0,0,0],
[0,0,41.3,20.3,0,0,0,0]
]

IDCost = [158, 147, 193]
DeliveryCost = 0.2 # per km
AccessCost = 1.0 # per km
LVCUCost = [1426000,1403000,1346000,1676000,1883000,1456000,1832000,1048000]
LVCCCost = [5789000,4595000,5073000,4824000,4748000,4044000,3625000,5036000]
m = Model("Vaccine Distribution Strategy")

# Variables

# X[i,l] is amount to send from ID i to LVC l
X = { (i,l): m.addVar() for i in I for l in L}

# Y[c,l] is people for CCD c to send to LVC l
Y = { (c,l): m.addVar() for c in C for l in L}

#Whether LVC[l] is upgraded or not
Z= { (l): m.addVar(vtype=GRB.BINARY) for l in L}

#Whether LVC[l] is closed or not
W= { (l): m.addVar(vtype=GRB.BINARY) for l in L}

#Whether LVC[l] serves CCD[c]
A = {(c,l):m.addVar(vtype=GRB.BINARY) for c in C for l in L}

# Objective
m.setObjective(quicksum((IDCost[i] + DeliveryCost*IDtoLVC[i][l])*X[i,l] for i in I for l in L) +
	quicksum(AccessCost*CCDtoLVC[c][l]*Y[c,l] for c in C for l in L) + quicksum(Z[l]*LVCUCost[l] for l in L)
    -quicksum((1-W[l])*LVCCCost[l] for l in L)
    , GRB.MINIMIZE)

# Constraints

# Balance at each LVC
for l in L:
	m.addConstr(quicksum(X[i,l] for i in I) == quicksum(Y[c,l] for c in C))

# Meet population demands
for c in C:
	m.addConstr(quicksum(Y[c,l] for l in L) == CCDPop[c])
	
# If no connection then Y must by 0
for c in C:
	for l in L:
		if CCDtoLVC[c][l] == 0:
			m.addConstr(Y[c,l] == 0)

# Communication 6 - Limit capacities of IDs and LVCs

IDMax = 47000
LVCMax = 14000
UpLVCMax=21000

for i in I:
	m.addConstr(quicksum(X[i,l] for l in L) <= IDMax)
for l in L:
	m.addConstr(quicksum(Y[c,l] for c in C) <= LVCMax+7000*Z[l])	


#Communication 7 - Savings through closing LVCs (W[l]=0 if closing, W[l]=1 if open)

for l in L:
   m.addConstr(UpLVCMax*W[l]>=quicksum(Y[c,l] for c in C))


#Communication 8 - each CCD can only be served by 1 LVC

for c in C:
    for l in L:
        m.addConstr(Y[c,l]==A[c,l]*CCDPop[c])

for c in C:
    m.addConstr(quicksum(A[c,l] for l in L)==1)



m.optimize()
print(m.objVal)