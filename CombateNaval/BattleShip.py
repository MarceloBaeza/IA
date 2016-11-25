from constraint import *
import random

def Print_Solution(s,TAM):
    print "Solution: " + str(len(s))
    for i in range (0,TAM):
        for j in range (0, TAM):
            print s[i*TAM + j],
        print

def Battle_Ship(Cols, Rows,TAM):
    print TAM
    problem = Problem()

    #ADD ROW AND COLUMNS
    for row in range (0, TAM):
        for col in range (0, TAM):
            problem.addVariable(row*TAM + col, [0,1])

    #Add the number of ship's in row
    for row in range (0,TAM):
        problem.addConstraint(ExactSumConstraint(Rows[row]),[row*TAM + col for col in range(0,TAM)])

    #Add the number of ship's in column
    for col in range (0,TAM):
        problem.addConstraint(ExactSumConstraint(Cols[col]),[col + row*TAM for row in range(0,TAM)])

    #GET SOlUTION, AND PRINT THAT
    solution=problem.getSolution()
    if not solution:
        print "No solution"
        exit()
    print Print_Solution(solution, TAM)


def main():
    TAM= random.randint(3, 4)
    Rows=[]
    Cols=[]
    for i in range (0, TAM):
        Rows.append(random.randint(0,4))
        Cols.append(random.randint(0,4))
    print "MAP"
    for i in range (0, TAM):
        for j in range (0, TAM):
            print 0,
        print Rows[i]
        print
    for i in range (0, TAM):
        print Cols[i],
    print

    Battle_Ship(Cols, Rows, len(Rows))

if __name__=="__main__":
    main()
