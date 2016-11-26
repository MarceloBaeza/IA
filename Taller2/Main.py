# Froms
from Norvig import Node
from Problem import Problem
from utils import *
from random import shuffle
# imports
import matplotlib.pyplot as plt
import numpy as np


class TSP:

    def __init__(self, point, x, y):
        self.point = point
        self.X = x
        self.Y = y


def hill_climbing(problem):
    """From the initial node, keep choosing the neighbor with highest value,
    stopping when no neighbor is better. [Figure 4.2]"""
    # Listo ...
    current = Node(problem.initial)
    while True:
        # Creo que listo
        neighbors = current.expand(problem)
        if not neighbors:
            break
        neighbor = argmax_random_tie(
            neighbors, key=lambda node: problem.value(node.state))

        if problem.value(neighbor.state) <= problem.value(current.state):
            break
        current = neighbor
    return current.state


def Read():

    File = open("TSP225.txt", 'r')
    List = []
    v = 1
    for line in File:

        if v >= 7:
            line2 = line.split(" ")
            if line2[0] == "EOF\n":
                break
            if(len(line2) == 5):
                Node = line2[2]
                X = float(line2[3])
                Y = float(line2[4])
                tsp = TSP(Node, X, Y)
                List.append(tsp)
                continue

            if(len(line2) == 4):
                Node = line2[1]
                X = float(line2[2])
                Y = float(line2[3])
                tsp = TSP(Node, X, Y)
                List.append(tsp)
                continue

            if(len(line2) == 3):
                Node = line2[0]
                X = float(line2[1])
                Y = float(line2[2])
                tsp = TSP(Node, X, Y)
                List.append(tsp)
                continue
        v += 1
    return List, List


def Initial(Nodes):
    shuffle(Nodes)
    return Nodes


def Cost(Ciclo):
    dist = 0
    for i in range(len(Ciclo) - 1):
        a = [Ciclo[i].X, Ciclo[i].Y]
        a = np.array(a)
        b = [Ciclo[i + 1].X, Ciclo[i + 1].Y]
        b = np.array(b)
        dist += np.linalg.norm(a - b)
    return dist


def SHOW(Node):
    print("Graficando ...")
    # print(Solution)
    x = []
    y = []
    for n in Node:
        x.append(n.X)
        y.append(n.Y)
    plt.figure('Solucion Final')
    plt.plot(x, y, 'co')
    a_scale = float(max(x)) / float(100000)
    plt.arrow(x[-1], y[-1], (x[0] - x[-1]), (y[0] - y[-1]), head_width=a_scale,
              color='g', length_includes_head=True)
    for i in range(0, len(x) - 1):
        plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=a_scale,
                  color='g', length_includes_head=True)

    # Set axis too slitghtly larger than the set of x and y
    # plt.xlim(0, max(x))
    # plt.ylim(0, max(y))
    plt.show()
    # for it1 in Node:
    #     print(str(it1.point) + " : " + str(it1.X) + ", " + str(it1.Y))


if __name__ == "__main__":
        # Lectura de archio
    print("Leyendo archivo")
    Nodes_original, Nodes_init = Read()
    # Genero la primera inicialización
    print("Iniciando nodos")
    Nodes_init = Initial(Nodes_init)
    print("Gerando problem")
    # Genero un objeto Problem
    P1 = Problem(Nodes_init)
    print("Distancia Inicial: " + str(Cost(Nodes_init)))
    print("Iniciando hill_climbing")
    Solution = hill_climbing(P1)
    print("Distancia Final: " + str(Cost(Nodes_init)))
    SHOW(Nodes_init)
