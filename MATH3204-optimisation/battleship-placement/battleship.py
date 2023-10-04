from gurobipy import *
import csv
Ship=[
  [],
  [[1]],
  [[2,3],[4,5]],
  [[2,6,3],[4,6,5]],
  [[2,6,6,3],[4,6,6,5]],
  [[2,6,6,6,3],[4,6,6,6,5]]
]

ShipChar='0123456'
 
f = open('/Users/emmawheeley/hot-jams/MATH3204-optimisation/battleship-placement/30x20.csv')
# Read the dimensions
nRow,nCol = [int(s) for s in f.readline().split(',')[:2]]
Row = range(nRow)
Col = range(nCol)
# Read the number of ships of each length
L = [int(s) for s in f.readline().split(',')[:len(Ship)]]
Len = range(1,len(L))
# Read the general data
D = [[int(s) for s in f.readline().split(',')[:nCol+1]] for i in Row]
# Read the row of column sums
ColSum = [int(s) for s in f.readline().split(',')[:nCol]]
# Take the row sums from the end of the general data
RowSum = [D[i][-1] for i in Row]
for i in Row:
  D[i] = D[i][0:-1]

# Wipe out the data for testing purposes
##D = [[100 for j in Col] for i in Row]

def PieceOK(d,i,j,l):
  # Is it OK to place a ship of length l at location i,j in orientation d
  if l == 1:
    # Only have horizontal submarines
    if d == 1:
      return False
  # Check for running off the end, all compatible squares and surrounded by water
  if d == 0:
    if j+l > nCol:
      return False
    for ll in range(l):
      if D[i][j+ll] < 100 and D[i][j+ll] != Ship[l][d][ll]:
        return False
    for ii in range(max(0,i-1),min(i+2,nRow)):
      for jj in range(max(0,j-1),min(j+l+1,nCol)):
        ## Fail if it is not in the ship itself and it is anything except water
        if ii < i or ii > i or jj < j or jj >= j+l:
          if D[ii][jj] < 100 and D[ii][jj] > 0:
            return False
  else:
    if i+l > nRow:
      return False
    for ll in range(l):
      if D[i+ll][j] < 100 and D[i+ll][j] != Ship[l][d][ll]:
        return False
    for ii in range(max(0,i-1),min(i+l+1,nRow)):
      for jj in range(max(0,j-1),min(j+2,nCol)):
        ## Fail if it is not in the ship itself and it is anything except water
        if ii < i or ii >= i+l or jj < j or jj > j:
          if D[ii][jj] < 100 and D[ii][jj] > 0:
            return False
  return True    

m = Model('BattleShip')
# Our placement variables are indexed by H/V(0/1), i, j, len
X = {
  (d,i,j,l): m.addVar(vtype=GRB.BINARY)
  for d in [0,1] for i in Row for j in Col for l in Len
  if PieceOK(d,i,j,l)
  }
m.update()

XL = tuplelist(X)
# Right number of ships of each length
[m.addConstr(quicksum(X[d,i,j,l] for d,i,j,l in XL.select('*','*','*',l)) == L[l], name='L%d'%l)
 for l in Len]
# Row and col sums add up
[m.addConstr(quicksum(l*X[d,i,j,l] for d,i,j,l in XL.select(0,i,'*','*'))
             + quicksum(X[d,ii,j,l] for d,ii,j,l in XL.select(1,'*','*','*') if ii<=i and ii+l>i)
             == RowSum[i], name='R%d'%i)
 for i in Row]
[m.addConstr(quicksum(l*X[d,i,j,l] for d,i,j,l in XL.select(1,'*',j,'*'))
             + quicksum(X[d,i,jj,l] for d,i,jj,l in XL.select(0,'*','*','*') if jj<=j and jj+l>j)
             == ColSum[j], name='C%d'%j)
 for j in Col]
# Each square covered at most once (or exactly once if non-zero)
Cover = [[m.addLConstr(lhs=0, rhs=1,
            sense=GRB.LESS_EQUAL if (D[i][j] == 0 or D[i][j] == 100) else GRB.EQUAL
                      ,name='V%d,%d'%(i,j))
          for j in Col] for i in Row]
m.update()
for d,i,j,l in XL:
  if d==0:
    for ii in range(i, min(i+2,nRow)):
      for jj in range(j, min(j+l+1,nCol)):
        m.chgCoeff(Cover[ii][jj],X[d,i,j,l],1)
  else:
    for ii in range(i, min(i+l+1,nRow)):
      for jj in range(j, min(j+2,nCol)):
        m.chgCoeff(Cover[ii][jj],X[d,i,j,l],1)

while True:        
  m.optimize()
  if m.Status != GRB.OPTIMAL:
    break
  ## Write out the answer
  STR = [['-' for j in Col] for i in Row]
  for d,i,j,l in XL:
    if X[d,i,j,l].x > 0.1:
      for ll in range(0,l):
        STR[i+d*ll][j+(1-d)*ll] = ShipChar[Ship[l][d][ll]]

  for i in Row:
    print (''.join(STR[i]))

  TL = [X[d,i,j,l] for d,i,j,l in XL if X[d,i,j,l].x > 0.1]
  print (len(TL), sum(L))
  # Remove this next break if you want to check for multiple solutions
  break
  m.addConstr(quicksum(TL) <= len(TL) - 1)