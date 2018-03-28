import networkx as nx
from networkx.algorithms.flow import edmonds_karp
import matplotlib.pyplot as plt

G = nx.DiGraph()

#Source to User Edges
G.add_edge('s','U1', capacity=10.0)
G.add_edge('s','U2', capacity=10.0)
G.add_edge('s','U3', capacity=10.0)
G.add_edge('s','U4', capacity=10.0)
G.add_edge('s','U5', capacity=10.0)
G.add_edge('s','U6', capacity=10.0)
G.add_edge('s','U7', capacity=10.0)

# User1 U2P relations
G.add_edge('U1','P1', capacity=4.0)
G.add_edge('U1','P2', capacity=9.0)
G.add_edge('U1','P3', capacity=6.0)
G.add_edge('U1','P4', capacity=3.0)
G.add_edge('U1','P5', capacity=2.0)
G.add_edge('U1','P6', capacity=1.0)
G.add_edge('U1','P7', capacity=5.0)

# User2 U2P relations
G.add_edge('U2','P1', capacity=3.0)
G.add_edge('U2','P2', capacity=2.0)
G.add_edge('U2','P3', capacity=8.0)
G.add_edge('U2','P4', capacity=5.0)
G.add_edge('U2','P5', capacity=4.0)
G.add_edge('U2','P6', capacity=1.0)
G.add_edge('U2','P7', capacity=9.0)

# User3 U2P relations
G.add_edge('U3','P1', capacity=1.0)
G.add_edge('U3','P2', capacity=6.0)
G.add_edge('U3','P3', capacity=2.0)
G.add_edge('U3','P4', capacity=7.0)
G.add_edge('U3','P5', capacity=8.0)
G.add_edge('U3','P6', capacity=4.0)
G.add_edge('U3','P7', capacity=9.0)

# User4 U2P relations
G.add_edge('U4','P1', capacity=6.0)
G.add_edge('U4','P2', capacity=8.0)
G.add_edge('U4','P3', capacity=9.0)
G.add_edge('U4','P4', capacity=2.0)
G.add_edge('U4','P5', capacity=5.0)
G.add_edge('U4','P6', capacity=3.0)
G.add_edge('U4','P7', capacity=10.0)

# User5 U2P relations
G.add_edge('U5','P1', capacity=4.0)
G.add_edge('U5','P2', capacity=3.0)
G.add_edge('U5','P3', capacity=1.0)
G.add_edge('U5','P4', capacity=9.0)
G.add_edge('U5','P5', capacity=7.0)
G.add_edge('U5','P6', capacity=5.0)
G.add_edge('U5','P7', capacity=8.0)

# User6 U2P relations
G.add_edge('U6','P1', capacity=2.0)
G.add_edge('U6','P2', capacity=8.0)
G.add_edge('U6','P3', capacity=6.0)
G.add_edge('U6','P4', capacity=7.0)
G.add_edge('U6','P5', capacity=3.0)
G.add_edge('U6','P6', capacity=9.0)
G.add_edge('U6','P7', capacity=1.0)

# User7 U2P relations
G.add_edge('U7','P1', capacity=3.0)
G.add_edge('U7','P2', capacity=9.0)
G.add_edge('U7','P3', capacity=2.0)
G.add_edge('U7','P4', capacity=10.0)
G.add_edge('U7','P5', capacity=4.0)
G.add_edge('U7','P6', capacity=6.0)
G.add_edge('U7','P7', capacity=8.0)

# Project to Sink Edges
G.add_edge('P1','t', capacity=10.0)
G.add_edge('P2','t', capacity=10.0)
G.add_edge('P3','t', capacity=10.0)
G.add_edge('P4','t', capacity=10.0)
G.add_edge('P5','t', capacity=10.0)
G.add_edge('P6','t', capacity=10.0)
G.add_edge('P7','t', capacity=10.0)
#G.add_edge('x','a', capacity=3.0)
#G.add_edge('x','b', capacity=1.0)
#G.add_edge('a','c', capacity=3.0)
#G.add_edge('b','c', capacity=5.0)
#G.add_edge('b','d', capacity=4.0)
#G.add_edge('d','e', capacity=2.0)
#G.add_edge('c','y', capacity=2.0)
#G.add_edge('e','y', capacity=3.0)
R = edmonds_karp(G, 's', 't')
print (R.graph['flow_value']*10)/7, '%'

nx.draw(R)
plt.show()
