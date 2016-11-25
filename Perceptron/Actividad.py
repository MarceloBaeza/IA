import numpy as np
import matplotlib.pyplot as plt
from mlxtend.evaluate import plot_decision_regions
from perceptron import Perceptron


def First():
    X = np.genfromtxt('iris.csv', delimiter=',', usecols=(0, 2))[0:100]
    Y = np.genfromtxt('iris.csv', delimiter=',', usecols=(4), dtype=str)[0:100]

    Y = np.where(Y == 'setosa', -1, 1)

    ppn = Perceptron(0.01, 5000)
    ppn.train(X, Y)
    print ("Pesos: %s\n" % ppn.w_)
    plot_decision_regions(X, Y, clf=ppn)
    plt.title("Perceptron Setosa-Versicolor")
    plt.show()


def Second():
    X = np.genfromtxt('iris.csv', delimiter=',', usecols=(1, 3))[51:150]
    Y = np.genfromtxt('iris.csv', delimiter=',',
                      usecols=(4), dtype=str)[51:150]

    Y = np.where(Y == 'versicolor', -1, 1)

    ppn = Perceptron(0.01, 100)
    ppn.train(X, Y)
    print ("Pesos: %s\n" % ppn.w_)
    plot_decision_regions(X, Y, clf=ppn)
    plt.title("Perceptron Versicolor-Virginica")
    plt.show()

if __name__ == "__main__":
    print "Perceptron Setosa-Versicolor"
    First()
    print "Perceptron Versicolor-Virginica"
    Second()
