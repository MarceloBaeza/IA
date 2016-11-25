CHO="CHOCO"
VAC="VALLE DEL CAUCA"
CAU="CAUCA"
NAR="NARINO"
PUT="PUTUMAYO"
AMA="AMAZONAS"
ANT="ANTIOQUIA"
RISA="RISARALDA"
QUI="QUINDIO"
TOL="TOLIMA"
VAU="VAUPES"
CAL="CALDAS"

class MapColor(object):
    def __init__(self,graph,colors):
        self.check_valid(graph)
        self.graph=graph
        nodes=list(self.graph.keys()) #obtiene las llaves primarias del grafo...
        self.node_colors={node:None for node in nodes}
        self.domains={node: set(colors) for node in nodes}#SON LOS COLORES...

    def solve (self):
        uncolored_nodes=[n for n,c in self.node_colors.iteritems() if c is None]
        if not uncolored_nodes:
            print (self.node_colors)
            return True
        node =uncolored_nodes[0]
        print ("dominio para " + node + ":" + str(self.domains[node]))
        #BEGIN BACKTRACKING
        for color in self.domains[node]:
            #FORMA UNA LISTA...PARA CADA UNO DE LOS ELEMENTOS QUE ESTAN EN GRAFO COLOR...
            #
            if all(color!=self.node_colors[n] for n in self.graph[node]): #verificamos que el nodo no se encuentre ..
                #si no esta, fijamos un color...
                self.set_color(node,color)
                self.remove_from_domais(node,color)
                #llamamos recursivamente la funcion, y si encontro una funcion retornamos verdaderp.
                if self.solve(): return True
                self.set_color(node,None)
                self.add_to_domais(node, color)
        return False
    def set_color(self,key,color):
        self.node_colors[key]=color
    def remove_from_domais(self,key,color):
        for node in self.graph[key]:
            if color in self.domains[node]:
                self.domains[node].remove(color)
    def add_to_domais(self, key,color):
        for node in self.graph[key]:
            self.domains[node].add(color)
    def check_valid(self,graph):
        for node,nexts in graph.iteritems():
            assert(nexts)
            assert(node not in nexts)
            for next in nexts:
                assert(next in graph and node in graph[next])

colombia={CHO:{RISA},RISA:{CHO}}
colores={'r','g','b','y'}
g=MapColor(colombia,colores)
g.solve()
